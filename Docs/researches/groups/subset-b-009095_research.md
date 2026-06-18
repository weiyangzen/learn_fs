# subset-b-009095 research

Grouped research report for WiredTiger tool helpers, binary/disaggregated decode utilities, RTS verifier scripts, TSAN playground files, tcmalloc helpers, MCP server tooling, and related tests. Each file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/disagg.py -->
# sources/storage-engines/wiredtiger/tools/py_common/disagg.py

Purpose: provides the common disaggregated-storage page decoding model used by both page-service JSON input and SQLite page-log input. It wraps page metadata and bytes, tracks table-level full/delta counts, and validates delta-chain ordering before delegating to the generic B-tree page decoder.

Important APIs and control flow: `UpdateTypeFlags` mirrors page service update-type constants. `Metadata` carries `lsn`, `page_id`, `table_id`, optional `base_lsn`/`backlink_lsn`, and a `delta` flag; `is_metadata_page()` treats table id 1 as a metadata file. `DisaggTableSummary.update_with_page()` accumulates full vs delta pages. `process_disagg_pages()` iterates a list of per-page chains, prints metadata, special-cases metadata pages by extracting an `addr="..."` root address, parses normal pages through `btree_format.WTPage.parse(disagg=True)`, validates base/delta magic numbers, validates previous checksum links within a delta chain, warns on write-generation ordering, prints either headers or full page contents, and returns the summary.

State and persistence behavior: no persistent state is written. The only mutable runtime state is the current `delta_chain` and the accumulated `DisaggTableSummary`. Output is written to stdout through `Printer`.

Dependencies and integration points: depends on `binary_data.BinaryFile`, `btree_format.WTPage`, `btree_format.BlockDisaggHeader`, `btree_format.DisaggAddr`, `DecodeOptions`, and `Printer`. It is called by `py_common.page_service.process_disagg_table()` and `py_common.sqlite_format.process_sqlite_file()`.

Risks: metadata-page parsing assumes an ASCII metadata string containing `addr="..."`; malformed metadata raises rather than producing a graceful diagnostic. Delta-chain validation logs errors but does not fail decoding. The write-generation ordering check is only as reliable as input ordering, which differs across page-service and SQLite sources. Metadata table id 1 is a convention embedded in code.

Test signals: `test_decode_disagg_delta_chain.py` expects one full-image block and ten delta blocks from a log dump. `test_decode_disagg_table.py` validates full/delta totals for encrypted page-service JSONL when `DISAGG_KEYFILE` is configured. `test_sqlite_format.py` exercises SQLite-to-`DisaggPage` chain construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/disagg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/file_format.py -->
# sources/storage-engines/wiredtiger/tools/py_common/file_format.py

Purpose: decodes ordinary WiredTiger `.wt` file objects or fragments into human-readable pages and optional CSV page statistics.

Important APIs and control flow: `file_header_decode()` parses `BlockFileHeader`, logs header fields, and validates magic, major/minor version, and unused bytes. `outfile_header()` writes CSV column names when `DecodeOptions.output` is present. `wtdecode_file_object()` creates a `Printer`, validates the file header when decoding from offset zero, aligns to the first block after a valid header, then loops over page starts until the byte limit or page limit is reached. Each iteration seeks to `startblock`, prints the decode address, parses a `WTPage`, prints page data or headers depending on options, emits CSV stats when available, and advances either to the parser's current position or by one 512-byte block to avoid stalling.

State and persistence behavior: input file position is mutated during scanning. Optional CSV output is appended to the passed output handle. The decoder has no repository or database persistence.

Dependencies and integration points: used by `wt_binary_decode.decode_wt_binary_input()` and `mdb_log_parse` for hex-dump fragments. It depends on `binary_data.d_and_h`, `btree_format.BlockFileHeader`, `btree_format.WTPage`, `Printer`, `DecodeOptions`, and `PageStats`.

Risks: on missing `python-snappy`, `ModuleNotFoundError` triggers `exit(1)`, which is abrupt for library callers. Generic decode exceptions are swallowed after logging and the scanner advances, so failures may be easy to miss unless verbose logging is enabled. Fragment handling relies on `opts.offset`, `opts.disagg`, and the parser position being sensible. CSV output has no quoting and assumes integer/string fields do not contain commas.

Test signals: `test_decode_page.py` validates page and block header fields from a known hex dump. Higher-level tests through `wt_binary_decode.wtdecode()` cover dump-in and disaggregated modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/file_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/mdb_log_parse.py -->
# sources/storage-engines/wiredtiger/tools/py_common/mdb_log_parse.py

Purpose: extracts raw WiredTiger block bytes from text logs, supporting both MongoDB structured JSON log entries and WiredTiger-style hex dumps, then sends the bytes through the page decoder as fragments.

Important APIs and control flow: `process_logs()` peeks at the first line and routes JSON-looking input to `process_mongod_log()` or other input to `process_wiredtiger_log()`. `extract_mongodb_log_hex()` scans JSON lines for `__wt_bm_corrupt_dump` messages, parses `{offset, size, checksum}: (chunk N of M): hexdata`, validates characters and expected byte size, and returns the first complete block. `encode_bytes()` decodes line-oriented hex dump chunks from the current file position, respecting optional chunk counters. `HexDumpCorruptError`, `validate_hexdata()`, and `validate_hex_block_size()` separate corrupt dump diagnostics from incidental parse failures.

State and persistence behavior: no persistent writes. File objects are advanced as blocks are consumed; JSON decode fallback can seek back to the start and parse as ordinary hex. Decoded bytes are transient `bytearray`/`bytes` buffers.

Dependencies and integration points: depends on `json`, `re`, `codecs`, `binary_data.BinaryFile`, `DecodeOptions`, and `file_format.wtdecode_file_object()`. It is selected by `wt_binary_decode` when `--dumpin` is passed and is directly used by `test_decode_page.py`.

Risks: MongoDB log detection is simply `line.startswith('{')`, so non-Mongo JSON logs may enter the structured parser. Regexes are tailored to current checksum-mismatch log text. Incomplete MongoDB blocks are returned with a warning rather than rejected. `encode_bytes()` strips all non-hex characters from the payload part, which is useful for noisy logs but can also decode unintended hex-looking text.

Test signals: `test_decode_log_mongodb.py` verifies corrupt non-hex, odd-length, and block-size-mismatch diagnostics; valid and incomplete cases are currently skipped under FIXME-WT-16726. `test_decode_page.py` uses `encode_bytes()` to decode `WiredTiger01.txt`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/mdb_log_parse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/page_service.py -->
# sources/storage-engines/wiredtiger/tools/py_common/page_service.py

Purpose: adapts Object Read Proxy/GetTableAtLSN JSONL output into decrypted `DisaggPage` objects for the disaggregated page decoder.

Important APIs and control flow: `extract_value()` unwraps typed metadata values from page-service JSON. `parse_metadata()` extracts page `lsn`, required `flags`, `page_id`, `table_id`, and optional `base_lsn`/`backlink_lsn`, mapping the delta flag to `disagg.Metadata`. `decrypt_page()` validates the external `pagedecryptor` binary and keyfile, writes page entry bytes as base64 to a temporary input, invokes `pagedecryptor` with page identity and chain metadata, and reads decrypted bytes from a temporary output. `process_disagg_table()` reads JSONL lines, converts each `entries` list into a page chain, skips empty entries, decrypts non-empty pages, and calls `disagg.process_disagg_pages()`.

State and persistence behavior: creates temporary files for decryption and deletes them automatically. It does not mutate source files or database state. It logs decryptor stdout/stderr at debug level and returns a `DisaggTableSummary`.

Dependencies and integration points: depends on MongoDB's external `pagedecryptor`, a KEK keyfile, `base64`, `json`, `subprocess`, `tempfile`, `DecodeOptions.keyfile`, and `py_common.disagg`. It is invoked from `wt_binary_decode` via `--disagg-table`.

Risks: decryption is unavailable unless the MongoDB encryption module tool is built and on `PATH`. Every page incurs a subprocess call, which is expensive for large tables. Metadata unwrapping assumes a single value inside `metadata[key]["val"]`. The temporary output file is opened before the subprocess writes it; this works for normal files but is sensitive to platform semantics. Decrypt failures propagate after logging.

Test signals: `test_decode_disagg_table.py` skips unless `DISAGG_KEYFILE` is set, then expects 8 total pages, 2 delta pages, and 6 full pages from `disagg_oplog.jsonl`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/page_service.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/printer.py -->
# sources/storage-engines/wiredtiger/tools/py_common/printer.py

Purpose: centralizes formatted decode output for binary page tooling, including split raw-byte annotations, cell numbering, packed integer/string heuristics, and binary hex dumps.

Important APIs and control flow: `Printer.begin_cell()` records a cell prefix and resets saved bytes; `end_cell()` clears cell state; `rint()` prints saved input bytes alongside decoded text when split mode is enabled, then prints the requested line with cell indentation. `raw_bytes()` tries to describe byte strings as packed integers followed by UTF-8 text, falling back to `binary_to_pretty_string()`. `binary_to_pretty_string()` renders bytes as hex plus printable ASCII columns. `dumpraw_to_log()` preserves the input file position, reads 256 bytes around a position, and logs a formatted dump.

State and persistence behavior: `Printer` holds transient output formatting state (`cellpfx`, `in_cell`) and reads saved-byte state from its `BinaryFile`. It writes to stdout and logger only.

Dependencies and integration points: used by `file_format`, `disagg`, and `btree_format` page/cell printing. It depends on `binary_data.unpack_int()` and `binary_data.BinaryFile.saved_bytes()`.

Risks: `raw_bytes()` uses heuristics, so packed integers and strings can be misclassified; `btree_format` already notes a FIXME around this behavior. `rint()` prints directly rather than using a provided stream, which limits reuse and test capture options. Bare `except` in string decoding hides the specific decode failure.

Test signals: there are no direct unit tests in this subset. Indirect coverage comes from decode tests that assert output content or parse pages after printing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/printer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/snappy_util.py -->
# sources/storage-engines/wiredtiger/tools/py_common/snappy_util.py

Purpose: handles WiredTiger page payload decompression for pages compressed with Snappy and provides detailed diagnostics when decompression fails.

Important APIs and control flow: import-time detection sets `HAVE_SNAPPY`. `snappy_decompress_page()` preserves the uncompressed prefix up to the 64-byte compression skip, reads WiredTiger's stored compressed byte count, calculates the remaining block length, reads enough bytes for either interpretation, seeks to the end of the disk block, and tries Snappy validation/decompression first with the stored length and then with calculated length. On failure it calls `print_snappy_diagnostics()` and returns only the uncompressed prefix. `decode_snappy_varint()` parses Snappy's uncompressed-length varint. `print_snappy_diagnostics()` logs compressed sizes, expected uncompressed size, and selected backreference/output-position details from `snappy.UncompressError`.

State and persistence behavior: mutates the `BinaryFile` read position to the end of the page block. It does not write persistent state. Diagnostics go to logging and some lower-level code may print via the page decoder.

Dependencies and integration points: imported by `btree_format.WTPage.parse()` for compressed pages. `wt_binary_decode.feature_check()` warns when Snappy support is missing. It requires `python-snappy` when compressed pages must be decoded.

Risks: missing Snappy support raises `ModuleNotFoundError` from `snappy_decompress_page()` and may terminate the top-level file decode. Failed decompression returns partial page bytes rather than a hard failure, so callers may continue with incomplete data. The stored-vs-calculated length fallback is diagnostic-friendly but may mask format drift if both happen to decode.

Test signals: no direct Snappy tests are in this subset. Runtime signal is successful compressed-page decoding plus absence of feature-check warnings when `python-snappy` is installed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/snappy_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/sqlite_format.py -->
# sources/storage-engines/wiredtiger/tools/py_common/sqlite_format.py

Purpose: detects and reads SQLite page-log databases containing disaggregated page records, reconstructing page chains for the shared disaggregated decoder.

Important APIs and control flow: `is_sqlite3_file()` checks the SQLite signature unless stdin is used. `_load_rows_for_page()` finds non-discarded base pages for a page id, warns when multiple bases exist, picks the newest base LSN, and returns rows at or after that base in descending LSN order. `_load_row_for_lsn()` selects one non-discarded row. `_rows_to_disagg_pages()` converts SQLite rows into `disagg.DisaggPage` objects using `WT_PAGE_LOG_DELTA`. `_load_disagg_pages_all()`, `_load_disagg_pages_for_lsn()`, and `_load_disagg_pages_for_page_id()` implement the selection modes. `load_disagg_pages()` gives LSN precedence over page-id chain traversal. `process_sqlite_file()` feeds loaded chains to `disagg.process_disagg_pages()`.

State and persistence behavior: opens SQLite read connections and returns in-memory page chains. It does not modify the SQLite database. Page limits apply to loaded row count during all-pages mode.

Dependencies and integration points: selected automatically by `wt_binary_decode` when the input file signature matches SQLite. Depends on `sqlite3`, `DecodeOptions`, and `py_common.disagg`.

Risks: the schema is assumed to contain `pages(table_id,page_id,lsn,backlink_lsn,base_lsn,flags,discarded,page_data)`. Multiple base page handling chooses the newest and only logs a warning. Rows are ordered by `lsn DESC`, not by explicitly following `backlink_lsn`, so malformed chains may still be decoded in timestamp order. All-pages mode iterates distinct page ids without deterministic ordering.

Test signals: `test_sqlite_format.py` covers signature detection, latest-base selection, LSN precedence, page limit behavior, discarded-row filtering, base-chain ordering, and page-id/LSN mismatch errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/sqlite_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/stats.py -->
# sources/storage-engines/wiredtiger/tools/py_common/stats.py

Purpose: stores and emits per-page decode statistics for keys, timestamp metadata, durable timestamp metadata, and transaction IDs.

Important APIs and control flow: `PageStats` is a dataclass with counters and byte-size accumulators for keys, durable start/stop timestamps, start/stop timestamps, and start/stop transaction ids. Computed properties `num_ts`, `ts_sz`, `num_txn`, and `txn_sz` aggregate related counters. `csv_cols()` and `to_csv_cols()` define the CSV schema. `outfile_stats_start()` and `outfile_stats_end()` write block/page/stat columns to an optional output handle. `process_timestamps()` inspects parsed cell attributes with `getattr()` and increments the relevant counters and sizes.

State and persistence behavior: instances are mutable accumulators attached to a decoded page. Optional CSV writing is the only external side effect.

Dependencies and integration points: `btree_format.Cell.process_timestamps()` and `WTPage` populate these stats, while `file_format.wtdecode_file_object()` writes them when `--csv` is passed.

Risks: CSV schema alignment depends on `file_format.outfile_header()` matching `outfile_stats_end()`. Prepared update fields are present but marked as not currently reported in comments. `process_timestamps()` relies on dynamic cell attributes, so missing or renamed fields silently count as absent.

Test signals: no direct unit test in this subset validates CSV output. Indirect signal is non-null `page.pagestats` during successful page decode and stable CSV column count when `--csv` is used.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/wiredtiger_util.py -->
# sources/storage-engines/wiredtiger/tools/py_common/wiredtiger_util.py

Purpose: locates and imports the built WiredTiger Python extension for scripts that need `wiredtiger_open`.

Important APIs and control flow: `setup_python_path()` walks upward from the current working directory until it finds a built `wt` or `wt.exe`, then inserts `<build>/lang/python` into `sys.path`; if no build root is found it prints an error and exits. `import_wiredtiger()` first tries `from wiredtiger import wiredtiger_open`, falls back to `setup_python_path()`, then retries. Module import binds the exported name `wiredtiger_open`.

State and persistence behavior: mutates process-global `sys.path` and may terminate the process. It does not write files or database state.

Dependencies and integration points: intended for Python tools run from a WiredTiger build directory. It integrates with the generated/built `wiredtiger` Python module under `lang/python`.

Risks: import-time side effects mean merely importing this module can exit the process. The build-root search is based on `os.getcwd()`, not the script location. Inserting at index 1 may interact with other path entries in surprising ways.

Test signals: no direct tests are present. Practical validation is importing from both a configured Python path and a build directory where `wt` exists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/py_common/wiredtiger_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/pytest_parallel -->
# sources/storage-engines/wiredtiger/tools/pytest_parallel

Purpose: runs selected WiredTiger Python suite tests in parallel from a build directory while labeling output and preserving per-test WT home directories.

Important APIs and control flow: shell functions `Usage()`, `waitone()`, `showprocs()`, and `label_output()` handle help, error attribution, progress diagnostics, and output prefixing. Argument parsing accepts `-j`, `--python`, `--help`, arbitrary `run.py` options before `--`, and test filenames after `--`. It requires a local `wt` executable, deletes `WT_TEST.*`, then starts `../test/suite/run.py -D WT_TEST.<test> --noremove ...` jobs up to the parallel limit. `waitone()` uses `wait -n`, compares job lists before/after, records failed process names, and exits nonzero if any failed.

State and persistence behavior: deletes `WT_TEST.*` in the build directory, creates per-test `WT_TEST.<pyfile>` homes, and may create TSAN log directories when `TESTUTIL_TSAN=1`. It mutates `TSAN_OPTIONS` while launching tests and restores it afterward.

Dependencies and integration points: depends on Bash job control, associative arrays, `nproc`, `sed`, `git rev-parse` for TSAN log paths, Python, and WiredTiger `test/suite/run.py`. It is a faster alternative to `run.py -j` for independent test scripts.

Risks: deleting `WT_TEST.*` is broad. `waitone()` can misattribute failures if multiple jobs exit between before/after snapshots. Test names are used in directory and log path construction. It must run from a build directory, not the source root.

Test signals: success prints `Success`; failures print labeled output and a summary. Useful validation is running a small pair of known passing tests with `-j 2`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/pytest_parallel -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/basic_types.py -->
# sources/storage-engines/wiredtiger/tools/rts_verifier/basic_types.py

Purpose: defines the small domain model used by the rollback-to-stable verbose-log verifier.

Important APIs and control flow: enums `PrepareState`, `UpdateType`, and `PageType` mirror WiredTiger RTS values seen in verbose messages. `Timestamp` stores `(start, stop)` pairs and implements equality and ordering by tuple comparison. `Tree` stores a filename and mutable `logged` flag, with equality/hash based on file. `Page` stores an address and mutable `modified` flag, with equality/hash based on address.

State and persistence behavior: instances are in-memory only. `Tree.logged` and `Page.modified` are populated by `Checker` as log lines are processed.

Dependencies and integration points: imported by `operation.py` for parsing enum names and by `checker.py` for visited tree/page tracking.

Risks: enum values must stay synchronized with logged symbol names and parser expectations. `Tree.__eq__` and `Page.__eq__` assume `other` has the same attributes. Timestamp ordering is lexicographic and does not encode any WiredTiger-specific timestamp validity rules.

Test signals: no direct tests in this subset. Parser failures in `Operation` are the main signal that enum names drifted.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/basic_types.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/checker.py -->
# sources/storage-engines/wiredtiger/tools/rts_verifier/checker.py

Purpose: applies semantic checks to parsed rollback-to-stable verbose operations. In current form it is mostly a scaffold: it tracks stable timestamp, current tree, visited trees, and visited pages, while many intended assertions are disabled under PM-3095 comments or TODO placeholders.

Important APIs and control flow: `Checker.apply()` dispatches by `operation.type.name.lower()` to private `__apply_check_*` methods. `__apply_check_init()` resets stable/current state. `__apply_check_tree()` records the current `Tree` and could validate visit necessity and durable/stable comparisons. `__apply_check_tree_logging()` tracks logging state. `__apply_check_page_rollback()` records page address and modified state. `__apply_check_update_abort()`, `__apply_check_page_abort_check()`, and `__apply_check_key_clear_remove()` compute rollback/abort expectations but currently suppress errors. Remaining handlers exist for all parsed RTS operation types and mostly pass.

State and persistence behavior: all state is in-memory and scoped to one checker instance. No output is produced unless a check raises; currently most checks are disabled.

Dependencies and integration points: consumed by `rts_verify.py`, with operation classes from `operation.py` and basic types from `basic_types.py`. It integrates with WiredTiger verbose logging containing `WT_VERB_RTS`.

Risks: because most assertions are commented out, a successful run mostly proves that log lines were parseable, not that RTS behavior was correct. Dispatch through private method naming raises if an operation lacks a handler. Some check methods refer to properties such as `operation.needs_abort` that may not be initialized by the parser for the relevant operation, but disabled code hides the issue.

Test signals: there are no direct unit tests. Meaningful validation would require fixture logs for each operation type and expected pass/fail cases once PM-3095 checks are enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/checker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/operation.py -->
# sources/storage-engines/wiredtiger/tools/rts_verifier/operation.py

Purpose: parses individual `WT_VERB_RTS` verbose log lines into typed operation objects with fields used by the checker.

Important APIs and control flow: `OpType` enumerates RTS message categories. `Operation.__init__()` extracts the bracketed RTS message name with a regex, lowercases it, dispatches to `__init_<name>()`, and leaves parsed attributes on `self`. Helpers parse file/tiered names, timestamp tuples, and pointer values with platform-specific pointer formats. The many `__init_*` methods parse tree visits, logging state, page rollback, update aborts, page abort checks, history-store updates, checkpoint recovery, stable timestamp state, page delete, update-chain verify, and other RTS messages. `_TIME_WINDOW_REGEX` centralizes parsing of verbose time-window structures.

State and persistence behavior: each `Operation` is immutable by convention after parsing but stored as a regular object with dynamic attributes. It does not write files or external state.

Dependencies and integration points: imported by `rts_verify.py` and `checker.py`. It depends on exact text formats emitted by WiredTiger RTS verbose logging and enums from `basic_types.py`.

Risks: parsing is brittle: most regex matches are used without checking for `None`, so message-format drift crashes verification. Some handlers appear to set incorrect types or fields, such as `__init_hs_update_restored()` setting `OpType.HS_UPDATE_VALID`, `__init_stable_pg_walk_skip()` setting `KEY_REMOVED`, and several copied timestamp assignments using start values for stop fields. `SKIP_DEL = 45,` creates a tuple value in the enum definition. Some boolean parses use `.lower` without calling it. These risks matter more once semantic checking is enabled.

Test signals: no direct tests are present. A robust test suite should feed representative `WT_VERB_RTS` lines for every `OpType`, assert parsed fields, and assert parser failures for malformed lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/operation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/rts_verify.py -->
# sources/storage-engines/wiredtiger/tools/rts_verifier/rts_verify.py

Purpose: command-line entry point for verifying rollback-to-stable verbose logs.

Important APIs and control flow: parses a single positional log file argument, constructs a `Checker`, reads the file line by line, and for each line containing `WT_VERB_RTS` creates an `Operation` and applies it to the checker.

State and persistence behavior: read-only over the input log. Checker state accumulates in memory for the duration of the process. No output is emitted on success.

Dependencies and integration points: depends on sibling modules `checker` and `operation`. It is intended for logs generated with WiredTiger RTS verbose logging enabled.

Risks: there is no summary output, no count of processed lines, and no controlled error reporting around parser/checker exceptions. Because `checker.py` mostly suppresses assertions, a zero exit code currently means parse success more than semantic correctness.

Test signals: no direct tests. A useful smoke test is running it against a fixture log containing at least one line for each supported RTS operation and confirming nonzero behavior on malformed text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/rts_verifier/rts_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/run_parallel.sh -->
# sources/storage-engines/wiredtiger/tools/run_parallel.sh

Purpose: repeats an arbitrary shell command for a number of iterations, running multiple parallel copies per iteration.

Important APIs and control flow: validates at least command and iteration count, derives CPU count from `/proc/cpuinfo`, defaults parallelism to half the cores, prints the run configuration, appends iteration markers to `outfile.txt`, shows `df -h .`, launches `num_parallel` copies through `eval nohup $command > nohup.out.$t 2>&1 &`, waits for all PIDs, and on first nonzero exit prints the last 100 lines of that worker's output and exits with the worker status.

State and persistence behavior: writes or appends `outfile.txt` and overwrites `nohup.out.<slot>` in the current directory. It does not clean prior outputs.

Dependencies and integration points: uses Bash, Linux `/proc/cpuinfo`, `seq`, `df`, `nohup`, and shell `eval`. It is a generic stress/repro harness for WiredTiger commands or tests.

Risks: `eval` on the command string means shell metacharacters are interpreted, so callers must treat input as trusted. The Linux-only CPU detection can fail elsewhere, producing weak defaults. Parallel slot outputs are overwritten each iteration. A single failure stops all later iterations but only after the current set has been waited in sequence.

Test signals: visible iteration markers, per-slot `nohup.out.*`, and exit status provide validation. Running `./run_parallel.sh 'true' 1 2` should complete with zero status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/run_parallel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tcmalloc/build-tcmalloc.sh -->
# sources/storage-engines/wiredtiger/tools/tcmalloc/build-tcmalloc.sh

Purpose: builds a patched `libtcmalloc.so` for a WiredTiger workspace from a supplied source archive URL and source-directory name, placing the result in `TCMALLOC_LIB`.

Important APIs and control flow: runs with `set -euf -o pipefail` and a `die()` helper. It requires exactly `url srcdir`, verifies the repository top level with `git rev-parse`, checks for `CMakeLists.txt`, refuses to overwrite an existing `TCMALLOC_LIB`, requires `bazel` and `/opt/mongodbtoolchain/v5/bin`, downloads the tarball with retrying `curl`, extracts it, writes a Bazel `BUILD` file defining `cc_shared_library(name="libtcmalloc")`, builds with the MongoDB toolchain prepended to `PATH`, then creates `TCMALLOC_LIB` and copies `bazel-bin/libtcmalloc.so`.

State and persistence behavior: downloads an archive into the current working directory, extracts a source tree, writes `${srcdir}/BUILD`, creates `TCMALLOC_LIB`, and copies the shared library there.

Dependencies and integration points: depends on MongoDB toolchain v5, Bazel, curl, tar, git, and the patched tcmalloc archive referenced by Evergreen scripts. The output integrates with `define-with_tcmalloc.sh` and `LD_PRELOAD` workflows.

Risks: it writes into the extracted source tree and current workspace without cleanup. The expected toolchain path is hard-coded. The `srcdir` argument must match the tarball's top-level directory. The comments explicitly prefer prebuilt tcmalloc on spawn hosts, suggesting this is a fallback.

Test signals: successful build leaves `TCMALLOC_LIB/libtcmalloc.so`. Fail-fast checks cover missing workspace, duplicate output, missing Bazel, and missing toolchain.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tcmalloc/build-tcmalloc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tcmalloc/define-with_tcmalloc.sh -->
# sources/storage-engines/wiredtiger/tools/tcmalloc/define-with_tcmalloc.sh

Purpose: defines a shell helper function that runs commands with the workspace's built `libtcmalloc.so` preloaded.

Important APIs and control flow: intended to be sourced, not executed. It finds the git top level, checks `${TOP__}/TCMALLOC_LIB/libtcmalloc.so`, then uses `eval` to define `with_tcmalloc() { LD_PRELOAD=$SO__:$LD_PRELOAD "$@"; }`, and unsets temporary variables.

State and persistence behavior: mutates the current shell by defining `with_tcmalloc`. It does not write files.

Dependencies and integration points: pairs with `build-tcmalloc.sh` output. It depends on Git and dynamic linker `LD_PRELOAD` behavior.

Risks: `if ! [[ $? ]]; then` does not robustly test `git rev-parse` failure because `$?` is numeric and non-empty; however command substitution failure may still leave unusable paths. `LD_PRELOAD=$SO__:$LD_PRELOAD` can introduce a trailing empty path component. `return` requires sourcing; executing the script directly from a shell may produce return errors.

Test signals: after sourcing from a repo with `TCMALLOC_LIB/libtcmalloc.so`, `type with_tcmalloc` should show the function and `with_tcmalloc env` should include the shared library in `LD_PRELOAD`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tcmalloc/define-with_tcmalloc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_chain.py -->
# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_chain.py

Purpose: unit test for decoding a disaggregated delta-chain log through the top-level binary decoder.

Important APIs and control flow: appends the tools directory to `sys.path`, imports `wt_binary_decode` and `DecodeOptions`, locates `binary_files/disagg_delta_chain.log`, captures stdout with `contextlib.redirect_stdout`, calls `wt_binary_decode.wtdecode(log_path, DecodeOptions(disagg=True, dumpin=True))`, then asserts non-empty output, one full-image magic string, and exactly ten delta magic strings.

State and persistence behavior: read-only over the fixture log. It captures output in memory and writes nothing persistent.

Dependencies and integration points: exercises `wt_binary_decode`, `mdb_log_parse`, `file_format`, `disagg` mode page parsing, and `btree_format` disaggregated block headers.

Risks: asserts on formatted output strings rather than structured decode results, so wording changes can break the test. It does not assert checksum-chain diagnostics or decoded cell content.

Test signals: pass confirms the fixture is available and the decode stack recognizes base and delta block magic values in the expected counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_chain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_page.py -->
# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_page.py

Purpose: unit test for parsing a single disaggregated delta page binary fixture.

Important APIs and control flow: locates `binary_files/disagg_delta_oplog.bin`, wraps it in `binary_data.BinaryFile`, calls `btree_format.WTPage.parse(..., disagg=True)`, prints the page with BSON decoding enabled, and asserts page header fields, block disaggregated header fields, checksum flags, cell count, key/value cell roles, value data length, and a known start timestamp.

State and persistence behavior: read-only over the binary fixture; stdout printing is incidental.

Dependencies and integration points: directly tests `py_common.btree_format` and `py_common.binary_data` disaggregated page support, indirectly depending on optional BSON support for printed output only.

Risks: fixture-specific constants make the test precise but brittle to intentional fixture replacement. It does not verify the complete decoded BSON payload.

Test signals: pass validates delta magic/version/header-size/checksum parsing, page header decoding, cell extraction, and timestamp parsing for delta pages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_delta_page.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_table.py -->
# sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_table.py

Purpose: integration-style unit test for decoding an encrypted disaggregated table JSONL fixture through the page-service adapter.

Important APIs and control flow: requires `DISAGG_KEYFILE`; otherwise it skips. It opens `binary_files/disagg_oplog.jsonl`, calls `page_service.process_disagg_table(disagg_file, DecodeOptions(keyfile=keyfile, bson=True))`, and asserts the returned summary has 2 delta pages, 6 full pages, and 8 total pages.

State and persistence behavior: read-only over the JSONL fixture and keyfile. The underlying page-service code creates temporary decryptor files.

Dependencies and integration points: exercises `page_service`, external `pagedecryptor`, `disagg.process_disagg_pages`, and the BSON decode path. It is sensitive to the MongoDB encryption-module toolchain being installed.

Risks: skipped by default without environment setup, so CI may not cover this path. It validates counts, not full decoded content or metadata-page root address behavior.

Test signals: when enabled, pass confirms decryptor integration and full/delta page classification for the sample table.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_disagg_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_log_mongodb.py -->
# sources/storage-engines/wiredtiger/tools/test/test_decode_log_mongodb.py

Purpose: tests MongoDB JSON log hex-dump validation and error logging for corrupt checksum-mismatch dumps.

Important APIs and control flow: `setUp()` records the binary fixture directory. `run_decode()` captures stdout and `py_common.mdb_log_parse` INFO logs while calling `wt_binary_decode.wtdecode(log_path, DecodeOptions(dumpin=True))`. Three active tests assert diagnostics for non-hex characters, odd-length hex, and block-size mismatch. Valid, multi-chunk valid, incomplete-chunk, and no-checksum-mismatch tests are present but skipped under FIXME-WT-16726.

State and persistence behavior: read-only over log fixtures; captures output/logs in memory.

Dependencies and integration points: exercises `wt_binary_decode` dump-in routing and `mdb_log_parse.extract_mongodb_log_hex()` corruption paths.

Risks: most positive-path coverage is skipped, leaving successful MongoDB log extraction under-tested. Assertions depend on exact log message substrings. The helper captures INFO logs but not DEBUG details that could aid diagnosis.

Test signals: active tests confirm corrupt input returns no valid byte dump and logs the specific validation error class.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_log_mongodb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_page.py -->
# sources/storage-engines/wiredtiger/tools/test/test_decode_page.py

Purpose: unit test for decoding one ordinary WiredTiger page from a text hex dump fixture.

Important APIs and control flow: `load_page_bytes()` reads `binary_files/WiredTiger01.txt` and decodes it with `mdb_log_parse.encode_bytes()`. The test wraps bytes in `BinaryFile`, parses a `WTPage` with `skip_data=True`, then asserts page header fields (`recno`, `write_gen`, `mem_size`, entries, type, flags, version) and block header fields (`disk_size`, checksum, flags).

State and persistence behavior: read-only fixture use and in-memory decode only.

Dependencies and integration points: validates `mdb_log_parse.encode_bytes()`, `binary_data.BinaryFile`, and `btree_format.WTPage.parse()` for standard blocks.

Risks: header-only parsing does not validate cell decoding or payload display. The fixture constants encode one page layout and do not cover compressed or corrupted blocks.

Test signals: pass confirms the basic non-disaggregated page parser still matches the known fixture.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_decode_page.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_sqlite_format.py -->
# sources/storage-engines/wiredtiger/tools/test/test_sqlite_format.py

Purpose: unit tests for SQLite disaggregated page-log loading and selection semantics.

Important APIs and control flow: `_create_test_db()` creates a temporary SQLite database with a `pages` table and sample rows covering base pages, deltas, multiple bases, and discarded records. Tests cover `is_sqlite3_file()`, newest-base selection with warning, LSN-specific selection, single-base selection, all-pages page limit, LSN without page id, discarded-row filtering, page-id chain ordering, and page-id/LSN mismatch errors. `tearDown()` removes the temp database.

State and persistence behavior: creates and deletes a temporary `.db` file for each test case. No repository files are modified.

Dependencies and integration points: directly covers `py_common.sqlite_format` and indirectly verifies conversion to `disagg.DisaggPage` metadata.

Risks: the synthetic `page_data` is arbitrary bytes, so these tests validate row selection and metadata conversion rather than downstream page parsing. Multiple-base behavior is intentionally warning-and-select-newest; future stricter semantics would require test changes.

Test signals: pass provides strong coverage for SQLite query filters, discarded handling, page/LSN precedence, and delta flag conversion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/test/test_sqlite_format.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/CMakeLists.txt

Purpose: declares a build matrix of TSAN playground executables, each compiling the same `tsan_playground.c` with a different atomic/barrier API implementation macro.

Important APIs and control flow: sets C standard to C11, then calls `create_test_executable()` for C11 atomics, C11 acq/rel barriers, C11 full barriers, GCC atomics, GCC acq/rel barriers, GCC full barriers, WT atomics, WT acq/rel barriers, WT store/load-with-barriers, WT full barriers, and dummy atomics. GCC barrier variants add `-Wno-error=tsan` because TSAN warns about unsupported `atomic_thread_fence`.

State and persistence behavior: build-system only; it produces executables under the build tree.

Dependencies and integration points: depends on the repository's CMake `create_test_executable` helper and the header variants in the same directory. The executables are consumed by `collect_warnings.sh`.

Risks: targets using WT headers require include paths and generated headers supplied by the broader WiredTiger build. The matrix can compile but still have different TSAN runtime behavior, so build success is not enough.

Test signals: successful CMake configuration/build creates `tools/tsan_playground/tsan_playground_*` executables. Runtime signal comes from `collect_warnings.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_acq_rel_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_acq_rel_barriers.h

Purpose: implements the TSAN playground atomic API using C11 relaxed load/store plus separate acquire/release fences.

Important APIs and control flow: defines `atomic_t` as `atomic_uint_fast64_t`, `value_t` as `uint64_t`, `ATOMIC_DEFINE`, `atomic_store_release()` with `atomic_thread_fence(memory_order_release)` followed by relaxed store, `atomic_load_acquire()` with relaxed load followed by acquire fence, and `get_mode()`.

State and persistence behavior: only manipulates caller-provided atomic variables in memory.

Dependencies and integration points: included by `tsan_playground.c` when `_C11_ACQ_REL_BARRIERS` is defined. Requires C11 `<stdatomic.h>`.

Risks: fence-plus-relaxed patterns are exactly what the playground is meant to study; TSAN may not model them the same as acquire/release atomics. `atomic_uint_fast64_t` may not be exactly 64 bits on all platforms, though values are used as counters.

Test signals: executable should print `Implementation: C11 acq/rel barriers`; TSAN warnings collected by `collect_warnings.sh` indicate whether this synchronization is recognized.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_acq_rel_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_atomics.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_atomics.h

Purpose: implements the TSAN playground atomic API using native C11 acquire/release atomic operations.

Important APIs and control flow: defines `atomic_t`, `value_t`, `ATOMIC_DEFINE`, `atomic_store_release()` as `atomic_store_explicit(..., memory_order_release)`, `atomic_load_acquire()` as `atomic_load_explicit(..., memory_order_acquire)`, and `get_mode()`.

State and persistence behavior: only updates the shared counter used by the playground.

Dependencies and integration points: included by `tsan_playground.c` under `_C11_ATOMICS`; requires `<stdatomic.h>`.

Risks: this is the baseline standard-atomic implementation and should be TSAN-friendly. Portability risk is mainly compiler/library C11 atomic support.

Test signals: executable label is `C11 atomics`; expected runtime behavior is no data-race warning for the protected shared message/position accesses.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_atomics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_full_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_full_barriers.h

Purpose: implements the TSAN playground atomic API using C11 sequentially consistent fences around relaxed access.

Important APIs and control flow: `atomic_store_release()` issues `atomic_thread_fence(memory_order_seq_cst)` then relaxed store. `atomic_load_acquire()` performs relaxed load then seq-cst fence. `get_mode()` returns `C11 full barriers`.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_C11_FULL_BARRIERS` in `tsan_playground.c`; requires C11 atomics.

Risks: full fences may be stronger architecturally but still may not create a TSAN-recognized synchronization relation around relaxed accesses. Runtime warnings are the point of this variant.

Test signals: build plus `collect_warnings.sh` output identifies whether TSAN reports races for this barrier style.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_full_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_dummy.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_dummy.h

Purpose: intentionally unsynchronized implementation of the playground atomic API, used as a negative control.

Important APIs and control flow: defines `atomic_t` and `value_t` as plain `uint64_t`, `ATOMIC_DEFINE` as a static plain variable, `atomic_store_release()` as `*var = value`, `atomic_load_acquire()` as `return *var`, and `get_mode()`.

State and persistence behavior: mutates shared memory without atomics or barriers.

Dependencies and integration points: selected by `_DUMMY_ATOMICS` or as the fallback include for editor parsing before the compile-time `#error` in `tsan_playground.c`.

Risks: it intentionally contains data races and should not be used as a synchronization template.

Test signals: TSAN should report warnings for the dummy executable; absence of warnings would indicate the playground or sanitizer setup is ineffective.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_dummy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_acq_rel_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_acq_rel_barriers.h

Purpose: implements the playground API using GCC `__atomic` relaxed accesses plus acquire/release fences.

Important APIs and control flow: defines plain `uint64_t` storage, stores with `__atomic_thread_fence(__ATOMIC_RELEASE)` followed by `__atomic_store_n(..., __ATOMIC_RELAXED)`, and loads with relaxed `__atomic_load_n()` followed by `__atomic_thread_fence(__ATOMIC_ACQUIRE)`. `get_mode()` labels the implementation.

State and persistence behavior: in-memory counter synchronization only.

Dependencies and integration points: compiled under `_GCC_ACQ_REL_BARRIERS`; requires GCC/Clang support for `__atomic` builtins.

Risks: TSAN commonly warns that fences are not supported or are not sufficient for race modeling, hence the CMake target suppresses `-Werror=tsan`. This variant is diagnostic, not a recommended pattern without verifying sanitizer behavior.

Test signals: `collect_warnings.sh` should show whether TSAN reports races or unsupported-fence summaries for this executable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_acq_rel_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_atomics.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_atomics.h

Purpose: implements the playground API using GCC `__atomic` acquire/release load/store builtins.

Important APIs and control flow: `atomic_store_release()` calls `__atomic_store_n(var, value, __ATOMIC_RELEASE)`, `atomic_load_acquire()` calls `__atomic_load_n(var, __ATOMIC_ACQUIRE)`, and `get_mode()` returns `GCC atomics`.

State and persistence behavior: only updates in-memory shared counter state.

Dependencies and integration points: selected by `_GCC_ATOMICS`; requires compiler support for GNU atomic builtins.

Risks: this is the GNU builtin baseline and should be understood by TSAN, but behavior depends on compiler and sanitizer instrumentation.

Test signals: expected to run without TSAN data-race warnings if the acquire/release counter correctly orders message writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_atomics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_full_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_full_barriers.h

Purpose: implements the playground API using GCC sequentially consistent fences around relaxed access.

Important APIs and control flow: `atomic_store_release()` executes `__atomic_thread_fence(__ATOMIC_SEQ_CST)` then relaxed store. `atomic_load_acquire()` performs relaxed load then a seq-cst fence. `get_mode()` labels the variant.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_GCC_FULL_BARRIERS`; CMake suppresses TSAN warning-as-error for this target.

Risks: full barriers may not be represented as sanitizer synchronization around relaxed operations. This is a comparison target for TSAN behavior rather than a production abstraction.

Test signals: runtime TSAN summaries from `collect_warnings.sh` indicate whether the sanitizer accepts or flags this style.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_full_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_acq_rel_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_acq_rel_barriers.h

Purpose: adapts the playground API to WiredTiger's acquire/release barrier macros plus relaxed WT atomic helpers.

Important APIs and control flow: includes `wt_internal.h`, defines plain `uint64_t` storage, uses `WT_RELEASE_BARRIER()` before `__wt_atomic_store_uint64_relaxed()`, and uses `__wt_atomic_load_uint64_relaxed()` followed by `WT_ACQUIRE_BARRIER()` for loads. `get_mode()` labels `WT acq/rel barriers`.

State and persistence behavior: in-memory shared counter synchronization only.

Dependencies and integration points: selected by `_WT_ACQ_REL_BARRIERS`; depends on WiredTiger internal headers and atomic macros from the build.

Risks: sanitizer recognition of WT barrier macros is the key uncertainty. The variant also depends on internal header include paths and macro definitions, so it is build-tree dependent.

Test signals: comparing its TSAN warnings to C11/GCC barrier variants indicates whether WT barrier macros are sanitizer-visible enough for this pattern.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_acq_rel_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_atomics.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_atomics.h

Purpose: implements the playground API using WiredTiger's internal acquire/release uint64 atomic helpers.

Important APIs and control flow: `atomic_store_release()` calls `__wt_atomic_store_uint64_release()`, `atomic_load_acquire()` calls `__wt_atomic_load_uint64_acquire()`, and `get_mode()` returns `WT atomics`.

State and persistence behavior: in-memory counter synchronization only.

Dependencies and integration points: selected by `_WT_ATOMICS`; requires `wt_internal.h` and the repository's configured atomic abstraction.

Risks: this tests whether WT's native atomic helpers are both correct and visible to TSAN. It is not standalone outside a WiredTiger build.

Test signals: expected no TSAN data-race warnings if WT acquire/release helpers map to sanitizer-recognized operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_atomics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_full_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_full_barriers.h

Purpose: implements the playground API using WiredTiger full barriers around relaxed WT atomic accesses.

Important APIs and control flow: `atomic_store_release()` calls `WT_FULL_BARRIER()` then `__wt_atomic_store_uint64_relaxed()`. `atomic_load_acquire()` uses relaxed load then `WT_FULL_BARRIER()`. `get_mode()` labels the variant.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_WT_FULL_BARRIERS`; depends on WT internal barrier and atomic macros.

Risks: like the other fence variants, architectural ordering and TSAN modeling may diverge. Full barriers can also be more expensive than necessary if used as a production pattern.

Test signals: `collect_warnings.sh` shows whether TSAN accepts this WT full-barrier pattern or reports races.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_full_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_store_load_with_barriers.h -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_store_load_with_barriers.h

Purpose: implements the playground API with WiredTiger combined store/load barrier macros rather than explicit relaxed atomics plus separate barriers.

Important APIs and control flow: `atomic_store_release()` uses `WT_RELEASE_WRITE_WITH_BARRIER(*var, value)`. `atomic_load_acquire()` uses `WT_ACQUIRE_READ_WITH_BARRIER(result, *var)` and returns the loaded value. `get_mode()` currently returns the same `WT acq/rel barriers` label as another variant.

State and persistence behavior: mutates caller-provided in-memory counter state.

Dependencies and integration points: selected by `_WT_STORE_LOAD_WITH_BARRIERS`; depends on WT internal macros from `wt_internal.h`.

Risks: duplicate `get_mode()` label can make `collect_warnings.sh` output ambiguous between this target and `api_wt_acq_rel_barriers.h`. Correctness depends on macro expansion and sanitizer visibility.

Test signals: target-specific executable name plus collected TSAN summaries are needed because the printed implementation label is not unique.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_store_load_with_barriers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/collect_warnings.sh -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/collect_warnings.sh

Purpose: runs all built TSAN playground executables and summarizes ThreadSanitizer warnings for each implementation variant.

Important APIs and control flow: assumes it is run from a build folder, scans `./tools/tsan_playground/tsan_playground_*`, resolves each executable path, runs it with a five-second `timeout`, extracts the `Implementation:` label and `SUMMARY: ThreadSanitizer:` lines, reports timeout/completed/error status and exit code, then prints warnings or `No warnings detected`.

State and persistence behavior: read-only over built executables; no files are written.

Dependencies and integration points: depends on Bash, `realpath`, `timeout`, `grep`, and the CMake-built playground executables. It is the runtime companion to `CMakeLists.txt`.

Risks: the hard-coded build-relative folder must match CMake output layout. Capturing all output into a shell variable may be large for verbose TSAN runs. It only reports summary lines, not full race traces. Five seconds may be too short on slow sanitizer builds.

Test signals: output gives per-executable labels and TSAN summary lines; the dummy variant should warn, while expected-safe atomic variants ideally do not.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/collect_warnings.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/tsan_playground.c -->
# sources/storage-engines/wiredtiger/tools/tsan_playground/tsan_playground.c

Purpose: common concurrent workload used to compare how TSAN treats different atomic and barrier implementations.

Important APIs and control flow: compile-time macros select one API header. Shared state includes `message`, `pos`, and atomic `count`. `ping_pong()` waits until `count % NUM_THREADS` matches its thread id, writes one character into `message`, increments `pos`, prints a line, then release-stores `count + 1`. `main()` prints the implementation label, initializes shared state, starts four pthreads, and joins them.

State and persistence behavior: all state is process memory and stdout. No files or database state are written.

Dependencies and integration points: depends on pthreads and the selected atomic API header. Built as many executables by `CMakeLists.txt` and evaluated by `collect_warnings.sh`.

Risks: the workload relies on the counter creating a happens-before relationship for non-atomic `message` and `pos`; if the chosen implementation is not sanitizer-visible, TSAN reports races even if hardware ordering is intended. `printf` interleaves with shared message mutation and may add synchronization/noise. The character calculation can produce non-printable bytes after enough iterations, though `num_iters` is small.

Test signals: all variants should terminate; TSAN warnings distinguish recognized synchronization from dummy or fence-only patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/tsan_playground/tsan_playground.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/voidstar/include/instrumentation.h -->
# sources/storage-engines/wiredtiger/tools/voidstar/include/instrumentation.h

Purpose: declares the Antithesis instrumentation interface used by instrumented programs or harnesses to request fuzzer input, emit messages/guidance, and report coverage.

Important APIs and control flow: input functions include `fuzz_getchar()`, `fuzz_get_random()`, `fuzz_coin_flip()`, and `fuzz_getblob()`. Output functions include `fuzz_set_source_name()`, info/error message and data calls, `fuzz_png()`, `fuzz_bytes()`, `fuzz_kv32_pairs()`, `fuzz_flush()`, and `fuzz_exit()`. Coverage callbacks include LLVM sanitizer coverage hooks `__sanitizer_cov_trace_pc_guard_init()` and `__sanitizer_cov_trace_pc_guard()`, plus manual module/edge APIs `init_coverage_module()` and `notify_coverage()`. Comments describe three implementations: stub `libvoidstar.so`, legacy socket-based instrumentation, and deterministic hypervisor instrumentation.

State and persistence behavior: this header declares interfaces only. Implementations may buffer output, set a process/source name, send stateful coverage messages, terminate the process, or synchronize with a fuzzer/hypervisor.

Dependencies and integration points: C/C++ compatible via `extern "C"`, includes `stddef.h`, `stdint.h`, and `stdbool.h`. WiredTiger or tests link against the stub library and can substitute real instrumentation with `LD_PRELOAD` or environment setup.

Risks: comments document significant runtime semantics: output buffering can cross timing boundaries across multiple library copies, deterministic hypervisor calls are not usable outside the hypervisor, and coverage volume can be expensive. The reserved LLVM sanitizer symbol names require diagnostic suppression for Clang.

Test signals: compile/link tests against `libvoidstar.so` validate ABI availability. Runtime Antithesis campaigns validate input/output/coverage behavior under the chosen implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/voidstar/include/instrumentation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-config-format -->
# sources/storage-engines/wiredtiger/tools/wt-config-format

Purpose: formats WiredTiger configuration strings or Turtle files into a more readable indented form.

Important APIs and control flow: a Bash wrapper invokes a single Perl `-npE` expression. For lines containing `=` and an opening delimiter, it rewrites commas and parentheses/braces/brackets into newlines with indentation based on nesting depth.

State and persistence behavior: reads stdin or file arguments and writes formatted text to stdout. It does not modify inputs.

Dependencies and integration points: depends on Bash and Perl. Used manually for inspecting WT config strings, including `WiredTiger.turtle` content.

Risks: this is a lexical formatter, not a full WT config parser; quoted delimiters or unusual syntax can be reformatted incorrectly. Indentation counter is per input line because `$i=0` is reset for each line.

Test signals: piping a nested config string should produce line breaks after commas and nested indentation; no automated test is present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-config-format -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-mcp/pyproject.toml -->
# sources/storage-engines/wiredtiger/tools/wt-mcp/pyproject.toml

Purpose: defines the Python package metadata and dependencies for the WiredTiger MCP server.

Important APIs and control flow: `[project]` names the package `wt-mcp`, sets version `0.1.0`, requires Python `>=3.13`, and declares dependencies on `mcp[cli]>=1.23.0`, `pydantic>=2.11.4`, and `python-dotenv>=1.1.0`.

State and persistence behavior: static project metadata only.

Dependencies and integration points: consumed by Python packaging tools such as `uv`, `pip`, or build backends. It supports `server.py`, which imports FastMCP, Pydantic field helpers, and dotenv.

Risks: no build system table or script entry point is declared here, so invocation likely depends on direct script execution or surrounding tooling. Python 3.13 is a high floor and may limit developer environments.

Test signals: environment creation should install the three dependency families and allow `python server.py` to import MCP/Pydantic/dotenv before looking for WiredTiger build artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-mcp/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-mcp/server.py -->
# sources/storage-engines/wiredtiger/tools/wt-mcp/server.py

Purpose: implements a stateful Model Context Protocol server for WiredTiger debugging and development, exposing connection, cursor, transaction, schema, diagnostic, timestamp, checkpoint, and log-reading operations as MCP tools.

Important APIs and control flow: startup loads `.env`, resolves `WT_BUILDDIR` or a nearby `build`/`cmake_build`, amends `sys.path`, imports `wiredtiger`, and constructs a `FastMCP` with lifespan cleanup. Global registries `_connections` and `_cursors` hold `ConnectionInfo` and `CursorInfo`. Helpers `_parse_config_field()`, `metadata_search()`, `_convert_key()`, and `_convert_value()` parse metadata and convert single-field key/value formats. Tool groups include connection lifecycle (`open_connection`, `close_connection`, `list_connections`), cursor operations (`open_cursor`, `cursor_next`, `cursor_prev`, `cursor_search`, `cursor_search_near`, `cursor_reset`, `cursor_largest_key`, `cursor_insert`, `cursor_remove`), transactions (`begin_transaction`, `commit_transaction`, `rollback_transaction`), schema operations (`list_tables`, `get_metadata`, `get_schema`, `create_table`, `drop_table`, `rename_table`, `alter_table`, `truncate`), diagnostics (`query_timestamps`, `verify_table`, `dump_block`, `get_statistics_by_category`), and maintenance (`checkpoint`, `reconfigure_connection`, `set_timestamp`, `rollback_to_stable`, `read_log`). `main` configures logging and runs MCP over stdio.

State and persistence behavior: process-global state tracks open WT connections, sessions, and cursors across MCP calls. Many tools mutate database state: create/drop/rename/alter/truncate tables, insert/remove records, begin/commit/rollback transactions, set timestamps, checkpoint, reconfigure, and rollback to stable. `verify_table()` and `dump_block()` temporarily redirect process stdout/stderr file descriptors to pipes to capture C-level WiredTiger output.

Dependencies and integration points: depends on the built WiredTiger Python API, FastMCP, Pydantic, dotenv, JSON serialization, and a usable WT build directory. It integrates directly with WiredTiger's Python `Connection`, `Session`, and `Cursor` APIs and exposes them to MCP clients.

Risks: global registries are not protected by locks, so concurrent MCP calls could race. `_convert_key()` and `_convert_value()` only handle one-character formats; composite formats and column-store cursors are limited or rejected. Import-time failure exits the process if build discovery fails. `verify_table()`/`dump_block()` pipe reads occur after the verify call and can deadlock if C output exceeds pipe capacity before restore/read. The fd redirection is process-wide and unsafe with concurrent requests. Destructive tools are exposed without confirmation beyond tool arguments.

Test signals: no direct tests in this subset. Practical smoke tests require a built WT Python module, then opening a temporary home, creating a table, inserting/searching data, listing metadata, checkpointing, querying timestamps, and closing the connection. Diagnostic tools need homes configured with statistics/logging to exercise those surfaces.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-mcp/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-ret-trace1 -->
# sources/storage-engines/wiredtiger/tools/wt-ret-trace1

Purpose: destructive Perl source-rewriting tool that assigns unique negative error codes to individual WiredTiger error-return sites so identical base errors can be traced back to the exact file/function/line where they originated.

Important APIs and control flow: help text describes the workflow and warns about in-place modification. The script confirms when run interactively unless `-y`, `-q`, or `-f` is used, changes to the git top level, scans `src/**/*.c/h`, parses return/error macro calls with recursive regex token patterns, replaces base error constants with generated `ERR_AT_func___file_line` symbols, records mappings, rewrites comparisons/cases in `src`, `bench`, `test`, `ext`, and `examples` to use generated `WT_E_EQ__ERR()` helpers, rewrites `src/include/error.h` comparisons, prepends `#pragma once` and appends generated defines/macros to `src/include/wiredtiger.h.in`, then relaxes CMake `-Werror` to `-Wno-gnu-statement-expression`. Optional thread support parallelizes first-pass source processing with `pmap()`.

State and persistence behavior: heavily mutates source files in place across the repository. It writes generated macro definitions into `wiredtiger.h.in` and changes CMake files. It prints the base-error regex at the end.

Dependencies and integration points: depends on Perl 5.27, optional Perl threads, git, find, shell commands, and WiredTiger source layout. It targets WT error macros such as `WT_RET`, `WT_ERR`, `WT_TRET`, `WT_RET_MSG`, `WT_ERR_PANIC`, and comparison sites.

Risks: extremely high blast radius and intentionally destructive. Regex parsing of C is sophisticated but still heuristic; macros, generated files, comments, or unusual formatting can be rewritten incorrectly. Generated error-code ranges leak through public API unless `WT_E_BASE()` is applied at API boundaries. It modifies build flags globally. It should only be used on a disposable branch/worktree.

Test signals: after running, CMake/build failures identify missed rewrites; runtime with verbose `error_returns` can trace unique codes. The help text includes a follow-up workflow for wrapping generated codes in `__wt_set_return()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt-ret-trace1 -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_binary_decode.py -->
# sources/storage-engines/wiredtiger/tools/wt_binary_decode.py

Purpose: top-level command-line decoder for WiredTiger binary data, including `.wt` files, hex dumps embedded in logs, disaggregated page-service JSONL, and SQLite page-log files.

Important APIs and control flow: `open_input_file()` supports stdin for text or binary modes. `decode_dumpin_input()`, `decode_disagg_table_input()`, `decode_sqlite_input()`, and `decode_wt_binary_input()` route to specialized helpers. `wtdecode()` selects dump-in first, then explicit disagg-table, then automatic SQLite signature detection, otherwise ordinary WT binary decode. `feature_check()` warns about missing BSON, Snappy, and CRC32C support. `get_arg_parser()` defines CLI options for version, input mode, BSON, disagg flags, offset, page id, LSN, page count, skip-data, keyfile, verbosity, byte/split output, CSV output, and continue-on-checksum-failure. The `__main__` block configures logging, opens optional CSV output, builds `DecodeOptions`, and handles keyboard/broken-pipe exits.

State and persistence behavior: read-only over decode input. Optional CSV output writes to the path from `--csv`. The tool prints decoded content to stdout and logs warnings/errors.

Dependencies and integration points: orchestrates `py_common.mdb_log_parse`, `binary_data`, `btree_format`, `snappy_util`, `file_format`, `page_service`, and `sqlite_format`. It is the primary entry point exercised by the decode tests.

Risks: SQLite auto-detection opens the filename and does not apply to stdin. Optional dependency warnings do not always prevent later hard failures, especially for Snappy-compressed pages. Some options are mode-specific but accepted globally, so invalid combinations rely on downstream behavior. Disaggregated table decryption needs external `pagedecryptor` and keyfile.

Test signals: tests in this subset cover ordinary page decode, dump-in disagg delta-chain decode, MongoDB corrupt-log diagnostics, and page-service JSONL decode when environment prerequisites exist.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_binary_decode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_ckpt_decode.py -->
# sources/storage-engines/wiredtiger/tools/wt_ckpt_decode.py

Purpose: decodes WiredTiger checkpoint address cookies from hex strings into root/extent offsets, sizes, checksums, and disaggregated root-page address fields.

Important APIs and control flow: `usage()` and `err_usage()` handle CLI help. `show_one()` and `show_ref()` format numeric fields with decimal and hex. `decode_arg()` converts a hex argument to bytes, treats version byte `1` as ordinary WT checkpoint format and other leading bytes as disaggregated format, unpacks as many integers as possible using `unpack_int()`, validates expected counts, and prints either four address cookies plus file/checkpoint size for regular/tiered checkpoints or root page id/LSN/checkpoint id/record id/size/checksum for disaggregated address cookies. CLI option `-a` sets allocation size, defaulting to 4096.

State and persistence behavior: pure stdout decoder; no input files or persistent writes.

Dependencies and integration points: depends on `py_common.binary_data.unpack_int()` and WiredTiger checkpoint cookie format. It is a standalone diagnostic script.

Risks: disaggregated detection assumes any first byte other than version `1` is a disagg cookie. Error handling for invalid hex or unpack failures is minimal. The `--allocsize` long option is declared without explicit `=` handling but only `-a` is implemented in the option loop.

Test signals: no automated tests in this subset. Commented sample address cookies provide manual smoke cases for regular, tiered, disagg 5-entry, disagg 6-entry, and bad formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_ckpt_decode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_cmp_dir -->
# sources/storage-engines/wiredtiger/tools/wt_cmp_dir

Purpose: compares logical content of two WiredTiger home directories by listing comparable URIs and delegating per-URI comparison to `wt_cmp_uri.py`.

Important APIs and control flow: `usage_exit()` prints arguments. `init_wt_utility()` walks upward from the current directory to find an executable `wt`. `wtfiles()` runs `$wt -h <home> list`, filters metadata URIs to include `table:*` and orphan `file:*` entries without matching tables, and emits one URI per line. CLI parsing supports a shared `-t timestamp`, an ignore regex `-i`, and an optional second `-t` for the second directory. It compares filtered URI lists exactly, then loops through each URI and runs `python3 <scriptdir>/wt_cmp_uri.py` with timestamp options and directory/URI paths, accumulating nonzero status.

State and persistence behavior: creates temporary `/tmp/wcd$$out` and `/tmp/wcd$$err` files during `wt list` and removes them. It reads WT homes and writes comparison progress to stdout/stderr.

Dependencies and integration points: requires a built `wt` utility in an ancestor directory, `wt_cmp_uri.py` next to the script, Python 3, grep/sed/tr, and usable WiredTiger home directories. It integrates with timestamped comparison workflows through `wt_cmp_uri.py`.

Risks: URI list equality is string-order sensitive. Temporary filenames based only on PID can collide in unusual circumstances. Paths like `"$dir1"/$f` assume URI strings are accepted by `wt_cmp_uri.py` in that form. The TODO notes corruption handling is not checked during list. Ignore regex is applied to URI lines and can hide relevant differences.

Test signals: successful comparison exits zero after printing each URI. Different URI lists produce an explicit stop message; per-URI differences produce nonzero final exit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_cmp_dir -->
