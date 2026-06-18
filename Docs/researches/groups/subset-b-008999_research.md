# subset-b-008999 Research

Grouped research for the requested WiredTiger utility commands and vendored Python test-support packages. Each section is bounded for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_misc.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_misc.c

Purpose: Shared utility helpers for the `wt` command-line tool: error reporting, stdin line reading, numeric parsing, flush/drop fallback, usage formatting, allocator wrappers, string duplication, and output-file lifecycle.

Important APIs/functions: `util_cerr` formats cursor-operation errors through `util_err`; `util_err` writes `progname`, optional formatted context, and either `wiredtiger_strerror` or `WT_SESSION::strerror`; `util_read_line` grows a `ULINE` buffer in 1024-byte increments and returns EOF status separately; `util_str2num` parses unsigned decimal/hex strings using WiredTiger's `__wt_strtouq`; `util_flush` checkpoints and drops the URI if checkpoint fails; `util_usage` prints common subcommand help; `util_malloc`, `util_calloc`, `util_realloc`, `util_free`, and `util_strdup` centralize allocation, including optional Windows TCMalloc support; `util_open_output_file` and `util_close_output_file` abstract stdout versus named output.

Control flow: Helpers are mostly leaf functions called by other utility subcommands. Error helpers always return `1` for caller-friendly utility failure. `util_read_line` increments a static line counter, loops over `getchar`, handles expected EOF, unexpected EOF, and missing newline distinctly, and null-terminates the buffer. `util_str2num` rejects a non-digit first byte before calling `__wt_strtouq`, then optionally requires full-string consumption.

State and persistence behavior: Persistent database effect is limited to `util_flush`, which calls `session->checkpoint` and may delete the target with `session->drop` on checkpoint failure. `util_read_line` has process-local state through a static line counter and caller-owned `ULINE` memory. Allocation wrappers must be paired consistently because Windows community TCMalloc uses a different allocation family.

Dependencies and integration points: Includes `util.h`, WiredTiger internal helpers/macros, global `progname` and `usage_prefix`, `WT_SESSION`, `WT_CURSOR`, and optional `<gperftools/tcmalloc.h>` gated by `ENABLE_WINDOWS_TCMALLOC_COMMUNITY_SUPPORT`. Output helpers integrate with commands that optionally write to files.

Risks: `util_flush` drops data on checkpoint failure by design, so callers must only use it where a failed load/create should be discarded. `util_read_line`'s static line counter is not reset between logical streams and is not thread-local. `util_strdup` under non-TCMalloc returns `strdup` memory that must still be released with `util_free`; that is safe only because `util_free` maps to `free` in that build. `util_open_output_file` returns `NULL` on `fopen` failure and callers must check it.

Test signals: Covered indirectly by all utility commands that parse numeric options, read load input, report errors, and write files. Useful focused tests would exercise EOF/no-newline diagnostics, hex and invalid numeric parsing, stdout versus file close behavior, and the checkpoint-failure drop path with a mocked session.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_page.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_page.c

Purpose: Implements the `wt page` diagnostic subcommand, which reads/debugs a single page by page id and LSN from a file URI.

Important APIs/functions: `usage` documents required `-p page_id` and `-l lsn`. `util_page` parses options with `__wt_getopt`, converts both numeric arguments through `util_str2num`, canonicalizes the operand with `util_uri(..., "file")`, acquires a data handle via `__wt_session_get_dhandle`, and in diagnostic builds calls `__wt_debug_disagg_page_id(session_impl, page_id, lsn, NULL)`.

Control flow: The command rejects missing `-p`, missing `-l`, and wrong operand counts before opening the handle. It casts public `WT_SESSION` to `WT_SESSION_IMPL` for internal debug APIs, releases the data handle with `WT_TRET`, frees the URI, and converts nonzero internal return codes to utility exit status `1`.

State and persistence behavior: It should be read/debug-only. It temporarily pins a data handle in the session and releases it before returning. No durable metadata or table content is intentionally modified.

Dependencies and integration points: Depends on the utility URI resolver, numeric parser, WiredTiger internal session handle APIs, `HAVE_DIAGNOSTIC`, and the disaggregated page debug function. It is integrated into the `wt` utility command dispatcher and only has useful behavior in diagnostic builds.

Risks: Non-diagnostic builds return `ENOTSUP`, so scripts must not assume availability. Internal debug APIs and direct `WT_SESSION_IMPL` casts make this sensitive to WiredTiger internal ABI changes. Numeric parsing permits `0x`-prefixed values because base 0 is used after the first-digit check, matching the usage text.

Test signals: Expected tests are command-line validation, diagnostic-build page lookup behavior, and non-diagnostic `ENOTSUP` messaging. A mock or diagnostic integration environment is needed for the actual page access path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_printlog.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_printlog.c

Purpose: Implements `wt printlog`, formatting WiredTiger log records with optional output file, LSN range, message-only filtering, redaction override, and hexadecimal item display.

Important APIs/functions: `usage` describes `-f`, `-l`, `-m`, `-u`, and `-x`. `util_printlog` parses flags, decodes `-l` as either `start-file,start-offset` or `start-file,start-offset,end-file,end-offset` with `sscanf`, builds `WT_LSN` values using `WT_SET_LSN`, and delegates to `__wt_txn_printlog(session, ofile, flags, start_lsn_or_null, end_lsn_or_null)`.

Control flow: The command accumulates `WT_TXN_PRINTLOG_MSG`, `WT_TXN_PRINTLOG_UNREDACT`, and `WT_TXN_PRINTLOG_HEX` flags. It rejects extra operands and malformed LSN strings. By default it leaves user data redacted and only passes the unredact flag when `-u` is explicit.

State and persistence behavior: The command is read-only with respect to database state. It may create/truncate the named output file through the lower printlog implementation. LSN range state is local to the invocation.

Dependencies and integration points: Uses WiredTiger log structures (`WT_LSN`), printlog flags, and the internal transaction log printer. It is a support/diagnostic interface for inspecting recovery logs and customer data while minimizing accidental user-data exposure.

Risks: `sscanf` accepts some partially numeric forms according to C conversion rules; malformed separators are rejected only when the parsed count is not 2 or 4. `-u` can expose application data, while `-x` changes display semantics for downstream parsers. Output file errors depend on `__wt_txn_printlog` handling.

Test signals: Tests should cover default redaction, flag combinations, two-value and four-value LSN forms, bad LSN usage errors, and output-file creation. Integration tests need a database with log records and stable expected output patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_printlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_read.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_read.c

Purpose: Implements `wt read`, a simple command-line lookup tool for reading string values by record-number or string keys from a table.

Important APIs/functions: `usage` defines `read uri key ...`. `util_read` resolves the first operand as a table URI, opens a cursor, validates key format is `r` or `S` and value format is `S`, sets keys from command arguments, calls `cursor->search`, retrieves values with `cursor->get_value`, and prints each value.

Control flow: After option parsing, it requires at least a URI and one key. It frees the resolved URI immediately after `open_cursor`. Record-number keys are parsed through `util_str2num`; string keys are passed directly. Missing keys are reported with `util_err(..., 0, "%s: not found")` and remembered so the final exit status is nonzero even if later keys succeed.

State and persistence behavior: Read-only from the database perspective. It opens a session cursor and uses cursor state for each search; it does not close the cursor explicitly in this file, relying on utility/session cleanup at process teardown or higher-level lifecycle.

Dependencies and integration points: Depends on WiredTiger cursor API, `util_uri`, `util_str2num`, `util_cerr`, `WT_STREQ`, and command globals. It integrates with tables that have simple scalar key/value formats and intentionally excludes compound or binary formats.

Risks: Unsupported formats return after opening the cursor without explicit cursor close. Printed string values are emitted raw, so embedded terminal control characters or newlines can affect output consumers. A single invalid record number aborts the command immediately.

Test signals: Useful tests cover string-key reads, record-number reads, `WT_NOTFOUND` exit status, unsupported key/value formats, invalid numeric record keys, and stdout write failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_salvage.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_salvage.c

Purpose: Implements `wt salvage`, invoking WiredTiger salvage on a file URI, optionally with force.

Important APIs/functions: `usage` documents `salvage [-F] uri`. `util_salvage` parses `-F`, resolves the operand as a file URI, and calls `session->salvage(session, uri, force)` where `force` is either `NULL` or the string `"force"`.

Control flow: The command accepts exactly one URI after options. It reports `session.salvage` errors through `util_err`; on success with verbose progress enabled it prints a newline to finish the progress line.

State and persistence behavior: This is a mutating recovery/repair operation. It can rewrite or reconstruct on-disk file contents according to WiredTiger salvage semantics, and `-F` bypasses basic refusal behavior for damaged files.

Dependencies and integration points: Uses public `WT_SESSION::salvage`, the shared URI resolver, shared usage and error helpers, and global `verbose`. It is an administrative repair command in the `wt` utility.

Risks: Salvage can discard unrecoverable data, and forced salvage increases that risk. Passing `"force"` as a bare config string depends on WiredTiger configuration parsing accepting that shorthand. Operators need clear backups before use.

Test signals: Tests should verify option parsing, forced versus default config passed to a mocked session, verbose newline behavior, and real salvage behavior on intentionally damaged test files where practical.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_salvage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_stat.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_stat.c

Purpose: Implements `wt stat`, printing connection or object statistics as `description=value` lines.

Important APIs/functions: `usage` documents `stat [-f] [uri]` and compatibility `-a` is accepted in parsing. `util_stat` resolves optional object URI, constructs `statistics:<object>` with `__wt_snprintf`, opens a statistics cursor with optional `statistics=(fast)`, iterates with `cursor->next`, and reads `desc` and printable value via `cursor->get_value`.

Control flow: No operand selects connection statistics (`statistics:`). One operand selects table statistics after `util_uri(..., "table")`. More operands fail usage. Iteration stops on `WT_NOTFOUND`, which is normalized to success. Errors during allocation, cursor open, printf, or cursor get go to a common `err` block that returns `1`.

State and persistence behavior: Read-only. It allocates temporary strings for object and statistics URIs and opens a cursor; no durable database state is changed. Fast statistics may avoid expensive gathering and can therefore report a subset.

Dependencies and integration points: Depends on WiredTiger statistics cursors, utility allocation wrappers, URI resolution, and global program name. It is integrated into monitoring/support workflows that scrape utility output.

Risks: The `-a` option is silently retained for compatibility but no longer changes behavior, which can confuse older scripts. It does not explicitly close the cursor in this function. Output descriptions are human-oriented strings, so consumers relying on exact text are sensitive to WiredTiger stat-description changes.

Test signals: Tests should cover connection versus table statistics URIs, `-f` config, compatibility `-a`, allocation/format failures by injection, and stable handling of `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_truncate.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_truncate.c

Purpose: Implements `wt truncate`, removing all data from a table URI.

Important APIs/functions: `usage` defines `truncate uri`. `util_truncate` resolves the sole operand as a table URI and calls `session->truncate(session, uri, NULL, NULL, NULL)`.

Control flow: It supports only `-?`, requires exactly one operand, frees the resolved URI after the truncate call, and reports errors with `util_err`.

State and persistence behavior: Mutates persistent table contents by truncating the full object range. Passing `NULL` cursors and config requests a whole-object truncate through WiredTiger.

Dependencies and integration points: Public `WT_SESSION::truncate`, `util_uri`, `util_usage`, and `util_err`. This command is a destructive administrative shortcut in the `wt` utility.

Risks: There is no confirmation prompt or dry-run path. URI resolution defaults to table, so accidental table name entry can erase all records. Recovery semantics depend on WiredTiger transaction/log configuration outside this file.

Test signals: Tests should cover operand validation, URI resolution, successful full truncate, error propagation, and verification that data is gone after the command in an integration database.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verbose.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_verbose.c

Purpose: Provides the verbose `WT_EVENT_HANDLER` used by the utility to surface WiredTiger errors, messages, and progress updates.

Important APIs/functions: `__handle_error_verbose` writes errors to stderr; `__handle_message_verbose` writes messages to stdout; `__handle_progress_verbose` prints carriage-return progress with operation name and count. `__event_handler_verbose` wires these callbacks into a `WT_EVENT_HANDLER`, exposed as global `verbose_handler`.

Control flow: Each callback ignores unused handler/session fields and returns `EIO` when its printf/fprintf operation fails, otherwise `0`. Progress output uses `\r` rather than newline so callers such as salvage and verify add a newline after successful verbose runs.

State and persistence behavior: No database persistence. It affects process output and can influence WiredTiger callback return handling if writes to stdout/stderr fail.

Dependencies and integration points: Uses WiredTiger event handler ABI and `WT_UNUSED`. The main utility can pass `verbose_handler` when opening a connection/session to enable human-readable diagnostics.

Risks: Progress output can interleave with other stdout users and is not thread-synchronized. Returning `EIO` from event callbacks may turn output-device failures into command failures. The global pointer exposes a mutable handler object if other code writes through it.

Test signals: Tests can inject the handler and assert routing to stdout/stderr, progress formatting, and error return on closed/broken output streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verbose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verify.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_verify.c

Purpose: Implements `wt verify`, validating one table/layered object or all table/layered metadata entries with configurable diagnostic dump and timestamp options.

Important APIs/functions: `usage` lists verification controls. `verify_one` delegates to `session->verify(session, uri, config)` and handles verbose progress newline. `util_verify` builds a WiredTiger config string in a scratch buffer, supporting `read_corrupt`, dump modes (`dump_address`, `dump_blocks`, `dump_layout`, `dump_tree_shape`, `dump_offsets=[...]`, `dump_pages`), `dump_key_data`, `strict`, `stable_timestamp`, `do_not_clear_txn_id`, and `dump_all_data`.

Control flow: It allocates a session scratch buffer with `__wt_scr_alloc`, parses options with `__wt_getopt`, rejects simultaneous `-u` and `-k`, and then either verifies a resolved table URI or opens `metadata:` to enumerate all keys. In all-table mode it only verifies keys prefixed `table:` or `layered:` and either aborts on the first non-`ENOTSUP` error when `-a` is set or accumulates errors with `WT_TRET`.

State and persistence behavior: Verification is primarily read/validation, but options such as `do_not_clear_txn_id` imply default verification may clear transaction IDs as part of repair/cleanup semantics inside WiredTiger. Dump options can expose key or full application data depending on `-k`/`-u`.

Dependencies and integration points: Uses public `WT_SESSION::verify`, metadata cursor access through `WT_METADATA_URI`, internal scratch-buffer APIs, utility URI/error helpers, and WiredTiger macros for error handling. It is a central support command for checking database integrity and inspecting page/block layout.

Risks: Dumping all data can leak application content; the code explicitly prevents combining all-data and key-only modes but each separately changes redaction. The metadata cursor is not explicitly closed here. `dump_offsets` is accepted as a raw substring inside a config list, so validation is deferred to WiredTiger config parsing. In all-table mode, unsupported objects are filtered only by prefix and `ENOTSUP` handling.

Test signals: Tests should cover each option-to-config mapping, duplicate `dump_offsets` rejection, `-u`/`-k` conflict, single-URI verification, all-table metadata iteration, abort-on-error behavior, and verbose newline output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_write.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_write.c

Purpose: Implements `wt write`, a simple table mutation command for inserting/appending string values and removing one key.

Important APIs/functions: `usage` defines `write [-aor] uri key value ...`. `util_write` parses append, overwrite, and remove flags; validates operand shape; resolves the table URI; opens a cursor with `append=<bool>,overwrite=<bool>`; validates key format `r` or `S` and value format `S`; then performs `cursor->insert` or `cursor->remove`.

Control flow: Append mode treats operands after URI as values and lets WiredTiger assign record numbers. Remove mode requires exactly one key and stops after one `cursor->remove`. Normal mode consumes key/value pairs. Record-number keys use `util_str2num`; string keys are direct.

State and persistence behavior: Mutates persistent table data through cursor insert/remove operations. Overwrite behavior is controlled by cursor config; append mode depends on record-number tables. No explicit transaction boundaries are created in this file, so command behavior follows the session/connection defaults established by the utility main path.

Dependencies and integration points: Depends on WiredTiger cursor API, utility URI and numeric helpers, `__wt_snprintf`, and cursor format strings. It is the write-side counterpart to `util_read` for simple table layouts.

Risks: `-a` and `-r` are not rejected together at option parse time; append takes precedence in operand validation, while remove still causes `cursor->remove` without setting an append-assigned key, which is an invalid/confusing combination. Unsupported formats return without explicit cursor close. Raw string values cannot express arbitrary binary formats.

Test signals: Tests should cover insert, overwrite false/true, append on record-number tables, remove, invalid option combinations, unsupported formats, invalid record keys, and persistence observed by a later read.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py

Purpose: Vendored, locally modified `concurrencytest` helper that adapts `testtools.ConcurrentTestSuite` to run a unittest suite across forked worker processes and report results through subunit.

Important APIs/functions: `CPU_COUNT` defaults concurrency from `multiprocessing.cpu_count`. `wait_for_children` polls child PIDs with `os.waitpid(..., os.WNOHANG)`, converts wait status to exit code when Python provides `os.waitstatus_to_exitcode`, and logs unexpected exits with the parent PID prefix. `fork_for_tests(concurrency_num)` returns a `make_tests` closure for `ConcurrentTestSuite`. `partition_tests` uses `testtools.iterate_tests` and `itertools.cycle` to distribute tests round-robin.

Control flow: `fork_for_tests` partitions the suite, clears the original suite list to release references, creates a pipe per partition, forks, and in the child closes stdin/read-end, wraps the write pipe in `TestProtocolClient` with `AutoTimingTestResultDecorator`, tags results with the child PID, runs the partition suite, and exits. The parent closes the write end, wraps the read stream as `ProtocolTestCase`, stores child PIDs, and starts a thread to reap children.

State and persistence behavior: No durable persistence. It creates OS processes, pipes, and a background thread. It mutates the input suite by clearing `suite._tests` and clears partition lists after wrapping them into process suites to reduce memory retention.

Dependencies and integration points: Unix-only `os.fork`, `os.pipe`, `os.waitpid`, `subunit`, `testtools`, `unittest`, and threading. WiredTiger's Python test runner can use this to parallelize IO-heavy tests while retaining subunit-compatible reporting.

Risks: The wait thread is not joined and sleeps for five seconds per polling loop, so process cleanup messages can lag. Mutating private `suite._tests` depends on unittest internals. Empty partitions still fork if concurrency exceeds test count. The module declares `_all__` rather than `__all__`, so intended exports are not honored by wildcard import. Windows is not supported despite a comment in `wait_for_children`.

Test signals: The `__main__` demo compares sequential and four-process execution. Stronger tests would verify partition balancing, child traceback propagation, PID tagging, child reaping, and behavior when a child exits by signal or nonzero status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/concurrencytest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg

Purpose: Setuptools egg-info configuration for the vendored `concurrencytest` package.

Important APIs/types/functions: No executable APIs. The `[egg_info]` section clears `tag_build` and disables date and SVN revision tags with `tag_date = 0` and `tag_svn_revision = 0`.

Control flow: Consumed by setuptools during metadata generation; it has no runtime control flow.

State and persistence behavior: Affects generated package metadata file names and version tags during build/sdist/egg-info operations. It does not affect WiredTiger runtime state.

Dependencies and integration points: Used by `setup.py` and setuptools. It keeps vendored package metadata stable inside the WiredTiger third-party test tree.

Risks: Legacy `tag_svn_revision` is obsolete in modern setuptools but harmless. Metadata-only changes can still affect reproducible packaging if defaults change upstream.

Test signals: Build or `python setup.py egg_info` should produce untagged version metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.py

Purpose: Setuptools installer metadata for the vendored `concurrencytest` single-module package.

Important APIs/functions: Calls `setuptools.setup` with `name='concurrencytest'`, `version='0.1.2'`, `py_modules=['concurrencytest']`, dependencies on `python-subunit` and `testtools`, author/project metadata, keywords, GPLv3 license classifier, and POSIX/Unix/Python 2/3 classifiers.

Control flow: Top-level setup invocation only. Importing the file executes packaging setup behavior, as expected for legacy setup scripts.

State and persistence behavior: Creates package metadata and install artifacts when run by packaging tools. No database or test-run state is modified by the metadata itself.

Dependencies and integration points: Integrates with setuptools and the vendored module. WiredTiger's third-party test dependency packaging can reference this when building local Python dependencies.

Risks: The file imports `os` but does not use it. License comments in `concurrencytest.py` mention GPLv2+ while setup metadata says GPLv3, which is a compliance signal to verify before redistribution. The dependency names assume availability from the local third-party set or the Python environment.

Test signals: Packaging smoke test is `python setup.py egg_info` or installation into an isolated environment with `python-subunit` and `testtools`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/concurrencytest-0.1.2-locally-modified/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py

Purpose: Vendored `discover` 0.4.0 backport of unittest discovery for older Python versions, exposing a `DiscoveringTestLoader`, CLI `main`, default loader, and setup.py collector.

Important APIs/functions: `DiscoveringTestLoader` implements `loadTestsFromTestCase`, `loadTestsFromModule`, `loadTestsFromName(s)`, `getTestCaseNames`, `discover`, `_get_name_from_path`, `_get_module_from_name`, `_match_path`, and `_find_tests`. Failure helpers create synthetic failing test cases for import/load failures. `_CmpToKey` adapts legacy `cmp` sorting. `relpath` fallback supports Python versions without `os.path.relpath`. `_do_discovery`, `_run_tests`, `main`, `defaultTestLoader`, and `collector` provide CLI and setup integration.

Control flow: `discover` normalizes top-level and start directories, ensures the top-level directory is on `sys.path`, validates importability, then calls `_find_tests`. `_find_tests` scans files matching valid module names and the pattern, imports modules by derived dotted name, rejects globally installed shadow imports by comparing module paths, loads tests, and recurses only into packages containing `__init__.py`. Package-level `load_tests` can override recursion.

State and persistence behavior: No durable persistence. It mutates `sys.path`, stores `_top_level_dir` on the loader instance, imports modules into `sys.modules`, and can call arbitrary module-level import code during discovery.

Dependencies and integration points: Uses `unittest`, `optparse`, `fnmatch`, `types`, `traceback`, and filesystem APIs. It supports old Python compatibility required by the vendored test stack and exposes a console script through setup metadata.

Risks: Importing tests has side effects. Directory listing order is not sorted before discovery, though method names are sorted, so module discovery order can vary by filesystem. The compatibility code targets very old Python versions and uses broad `except` clauses to synthesize failures. `sys.path.remove(top_level_dir)` in dotted-module discovery assumes that exact entry was inserted and still exists.

Test signals: Self-tests should exercise discovery from directories and dotted names, pattern filtering, package `load_tests`, failed imports producing failing tests, top-level path validation, and CLI exit status. The package's `setup.py` declares `discover.collector` as its test suite.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/discover.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg

Purpose: Source distribution configuration for the vendored `discover` package.

Important APIs/functions: No runtime APIs. The `[sdist]` option `force-manifest = 1` tells legacy distutils/setuptools to regenerate the manifest for source distributions.

Control flow: Packaging-time only.

State and persistence behavior: Affects generated sdist manifests, not WiredTiger runtime or test execution.

Dependencies and integration points: Read by setup tooling invoked from `setup.py`.

Risks: `force-manifest` is legacy behavior and may be ignored or deprecated by newer tooling. If ignored, stale manifest issues would need another packaging path.

Test signals: Running an sdist build should refresh included file lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py

Purpose: Setuptools metadata and console-entry definition for the vendored `discover` module.

Important APIs/functions: Imports `discover.__version__`, defines metadata constants, reads `README.txt` as long description, builds `params`, adds console script `discover = discover:main`, sets `test_suite = discover.collector`, and calls `setup(**params)`.

Control flow: Top-level execution reads README, imports the local module, and invokes setuptools. It has no library code beyond packaging metadata assembly.

State and persistence behavior: Packaging commands generate metadata, source distributions, installs, and console scripts. No database state.

Dependencies and integration points: Requires setuptools and the adjacent `discover.py`. The console script can run test discovery from command line; `test_suite` lets legacy `setup.py test` invoke the collector.

Risks: `open('README.txt')` is relative to the current working directory, so running setup from another directory can fail. Importing `discover` during setup executes module top-level code. Classifiers target old Python versions and may not reflect current WiredTiger test runtime.

Test signals: Packaging smoke tests include `python setup.py egg_info`, console script generation, and `setup.py test` invoking `discover.collector`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/discover-0.4.0-locally-modified/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in

Purpose: Declares extra non-package files included in the vendored `extras` source distribution.

Important APIs/functions: No executable APIs. It includes `LICENSE`, `Makefile`, `MANIFEST.in`, `NEWS`, `README.rst`, and `.gitignore`.

Control flow: Packaging tools read this manifest during sdist creation.

State and persistence behavior: Influences distribution contents only; no runtime state.

Dependencies and integration points: Integrated with `setup.py` and setuptools/distutils source distribution behavior.

Risks: It does not include tests explicitly, relying on package discovery in setup for Python files. Including `.gitignore` may be unnecessary but reflects upstream package contents.

Test signals: Sdist inspection should confirm these metadata/support files are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile

Purpose: Developer convenience Makefile for the vendored `extras` package.

Important APIs/functions: `check` runs `PYTHONPATH=$(PWD) $(PYTHON) -m testtools.run extras.tests.test_suite`; `TAGS` and `tags` generate editor tags over `extras/`; `clean` removes tags and `*.pyc`; `apidocs` runs `pydoctor` with project metadata.

Control flow: Make targets execute shell commands. `SOURCES` is computed by `find extras -name "*.py"`.

State and persistence behavior: `check` only runs tests. Tags and apidocs create generated files/directories; `clean` removes tags and bytecode.

Dependencies and integration points: Depends on `make`, Python, testtools, ctags, and pydoctor. WiredTiger can use it when validating or maintaining the vendored package in isolation.

Risks: `find ... -exec rm '{}' \;` removes all pyc files under `extras`; safe for source tree cleanup but broad. `apidocs` depends on pydoctor not usually present in test environments. `PYTHON` defaults to `python`, which may point to an unexpected interpreter.

Test signals: `make check` is the primary test signal and should run the included `extras.tests.test_suite`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py

Purpose: Small compatibility utility package exporting safe attribute probing and optional import helpers.

Important APIs/functions: `__version__ = (0, 0, 3, 'final', 0)`. `try_import(name, alternative=None, error_callback=None)` progressively imports the longest available module prefix, then walks remaining attributes, returning `alternative` on import/attribute failure. `try_imports(module_names, alternative=_RAISE_EXCEPTION, error_callback=None)` tries a list and returns the first truthy import result or raises/returns fallback. `safe_hasattr(obj, attr, _marker=object())` uses `getattr` with a marker to avoid legacy `hasattr` exception-swallowing behavior.

Control flow: `try_import` splits dotted names, retries shorter module prefixes after `ImportError`, calls `error_callback` with the last import error when final resolution fails, then walks attributes. `try_imports` loops through names and delegates to `try_import`; if no module resolves and no alternative was provided, it raises a combined `ImportError`.

State and persistence behavior: No durable persistence. It imports modules into `sys.modules` as a side effect and can trigger import-time side effects from optional dependencies.

Dependencies and integration points: Uses only `sys`. `setup.py` uses `try_import('testtools.TestCommand')` to conditionally enable a test command. Other vendored testing packages can use these helpers for optional dependency compatibility.

Risks: `try_imports` tests `if module:` rather than `is not None`, so a resolved object with false boolean value would be skipped. Attribute lookup failure after a successful module import only reports `last_error` if an earlier import error happened; otherwise callback may not receive an error. Import side effects are unavoidable.

Test signals: `extras/tests/test_extras.py` covers missing modules, submodules, object attributes, callback counts, fallback ordering, and `safe_hasattr` behavior with properties including exception propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py

Purpose: Test-suite aggregator for the vendored `extras` package.

Important APIs/functions: `test_suite()` imports `extras.tests.test_extras`, loads tests from that module through `unittest.TestLoader`, and returns a `unittest.TestSuite` containing those suites.

Control flow: The import happens inside `test_suite` to avoid loading tests at package import time. `map(loader.loadTestsFromModule, modules)` produces suites and wraps them in `TestSuite`.

State and persistence behavior: No durable state. It imports test modules and constructs in-memory unittest suites.

Dependencies and integration points: Depends on `unittest.TestSuite` and `TestLoader`. Used by Makefile and setup.cfg test configuration.

Risks: On Python 3, `map` is lazy but `TestSuite` accepts an iterable, so behavior is acceptable. Adding new test modules requires updating the hard-coded `modules` list.

Test signals: Invoked by `python -m testtools.run extras.tests.test_suite` and legacy setup test commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py

Purpose: Unit tests for `extras.safe_hasattr`, `extras.try_import`, and `extras.try_imports`.

Important APIs/functions: `check_error_callback` is a shared assertion helper for callback behavior. `TestSafeHasattr` validates absent attributes, present attributes, properties, and property exceptions. `TestTryImport` covers missing modules, default fallback, existing modules/submodules, missing submodule attributes, object imports, and error callbacks. `TestTryImports` covers fallback sequences, combined `ImportError`, submodules, and callback counts.

Control flow: Tests use `testtools.TestCase` and matchers `Equals`, `Is`, and `Not`. The callback helper records `ImportError` instances, handles expected raised `ImportError`, and checks callback count against expectations.

State and persistence behavior: No durable state. Tests import standard-library modules such as `os` and inspect import helper behavior.

Dependencies and integration points: Depends on testtools and the local `extras` module. It is loaded by `extras.tests.test_suite`.

Risks: Tests use deprecated aliases such as `assertEquals`, which can warn or fail in future testtools/unittest versions. Negative import tests assume modules named `doesntexist` and `noreally` are absent from the environment. Callback tests expect implementation-specific callback counts.

Test signals: This file is the primary behavior specification for the `extras` package. Passing it confirms optional import fallback and safe attribute probing semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/extras/tests/test_extras.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg

Purpose: Legacy test and egg-info configuration for the vendored `extras` package.

Important APIs/functions: `[test]` sets `test_module = extras.tests`, `buffer = 1`, and `catch = 1`. `[egg_info]` disables build/date/SVN version tagging.

Control flow: Consumed by setuptools/test command; no runtime flow.

State and persistence behavior: Affects test command output buffering and interrupt catching, plus generated package metadata.

Dependencies and integration points: Works with `setup.py`, especially when `testtools.TestCommand` is available and registered as the `test` command.

Risks: `setup.py test` and the `[test]` command path are deprecated in modern setuptools. `catch` semantics may differ by runner.

Test signals: Running the package's test command should discover `extras.tests`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py

Purpose: Setuptools installer metadata for the vendored `extras` package.

Important APIs/functions: Imports local `extras`, conditionally imports `testtools.TestCommand` through `extras.try_import`, defines `get_version` from `extras.__version__`, defines `get_long_description` reading `README.rst` beside setup.py, registers `cmdclass['test']` when testtools is present, and calls `setup` with package metadata and packages `extras` and `extras.tests`.

Control flow: Top-level import checks optional testtools command, computes metadata lazily through helper calls, and invokes setuptools.

State and persistence behavior: Packaging-time metadata/install artifacts only. It reads README and may enable a custom test command based on the current Python environment.

Dependencies and integration points: Depends on setuptools, local `extras`, optional testtools, and README.rst. WiredTiger's vendored test dependency setup can install this package locally.

Risks: Importing `extras` from setup relies on the local source directory being first on `sys.path`. The description contains a typo ("shold"). Optional test command behavior varies with installed dependencies. No explicit install_requires are declared for testtools despite tests needing it.

Test signals: `python setup.py egg_info`, `python setup.py test` when testtools is available, and package import after installation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py

Purpose: Package facade for the vendored `iso8601` parser.

Important APIs/functions: Re-exports `UTC`, `FixedOffset`, `ParseError`, `is_iso8601`, and `parse_date` from `.iso8601`, and declares the same public names in `__all__`.

Control flow: Import-only module; importing `iso8601` imports the implementation module and binds public symbols.

State and persistence behavior: No durable state. It compiles/imports the regex in the implementation module as a side effect.

Dependencies and integration points: Gives consumers a stable package-level API, used by tests and any WiredTiger Python tooling that imports vendored `iso8601`.

Risks: `__all__` omits internal helpers such as `parse_timezone` and `ISO8601_REGEX`, though direct submodule imports can still access them. Import failure in implementation prevents package import.

Test signals: Tests import `.iso8601` directly for internals and package facade behavior can be covered by importing `from iso8601 import parse_date`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/iso8601.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/iso8601.py

Purpose: ISO 8601 date/time parser producing Python `datetime.datetime` objects with timezone support.

Important APIs/functions: `ISO8601_REGEX` accepts calendar dates with dashed or compact forms, optional time separated by `T` or space, optional minutes/seconds/fraction, and optional `Z` or signed offsets. `ParseError` wraps parsing/construction failures. `UTC` aliases `datetime.timezone.utc`. `FixedOffset` builds named `datetime.timezone` offsets. `parse_timezone` converts regex timezone groups into `UTC`, a default timezone, or a fixed offset. `parse_date` parses a string and constructs a datetime with defaulted missing date/time fields. `is_iso8601` checks regex match without constructing a datetime.

Control flow: `parse_date` matches the regex, filters out `None` groups, fills defaults (`month/day=1`, time parts zero), computes microseconds using `Decimal` to avoid float rounding, and wraps any regex or datetime construction exception in `ParseError`. `parse_timezone` handles `Z`, missing timezone, and signed offsets; negative signs negate both hours and minutes.

State and persistence behavior: No persistence. Regex is compiled once at import. Returned timezone objects are immutable standard-library objects.

Dependencies and integration points: Standard `datetime`, `re`, `typing`, and `decimal`. Integrated through the package facade and validated by pytest/hypothesis tests.

Risks: `is_iso8601` only checks regex shape, so strings with impossible dates can return true while `parse_date` raises during datetime construction. Regex accepts one- or two-digit dashed months/days and one- or two-digit seconds, which may be more permissive than strict ISO 8601. Defaulting timezone-less datetimes to UTC is intentional but not strict ISO behavior.

Test signals: `test_iso8601.py` covers fixed offsets, timezone defaulting, invalid strings, many valid historical/regression formats, round-tripping, deepcopy/pickle, and Hypothesis-generated datetimes with and without timezones.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/iso8601.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py

Purpose: Pytest/Hypothesis test suite for the vendored `iso8601` parser.

Important APIs/functions: `test_iso8601_regex`, `test_fixedoffset_eq`, default-timezone tests, parameterized `test_parse_invalid_date`, parameterized `test_parse_valid_date`, and two Hypothesis property tests for naive and timezone-aware datetimes.

Control flow: Invalid cases assert `is_iso8601` is false and `parse_date` raises `ParseError` with expected message prefix. Valid cases assert regex acceptance, field-by-field equality, complete datetime equality, isoformat expectations, deepcopy, pickle, and parse round-trip. Hypothesis tests serialize generated datetimes with `isoformat` and require exact parse equality.

State and persistence behavior: No durable state. Property tests may generate many cases and print debug representations during runs.

Dependencies and integration points: Depends on pytest, hypothesis, hypothesis.extra.pytz, pickle/copy, datetime, and local `.iso8601`. It is the primary quality gate for the parser.

Risks: Hypothesis timezone-aware equality can expose edge cases around pytz timezone offsets and fold/ambiguous times. Tests assume generated `datetime.isoformat()` strings are within parser support. The debug `print` calls can produce noisy logs. Some expected invalid cases only assert message prefix, not exact details.

Test signals: Passing this suite gives strong confidence for accepted date formats, regression issues, timezone offsets, fractions, and round-trip behavior. It also signals packaging dev dependencies from `pyproject.toml` are available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/iso8601/test_iso8601.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml

Purpose: Poetry project metadata and build configuration for vendored `iso8601` 2.1.0.

Important APIs/functions: `[tool.poetry]` declares package name, version, description, author, MIT license, README, homepage, repository, and documentation. Runtime dependency is `python >=3.7,<4.0`. Dev dependency group includes mypy, black, pytest, hypothesis, pytz, pre-commit, nox, Sphinx, changelog-manager, and ruff. `[build-system]` uses `poetry-core>=1.0.0`. `[tool.isort]` sets `profile = "black"`.

Control flow: Build and dependency tools consume the TOML; no runtime execution.

State and persistence behavior: Defines package metadata, build backend, and development dependency resolution. It does not affect parser behavior unless packaging/build commands are run.

Dependencies and integration points: Integrates with Poetry, PEP 517 build frontends, isort, and the pytest/Hypothesis test suite. WiredTiger vendors this metadata to preserve upstream package context.

Risks: Vendored environments that do not use Poetry may ignore dev dependency declarations. Version constraints allow Python 3.7 through 3.x but not Python 4. Tool dependencies are unpinned wildcards, which can make upstream development checks non-reproducible.

Test signals: Build smoke test is a PEP 517/Poetry build with poetry-core. Test/development environments should install pytest, hypothesis, and pytz to run `iso8601/test_iso8601.py`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml -->
