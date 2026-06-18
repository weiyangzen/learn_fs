# subset-b-008393 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTest.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTest.sh

Purpose: Joshua entrypoint for TestHarness2 correctness runs in containerized FoundationDB testing. It validates `JOSHUA_SEED`, builds `python3 -m test_harness.app` arguments, captures stdout/stderr, and guarantees Joshua receives XML even when Python crashes before normal output.

Important APIs and control flow: shell environment variables are the API. Required input is `JOSHUA_SEED`; optional knobs include `JOSHUA_TEST_FILES_DIR`, `OLDBINDIR`, `TH_ARCHIVE_LOGS_ON_FAILURE`, preservation flags, output location, buggify/valgrind/long-running settings passed indirectly through TestHarness2. The script creates a unique `th_run_*` directory, runs TestHarness2 with `--no-clean-up` and `--no-verbose-on-failure`, tees stdout to `python_app_stdout.log`, and derives exit status from Python exit plus `Ok="0"` in captured XML.

State and persistence: test artifacts live under `TH_OUTPUT_DIR`, `DIAG_LOG_DIR`, or `/tmp`. Cleanup is trap-based and preserves or deletes the run directory based on success, Python exit, XML failure, and archival environment settings.

Dependencies and integration: depends on bash, `python3`, `tee`, TestHarness2 importability, Joshua env vars, and optional `test_args.txt`. It integrates with Joshua by producing single-line XML results and with `test_harness.app` by passing run temp and binary paths.

Risks and test signals: XML failure detection is a grep over stdout and can miss JSON mode or altered formatting. Cleanup references `PYTHON_EXIT_CODE` before assignment if an early exit occurs. Strong test signals include missing-seed fallback XML, empty-output fallback XML, preserved logs on failure, and shell exit code consistency with `Ok`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTimeout.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTimeout.sh

Purpose: timeout-side Joshua wrapper for normal correctness tests. It converts a scheduler timeout into TestHarness2 summaries by running `python3 -m test_harness.timeout`.

Important APIs and control flow: no custom functions or arguments. The script uses `bash -u`, so unset variable expansions would fail, but it does not read shell variables directly. It delegates all behavior to `test_harness.timeout`, which scans the current working tree for trace files and emits killed-test summaries.

State and persistence: it does not create state itself. It assumes the current directory contains run artifacts from an interrupted TestHarness2/fdbserver execution.

Dependencies and integration: depends on Python module import path and the timeout module. It is paired with `correctnessTest.sh` in Joshua job configuration.

Risks and test signals: no explicit error handling; import failures or no traces mean Python behavior determines output. Test by running in a temp directory with trace files and verifying an `ExternalTimeout` summary is emitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTimeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/localClusterStart.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/localClusterStart.sh

Purpose: starts a local single-process FoundationDB cluster for Joshua-related scripts. It prepares work/log/config directories, writes an `fdb.cluster` file, starts `fdbserver`, configures a `single memory` database, verifies availability, and can stop the process.

Important APIs/functions: environment variables configure paths and behavior: `WORKDIR`, `LOGDIR`, `ETCDIR`, `BINDIR`, `FDBPORTSTART`, `FDBPORTTOTAL`, `SERVERCHECKS`, `CONFIGUREWAIT`, `FDBCLUSTERTEXT`, `AUDITCLUSTER`, `AUDITLOG`. Functions are `log`, `displayMessage`, `createDirectories`, `createClusterFile`, `startFdbServer`, `getStatus`, `verifyAvailable`, `createDatabase`, `startCluster`, and `stopCluster`.

Control flow: if `FDBCLUSTERTEXT` is absent it randomizes a loopback IP and port. `startCluster` sequences directory creation, cluster file generation, server launch, and database configuration. Availability is checked through `fdbcli status json`.

State and persistence: writes under `${SCRIPTDIR}/tmp/fdb.work` by default, with cluster config, logs, and data directories. It keeps the server PID in `FDBSERVERID` shell state and optionally writes audit log lines.

Dependencies and integration: requires executable `fdbserver` and `fdbcli` in `BINDIR`, bash, coreutils, and port availability. Other Joshua scripts can source or call it to get a local cluster file.

Risks and test signals: random ports can collide; `createDatabase` logs but ignores final availability failure; chmod scans broad script patterns; process cleanup relies on a valid PID. Test signals are `fdbclient.log`, `startcluster.log`, `database_available=true`, and successful `fdbcli` operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/localClusterStart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTest.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTest.sh

Purpose: Joshua wrapper for extended-duration simulation correctness runs. It disables ASAN leak detection, validates `JOSHUA_SEED`, creates a `th_longrunning_*` temp directory, and invokes TestHarness2 with `--long-running`.

Important APIs and control flow: uses `JOSHUA_SEED`, `OLDBINDIR`, `TH_OUTPUT_DIR`, and `DIAG_LOG_DIR`. It calls `python3 -m test_harness.app --joshua-seed ... --old-binaries-path ... --long-running --run-temp-dir ...`, redirecting Python stderr into the run directory.

State and persistence: run artifacts persist in the created temp directory; there is no cleanup trap in this wrapper, so lifecycle is owned by TestHarness2 config or external Joshua cleanup.

Dependencies and integration: depends on TestHarness2 and old binary path convention. `--long-running` maps to `run.py` disabling simulation speedup and using no timeout.

Risks and test signals: no stdout tee/fallback XML guard compared with `correctnessTest.sh`, so early Python failure can produce poor Joshua output. Test signals include long-running command line knobs in trace/config and absence of external timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTimeout.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTimeout.sh

Purpose: timeout companion for long-running correctness jobs. It runs `test_harness.timeout` with `--long-running` so generated timeout summaries carry long-running context.

Important APIs and control flow: no shell functions. It delegates argument parsing to the Python config layer, where `--long-running` affects `Summary.done()` timeout diagnostics.

State and persistence: reads existing trace artifacts from the current working directory and writes summaries to stdout.

Dependencies and integration: requires Python module importability and trace files left by an interrupted long-running job.

Risks and test signals: if no trace files exist, no summaries are emitted. Test with a killed long-running trace directory and verify `ExternalTimeout LongRunning="1"`-style attributes are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/longRunningCorrectnessTimeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTest.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTest.sh

Purpose: Joshua wrapper for running simulation correctness tests under Valgrind. It validates `JOSHUA_SEED`, creates `th_valgrind_*`, and invokes TestHarness2 with `--use-valgrind`.

Important APIs and control flow: consumes `JOSHUA_SEED`, `OLDBINDIR`, `TH_OUTPUT_DIR`, and `DIAG_LOG_DIR`; passes `--old-binaries-path`, `--use-valgrind`, and `--run-temp-dir` to `test_harness.app`.

State and persistence: artifacts and Valgrind XML are written under the run temp directory. Cleanup behavior is mostly delegated to TestHarness2.

Dependencies and integration: requires `valgrind` available to `run.py`, TestHarness2, current `fdbserver`, and optional debug path env. In `run.py`, only the current binary is valgrinded, not old restart binaries.

Risks and test signals: lacks the richer fallback/capture logic of `correctnessTest.sh`. Test signals include generated `valgrind-<seed>.xml`, `ValgrindError` summary children for non-leak errors, and longer timeout multiplier.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTimeout.sh -->
## sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTimeout.sh

Purpose: timeout companion for Valgrind jobs. It runs `test_harness.timeout --use-valgrind` so timeout summaries also parse available Valgrind XML files.

Important APIs and control flow: no direct options except the hard-coded Python flag. The timeout module recursively locates trace directories and `valgrind*.xml`.

State and persistence: reads current-directory artifacts and writes summaries to stdout.

Dependencies and integration: depends on TestHarness2 timeout and valgrind parser modules.

Risks and test signals: multiple Valgrind XML files are combined with each trace run, which can over-report if stale XML remains. Test with one trace run and one Valgrind XML to verify `ExternalTimeout` plus `ValgrindError` handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/Joshua/scripts/valgrindTimeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/SimpleOpt/CMakeLists.txt -->
## sources/storage-engines/foundationdb/contrib/SimpleOpt/CMakeLists.txt

Purpose: declares `contrib/SimpleOpt/include` as a CMake include directory for the vendored SimpleOpt single-header command-line parser.

Important APIs and control flow: the only command is `include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)`.

State and persistence: no build outputs are defined here; it mutates CMake include search state for consumers in the surrounding build.

Dependencies and integration: depends on the FoundationDB CMake hierarchy including this file before targets that include `SimpleOpt/SimpleOpt.h`.

Risks and test signals: directory-scoped include paths can unintentionally affect sibling targets. Build failures in C++ sources including `SimpleOpt/SimpleOpt.h` are the practical test signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/SimpleOpt/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/SimpleOpt/include/SimpleOpt/SimpleOpt.h -->
## sources/storage-engines/foundationdb/contrib/SimpleOpt/include/SimpleOpt/SimpleOpt.h

Purpose: vendored SimpleOpt 3.4, a portable single-header C++ command-line parser supporting short/long/word options, optional/required/multiple arguments, clumped short options, partial matching, case-insensitive matching, and Windows slash conversion.

Important APIs/types: enums `ESOError`, `_ESOFlags`, and `ESOArgType`; option descriptor `CSimpleOptTempl<SOCHAR>::SOption`; aliases `CSimpleOptA`, `CSimpleOptW`, and `CSimpleOpt`. Public methods include `Init`, `SetOptions`, `SetFlags`, `HasFlag`, `Next`, `Stop`, `LastError`, `OptionId`, `OptionText`, `OptionArg`, `OptionSyntax`, `MultiArg`, `FileCount`, `File`, and `Files`.

Control flow: `Next()` scans `argv`, normalizes slash options on Windows, handles combined `=` args, short arg forms, clumps, invalid options, and required separated args. Non-options are shuffled behind unprocessed args, preserving file order for `Files()`. `LookupOption` uses exact or best partial matching; `MultiArg` validates required arguments.

State and persistence: parser mutates the caller-provided `argv` array and may allocate a shuffle buffer when argc exceeds `SO_STATICBUF` unless `SO_MAX_ARGS` forces static operation.

Dependencies and integration: header-only C++ with optional C runtime use. FoundationDB includes it via the contrib CMake include path.

Risks and test signals: mutating `argv` surprises callers; partial matching can be ambiguous; `Copy` disables ASAN due overlapping moves; Unicode/MBCS support is limited. Tests should cover ambiguous prefixes, clumped flags, `SO_O_NOERR`, `SO_MULTI`, Windows slash behavior, and file ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/SimpleOpt/include/SimpleOpt/SimpleOpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/analyze_determinism_failure.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/analyze_determinism_failure.py

Purpose: standalone diagnostic tool comparing trace JSON from an initial simulation run and its determinism-check rerun to find divergence, especially around S3 and bulk dump events.

Important APIs/functions: `parse_trace_file`, `extract_key_events`, `normalize_event`, `compare_event_sequences`, `extract_s3_operations`, `analyze_s3_operations`, `compare_early_events`, `find_divergence_point`, `analyze_duplication_pattern`, and `main`.

Control flow: CLI takes two directories, loads all `*.json` traces from each, compares early event types and selected fields, locates the first divergence, detects approximate 2x duplication patterns, extracts key event types, compares S3 filenames, and prints a summary.

State and persistence: read-only; no output files. All state is in lists/dicts of parsed JSON events.

Dependencies and integration: Python stdlib only. `run.py` writes a README command pointing users at this script when determinism analysis directories are created.

Risks and test signals: assumes JSON line traces and directory-level glob ordering; comparisons are event-order sensitive and normalize only known timing fields. Test with synthetic traces covering count mismatch, first type mismatch, S3 object mismatch, malformed JSON, and missing files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/analyze_determinism_failure.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/__init__.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/__init__.py

Purpose: package marker for the TestHarness2 Python module. It intentionally contains no runtime code.

Important APIs and control flow: none; import side effects are absent.

State and persistence: none.

Dependencies and integration: enables `python3 -m test_harness.app` and sibling module imports from Joshua scripts.

Risks and test signals: packaging/import path issues surface as `ModuleNotFoundError` in wrappers. A basic import smoke test is sufficient.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/app.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/app.py

Purpose: primary TestHarness2 CLI entrypoint. It builds config from CLI/env, sets up logging, runs `TestRunner`, and ensures Joshua receives XML on ordinary failure, exception, or abnormal early termination.

Important APIs/functions: `setup_logging()` writes `app_log.txt` under `config.run_temp_dir` or `/tmp`; `create_error_xml()` constructs a `SummaryTree("Test")` with `Ok="0"` and a `JoshuaMessage`; the module main block wires argparse, config extraction, `TestRunner().run()`, and fallback XML.

Control flow: parse args, configure logging, run tests, exit 1 on false success, catch exceptions into fatal XML, and in `finally` emit emergency fallback XML if nothing was generated.

State and persistence: writes a log file and stdout XML/JSON summaries. It depends on global mutable `config`.

Dependencies and integration: imports `test_harness.config`, `run.TestRunner`, and `summarize.SummaryTree`; called by Joshua wrapper scripts.

Risks and test signals: `create_error_xml` returns a `SummaryTree` despite type hint `str`; logger setup occurs after config parsing, so config parse failures bypass file logging. Test with missing required `--run-temp-dir`, runner exceptions, and normal failed tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/app.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/config.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/config.py

Purpose: central configuration registry for TestHarness2, exposing every option as a mutable global `config` value with argparse and environment-variable support.

Important APIs/types: `BuggifyOptionValue`, `BuggifyOption`, `ConfigValue`, and `Config`. Main methods are `change_default`, `build_arguments`, `extract_args`, `_build_map`, `_read_env`, and `_parse_env_value`.

Control flow: `Config.__init__` declares defaults and `<name>_args` metadata, builds an ordered map by reflecting attributes, reads env defaults, and seeds `random` from `joshua_seed`. `build_arguments` emits argparse flags; `extract_args` writes parsed values back to the singleton and reseeds.

State and persistence: all harness modules read shared in-memory singleton state. It also defines paths and Joshua/FDB integration settings, but persists nothing directly.

Dependencies and integration: Python argparse/env, `Path`, random, and every TestHarness2 module. Joshua wrappers map env vars such as `JOSHUA_SEED`, `JOSHUA_TEST_FILES_DIR`, and `TH_ARCHIVE_LOGS_ON_FAILURE` into this layer.

Risks and test signals: reflection order and `_args` placement are fragile; bool env parsing is strict; `BuggifyOption` invalid values assert. Test CLI/env precedence, required `run_temp_dir`, env-name overrides, and choices for output/trace formats.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/fdb.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/fdb.py

Purpose: FoundationDB persistence layer for TestHarness2 coverage and per-test runtime statistics.

Important APIs/types: `str_to_tuple`, `open_db`, `chunkify`, transactional `write_coverage_chunk`, `set_initialized`, `_read_coverage`, public `write_coverage`/`read_coverage`, `TestStatistics`, `Statistics`, and `FDBStatFetcher`.

Control flow: sets FDB API version 630. Coverage writes are chunked by 100 entries, using directory layers for coverage and metadata; before initialization it writes uncovered probes too, later it only increments covered probes. Runtime stats store packed `<II` runtime/run-count values and are read into ordered maps.

State and persistence: caches a global FDB database handle, writes coverage keys under configured Joshua directories, and accumulates runtime statistics in FDB directory subspaces.

Dependencies and integration: external `fdb` Python binding, `fdb.tuple`, `struct`, `Coverage`, `SummaryTree`, and `run.StatFetcher`. Used by `Summary.summarize` and `TestPicker`.

Risks and test signals: API version and cluster availability are environmental; `config.joshua_dir` is asserted for coverage writes; global DB cache ignores cluster-file changes. Test with a local FDB cluster for coverage initialization and stats increment semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/fdb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/joshua.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/joshua.py

Purpose: reads Joshua ensemble results and prints compact reproduce/error summaries in the current TestHarness2 output format.

Important APIs/types: SAX `ToSummaryTree`, helper `_print_summary`, and public `print_errors(ensemble_id)`.

Control flow: opens Joshua model, tails ensemble results, parses each XML result line into `SummaryTree`, derives a reproduce command (`bin/fdbserver -r ... -f ... -s ... -b ... --crash --trace_format ...`), filters warnings/errors/buggify sections, and prints XML or JSON according to config.

State and persistence: no writes. Maintains per-call command de-duplication to avoid duplicate JSON/XML keys.

Dependencies and integration: external `joshua.joshua_model`, XML SAX, config, and `test_harness.run.is_no_sim`. Invoked by `results.py`.

Risks and test signals: assumes Joshua record tuple shapes and XML lines; `errors.name == "ValgrindError"` check likely does not detect valgrind because `errors.name` is fixed. Test with multiple result tuple formats, duplicate commands, details mode, and missing attributes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/joshua.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/results.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/results.py

Purpose: CLI/reporting layer for Joshua ensemble summaries. It prints per-error reproduce details and aggregate code-probe/runtime statistics.

Important APIs/types: `GlobalStatistics`, `EnsembleResults`, `write_header`, and `write_footer`. `EnsembleResults.dump()` emits `EnsembleResults`, `CodeProbe`, and optionally per-test runtime nodes.

Control flow: main configures pretty output, prints an XML/JSON envelope, tries to import Joshua summary printer, then computes coverage status from FDB coverage counts and runtime stats. Exit code is nonzero when coverage is not OK.

State and persistence: read-only from FDB via `test_harness.fdb.Statistics` and `read_coverage`.

Dependencies and integration: config filters, `SummaryTree`, `Coverage`, `quoteattr`, optional Joshua package. Consumed by humans/automation inspecting ensembles.

Risks and test signals: `ratio` is calculated before `total_test_runs` is populated, so missed-probe threshold may be wrong; JSON header formatting is hand-built. Test coverage-disabled mode, empty coverage, missed non-rare probe errors, and missing Joshua import warning.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/run.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/run.py

Purpose: core TestHarness2 orchestrator. It selects tests, chooses current/old binaries, runs `fdbserver`, handles buggify/restart/determinism/valgrind/long-running modes, records stats, decorates summaries, organizes determinism artifacts, and controls cleanup.

Important APIs/types: helpers `parse_test_args_file`, `binary_uses_sanitizers`, `resolve_fdbserver_memory`, predicates `is_restarting_test`/`is_negative`/`is_no_sim`/`is_rare`; classes `TestDescription`, `StatFetcher`, `TestPicker`, `OldBinaries`, `ResourceMonitor`, `TestRun`, and `TestRunner`.

Control flow: `TestPicker` scans configured test-type directories, parses `.txt/.toml` metadata, filters by regex, prioritizes rare tests, loads stats, and chooses least-runtime candidates. `TestRun.run()` builds the fdbserver command, optionally prefixes valgrind, sets TLS/memory/fault-injection/restart/buggify flags, runs with timeout, decodes output robustly, summarizes traces, and writes stdout capture. `TestRunner.run_tests()` handles restart sequences, optional unseed determinism reruns, Joshua logtool upload on failure, stats, and XML output.

State and persistence: creates per-UUID temp dirs under `config.run_temp_dir`; writes trace outputs, stdout, Valgrind XML, determinism analysis directories, README files, and maybe FDB stats/coverage through other modules. Cleanup deletes the UUID directory unless preserving failure logs.

Dependencies and integration: config singleton, `Version`, `Summary`, fdbserver binaries, old binary directory, Valgrind, `joshua_logtool.py`, FoundationDB trace naming, and OS resource accounting.

Risks and test signals: many environment-dependent branches; debug prints to stderr may affect failure classification; cleanup can remove artifacts unless archive env is set; `TestDescription.__eq__` appears to compare `<` instead of equality. Test direct args-file mode, restart binary selection, sanitizer memory auto-detection, decode errors, determinism failure organization, and logtool gating.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/summarize.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/summarize.py

Purpose: converts FoundationDB trace files and test process metadata into compact Joshua-compatible XML/JSON summaries, including errors, warnings, coverage, timeout, Valgrind, stderr, and determinism signals.

Important APIs/types: `SummaryTree`, `ParseHandler`, `Parser`, `XmlParser`, `JsonParser`, `Coverage`, `TraceFiles`, and `Summary`. `Summary.register_handlers()` installs event callbacks for ProgramStart, Simulation, ElapsedTime, warnings/errors, CodeCoverage, test counts, severity remaps, buggify/fault injection, stderr severity, and random reseeds.

Control flow: `Summary.summarize()` groups trace files by timestamp, parses the newest run, writes FDB coverage when configured, and calls `done()`. `done()` finalizes pass/fail state, adds warning/error limits, timeout, peak memory, Valgrind parse results, missing TestEnd, stderr truncation, and final `Ok`/`Runtime` attributes.

State and persistence: in-memory summary tree and coverage map; optional FDB coverage writes; reads trace files from run dirs.

Dependencies and integration: config, XML/JSON parsers, Valgrind parser, FDB persistence, and `run.py`.

Risks and test signals: XML parser ignores fatal errors; `negative_test_success` iterates attrs incorrectly; trace filename timestamp parsing assumes fixed dot layout; stderr defaults to severity 40. Tests should cover JSON/XML traces, no traces, missing elapsed time, valgrind leaks ignored, severity remap, negative tests, and output format serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/summarize.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/test_valgrind_parser.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/test_valgrind_parser.py

Purpose: tiny manual CLI harness for inspecting parsed Valgrind XML output.

Important APIs and control flow: imports `parse_valgrind_output`, parses the file path in `sys.argv[1]`, and prints each `ValgrindError` kind, primary backtrace, and auxiliary backtraces.

State and persistence: read-only input file, stdout output.

Dependencies and integration: depends on `test_harness.valgrind`; not a pytest/unittest despite the name.

Risks and test signals: no argument validation and no assertions, so it is a debugging utility rather than automated coverage. Useful smoke test for SAX parser output on captured Valgrind XML.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/test_valgrind_parser.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/timeout.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/timeout.py

Purpose: converts leftover trace artifacts from timed-out Joshua jobs into killed-test summaries.

Important APIs/functions: `files_matching`, `dirs_with_files_matching`, and main CLI. It builds config args, optionally finds Valgrind XML, then recursively finds directories containing `trace.*.(json|xml)`.

Control flow: for each trace timestamp group in each directory, construct `Summary(Path("bin/fdbserver"), was_killed=True, long_running=config.long_running)`, attach Valgrind XML when requested, summarize files, and dump stdout.

State and persistence: no writes; reads current working directory recursively.

Dependencies and integration: config, `Summary`, `TraceFiles`, regex, pathlib. Called by Joshua timeout shell wrappers.

Risks and test signals: recursive scan may include stale artifacts; Valgrind mode pairs every Valgrind file with every trace group. Test with nested trace dirs, no traces, long-running flag, and Valgrind XML parse errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/timeout.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/valgrind.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/valgrind.py

Purpose: SAX parser for Valgrind XML reports used by TestHarness2 summaries.

Important APIs/types: `ValgrindWhat`, `ValgrindError`, enum `ValgrindParseState`, `ValgrindHandler`, and `parse_valgrind_output`.

Control flow: SAX events push parser states for `<error>`, `<kind>`, `<what>`, `<auxwhat>`, `<stack>`, and `<ip>`. Text accumulates error kind/description and builds `addr2line -e fdbserver.debug ...` command strings from instruction pointers. Completed errors are appended to `handler.result`.

State and persistence: in-memory parse stacks only; reads one XML file.

Dependencies and integration: Python XML SAX, pathlib. `Summary.done()` consumes parsed errors and ignores leak kinds while treating other kinds as severity-40 failures.

Risks and test signals: state assertions make malformed or unexpected Valgrind XML fatal; only instruction-pointer stack data is captured; leak filtering is external. Test primary and auxiliary stacks, multiple errors, leaks, malformed XML, and byte/string character chunks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/valgrind.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/version.py -->
## sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/version.py

Purpose: small comparable FoundationDB version object for old-binary selection and feature gating.

Important APIs/types: `Version` with `version_tuple`, `_compare`, ordered comparisons, `__hash__`, `__str__`, `of_binary`, `parse`, and `max_version`.

Control flow: parsing splits `major.minor.patch`, defaulting missing minor/patch to zero. `of_binary` expects names like `fdbserver-7.1.0`; unversioned current binary returns `max_version`.

State and persistence: none.

Dependencies and integration: used by `run.py` for trace format, TLS plugin, fault injection flag support, and old binary candidate ranges.

Risks and test signals: `fdbserver-7.1.0.exe` is not stripped here, so Windows-style names may fail outside `OldBinaries._add_file`; malformed versions raise `ValueError`. Unit tests should cover comparisons against strings and `Version`, partial versions, current binary, and hash equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/CMakeLists.txt -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/CMakeLists.txt

Purpose: CMake build glue for the C# TraceLogHelper library.

Important APIs and control flow: sets project source list, .csproj path, .NET references, and output DLL. If `CSHARP_USE_MONO` is true, adds a custom Mono compiler command and target; otherwise calls `dotnet_build` and exports `TraceLogHelperDll`.

State and persistence: produces `packages/bin/TraceLogHelper.dll` or the dotnet build executable path variable.

Dependencies and integration: requires CSharp compiler variables or repository `dotnet_build` function; source files include Event, JSON/XML parsers, assembly metadata, and utilities.

Risks and test signals: Mono branch references `${SRCS}` instead of the local source variable, which may rely on outer scope or be wrong. Build test both Mono and dotnet paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/Event.cs -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/Event.cs

Purpose: shared C# data model for FoundationDB trace analysis in the Magnesium namespace.

Important APIs/types: `Severity`, `Event`, nested dynamic `MyExpando`, `TestPlan`, `Test`, graph structs/classes (`AreaGraphPoint`, `LineGraphPoint`, `Interval`, `MachineRole`, `Location`), `LocationTimeOp`, and `LocationTime`.

Control flow: `Event.DDetails` wraps dictionaries in `MyExpando` so details are accessible dynamically and as a dictionary. `FormatTestError` formats well-known event types using dynamic details and appends common error fields.

State and persistence: pure data objects; `original` optionally holds the parsed XML element for callers that need source data.

Dependencies and integration: used by `JsonParser`, `XmlParser`, and `TraceLogUtil`.

Risks and test signals: dynamic detail access throws at runtime if expected keys are absent; `emptyDetails` is static shared immutable-by-convention but the underlying dictionary is mutable. Tests should cover formatting for known error types and detail dictionaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/Event.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/JsonParser.cs -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/JsonParser.cs

Purpose: parses line-delimited JSON FoundationDB traces into `Event` objects.

Important APIs/functions: static `JsonParser.Parse(Stream, file, keepOriginalElement, startTime, endTime, samplingFactor, nonFatalErrorMessage)` and private `ParseEvent`.

Control flow: reads one JSON line at a time, converts it to `XElement` via `JsonReaderWriterFactory`, optionally samples, handles `TrackLatestType=Rolled` by using `OriginalTime`, filters by time range, interns common strings, and stores remaining fields in `DDetails`.

State and persistence: read-only stream iteration; static `Random` controls sampling.

Dependencies and integration: System.Runtime.Serialization.Json, XML LINQ/XPath, and `Event`.

Risks and test signals: malformed JSON throws and aborts; the nonfatal callback parameter is unused; XPath lookups assume required fields exist. Test rolled events, sampling, time filtering, missing Severity/ID defaults, and malformed lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/JsonParser.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/Properties/AssemblyInfo.cs -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/Properties/AssemblyInfo.cs

Purpose: assembly metadata for TraceLogHelper.

Important APIs: assembly attributes set title/product to `TraceLogHelper`, company to Apple Inc., COM visibility false, a typelib GUID, and version/file version `1.0.0.0`.

Control flow and state: no executable logic; metadata is embedded at compile time.

Dependencies and integration: consumed by C# compiler in the TraceLogHelper build target.

Risks and test signals: stale copyright/version metadata can be misleading but does not affect parsing behavior. Build output metadata inspection is the only relevant signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/Properties/AssemblyInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/TraceLogUtil.cs -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/TraceLogUtil.cs

Purpose: helper algorithms over parsed trace events.

Important APIs/functions: `TraceLogUtil.IdentifyFailedTestPlans(IEnumerable<Event>)`.

Control flow: streams events, tracks `TestPlan` entries keyed by `TestUID + TraceFile`, removes them when a matching `Test` summary appears, handles `-2.txt` restart companion cleanup, yields normal events immediately, and at the end emits synthetic `Test` objects of type `FailedTestPlan` for plans that never summarized.

State and persistence: in-memory dictionary of pending plans; no external writes.

Dependencies and integration: relies on `Event`, `TestPlan`, and `Test` models. Useful for tooling that wants missing test summaries represented as events.

Risks and test signals: key concatenation can collide without separators; restart filename split is simplistic. Test with completed plans, missing plans, restart `-1/-2` pairs, and empty TestUID.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/TraceLogUtil.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/XmlParser.cs -->
## sources/storage-engines/foundationdb/contrib/TraceLogHelper/XmlParser.cs

Purpose: streaming parser for XML FoundationDB trace files and summarized TestHarness XML.

Important APIs/functions: `XmlParser.Parse`, private `ParseEvent`, `ParseTestPlan`, `ParseTest`, and `StreamElements`.

Control flow: advances to the `Trace` element, streams child elements, maps `<Event>` to `Event`, `<TestPlan>` to `TestPlan`, and `<Test>` to `Test`; supports sampling, time filtering, rolled event original time, defaulted attributes, original element retention, and nested summarized test events.

State and persistence: read-only stream parser with static `Random`.

Dependencies and integration: System.Xml, LINQ to XML, TraceLogHelper data types.

Risks and test signals: `reader.ReadToDescendant("Trace")` assumes trace wrapper; `bool.Parse` for `OK` is strict while other code often uses `Ok`; nonfatal streaming errors break the parse. Test event, TestPlan, Test, rolled event, time filter, malformed tail, and missing optional attributes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/TraceLogHelper/XmlParser.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/alloc_instrumentation.py -->
## sources/storage-engines/foundationdb/contrib/alloc_instrumentation.py

Purpose: post-processes stdout generated by `ALLOC_INSTRUMENTATION_STDOUT` in `FastAlloc.h` and reports live allocation stacks by bytes or count.

Important APIs/types: global `allocs`, `Allocation`, `print_stacks`, `process_line`, and `non_negative_int`.

Control flow: reads files/stdin with `fileinput`, tracks `Alloc` records by ID, removes on `Dealloc`, optionally echoes unparsed lines, periodically prints top stacks, then prints final stacks.

State and persistence: all live allocations are held in memory; no output files.

Dependencies and integration: Python argparse/fileinput and the exact tab-separated instrumentation format.

Risks and test signals: malformed instrumentation lines can raise index/value errors; long runs may retain large live maps. Test with alloc/dealloc pairs, duplicate IDs, quiet mode, periodic logging frequency, and count-vs-size sorting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/alloc_instrumentation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/alloc_instrumentation_traces.py -->
## sources/storage-engines/foundationdb/contrib/alloc_instrumentation_traces.py

Purpose: analyzes `MemSample` JSON trace events from allocation instrumentation and prints top memory users by total size and allocation count.

Important APIs/functions: module-level stdin loop and helper `byte_str`.

Control flow: reads JSON lines from stdin, filters `Type == "MemSample"` and non-`na` backtraces, resets aggregate lists when `Time` changes, stores tuples for count and size ordering, then prints top 10 by size and top 5 by count for the last timestamp seen.

State and persistence: in-memory lists for the current timestamp only; stdout report only.

Dependencies and integration: Python json/stdin and `MemSample` trace schema.

Risks and test signals: only the last timestamp is reported; malformed JSON or missing fields abort; `byte_str` can run past suffixes for extreme sizes. Test with multiple timestamps, `Bt=na`, size/count ordering, and empty input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/alloc_instrumentation_traces.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/apiversioner.py -->
## sources/storage-engines/foundationdb/contrib/apiversioner.py

Purpose: scans and optionally rewrites FoundationDB API version references across a source tree.

Important APIs/functions: constants `EXCLUDED_FILES`, `SUSPECT_PHRASES`; helpers `positive_response`, `rewrite_lines`, `address_file`, `address_path`, and `run`.

Control flow: CLI selects path, old version, optional new version, suspect-only mode, diffs, rewrite, confirmation, grayscale, and paths-only. Directory traversal skips generated/binary/third-party paths. In suspect mode it matches API-setting patterns; otherwise it finds standalone old-version numbers. Rewrites show contextual diffs and optionally prompt before changing lines.

State and persistence: read-only unless `--rewrite` is passed, in which case matched files are overwritten with joined rewritten lines.

Dependencies and integration: Python stdlib only. Intended for release/API maintenance.

Risks and test signals: broad non-suspect search can rewrite unrelated numbers; writing uses normal open without atomic replace; `matching_lines` filter truthiness is always true in Python 3, though iteration still controls logging. Test suspect regexes, excludes, diff-only, rewrite with/without confirmation, and UnicodeDecodeError handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/apiversioner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/benchmark_comparison.py -->
## sources/storage-engines/foundationdb/contrib/benchmark_comparison.py

Purpose: runs `flow_bench` benchmark filters and prints a formatted actor-vs-coroutine performance comparison report for delay, net2, and callback benchmark families.

Important APIs/functions: `geomean`, `get_benchmark_data`, and `main`.

Control flow: `get_benchmark_data` invokes `./bin/flow_bench --benchmark_filter=... --benchmark_format=json` with hard-coded cwd `/root/build_output`. `main` pairs actor and coroutine benchmarks by scale/template size, computes relative real-time and CPU changes, prints rows, and prints section geomeans.

State and persistence: no files; subprocess output parsed as JSON and report printed to stdout.

Dependencies and integration: requires a build tree containing `bin/flow_bench` and Google Benchmark JSON format.

Risks and test signals: hard-coded cwd limits portability; geomean uses absolute changes and loses improvement/degradation sign semantics for mixed sets; missing benchmarks are silently skipped. Test with mocked JSON, missing executable, zero old timings, and each benchmark family.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/benchmark_comparison.py -->
