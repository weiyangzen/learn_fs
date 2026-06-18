# subset-b-009096 Research

Grouped research report for subset `subset-b-009096`. Each section is source-tree-aligned and wrapped for reconciliation into one per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_cmp_uri.py -->
# sources/storage-engines/wiredtiger/tools/wt_cmp_uri.py Research

## Purpose

`wt_cmp_uri.py` is a WiredTiger diagnostic CLI for comparing the key/value contents of two WiredTiger URIs, usually in two separate home directories. It can also compare the same home at different read timestamps, which is useful for validating timestamp visibility, checkpoint snapshots, and test/format mirror-table output. The tool exits with status `0` when the cursor streams match and `1` when it finds missing keys, value differences, EOF mismatches, or cursor/opening errors.

## Important APIs, Types, and Functions

The main entry point is `wiredtiger_compare_uri(args)`, called from `__main__`. It parses `-v` and one or two `-t` timestamp options, splits each positional argument with `get_dir_uri()`, opens WiredTiger connections with `py_common.wiredtiger_util.wiredtiger_open`, and obtains `CompareCursor` wrappers through `get_compare_cursor()`.

`CompareCursor` encapsulates a WiredTiger cursor, URI/name metadata, a detected `reverse` collation flag, and an `at_end` latch. Its `cursor_next()` method normalizes cursor iteration: once `WT_NOTFOUND` is observed, all future calls return `WT_NOTFOUND`, and unexpected WT errors are converted to a diagnostic plus `sys.exit(1)`. `wt_open()` opens a session, optionally begins a transaction at `read_timestamp=<timestamp>`, and opens a readonly cursor. `is_reverse()` reads the `metadata:` cursor for a URI and detects `collator=reverse`, which is a test/format-specific custom collation case. `compare_cursors()` is the core merge-walk comparison algorithm. `compare_version_cursors()` is an unfinished deeper version-cursor comparator; the main path deliberately passes `False` for version comparison.

## Control Flow

Argument parsing first consumes a leading `-v` and optional first timestamp, then requires `dir1/uri1`, optionally accepts a second timestamp before `dir2/uri2`, and rejects extra arguments. `wiredtiger_compare_uri()` opens one or two readonly connections; if both home directories are equal it reuses the first connection so same-home timestamp comparisons do not attempt a second open.

`compare_cursors()` advances cursor 1, then cursor 2, compares keys, and performs a sorted merge. If keys differ, it advances the side with the smaller key, adjusted for the `reverse` collator, and prints missing-key diagnostics with throttling after ten consecutive missing entries. Equal keys lead to value comparison. At the end, it checks whether cursor 2 still has records after cursor 1 is exhausted. Record counts are printed on exit paths.

## State and Persistence Behavior

The tool is read-only against WiredTiger data. It creates sessions and cursors, may begin read transactions for timestamp reads, and closes cursors, sessions, and connections explicitly. Its only persistent side effect is process output. Global state is limited to `verboseFlag`.

## Dependencies and Integration Points

This script requires the Python WiredTiger bindings, `WT_NOTFOUND`, `wiredtiger_strerror`, and the repository helper `py_common.wiredtiger_util.wiredtiger_open`. `validate_mirror_tables.py` imports `wiredtiger_compare_uri`, so the function-level entry point is part of internal test tooling. The metadata cursor ties comparison behavior to WiredTiger object metadata and collator configuration.

## Risks and Edge Cases

`get_dir_uri()` uses the last slash and will throw if an argument lacks `/`; malformed inputs are mostly handled by usage checks but not by path-specific validation. `is_reverse()` assumes the URI exists in metadata and that metadata is readable. The version-cursor branch is not currently used and has constructor calls missing the `reverse` argument, so enabling it would fail without repair. Generic `except:` blocks around cursor open print context but re-raise without narrowing error types. Custom collators other than the detected reverse collator are not supported; if two objects have equal-looking keys but incompatible ordering, merge recovery can misreport differences.

## Test Signals

Useful tests include matching and intentionally divergent tables, EOF mismatches, reverse-collator tables from test/format, same-home comparisons at two timestamps, and invalid URI/path arguments. A regression test should also cover imported `wiredtiger_compare_uri()` usage because callers depend on the function exiting with the comparison status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_cmp_uri.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_disagg_addr_decode.py -->
# sources/storage-engines/wiredtiger/tools/wt_disagg_addr_decode.py Research

## Purpose

`wt_disagg_addr_decode.py` is a small diagnostic CLI that decodes a WiredTiger disaggregated-storage address cookie from a hex string into readable JSON. The decoded fields represent page metadata needed to fetch a page from disaggregated page/log services, such as page id, LSNs, size, checksum, flags, and version.

## Important APIs, Types, and Functions

The only functional API is `decode_addr(addr_raw)`. It converts user-provided hex text with `bytes.fromhex()`, parses the bytes with `py_common.btree_format.DisaggAddr.parse`, and prints `json.dumps(addr.__dict__, indent=2)`. The `__main__` block uses `argparse.ArgumentParser` to require one positional `hex_address`.

## Control Flow

The CLI parses a single address string, calls `decode_addr()`, and writes the parsed object to stdout. There is no streaming mode, no file input, and no explicit error recovery. Invalid hex, parse failures, or unexpected object shapes propagate as Python exceptions.

## State and Persistence Behavior

The script has no persistent state and does not read or write WiredTiger data files. It only transforms one input string into JSON output.

## Dependencies and Integration Points

The key dependency is `py_common.btree_format.DisaggAddr`, which defines the binary cookie layout. The description says the format is defined in WiredTiger `block.h`; this script is therefore tightly coupled to the current C address-cookie encoding. It also depends on Python `argparse` and `json`.

## Risks and Edge Cases

Because output is based on `addr.__dict__`, changes to `DisaggAddr` internals can change JSON field names or include non-serializable values. There is no validation that the input length matches the expected cookie size before parsing. Exceptions are not converted into user-friendly CLI errors. Any update to the disaggregated address structure requires the parser in `btree_format` to remain synchronized.

## Test Signals

The comment includes a sample hex input and expected field output that can become a smoke test. Additional tests should cover malformed hex, truncated cookies, extra bytes, and a fixture generated by the C implementation after any address-cookie layout change.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_disagg_addr_decode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_timestamps -->
# sources/storage-engines/wiredtiger/tools/wt_timestamps Research

## Purpose

`wt_timestamps` is a WiredTiger diagnostic CLI that prints global timestamp values for one or more WiredTiger home directories. By default it queries `all_durable`, `last_checkpoint`, `oldest`, `oldest_reader`, `pinned`, `recovery`, and `stable`, while allowing callers to request one or more specific timestamp categories with `-q`.

## Important APIs, Types, and Functions

`default_query` is the canonical list of timestamp query names used when no `-q` appears. `usage_exit()` prints accepted query names and exits. `wt_timestamps(conn, query)` opens a session and prints `<query>=<timestamp>` using `conn.query_timestamp('get=' + s)` for each requested item. The top-level script performs all argument parsing and directory iteration.

## Control Flow

The script consumes leading `-q <name>` pairs, requires at least one directory, substitutes `default_query` when the requested query list is empty, and then opens each directory read-only through `wiredtiger_open(arg, 'readonly')`. It prints a directory header, emits query results, closes the connection, and separates multiple directories with a blank line.

## State and Persistence Behavior

The tool opens read-only WiredTiger connections and does not mutate database state. It creates a session in `wt_timestamps()` but does not explicitly close it before closing the connection. Output is stdout-only. The module performs work at import time because parsing is top-level, so it is intended as an executable script rather than an importable library.

## Dependencies and Integration Points

It depends on `py_common.wiredtiger_util.wiredtiger_open` and the WiredTiger connection method `query_timestamp`. The query names must match what WiredTiger accepts in `query_timestamp('get=...')`; the comments document aliases intentionally omitted from the default list.

## Risks and Edge Cases

The usage line contains a typo, `wt_typestamp`, which can confuse users. Query values are not validated against `default_query`, despite the usage text implying a constrained set; invalid names are deferred to WiredTiger. The parser only accepts options while at least two arguments remain and the first begins with `-`, so a trailing malformed option can be treated as a directory. Importing the module will execute the CLI.

## Test Signals

Smoke tests should invoke the script against a temporary WiredTiger home and verify default labels, multiple directories, and repeated `-q` arguments. Negative tests should cover invalid query names, missing directory arguments, and readonly-open failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_timestamps -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_to_mdb_bson.py -->
# sources/storage-engines/wiredtiger/tools/wt_to_mdb_bson.py Research

## Purpose

`wt_to_mdb_bson.py` converts MongoDB BSON values embedded in WiredTiger utility output into human-readable Python pretty output or Canonical Extended JSON. It supports output from `wt dump -x`, `wt verify -d dump_pages`, and `wt printlog -x -u`, either by reading stdin or by executing a provided `wt` binary.

## Important APIs, Types, and Functions

`Mode` distinguishes `DUMP`, `VERIFY`, and `PRINTLOG`. `print_bson()` formats decoded BSON as canonical JSON via `bson.json_util.dumps(..., CANONICAL_JSON_OPTIONS)` or as indented `pprint.pformat`. `convert_byte()` converts the escaped byte representation emitted by verify output into bytes suitable for BSON decoding. `wt_verify_to_bson()`, `wt_printlog_to_bson()`, and `wt_dump_to_bson()` implement the three conversion modes. `find_data_section()` and `decode_data_section()` locate and decode `wt dump` data pairs. `execute_wt()` builds subprocess argument lists for the supported `wt` invocations. `main()` owns argparse, mode mapping, stdin/subprocess selection, and dispatch.

## Control Flow

The CLI requires `-m/--mode` and optionally accepts `-j/--json`, `-f/--wt-path`, and an optional URI. If either URI or wt path is supplied, both are required by validation, although `printlog` later ignores the URI by passing `None` internally. Without `-f`, all input is read from stdin as lines. Dump mode searches for a `Data` marker and then decodes alternating key/value hex lines. Verify mode echoes every original line and appends decoded BSON under matching `V {...}` records. Printlog mode searches each line for `value-hex`, decodes it when possible, and otherwise preserves the original value-hex line.

## State and Persistence Behavior

The script does not mutate database contents. It may spawn the `wt` executable and read all subprocess stdout into memory. It writes converted content to stdout only. No temporary files are created.

## Dependencies and Integration Points

It depends on PyMongo's `bson` package, `bson.json_util`, Python `codecs`, `subprocess`, `argparse`, and regexes that match current `wt` output formats. It integrates with WiredTiger command output and MongoDB data files, especially `_mdb_catalog.wt` and value records that are BSON documents.

## Risks and Edge Cases

`decode_data_section()` assumes an even number of lines after `Data`; malformed dump output can index past the end. `convert_byte()` reads `inp[idx+1]` after a backslash without checking bounds, so truncated escapes can fail. Printlog decoding catches all exceptions and silently falls back to hex, which is robust but can hide format drift. Regexes are narrow and may fail if `wt` output spacing changes. The `printlog` path requires a URI whenever `-f` is used even though it does not use one, which is a CLI ergonomics issue. The subprocess call for printlog hard-codes `log=(compressor=snappy,path=journal/)`, coupling the tool to MongoDB journal layout and snappy availability.

## Test Signals

Fixtures should cover all three modes using captured `wt` output, both pretty and JSON output, invalid BSON fallback in printlog, verify escaped bytes with single and double backslashes, dumps without `Data`, odd dump line counts, and subprocess argument construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_to_mdb_bson.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_turtle_config_parse.py -->
# sources/storage-engines/wiredtiger/tools/wt_turtle_config_parse.py Research

## Purpose

`wt_turtle_config_parse.py` parses the final nonblank line of a `WiredTiger.turtle` file as a WiredTiger configuration string and prints a nested Python dictionary. It is a lightweight inspection tool for turning compact WiredTiger config syntax into something easier to read.

## Important APIs, Types, and Functions

`parse_wiredtiger_config(config_str)` is the main parser. It contains a nested `parse_section(s, start=0)` recursive-descent helper that tracks `key`, `value`, whether it is reading a key, and whether it is inside double quotes. Parenthesized values become nested dictionaries. `parse_turtle_file(filename)` reads nonblank lines, selects the last line, and parses it. The `__main__` block validates exactly one filename, pretty-prints the result, and catches exceptions as `Error: ...`.

## Control Flow

The parser walks one character at a time. In key mode it accumulates until `=` or an unquoted comma, treating standalone keys as empty-string values. In value mode it toggles quote state on `"`, recurses on unquoted `(`, returns on unquoted `)`, finalizes entries on unquoted commas, and appends all other characters to the value. At end of input it writes the last key/value pair and returns the result.

## State and Persistence Behavior

The tool reads one file and writes pretty output to stdout. It does not change the source file or WiredTiger home. Parser state is local to recursive calls.

## Dependencies and Integration Points

The script only uses the Python standard library (`sys`, `typing`, `pprint`). It is not using WiredTiger's native config parser, so it is an independent approximation of WiredTiger syntax. Its integration point is the `WiredTiger.turtle` file format and the convention that the last nonblank line contains the relevant config string.

## Risks and Edge Cases

The parser handles quotes and nested parentheses but not escaped quotes or all WiredTiger config grammar details. A nested section assigned to `value` replaces any accumulated value text, so mixed scalar-plus-nested forms may not preserve all content. It does not report trailing unmatched parentheses as an error when parsing from the top level. Values are returned as strings or nested dicts only; no numeric or boolean normalization is attempted. The usage text names `parse_wiredtiger_config.py`, not this file.

## Test Signals

Tests should include simple key/value pairs, bare keys, quoted commas, nested sections, empty files, malformed empty keys before `=`, unmatched parentheses, and real `WiredTiger.turtle` samples from current WiredTiger homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_turtle_config_parse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_verify/wt_verify.py -->
# sources/storage-engines/wiredtiger/tools/wt_verify/wt_verify.py Research

## Purpose

`wt_verify.py` wraps the WiredTiger `wt verify -t` tool and parses its `dump_pages` or `dump_blocks` diagnostic output into structured dictionaries, optional pretty text, and interactive visualizations. It supports row-store and variable-length column-store output and is meant for inspecting page metadata, block allocation, free gaps, and checkpoint-level page distributions.

## Important APIs, Types, and Functions

Parsing is split by dump type. `parse_dump_pages()` reads checkpoint sections separated by `SEPARATOR`, delegates checkpoint headers to `parse_chkpt_info()`, and page bodies to `parse_node()` plus `parse_metadata()`. `parse_dump_blocks()` extracts root and address ranges into `{checkpoint: {page_type: [(offset, size), ...]}}`. `is_int()` performs opportunistic integer conversion.

Visualization functions include `show_block_distribution_broken_barh()`, `show_block_distribution_hist()`, `show_free_block_distribution()`, `histogram()`, `pie_chart()`, `visualize_chkpt()`, and `visualize()`. They use `matplotlib`, `numpy`, `pandas`, and `mpld3.serve` to create browser-served HTML. Execution helpers include `find_wt_exec_path()`, `construct_command(args)`, and `execute_command(command, output_file)`. `output_pretty()` serializes parsed dictionaries into a custom brace-heavy string.

## Control Flow

`main()` parses `--dump` as `dump_blocks` or `dump_pages`, optional filename/home/input/output/print/visualize/wt path flags, and either uses an existing input file or constructs and runs a `wt` command. Generated `wt` output is always written to `wt_output_file.txt`, then parsed. Dump-pages mode can write pretty output and optionally serve requested histograms/pie charts. Dump-blocks mode always builds three visualizations and serves them, regardless of `--visualize`. If no parsed data exists, it prints a no-data message and returns.

## State and Persistence Behavior

The wrapper may create or overwrite `wt_output_file.txt` in the current directory and may write a user-specified parsed output file. It starts a WebAgg/mpld3 server for visualization. It does not modify WiredTiger data, but it runs `wt verify` against the requested home and file.

## Dependencies and Integration Points

The script depends on a local `wt` executable, either supplied by `-wt` or discovered under the WiredTiger root relative to the script. It depends on stable textual formats from `wt verify -t -d dump_pages` and `dump_blocks`. Python dependencies are substantial: `numpy`, `pandas`, `matplotlib` with WebAgg, `mpld3`, and standard `argparse`, `subprocess`, `json`, `re`, and `operator.itemgetter`.

## Risks and Edge Cases

`construct_command()` builds a shell command string and `execute_command()` runs it with `shell=True`; although the filename is quoted, `home_dir`, `dump`, and `wt_exec_path` are interpolated directly, so untrusted arguments are unsafe. `parse_metadata()` uses `dict` as a local name and assumes metadata split patterns are exact. Some parsing errors are hard exceptions, which is appropriate for diagnostics but brittle across output changes. `show_block_distribution_hist()` uses `all_addr` after loops and will fail if data has no page entries. `histogram()` assumes both internal and leaf lists have data; empty DataFrames can fail on `describe().loc[...]`. Visualization calls can block by serving HTML, which is expected for an interactive tool but not ideal for automated runs.

## Test Signals

Fixtures should cover both dump formats, multiple checkpoints, root-only or empty trees, VLCS/row-store page types, address gap calculations, malformed separator/header lines, and visualization paths with missing internal or leaf pages. Security-oriented tests should validate command construction with spaces and shell metacharacters, or motivate replacing `shell=True` with an argument vector.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/wt_verify/wt_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/xray_to_optrack/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/tools/xray_to_optrack/CMakeLists.txt Research

## Purpose

This CMake file conditionally builds the `xray_to_optrack` utility, which converts LLVM XRay traces to WiredTiger OpTrack logs. It ensures the tool is only built when the compiler and LLVM libraries support the required XRay APIs.

## Important APIs, Types, and Functions

The script sets `cmake_minimum_required(VERSION 3.21)` and declares a CXX project. It checks `CMAKE_CXX_COMPILER_ID` for Clang or AppleClang, requires compiler version at least 8, configures CMake package sorting to prefer the newest LLVM package, calls `find_package(LLVM CONFIG REQUIRED)`, requires `LLVM_PACKAGE_VERSION >= 8`, maps LLVM components with `llvm_map_components_to_libnames(llvm_libs support core symbolize xray)`, and creates the executable from `xray_to_optrack.cpp`.

## Control Flow

Configuration returns early with a status message when the compiler is not Clang-like, the compiler is too old, or LLVM is too old. If all gates pass, it adds include directories, compile definitions, and target libraries from LLVM.

## State and Persistence Behavior

This file affects build-system configuration only. It creates the build target when dependencies are present and otherwise skips it without failing the whole WiredTiger build. It writes no runtime state.

## Dependencies and Integration Points

The parent WiredTiger CMake build includes this directory from `sources/storage-engines/wiredtiger/CMakeLists.txt`. The utility depends on LLVM Support, Core, Symbolize, and XRay components plus Clang-compatible XRay instrumentation support.

## Risks and Edge Cases

`find_package(LLVM CONFIG REQUIRED)` is reached only after compiler checks but remains required; a Clang build without LLVM CMake package files can fail configuration instead of silently skipping. The component list and LLVM APIs may shift across newer LLVM versions. Returning from a subdirectory CMake file is intentional but depends on being included with `add_subdirectory`.

## Test Signals

Build matrix coverage should include non-Clang compilers, Clang without LLVM package files, LLVM below 8, and a modern LLVM/Clang environment that successfully links `xray_to_optrack`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/xray_to_optrack/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/xray_to_optrack/xray_to_optrack.cpp -->
# sources/storage-engines/wiredtiger/tools/xray_to_optrack/xray_to_optrack.cpp Research

## Purpose

`xray_to_optrack.cpp` converts an LLVM XRay trace plus instrumentation map into one OpTrack log file per thread. Each output record is a line of `record_type function_name tsc`, where enter events map to `0` and exit/tail-exit events map to `1`.

## Important APIs, Types, and Functions

The implementation lives in namespace `xray_to_optrack`. `make_error()` creates LLVM `StringError` values. `xray_to_optrack_record_type()` maps `llvm::xray::RecordTypes` to OpTrack integer record types and rejects unsupported XRay record kinds. `write_optrack_record()` writes one line to an output stream. `symbolize_func_id()` maps an XRay function id to a full symbol name using an instrumentation map address table, `llvm::symbolize::LLVMSymbolizer`, and a `llvm::DenseMap<uint32_t, std::string>` cache. `generate_optrack_log_name()` constructs `optrack_<pid>_<tid>`. The central `xray_to_optrack(instr_map, input)` loads the LLVM instrumentation map and trace file, opens per-thread output streams, symbolizes each record, and writes converted records. `main()` validates two arguments and prints LLVM errors.

## Control Flow

The converter loads the map first, then the trace. It iterates every `llvm::xray::XRayRecord`, lazily opens an output file keyed by `record.TId`, converts the record type, resolves the function name, and appends a line with the record TSC. Errors short-circuit through LLVM `Error`/`Expected` values and cause `main()` to return failure.

## State and Persistence Behavior

The tool writes output files named only by process id and thread id in the current working directory. It maintains an in-memory symbol cache and output-file map for the life of the process. It does not append explicitly; default `std::ofstream` construction truncates any existing file with the same name.

## Dependencies and Integration Points

It depends on LLVM XRay trace/instrumentation APIs, LLVM symbolization, DenseMap, and standard file streams. Its output format is the integration point with WiredTiger OpTrack consumers. It expects the instrumentation map path to be symbolizable by LLVM against the addresses returned by `map->getFunctionAddresses()`.

## Risks and Edge Cases

Files are keyed only by thread id in the `files` map, so if a trace contains the same TID under multiple PIDs, records would share one stream even though the filename includes the PID from the first record. Existing `optrack_*` files can be overwritten. Unsupported XRay record types abort the whole conversion. Symbol names containing whitespace are written unescaped, which may matter to downstream parsers expecting space-separated fields. The error output streams `llvm::Error` directly; compatibility depends on LLVM's raw_ostream operator overloads.

## Test Signals

Tests should use a small synthetic XRay trace/instrumentation map with enter, exit, and tail-exit records, verify per-thread output names and line format, exercise missing function ids and invalid symbols, and check overwrite/current-directory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/xray_to_optrack/xray_to_optrack.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/FUNDING.yml -->
# sources/sync-backup/borg/.github/FUNDING.yml Research

## Purpose

`FUNDING.yml` configures GitHub Sponsors and funding links for BorgBackup. It advertises `borgbackup` on GitHub Sponsors, Liberapay, Open Collective, and a custom support page.

## Important APIs, Types, and Functions

This is GitHub metadata, not executable application code. Keys are GitHub-recognized funding providers: `github`, `liberapay`, `open_collective`, and `custom`.

## Control Flow

There is no runtime control flow. GitHub reads this YAML file and renders funding links in repository UI.

## State and Persistence Behavior

The file is static repository configuration. It does not store secrets or mutate state.

## Dependencies and Integration Points

It integrates with GitHub's funding UI and external funding providers. The custom URL points at BorgBackup's support funding page.

## Risks and Edge Cases

Incorrect account names or a stale custom URL would send users to broken or unintended funding destinations. YAML structure is simple; syntax breakage would disable GitHub funding rendering.

## Test Signals

Validation is mostly by GitHub UI behavior or YAML linting. Link checks can verify that the custom funding URL remains reachable.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/dependabot.yml -->
# sources/sync-backup/borg/.github/dependabot.yml Research

## Purpose

`dependabot.yml` configures Dependabot updates for BorgBackup's GitHub Actions and Python requirement files. It groups update PRs to reduce churn and applies cooldowns for Python dependency updates.

## Important APIs, Types, and Functions

The file uses Dependabot config `version: 2` and two `updates` entries. The `github-actions` ecosystem scans `/` weekly and groups all actions under `actions`. The `pip` ecosystem scans `/requirements.d`, ignores `black`, runs weekly, applies semver cooldowns of 90 days for major and 30 days for minor updates, and groups all matching dependencies under `pip-dependencies`.

## Control Flow

Dependabot evaluates the schedule and opens grouped PRs according to ecosystem, directory, ignore, cooldown, and grouping rules. There is no in-repo executable flow.

## State and Persistence Behavior

Dependabot state lives in GitHub/Dependabot service data and PRs. The repository file is declarative and stores no secrets.

## Dependencies and Integration Points

It integrates with GitHub Dependabot, `.github/workflows/*`, and files under `requirements.d`. The `black` ignore aligns with the dedicated Black workflow and pinned pre-commit config, reducing formatter churn.

## Risks and Edge Cases

Grouped updates can make bisecting dependency regressions harder. Ignoring Black means formatter updates require manual maintenance. Cooldowns delay adoption of new upstream versions, trading stability for slower security or compatibility updates. Dependabot support for `cooldown` must remain compatible with GitHub's schema.

## Test Signals

Signals are Dependabot PR creation, GitHub's dependency graph/dependabot logs, and YAML/schema linting. A dry-run or service log should confirm both ecosystems are recognized.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/backport.yml -->
# sources/sync-backup/borg/.github/workflows/backport.yml Research

## Purpose

`backport.yml` automates creation of backport pull requests after a PR is merged or when a maintainer comments `/backport` on a pull request. It uses labels matching `port/<target>` to select backport destinations.

## Important APIs, Types, and Functions

The workflow is triggered by `pull_request_target` on closed PRs and `issue_comment` on created comments. Permissions grant `contents: write` and `pull-requests: write`. The single job runs on `ubuntu-24.04`, times out after five minutes, checks out the repository with `actions/checkout@v6`, and invokes `korthout/backport-action@v4` with `label_pattern: '^port/(.+)$'`.

## Control Flow

The job-level `if` permits execution only for merged pull requests or issue comments on PRs where the commenter is not the known backport-action bot and the comment starts with `/backport`. The action then inspects labels and creates backport PRs.

## State and Persistence Behavior

The workflow can create branches, commits, comments, and pull requests through GitHub APIs using the workflow token. It stores no local persistent artifacts.

## Dependencies and Integration Points

It integrates with GitHub Actions, PR labels, GitHub comments, and repository branch permissions. The bot-user-id filter prevents recursive comment-triggered loops.

## Risks and Edge Cases

`pull_request_target` runs with elevated token permissions, so action pinning and trust boundaries matter. The third-party action is version-pinned by tag rather than immutable SHA. If the bot user id changes because a different token/bot is used, recursion prevention may fail. Label naming must stay aligned with development docs and maintenance branch conventions.

## Test Signals

Test by merging a labeled PR in a safe repository or using a manual `/backport` comment. Also validate that unlabeled merged PRs do nothing and bot-authored comments do not retrigger.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/backport.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/black.yaml -->
# sources/sync-backup/borg/.github/workflows/black.yaml Research

## Purpose

`black.yaml` runs Black formatting checks for Python-related changes. It is a focused lint workflow separate from the broader CI workflow.

## Important APIs, Types, and Functions

The workflow triggers on pushes and pull requests touching `**.py`, `pyproject.toml`, or itself. It uses concurrency cancellation for pull requests, runs one `lint` job on `ubuntu-24.04`, checks out with `actions/checkout@v6`, and runs `psf/black` pinned to commit `87928e6d6761a4a6d22250e1fee5601b3998086e` with `version: "~= 24.0"`.

## Control Flow

GitHub path filters decide whether the workflow starts. The Black action installs/runs the requested Black version and fails the job if formatting differs.

## State and Persistence Behavior

The workflow does not commit formatting changes; it only reports pass/fail status. Concurrency can cancel older PR runs.

## Dependencies and Integration Points

It integrates with GitHub Actions, Black, Python source files, and `pyproject.toml` formatting settings. The comment notes that the workflow version should match local requirements in `requirements.d/codestyle.txt`.

## Risks and Edge Cases

The action is pinned by SHA, which is good for supply-chain stability, but the Black version range can still resolve to newer 24.x releases. If local pre-commit uses a different Black version, contributors can see mismatches. Path filters exclude non-Python generated formatting contexts.

## Test Signals

Signals are PR status checks and intentionally misformatted Python fixture changes. Compare workflow Black version against pre-commit and requirement pins during dependency updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/black.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/canary.yml -->
# sources/sync-backup/borg/.github/workflows/canary.yml Research

## Purpose

`canary.yml` runs scheduled and manually triggered tests with unlocked Python requirements to detect upstream dependency breakages before they affect locked CI. It covers representative Linux/macOS tox environments and a Windows PyInstaller/test path.

## Important APIs, Types, and Functions

The workflow triggers daily at `07:00 UTC` and via `workflow_dispatch`, with read-only contents permissions. `canary_tests` uses a matrix of Ubuntu and macOS Python/toxenv combinations, installs system packages, installs `requirements.d/development.txt` rather than the lock file, installs Borg with the extra matching the FUSE backend, and runs tox with an override to use unlocked development requirements. `windows_canary` uses `msys2/setup-msys2@v2`, Borg's `scripts/msys2-install-deps development`, a system-site-packages venv, PyInstaller requirements, editable install with extras, binary build, and pytest.

## Control Flow

Each matrix entry provisions OS and Python dependencies, installs Borg, and runs the environment-specific test command. Linux package selection branches by toxenv substring for `llfuse`, `pyfuse3`, or `mfusepy`. Windows uses MSYS2 shell defaults and environment variables to avoid path conversion.

## State and Persistence Behavior

The workflow creates virtual environments, build outputs, and test result files inside ephemeral GitHub runners. It does not upload artifacts or coverage. No repository state is changed.

## Dependencies and Integration Points

It integrates with `tox`, `pytest`, Python versions 3.11-3.14, FUSE package variants, Homebrew bundle installation, MSYS2 dependency scripts, PyInstaller specs, and Borg extras (`cockpit`, FUSE backends, `s3`, `sftp`, `rclone` on Windows).

## Risks and Edge Cases

Unlocked requirements intentionally introduce instability, so failures are signal but may be noisy. The tox override depends on tox accepting `--override "env_run_base.deps=[-rrequirements.d/development.txt]"`. macOS `brew bundle install || true` can mask dependency setup failures. The Linux test command contains a branch for Windows toxenv names in a non-Windows job, likely defensive dead code. Windows canary has `if: true`, making temporary disablement manual.

## Test Signals

The primary signal is daily workflow status. Useful follow-up signals include tracking failures against dependency release dates, verifying tox override behavior, and comparing canary failures to locked CI to distinguish upstream breakage from repository regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/canary.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/ci.yml -->
# sources/sync-backup/borg/.github/workflows/ci.yml Research

## Purpose

`ci.yml` is BorgBackup's main continuous integration and release-build workflow. It runs lint, security checks, sanitizer tests, native tox matrices, cross-OS VM tests, Windows binary/tests, and an informational SHA256 pack-id lane. On tags matching `2.*`, selected jobs build, smoke-test, attest, and upload binaries.

## Important APIs, Types, and Functions

Triggers include pushes to `master`, tags `2.*`, and pull requests to `master` touching code/config/requirement paths but excluding `docs/**`. Global concurrency cancels stale PR runs. Default permissions are read-only contents, with broader id-token/attestations permissions on jobs that attest binaries.

Jobs include `lint` using `astral-sh/ruff-action@v3`; `security` installing `bandit[toml]`; `asan_ubsan` building Borg with sanitizer flags and running pytest with `LD_PRELOAD`; `native_tests` using a dynamic JSON matrix that is smaller for PRs and broader for pushes/tags; `vm_tests` using `cross-platform-actions/action@v1.2.0` for FreeBSD, NetBSD, OpenBSD, and OmniOS; `windows_tests` using MSYS2 and PyInstaller; and `sha256_pack_id_tests` as continue-on-error tox coverage for alternate pack IDs.

## Control Flow

Most test jobs depend on `lint`. Native tests set up Python, pip/tox caches, OS packages, optional SFTP and MinIO services, locked development requirements, editable Borg installs with extras chosen from `TOXENV`, optional tag-only binary builds, provenance attestation, artifact upload, tox execution, and Codecov uploads. VM tests run OS-specific shell branches inside a cross-platform action, including package installation, filesystem setup for NetBSD xattrs, OpenSSL naming for OpenBSD, and TMPDIR relocation for OmniOS. Windows builds a venv, builds Borg/PyInstaller artifacts, uploads the binary, and runs pytest.

## State and Persistence Behavior

The workflow creates caches, build artifacts, binary artifacts, provenance attestations, coverage and test-result uploads, local service state for SSH/MinIO during jobs, and GitHub Actions artifacts. It does not write back to the repository. Tag builds produce distributable binary artifacts.

## Dependencies and Integration Points

CI integrates with GitHub Actions runners across Linux, macOS, Windows, ARM, and BSD-like VMs; Python 3.11-3.14; tox; pytest; Codecov; PyInstaller; SFTP/OpenSSH; MinIO; rclone; FUSE variants; Homebrew; MSYS2; package managers for BSD/OmniOS; and GitHub artifact/provenance attestation APIs.

## Risks and Edge Cases

The workflow has high dependency surface and long timeouts, so third-party action changes, runner image changes, package repository outages, or service startup timing can break CI. Some actions are tag-pinned rather than SHA-pinned. VM tests are `continue-on-error`, so regressions on less common platforms may not block merges. Native matrix `fail-fast: true` can stop other matrix entries after one failure, reducing signal. Direct downloads of MinIO binaries are not checksum-verified. The PR path filter excludes docs changes, so documentation build breakage from docs-only edits is not caught here.

## Test Signals

The workflow itself is the dominant test signal. Important health indicators are sanitizer failures, tox matrix pass/fail, Codecov uploads, binary smoke tests, artifact presence on tags, provenance attestation success, cross-OS VM outcomes, and canary comparison for dependency drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/codeql-analysis.yml -->
# sources/sync-backup/borg/.github/workflows/codeql-analysis.yml Research

## Purpose

`codeql-analysis.yml` runs GitHub CodeQL semantic analysis for BorgBackup's C/C++ and Python code. It scans pushes and pull requests affecting code and runs a scheduled weekly scan.

## Important APIs, Types, and Functions

Triggers include pushes to `master`, pull requests to `master`, and a Friday cron. Path filters include Python, Cython, C, C headers, and the workflow itself. The `analyze` job runs on `ubuntu-24.04`, times out after twenty minutes, grants `security-events: write`, and uses a matrix over `cpp` and `python`. Steps check out full history, set up Python 3.11, cache pip, install native packages, initialize CodeQL with `github/codeql-action/init@v4`, build/install Borg in a venv, and run `github/codeql-action/analyze@v4`.

## Control Flow

For each language matrix item, the job provisions dependencies, initializes CodeQL for that language, builds Borg so compiled extensions and source context are available, and uploads analysis results through the CodeQL action.

## State and Persistence Behavior

The workflow creates temporary virtual environments and pip cache entries on the runner. CodeQL results are uploaded as security alerts/results to GitHub. It does not modify repository files.

## Dependencies and Integration Points

It integrates with GitHub CodeQL, GitHub security-events permissions, Borg's locked development requirements, native build dependencies (`libssl`, `libacl`, `liblz4`), setuptools-scm full-history needs, and Python/C++ build tooling.

## Risks and Edge Cases

Twenty minutes may be tight if dependency installation or analysis slows. CodeQL action versions are tag-pinned rather than SHA-pinned. Path filters omit docs and other configuration, which is appropriate for analysis but means some build-affecting non-code changes may not run CodeQL. The same build step is used for both language matrix entries, which is simple but duplicates work.

## Test Signals

Signals include successful CodeQL workflow completion, uploaded code scanning alerts, cache hit rates, and build/install success before analysis. A code change in both Python and C should trigger two matrix entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.pre-commit-config.yaml -->
# sources/sync-backup/borg/.pre-commit-config.yaml Research

## Purpose

`.pre-commit-config.yaml` defines local pre-commit hooks for Borg contributors. It runs Black formatting and Ruff linting before commits.

## Important APIs, Types, and Functions

The config references `https://github.com/psf/black` at `rev: 24.8.0` with hook `black`, and `https://github.com/astral-sh/ruff-pre-commit` at `rev: v0.15.0` with hook `ruff`.

## Control Flow

When pre-commit is installed, it creates hook environments at the pinned revisions and runs matching hooks against staged files. The file itself has no runtime logic.

## State and Persistence Behavior

Pre-commit creates local hook caches outside or under user cache directories, but the repository config is static. It does not store secrets.

## Dependencies and Integration Points

It integrates with contributor local workflows, Black, Ruff, and formatting/lint settings in project config such as `pyproject.toml`. It should stay aligned with GitHub workflows that run Black/Ruff.

## Risks and Edge Cases

Black is pinned to 24.8.0 while the GitHub Black action allows `~= 24.0`; this is likely compatible but can drift if the action resolves a newer patch/minor. Ruff is pinned locally while CI uses `astral-sh/ruff-action@v3`, whose installed Ruff version may differ unless separately configured. Version drift can produce local/CI mismatches.

## Test Signals

Run `pre-commit run --all-files` and compare results to CI lint jobs. Dependency update PRs should intentionally update this file with workflow versions when needed.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/.readthedocs.yaml -->
# sources/sync-backup/borg/.readthedocs.yaml Research

## Purpose

`.readthedocs.yaml` configures Read the Docs builds for BorgBackup documentation, including OS image, Python version, checkout behavior, native packages, Python installs, Sphinx config, and downloadable formats.

## Important APIs, Types, and Functions

The config uses Read the Docs schema `version: 2`, builds on `ubuntu-22.04` with Python `3.11`, runs `git fetch --unshallow` after checkout, installs native packages needed to build Borg extensions, installs `requirements.d/development.lock.txt`, `requirements.d/docs.txt`, and the project itself via pip, points Sphinx at `docs/conf.py`, and requests `htmlzip` and `pdf` formats.

## Control Flow

Read the Docs provisions the environment, runs the post-checkout job, installs apt and Python dependencies, invokes Sphinx using the configured file, and publishes requested output formats.

## State and Persistence Behavior

All build state is in the Read the Docs build environment. Published documentation artifacts are hosted by Read the Docs. The config stores no secrets.

## Dependencies and Integration Points

It integrates with `docs/conf.py`, locked development dependencies, docs requirements, Borg's package build, setuptools-scm full-history versioning, native libraries (`acl`, `ssl`, `lz4`), and Sphinx PDF/html builders.

## Risks and Edge Cases

Building the package during docs means native dependency or lock-file issues can break documentation. `git fetch --unshallow` assumes the checkout is shallow and network access is available. PDF output depends on Read the Docs LaTeX support and Sphinx config. Python 3.11 must remain supported by Borg docs dependencies.

## Test Signals

Signals include Read the Docs build logs, generated HTMLzip/PDF availability, and local `tox -e docs` or `make -C docs html` comparisons using the same dependency set.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/.readthedocs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/MANIFEST.in -->
# sources/sync-backup/borg/MANIFEST.in Research

## Purpose

`MANIFEST.in` customizes BorgBackup source distribution contents. Because `setuptools_scm` includes git-committed files automatically, this file mostly excludes unneeded repository metadata and explicitly includes platform C source files.

## Important APIs, Types, and Functions

Directives include `exclude` for `.editorconfig`, `.gitattributes`, `.gitignore`, `.mailmap`, and `Vagrantfile`; `prune .github`; and `include` for platform-specific C files under `src/borg/platform/`.

## Control Flow

During sdist creation, setuptools applies these manifest rules on top of setuptools-scm's file discovery. The `.github` tree is omitted, while selected C files are retained.

## State and Persistence Behavior

This file affects package build artifacts only. It does not affect installed runtime behavior directly except by determining which source files are available in sdists.

## Dependencies and Integration Points

It integrates with `pyproject.toml`, `setup.py`/build backend behavior, setuptools-scm, and platform extension compilation. Development docs explicitly remind maintainers to verify `MANIFEST.in`, `pyproject.toml`, and setup metadata before release.

## Risks and Edge Cases

If new required generated or platform files are added and not committed or included, sdist builds can fail. Pruning `.github` is expected but removes workflow metadata from source archives. Comments imply setuptools-scm handles most committed files, so maintainers may overlook explicit include needs for unusual build inputs.

## Test Signals

Run `python -m build`, inspect the sdist file list, and install/test from the sdist rather than the git checkout. Release checks should verify platform C files are present.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/Makefile -->
# sources/sync-backup/borg/docs/Makefile Research

## Purpose

`docs/Makefile` is BorgBackup's Sphinx documentation build wrapper. It exposes common Sphinx builders such as HTML, dirhtml, singlehtml, epub, LaTeX, PDF, text, man pages, linkcheck, doctest, and changes.

## Important APIs, Types, and Functions

Configurable variables are `SPHINXOPTS`, `SPHINXBUILD`, `PAPER`, and `BUILDDIR`. `ALLSPHINXOPTS` passes doctree output, paper settings, extra options, and the current docs directory to Sphinx. Targets invoke `$(SPHINXBUILD) -b <builder> $(ALLSPHINXOPTS) $(BUILDDIR)/<builder>`, with `latexpdf` running `make -C $(BUILDDIR)/latex all-pdf`.

## Control Flow

Users run a make target; the target invokes Sphinx and prints a completion hint. `clean` removes build output. The `help` target lists available builders. The `.PHONY` declaration names documentation targets.

## State and Persistence Behavior

The Makefile writes generated documentation under `docs/_build` by default and removes it on `clean`. It does not modify source docs.

## Dependencies and Integration Points

It integrates with Sphinx, `docs/conf.py`, docs source `.rst` files, LaTeX toolchains for PDF, linkcheck network behavior, and doctest-enabled documentation. CI/readthedocs may call equivalent Sphinx builders rather than this Makefile directly.

## Risks and Edge Cases

The Makefile assumes `sphinx-build` is on PATH unless overridden. `latexpdf` assumes the generated LaTeX directory has a working Makefile and TeX toolchain. Network-sensitive `linkcheck` can be flaky. The target set is broad but conventional; failures usually reflect dependencies or Sphinx config.

## Test Signals

Run `make -C docs html`, `make -C docs man`, and `make -C docs linkcheck` as appropriate. Read the Docs builds and tox docs environments are external validation signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/_static/Makefile -->
# sources/sync-backup/borg/docs/_static/Makefile Research

## Purpose

`docs/_static/Makefile` builds static logo assets from `logo.svg` for documentation outputs. It creates `logo.pdf` for LaTeX/PDF builds and `logo.png` for raster uses.

## Important APIs, Types, and Functions

The `all` target depends on `logo.pdf` and `logo.png`. `logo.pdf` runs `inkscape logo.svg --export-pdf=logo.pdf`; `logo.png` runs `inkscape logo.svg --export-png=logo.png --export-dpi=72,72`; `clean` removes generated logo files.

## Control Flow

Make rebuilds the generated assets when `logo.svg` is newer or outputs are absent. `clean` deletes both outputs.

## State and Persistence Behavior

The file writes `logo.pdf` and `logo.png` in `docs/_static` and removes them on clean. It does not alter `logo.svg`.

## Dependencies and Integration Points

It depends on Inkscape CLI compatibility. `docs/conf.py` references `_static/logo.svg` for HTML and `_static/logo.pdf` for LaTeX, so the PDF output is relevant to documentation PDF builds.

## Risks and Edge Cases

Inkscape CLI flags have changed across versions; newer Inkscape versions may prefer different export option syntax. If `logo.pdf` is not prebuilt and Inkscape is unavailable in the docs environment, LaTeX builds can fail.

## Test Signals

Run `make -C docs/_static all` with the expected Inkscape version and verify both output files. PDF documentation builds validate the `logo.pdf` path.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/_static/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/conf.py -->
# sources/sync-backup/borg/docs/conf.py Research

## Purpose

`docs/conf.py` is BorgBackup's Sphinx configuration. It sets project metadata, derives documentation version from `borg.__version__`, configures HTML/theme/static behavior, LaTeX/man-page output, extensions, and small Sphinx runtime hooks.

## Important APIs, Types, and Functions

The config inserts `../src` into `sys.path` and imports `borg.__version__ as sw_version`. It computes `version` by splitting at `+` or `-`, sets `release = version`, defines `project`, copyright, source suffix, master doc, warning suppression, `primary_domain = "rst"`, and Pygments style. It imports `guzzle_sphinx_theme`, sets `html_theme_path`, `html_theme`, `html_theme_options`, logo/favicon/static/extra paths, sidebar templates, index/source-link/footer options, and LaTeX settings. `set_rst_settings(app)` updates docutils settings to remove field/option name limits, and `setup(app)` loads `sphinxcontrib.jquery`, adds `css/borg.css`, and connects the hook. `extensions` is finally set to include extlinks, autodoc, todo, coverage, viewcode, jquery, and guzzle theme. `extlinks` defines GitHub issue links.

## Control Flow

Sphinx imports this file during build. Import-time code adjusts `sys.path`, imports Borg and theme modules, computes config values, and registers the `setup()` hook. On builder initialization, the hook mutates `app.env.settings`.

## State and Persistence Behavior

The file does not persist state itself, but it controls generated HTML, LaTeX, man-page, and help output. Importing Borg during docs build can execute package import side effects and requires dependencies needed for the import to succeed.

## Dependencies and Integration Points

It integrates with Borg package metadata, Sphinx, docutils, `guzzle_sphinx_theme`, `sphinxcontrib.jquery`, static assets under docs, `src/borg/paperkey.html`, Read the Docs config, and docs Makefile builders. LaTeX output depends on `_static/logo.pdf` and selected appendices.

## Risks and Edge Cases

Importing `borg` to get the version couples docs builds to package importability. There are two assignments to `extensions`; the initial empty list is replaced later, which is harmless but can confuse maintenance. Theme dependencies must be installed in docs environments. Version splitting assumes local versions contain `+` or prerelease/build separators use `-`; unusual version strings may produce unexpected display versions.

## Test Signals

Run Sphinx HTML, man, and LaTeX/PDF builds with the same requirements as Read the Docs. Confirm version rendering, sidebar/theme assets, issue extlinks, and `paperkey.html` inclusion.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/docs/global.rst.inc -->
# sources/sync-backup/borg/docs/global.rst.inc Research

## Purpose

`global.rst.inc` centralizes common reStructuredText substitutions and external link targets used across BorgBackup documentation. It avoids repeating package names, repository URLs, cryptography terminology links, dependency links, and related references in many `.rst` files.

## Important APIs, Types, and Functions

The file sets default highlighting to bash with `.. highlight:: bash`, defines substitutions such as `|package_dirname|`, `|package_filename|`, `|package_url|`, and `|git_url|`, and declares named hyperlink targets for GitHub, the issue tracker, deduplication, AES, HMAC-SHA256, SHA256, PBKDF2, argon2, ACL/libacl/libattr, compression libraries, OpenSSL, Python 3, Buzhash, msgpack, FUSE bindings, userspace filesystems, Cython, and virtualenv.

## Control Flow

There is no executable control flow. Sphinx/docutils processes this include wherever docs use `.. include:: global.rst.inc` or relative includes from subdirectories.

## State and Persistence Behavior

The file contributes substitutions and link definitions to document parsing. It does not generate files directly or store runtime state.

## Dependencies and Integration Points

Many docs files include this file, including top-level and internals/deployment pages with relative paths. It integrates with Sphinx substitution replacement, external link checking, and documentation terminology consistency.

## Risks and Edge Cases

Stale external URLs can create linkcheck failures or mislead readers. Because includes are relative, moving docs files can break include paths. Substitution values using `|version|` depend on Sphinx version substitution from `docs/conf.py`.

## Test Signals

Sphinx builds validate substitution definitions and include paths. `make -C docs linkcheck` is the main signal for stale external references.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/docs/global.rst.inc -->
