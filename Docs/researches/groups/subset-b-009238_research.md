# subset-b-009238 research

Grouped research for IOR metadata benchmark, option parsing, utility, test, and libnfs integration files.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench.c -->
# sources/test-tools/ior/src/md-workbench.c

Purpose: implements the md-workbench metadata benchmark variant that drives filesystem-like dataset and object operations through the AIORI backend interface. It measures precreate, benchmark, and cleanup phases over MPI ranks and returns an `mdworkbench_results_t` API result.

Important APIs and functions: `md_workbench_run()` is the public entry point. `init_options()` seeds defaults in the file-global `struct benchmark_options o`. `run_precreate()` creates per-rank dataset directories and initial objects. `run_benchmark()` repeatedly stats, reads, optionally deletes, and creates objects in a FIFO rank-shifted pattern. `run_cleanup()` removes remaining objects and directories. `end_phase()` performs MPI reductions, gathers per-operation timers, computes quantiles, prints reports, and copies summary fields into `o.results`. Helper functions build path names, implement adaptive waiting, compute statistics, write latency CSVs, and persist restart position.

Control flow: `md_workbench_run()` initializes MPI timing, parses global and backend module options, selects and initializes an AIORI backend, initializes CUDA when requested, computes the current object index from restart state or `--start-item`, allocates the result array, then conditionally runs precreate, one or more benchmark iterations, adaptive waiting sub-iterations, and cleanup. Each phase allocates `phase_stat_t` timers, synchronizes ranks, runs operations, and calls `end_phase()`.

State and persistence: state is intentionally file-global in `o`, which makes the implementation simple but non-reentrant. Persistent outputs include the optional restart/status file `run_info_file`, optional latency CSV files, and created benchmark objects under `prefix`. Result memory is returned to the caller and must be freed by the caller. Phase timer arrays are freed in `end_phase()`.

Dependencies and integration: depends on MPI, AIORI backend methods (`mkdir`, `create`, `open`, `xfer`, `stat`, `remove`, `rmdir`, `xfer_hints`, `initialize`, `finalize`), `option.c`, `utilities.c`, and optional CUDA/GPU Direct support. It uses IOR memory-pattern utilities to generate and verify object payloads.

Risks: path construction uses fixed `MAX_PATHLEN` buffers and `sprintf`; long prefixes or rank/object counts can overflow. Several statistics helpers ignore their `count` argument and use `o.size`, making them tightly coupled to global state. `MPI_Reduce(&p->dset_create, ..., 2*(2+4), MPI_INT, ...)` relies on contiguous `op_stat_t` layout. `compute_histogram()` assumes `repeats > 0`. `return_position()` can broadcast an uninitialized `position` if non-root reaches the call after root exits on failure. Non-cleanup runs persist restart state and benchmark data.

Test signals: exercised indirectly through md-workbench CLI/API runs. Useful validation should cover POSIX/DUMMY backends, read-only benchmark mode, restart without precreate, latency output, stonewall modes, GPU buffer options, and error aggregation across ranks.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench.h -->
# sources/test-tools/ior/src/md-workbench.h

Purpose: public API and result contract for the md-workbench benchmark.

Important APIs and types: `time_statistics_t` stores per-operation latency quantiles and extrema. `mdworkbench_result_t` stores one phase result, including create/read/stat/delete latency stats, error count, throughput/rate, maximum operation time, runtime, and iterations completed. `mdworkbench_results_t` is a flexible-array container containing a count, total errors, and phase results. `md_workbench_run()` is the sole exported function and returns precreate, benchmark iteration, and cleanup results.

Control flow and integration: consumers call `md_workbench_run(argc, argv, MPI_Comm, FILE *)` after MPI is initialized. The implementation fills results in phase order as documented in the header comment: first precreate, then benchmark runs, then cleanup. It integrates with MPI, stdio logging, and the implementation in `md-workbench.c`.

State and persistence: the header does not own persistence, but its returned result pointer is heap allocated by the implementation. Callers must treat it as dynamically allocated memory and free it when done. The flexible array means callers should not stack-copy the structure without accounting for `count`.

Risks: the API does not expose an explicit destructor or allocation size. Callers must infer that `free()` is sufficient from the implementation. The comment says "iteration many benchmark runs", while adaptive waiting can return more benchmark result entries than the plain iteration count.

Test signals: compile-time users should include this header from C code, call the function under MPI, and verify `count`, phase ordering, and error aggregation against known small DUMMY/POSIX runs.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/md-workbench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/mdtest-main.c -->
# sources/test-tools/ior/src/mdtest-main.c

Purpose: minimal standalone executable entry point for mdtest.

Important APIs and functions: `main()` initializes MPI, calls `mdtest_run(argc, argv, MPI_COMM_WORLD, stdout)`, finalizes MPI, and returns zero.

Control flow: all option parsing, backend setup, benchmark phases, reporting, and result allocation are delegated to `mdtest_run()` in `mdtest.c`. The wrapper does not inspect the returned `mdtest_results_t *`.

State and persistence: no local persistent state. Runtime state and outputs are controlled by mdtest options and global state in `utilities.c`/`mdtest.c`. The returned result pointer is not freed here, so process exit is relied on for cleanup.

Dependencies and integration: includes `mdtest.h` and `aiori.h`; links against MPI and the IOR/AIORI library. It is the CLI bridge from the benchmark library API to a normal executable.

Risks: ignores a NULL result or benchmark error status and always returns success unless MPI itself aborts. It also leaks the returned result allocation for the lifetime of the process, which is harmless for a short-lived CLI but not a model for embedding.

Test signals: smoke test by running the mdtest binary with `-a DUMMY` and small item counts under `mpirun`; verify MPI init/finalize sequence and stdout reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/mdtest-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/mdtest.c -->
# sources/test-tools/ior/src/mdtest.c

Purpose: implements mdtest, the metadata benchmark for file and directory create, stat, read, rename, remove, tree create/remove, per-rank reporting, stonewalling, and backend-neutral operation dispatch.

Important APIs and types: public entry is `mdtest_run()`. The file-global `mdtest_options_t o` holds all runtime options, backend pointers, generated names, buffers, timers, and summary storage. `rank_progress_t` tracks per-rank item progress, stonewall deadlines, and optional per-operation timers. Core operations include `create_file()`, `remove_file()`, `create_remove_dirs()`, `create_remove_items()`, `mdtest_stat()`, `mdtest_read()`, `rename_dir_test()`, `directory_test()`, `file_test()`, `create_remove_directory_tree()`, `mdtest_iteration()`, and result summarizers.

Control flow: `mdtest_run()` initializes shared globals, parses mdtest plus backend module options, selects and initializes an AIORI backend, validates option combinations, computes directory tree and item counts, initializes random order and write buffers, prepares target paths, and optionally displays filesystem usage. It then sweeps task counts from `first` to `last` by `stride`, creates a subcommunicator for participating ranks, runs `mdtest_iteration()` for each iteration, summarizes results, optionally writes per-rank CSVs, reduces verification errors, and frees the communicator. Each iteration creates test directories/tree, runs directory and/or file phases depending on flags, and removes data when requested.

State and persistence: mutable benchmark state is global in `o` plus globals from `utilities.c` (`rank`, `verbose`, `testComm`, output files). Persistent side effects are benchmark directories/files, optional CSV files (`saveRankPerformanceDetails`, `savePerOpDataCSV`), optional stonewall status file, and optional backend-specific filesystem settings. `mdtest_run()` returns heap-allocated aggregated results and frees internal `o.summary_table`, random arrays, write buffers, and backend state.

Dependencies and integration: depends on MPI, AIORI backend methods, the option parser, memory-pattern utilities, filesystem statfs wrappers, optional GPFS create sharing, optional Lustre directory layout APIs, and optional CUDA buffers. The result shape is declared in `mdtest.h`.

Risks: heavy use of global mutable state makes the benchmark non-reentrant and sensitive to repeated calls in one process. Many paths use fixed arrays and `sprintf`/`strcat`. Some MPI gathers cast `mdtest_results_t` arrays to `double`, relying on struct layout and homogeneous fields despite integer fields. `parse_dirpath()` stores `strtok()` pointers into one duplicated string without retaining a separate owner pointer for later free. `create_remove_directory_tree()` mutates `o.size` in stonewall paths. Prologue and epilogue execute via `system()`. Several warning paths continue after failed file operations, so performance summaries may include partial work.

Test signals: existing `src/test/lib.c` and `lib.cpp` smoke-call `mdtest_run()` with the DUMMY backend. Meaningful coverage should also run small POSIX tests for files-only, dirs-only, shared file, unique dirs, random stat order, read/write verification, stonewall status reuse, per-op CSV output, and task-count sweep behavior under multiple ranks.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/mdtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/mdtest.h -->
# sources/test-tools/ior/src/mdtest.h

Purpose: public result interface for mdtest.

Important APIs and types: `mdtest_test_num_t` enumerates the result slots for directory create/stat/read/rename/remove, file create/stat/read/remove, tree create/remove, and sentinel `MDTEST_LAST_NUM`. `mdtest_results_t` stores per-test rates, rates before final barrier, times, times before barrier, item counts, total errors, and stonewall metrics. `mdtest_run()` is the exported benchmark API.

Control flow and integration: callers initialize MPI, pass command-line style arguments, communicator, and output stream to `mdtest_run()`, then inspect the returned array of `mdtest_results_t` entries. The array length is driven by the `-i` iterations option, not encoded in the type.

State and persistence: no direct state in the header. The returned pointer is heap allocated by `mdtest.c`; callers must free it. Result slots are indexed using the enum, so the enum order is an ABI-like contract with summarization code and CSV writers.

Risks: no destructor or result-count field is included. Callers need external knowledge of iteration count. Adding or reordering enum values requires coordinated updates in `mdtest_test_name()`, result summaries, CSV header generation, and consumers.

Test signals: compile against C and C++ consumers, verify enum slot names and result arrays for simple DUMMY backend runs, and check that `total_errors` propagates when verification fails.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/mdtest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/option.c -->
# sources/test-tools/ior/src/option.c

Purpose: table-driven command-line and directive parser shared by IOR, mdtest, md-workbench, and backend module options.

Important APIs and functions: `option_parse()` parses `argc/argv` against an `options_all_t` module list. `option_parse_str()` parses a single option token. `option_parse_key_value()` parses legacy `key=value` directives. `option_merge()` concatenates option arrays. `option_print_help()` and `option_print_current()` render help/current values. `string_to_bytes()` parses integer strings with k/m/g/t/p suffixes.

Control flow: `option_parse()` counts required options, iterates argv from index 1, and delegates each token to `option_parse_token()`. The token parser supports `--long`, `--long=value`, short options, compact repeated flags like `-vvv`, and short option values attached to the same token. It searches every registered module and writes directly into the target variable pointer using the option type code.

State and persistence: parser state is local, but parsed values mutate caller-owned variables. String arguments are duplicated with `strdup()` and become caller-owned. Help and error paths print to stdout and exit the process.

Dependencies and integration: exposed by `option.h`; used by parse_options, mdtest, md-workbench, and AIORI module option tables. Depends only on libc and the project option definitions.

Risks: parser mutates argv strings temporarily when handling `=`. `option_parse_key_value()` builds a 1024-byte stack string with `sprintf`. Optional arguments are effectively required once the option is present. Ambiguous module option names can set multiple variables because parsing continues through all modules after a match. Long-option detection relies on string length and `txt[0] == '-'` after stripping the first dash. The code exits on help/errors, which is awkward for library embedding.

Test signals: unit tests should cover suffix parsing, repeated flags, `--name=value`, missing values, hidden strings, module-prefixed long options, required option counting, and duplicate option names across modules.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/option.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/option.h -->
# sources/test-tools/ior/src/option.h

Purpose: defines the option table schema and parser API.

Important APIs and types: `option_value_type` distinguishes flags, optional arguments, and required arguments. `option_help` describes one option: short name, long name, help text, argument kind, data type code, and destination variable/function pointer. `option_module` groups options under an optional prefix and backend defaults. `options_all_t` stores all modules. `LAST_OPTION` terminates option arrays.

Control flow and integration: applications build arrays of `option_help`, combine them into `options_all_t` via AIORI helpers or local code, and call `option_parse()`, `option_parse_str()`, or `option_parse_key_value()`. `option_merge()` supports combining static option arrays.

State and persistence: no own state. The schema points directly to mutable caller variables, so option table lifetime and destination object lifetime must outlive parsing.

Risks: type codes are untyped characters (`d`, `l`, `u`, `s`, `H`, `f`, `F`, `c`, `p`), so mismatches between `type` and `variable` are compile-time invisible. `LAST_OPTION` depends on a zeroed sentinel. The name `OPTION_OPTIONAL_ARGUMENT` is misleading because the parser still fails if the option is present without an argument.

Test signals: compile checks for sentinel usage, parser tests for each type code, and C/C++ compatibility when included from test programs.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/option.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/parse_options.c -->
# sources/test-tools/ior/src/parse_options.c

Purpose: IOR-specific command-line and script parser that maps legacy IOR directives onto `IOR_param_t` plus AIORI module options.

Important APIs and functions: `ParseCommandLine()` initializes default parameters, parses CLI options, optionally reads a script, creates `IOR_test_t` nodes, allocates results, and validates run settings. `ReadConfigScript()` parses blocks between `IOR START` and `IOR STOP`, creating tests on `run` lines. `DecodeDirective()` maps one `option=value` directive to fields or backend module options. `ParseLine()` handles comma-separated directives. `createGlobalOptions()` builds the IOR global option table.

Control flow: command-line parsing starts with `init_IOR_Param_t()`, `GetPlatformName()`, global option creation, AIORI module option aggregation, `option_parse()`, and `updateParsedOptions()`. Script parsing clones previous test parameters on `run`, updates the current option table to point at the active test params, and snapshots backend options into each test. `CheckRunSettings()` defaults to write+read when no action is selected and validates dual mount constraints.

State and persistence: file-static `initialTestParams`, `parameters`, and `global_options` bridge the `-O` parser callback to current parameters. Side effects include opening `summaryFile`, truncating rank-detail CSV headers, allocating strings and option arrays, and constructing a linked list of tests.

Dependencies and integration: depends on `ior.h`, `aiori.h`, `option.c`, `utilities.c`, and IOR test construction helpers such as `CreateTest()` and `AllocResults()`. It is the main parser for the IOR benchmark rather than mdtest.

Risks: many string fields are duplicated without centralized cleanup. `ParseLine()` treats short substrings as fatal, which can reject blank comma fragments. `ReadConfigScript()` has fragile pointer use around `tail->next` when creating option tables. `DecodeDirective()` is a long manual mapping, so new `IOR_param_t` fields can be missed. Unknown directives fall back to module parsing, but error handling aborts MPI. Fixed-size buffers and `sscanf` can truncate or reject values with spaces.

Test signals: coverage should include CLI-only runs, script files with multiple `run` sections, `-O` comma directives, backend-specific options, summary formats, memory-per-node percentage parsing, dualMount validation, and unknown option failures.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/parse_options.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/parse_options.h -->
# sources/test-tools/ior/src/parse_options.h

Purpose: public declaration for IOR command-line parsing.

Important APIs: `ParseCommandLine(int argc, char **argv, MPI_Comm com)` returns an `IOR_test_t *` linked list of configured tests.

Control flow and integration: callers pass process command-line arguments and an MPI communicator. The implementation initializes default IOR parameters, parses command-line and optional script inputs, resolves AIORI backend options, allocates per-test result storage, and returns the test list.

State and persistence: no state in the header. The returned linked list and nested allocations are owned by the caller or later IOR cleanup paths.

Risks: only the top-level parser is declared, so tests that need `DecodeDirective()` or `ReadConfigScript()` must include private declarations or test through `ParseCommandLine()`. The API returns a raw pointer with no ownership documentation in the header.

Test signals: compile inclusion from IOR main code, parser smoke tests with DUMMY backend, and script parsing tests through the public function.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/parse_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/test/Makefile.am -->
# sources/test-tools/ior/src/test/Makefile.am

Purpose: Automake test build definition for small IOR library smoke tests.

Important content: sets `AM_LDFLAGS`, links test programs against `../libaiori.a` plus extra linker additions, declares `TESTS = testlib testexample`, and maps `testexample` to `example.c` and `testlib` to `lib.c`.

Control flow and integration: Automake uses `check_PROGRAMS` to build the tests during `make check` or `make distcheck`, then runs the names in `TESTS`. The tests exercise library/API linkage rather than full benchmark correctness.

State and persistence: no runtime state. Build outputs are generated by the Automake build tree.

Dependencies: relies on the static AIORI library and any `extraLDFLAGS`/`extraLDADD` configured by the project.

Risks: `lib.cpp` is not listed as a test source, so C++ linkage coverage may not run through Automake. MPI launcher requirements are not represented here, so tests run as local programs unless the harness adds MPI behavior.

Test signals: `make check` should build and run `testexample` and `testlib`; `make distcheck` validates distribution inclusion.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/test/example.c -->
# sources/test-tools/ior/src/test/example.c

Purpose: minimal C smoke test for initializing an `IOR_param_t` and linking against IOR internals.

Important APIs: calls `MPI_Init()`, `init_IOR_Param_t(&test, MPI_COMM_WORLD)`, mutates a few fields (`blockSize`, `transferSize`, `segmentCount`, `numTasks`, `filePerProc`), prints `OK`, and finalizes MPI.

Control flow: no benchmark is run. The test only verifies that headers, MPI setup, and parameter initialization can compile and execute.

State and persistence: creates a stack `IOR_param_t`; no files or persistent benchmark data are created.

Dependencies and integration: includes `ior.h` and `ior-internal.h`, so it reaches into internal initialization APIs. It is built by `src/test/Makefile.am` as `testexample`.

Risks: assertions are included but unused. The test does not validate any initialized defaults or run AIORI operations, so it can pass despite behavioral regressions in the benchmark path.

Test signals: useful as a build/link smoke test. Stronger tests would assert initialized fields and run a tiny DUMMY backend operation.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/test/example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/test/lib.c -->
# sources/test-tools/ior/src/test/lib.c

Purpose: C API smoke test for calling `ior_run()` and `mdtest_run()` through the static library.

Important APIs: initializes MPI, gets rank, and on rank 0 calls `ior_run(3, {"./ior","-a","DUMMY"}, MPI_COMM_SELF, stdout)` and `mdtest_run(3, {"./mdtest","-a","DUMMY"}, MPI_COMM_SELF, stdout)`. It checks for NULL results and frees the IOR result's `platform` string and struct.

Control flow: only rank 0 runs the library calls; all ranks finalize MPI and return `ret`.

State and persistence: DUMMY backend should avoid real filesystem effects. The mdtest result is not freed, so the test leaks it until process exit.

Dependencies and integration: includes public IOR and mdtest headers, links against `libaiori.a`, and is listed in Automake tests as `testlib`.

Risks: only checks non-NULL return values. Does not validate rates, error counts, or cleanup. Running library calls on `MPI_COMM_SELF` avoids multi-rank behavior. The IOR result free is manual and partial, which may drift from real ownership expectations.

Test signals: confirms that the public C API can be linked and called with DUMMY backend under MPI initialization.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/test/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/test/lib.cpp -->
# sources/test-tools/ior/src/test/lib.cpp

Purpose: C++ linkage smoke test for the C IOR and mdtest APIs.

Important APIs: wraps `ior.h` and `mdtest.h` in `extern "C"`, initializes MPI, and on rank 0 calls `ior_run()` and `mdtest_run()` with DUMMY backend parameters.

Control flow: mirrors `lib.c`, including rank-0-only API calls and MPI finalize.

State and persistence: no intended filesystem state because the DUMMY backend is used. The mdtest result allocation is not freed.

Dependencies and integration: requires a C++ compiler, MPI C++ compile path, and C ABI-compatible headers. The source is present but not listed in `Makefile.am`, so it may be a manual smoke test rather than an automated one.

Risks: C headers must remain valid under `extern "C"`. Because the file is not part of the declared Automake tests, C++ compatibility can regress unnoticed.

Test signals: manually compile with an MPI C++ compiler and link against the AIORI library; ideally add it to automated check targets if C++ API compatibility matters.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/test/lib.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/utilities.c -->
# sources/test-tools/ior/src/utilities.c

Purpose: shared runtime utility library for IOR/mdtest/md-workbench, covering global state, memory patterns, verification, timers, MPI topology, filesystem reporting, hints, timestamps, size parsing, delays, and aligned/GPU buffers.

Important APIs and functions: exports globals declared in `utilities.h` (`rank`, `verbose`, `testComm`, output files, output format). Memory functions include `generate_memory_pattern()`, `update_write_memory_pattern()`, `invalidate_buffer_pattern()`, and `verify_memory_pattern()`. Timing functions include `GetTimeStamp()`, `PrintTimestamp()`, and `OpTimer*`. Topology functions include `QueryNodeMapping()`, `GetNumNodes()`, `GetNumTasks()`, and `GetNumTasksOnNode0()`. Configuration helpers include `parsePacketType()`, `updateParsedOptions()`, `SetHints()`, and `ShowHints()`. Buffer functions include `aligned_buffer_alloc()` and `aligned_buffer_free()`.

Control flow: callers initialize globals and output streams, then use these helpers during option parsing and benchmark phases. Memory-pattern generation creates deterministic rank/item signatures, while update/verify functions adjust or check per-item data. MPI helpers split or gather communicator information for placement-aware rank shifting. `OpTimer` buffers one million operation samples before flushing CSV rows.

State and persistence: owns process-wide globals and static buffers for time/human-readable strings. `OpTimer` writes CSV files. Stonewall helpers read/write a count file on rank 0 and broadcast values. Filesystem reporting writes to `out_resultfile`. Aligned allocation stores the original malloc pointer immediately before the aligned address; GPU allocations use CUDA APIs when enabled.

Dependencies and integration: used by IOR, mdtest, md-workbench, AIORI backends, and parser code. Depends on MPI, optional CUDA/GPU Direct, POSIX APIs, regex, statfs/statvfs, and project headers.

Risks: globals make behavior non-reentrant. `OpTimerInit()` compares `FILE *` with `< 0` instead of NULL. Pattern code may ignore trailing bytes smaller than 8 except for final byte checks. `StringToBytes()` supports fewer suffixes than `option.c`'s `string_to_bytes()`. `ExtractHint()` mutates input with `strtok()` and assumes valid value tokens. `ShowFileSystemSize()` divides by totals without guarding zero. `aligned_buffer_free()` treats any nonzero `ior_memory_flags` as CUDA allocation. Several functions rely on `out_logfile` being non-NULL.

Test signals: unit tests should verify size parsing, data pattern generation/verification for each packet type, aligned allocation/free under CPU and GPU builds, MPI topology helpers with fake environment variables, stonewall file broadcast, and `OpTimer` CSV output.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/src/utilities.h -->
# sources/test-tools/ior/src/utilities.h

Purpose: shared utility declarations and global runtime variables for IOR benchmark components.

Important APIs and types: declares process globals (`rank`, `rankOffset`, `verbose`, `testComm`, `out_resultfile`, `outputFormat`), `MAX_PATHLEN`, `ERROR_LOCATION`, memory pattern APIs, CUDA initialization, filesystem reporting, regex, hint handling, human-readable formatting, MPI topology helpers, stonewall status helpers, timing helpers, `OpTimer`, random helpers, and aligned buffer allocation.

Control flow and integration: included by mdtest, md-workbench, parse_options, AIORI backends, and tests. Callers use the functions after MPI and output globals have been initialized by the benchmark entry point.

State and persistence: header exposes global mutable state, so any including module can read or alter benchmark-wide behavior. Several functions persist data through files, but paths are supplied by callers.

Risks: broad header coupling makes independent testing harder. `set_o_direct_flag(int *fd)` is declared as if it mutates a file descriptor, while implementation mutates an open flag bitmask. `PrintTimestamp()` is marked TODO for removal. Ownership and thread-safety for returned static strings are not documented.

Test signals: compile all users with this header, validate CPU and CUDA conditional declarations, and run API-level tests for exported helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/src/utilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ior/testing/libnfs/src/aiori-LIBNFS-test.c -->
# sources/test-tools/ior/testing/libnfs/src/aiori-LIBNFS-test.c

Purpose: CMocka integration tests for the LIBNFS AIORI backend, using a real NFS URL mapped to a local folder so backend operations can be verified via local filesystem checks.

Important APIs and functions: `main()` validates arguments, checks NFS availability, builds CMocka tests, and runs them. Helpers include `check_server_state()`, `clear_folder()`, `create_local_file()`, `read_local_file()`, `verify_local_file()`, and `local_directory_exists()`. Test setup/teardown call `libnfs_aiori.initialize()`/`finalize()` and clear the local folder. Test cases cover create, write, read at offsets, read/write combination, append, truncate, remove, mkdir/rmdir, and file size.

Control flow: the test binary expects two arguments: local folder path and NFS URL. It clears the folder, retries server availability up to five times, waiting through NFS grace mode, then runs each test with the shared `test_infrastructure_data` as prestate. Each test invokes the backend and asserts local side effects.

State and persistence: each test mutates the local folder and the NFS export. Setup and teardown clear the folder using `rm -rf folder/*`. Backend options store the NFS URL. No persistent state should remain after teardown if cleanup succeeds.

Dependencies and integration: depends on CMocka, libnfs (`nfsc/libnfs.h`), the LIBNFS AIORI backend, local POSIX file/stat helpers, and an external NFS server configuration matching the local folder.

Risks: `clear_folder()` builds a shell command from an argument without quoting, which is unsafe for spaces or metacharacters. `check_server_state()` does not check URL parse failure before using fields. Some helper path length checks omit separator/NUL details. Tests assume local folder view is coherent with NFS server writes immediately. The retry loop can run longer than expected in repeated grace mode. Duplicate `stdio.h` include is harmless.

Test signals: this file itself is an integration test. Passing signals include all CMocka cases succeeding against a live NFS server. Failure modes identify backend semantics for flags, offset handling, append/truncate behavior, directory operations, and stat size.
<!-- END_FILE_RESEARCH: sources/test-tools/ior/testing/libnfs/src/aiori-LIBNFS-test.c -->
