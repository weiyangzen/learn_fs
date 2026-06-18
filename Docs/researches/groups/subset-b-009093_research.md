# subset-b-009093 research

This grouped report covers the WiredTiger test utility, Windows compatibility, hang-analysis, wtperf, Antithesis, backup-analysis, callgraph, checksum, and GDB helper files assigned to `subset-b-009093`. Each section is bounded by source-path markers for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/misc.c -->
# sources/storage-engines/wiredtiger/test/utility/misc.c

## Purpose
`misc.c` is the central implementation file for generic WiredTiger test helpers declared in `test_util.h`. It supplies fatal error handling, program-name and directory helpers, test cleanup, progress logging, backup artifact copying/removal, build-directory discovery, environment flag checks, process wait helpers, timing/hash utilities, checked allocation wrappers, formatted `WT_ITEM` construction, and the shared `testutil_wiredtiger_open` wrapper that adds tiered/disaggregated test configuration.

## Important APIs and functions
Key exported functions include `testutil_die`, `testutil_set_progname`, `testutil_deduce_build_dir`, `testutil_build_dir`, `testutil_progress`, `testutil_cleanup`, `testutil_copy_data`, `testutil_copy_data_opt`, `testutil_clean_test_artifacts`, `testutil_verify_model`, `testutil_is_flag_set`, `testutil_wiredtiger_open`, `testutil_timeout_wait`, `testutil_sleep_wait`, `testutil_time_us`, `testutil_pareto`, `testutil_fnv1a_*`, `dcalloc`, `dmalloc`, `drealloc`, `dstrdup`, `dstrndup`, `testutil_format_item`, `example_setup`, `is_mounted`, and `testutil_system_internal`. The global `progname` and callback `custom_die` form the process-wide fatal-error context.

## Control flow and behavior
Most helpers are fail-fast: they call `testutil_die` on unexpected errors. `testutil_wiredtiger_open` composes user config, recovery/compatibility config, disaggregated config, tiered config, and extension config into one `wiredtiger_open` string. The non-Windows process wait helpers poll `waitpid`, validate child status, and kill timed-out children. Allocation wrappers normalize zero-size allocation to one byte so `NULL` is always treated as failure.

## State, dependencies, and integration
The file mutates `TEST_OPTS` fields such as `build_dir`, `progress_fp`, `local_retention`, and connection handles. It depends on WiredTiger internals (`__wt_*` formatting, timing, allocation, environment, abort, filesystem helpers), POSIX process APIs outside Windows, and platform directory APIs for mount detection. Integration points are broad: csuite tests, example setup, model verification, tiered/disaggregated extension loading, progress files, and backup artifact lifecycle.

## Risks and test signals
The main risks are fixed-size buffers for paths/config strings, global fatal-error state, shell command execution via `system`, and build-directory inference that depends on finding a `wt` binary above `argv0`. Test signals are tests aborting with `progname: FAILED`, progress-file creation under `opts->home`, successful tiered/disaggregated extension opens, timeout failures for child processes, and cleanup removing `.SAVE`, `.CHECK`, `.DEBUG`, and `.BACKUP` directories unless `preserve` is set.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/parse_opts.c -->
# sources/storage-engines/wiredtiger/test/utility/parse_opts.c

## Purpose
`parse_opts.c` initializes and parses the shared `TEST_OPTS` command-line structure used by WiredTiger C tests. It handles common options for home directories, thread counts, record/operation counts, table type, preservation, verbose mode, build directories, compatibility mode, in-memory mode, tiered storage, disaggregated storage, and deterministic random seeds.

## Important APIs and functions
The exported API is `testutil_parse_begin_opt`, `testutil_parse_single_opt`, `testutil_parse_end_opt`, and the convenience wrapper `testutil_parse_opts`. Internal helpers include `parse_number`, `parse_tiered_comma_separated_options`, `parse_tiered_artificial_errors`, `parse_tiered_artificial_delays`, `parse_tiered_random_seeds`, `parse_and_set_disagg_opt`, and `parse_tiered_opt`. The `EXPECT_OPTIONAL_ARG_IN_SUB_PARSE` macro adjusts WiredTiger getopt state for suboptions such as `-Pd` and `-Po`.

## Control flow and behavior
`testutil_parse_begin_opt` resets major `TEST_OPTS` fields, saves `argv`, sets `progname`, prints the command line, and builds a usage suffix from the caller's getopt string. `testutil_parse_single_opt` maps each option to a `TEST_OPTS` field. `-P` dispatches to tiered suboption parsing: `T` enables tiered storage, `S` parses `D`/`E` seeds, `d` and `e` parse artificial delay/error frequency plus milliseconds, and `o` validates `dir_store`. `testutil_parse_end_opt` supplies default home/progress/URI strings, fills default tiered source, deduces the build directory when extension loading is needed, and initializes two random states.

## State, dependencies, and integration
State lives entirely in `TEST_OPTS`; allocated strings are later released by `testutil_cleanup`. The parser depends on the WiredTiger getopt globals `__wt_optarg`, `__wt_optind`, `__wt_optopt`, and `__wt_optreset`, plus allocation and fatal helpers from `misc.c`. It integrates with `tiered.c`, `util_random.c`, disaggregated-storage config macros, and test binaries that either parse one option at a time or use the wrapper parser.

## Risks and test signals
Parsing uses `strtoll`/`atoll` with limited numeric validation, so malformed or overflowed input may not be rejected consistently. Tiered comma parsing rejects duplicated first values and too many comma values but has a typo in one `-PS` error message. Tests should cover default home/URI construction, seed reproducibility, tiered defaults after `-PT`, explicit build directories, usage output on unknown options, and correct extension build-directory deduction when tiered or disaggregated storage is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/parse_opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/test_util.h -->
# sources/storage-engines/wiredtiger/test/utility/test_util.h

## Purpose
`test_util.h` is the shared C test utility contract for WiredTiger tests. It centralizes constants, platform path definitions, configuration string macros, option/state structures, assertion/checking macros, inline timestamp/string helpers, and prototypes for filesystem, backup, LazyFS, operation-thread, tiered/disaggregated, random, modify, and process utilities.

## Important APIs and types
The key type is `TEST_OPTS`, which carries parsed command-line options, paths, random states, tiered/disaggregated settings, connection/session handles, shared thread flags, and resource pointers cleaned by `testutil_cleanup`. `TEST_PER_THREAD_OPTS` wraps per-worker operation counters. `WT_LAZY_FS`, `WT_FILE_COPY_OPTS`, and `WT_MKDIR_OPTS` describe LazyFS state and utility file operations. Macros include `testutil_assert`, `testutil_assert_errno`, `testutil_check`, `testutil_snprintf`, `testutil_drop`, `testutil_verify`, `WT_OP_CHECKPOINT_WAIT`, `testutil_system`, and the configuration templates used by `misc.c` and `tiered.c`.

## Control flow and behavior
The header enforces a fail-fast test style: checking macros call `testutil_die` with function and line context. Inline helpers `u64_to_string`, `u64_to_string_zf`, `testutil_timestamp_parse`, and `maximum_stable_ts` provide small utility logic without a separate compilation unit. `TESTUTIL_DISAGG_INIT` is intentionally exhaustive and documents that new disaggregated fields must be added to the initializer.

## State, dependencies, and integration
The header includes `wt_internal.h` and conditionally includes `windows_shim.h`, exposing test helpers to C and C++ via `extern "C"`. It binds many implementation files together: `misc.c`, `parse_opts.c`, `thread.c`, `tiered.c`, `util_modify.c`, `util_random.c`, backup helpers, LazyFS helpers, filesystem helpers, and Windows shims. `custom_die` and `progname` are declared as process-global integration points.

## Risks and test signals
Because this header exposes many macros and a large mutable `TEST_OPTS`, changes have high blast radius. Risks include macro double-evaluation if future macros are not careful, incomplete initialization when adding fields, config-buffer size assumptions, and platform divergence under `_WIN32`. Test signals are compile failures across C/C++ test targets, assertion output quality, successful Windows builds, tiered/disaggregated config strings, and command-line option behavior in tests using the shared parser.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/thread.c -->
# sources/storage-engines/wiredtiger/test/utility/thread.c

## Purpose
`thread.c` implements reusable thread bodies and event handlers for WiredTiger stress tests. It provides one append worker for variable-length column stores and several simple API-operation workers originally built for `test/fops`, exercising creates, drops, cursors, and bulk cursor races against checkpoints.

## Important APIs and functions
Exported functions are `thread_append`, `handle_op_error`, `handle_op_message`, `op_bulk`, `op_bulk_unique`, `op_cursor`, `op_create`, `op_create_unique`, and `op_drop`. All operation workers accept `TEST_PER_THREAD_OPTS *` except `thread_append`, which accepts `TEST_OPTS *`.

## Control flow and behavior
`thread_append` opens a session and append cursor, inserts formatted values until `opts->running` becomes false, and lets thread id zero update `opts->max_inserted_id` and terminate after `nrecords`. The operation workers open a session, perform one API sequence, tolerate expected racing errors such as `EEXIST`, `ENOENT`, `EBUSY`, and selected `EINVAL`, close resources, and increment `thread_counter`. The unique variants create object names using atomic `unique_id`, then drop them with randomly chosen forced or checkpoint-wait-disabled config.

## State, dependencies, and integration
Shared mutable state includes `opts->running`, `opts->next_threadid`, `opts->max_inserted_id`, `opts->unique_id`, and per-thread `thread_counter`. The code depends on WiredTiger connection/session/cursor APIs, atomic helpers, random helpers, yielding, and `DEFAULT_TABLE_SCHEMA`. The event handlers integrate with tests that intentionally provoke expected failures and need to suppress noisy error/message output.

## Risks and test signals
Risks are intentional races, non-atomic reads/writes of some shared flags, ignored return values in optional data insertion, and reliance on exact error-code behavior from checkpoint/cursor/drop races. Useful signals are stress tests such as checkpoint operation races completing without unexpected `testutil_die`, operation counters increasing during expected `EBUSY` loops, no leaked sessions/cursors, and append workers stopping at the configured record threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/tiered.c -->
# sources/storage-engines/wiredtiger/test/utility/tiered.c

## Purpose
`tiered.c` contains the runtime support needed by tests that optionally use WiredTiger tiered storage. It initializes tiered flush scheduling, sleeps until the next scheduled flush, updates scheduling after flush completion, and builds the tiered storage and extension configuration strings consumed by `testutil_wiredtiger_open`.

## Important APIs and functions
The exported functions are `testutil_tiered_begin`, `testutil_tiered_end`, `testutil_tiered_sleep`, `testutil_tiered_flush_complete`, and `testutil_tiered_storage_configuration`. The implementation reads and mutates `TEST_OPTS` fields such as `tiered_storage`, `tiered_begun`, `tiered_flush_interval_us`, `tiered_flush_next_us`, `absolute_bucket_dir`, `make_bucket_dir`, `build_dir`, artificial delay/error settings, `local_retention`, `home`, and `tiered_storage_source`.

## Control flow and behavior
`testutil_tiered_begin` asserts a connection exists, optionally opens a temporary session to schedule the first flush, and marks tiered state begun. `testutil_tiered_sleep` calculates an absolute wake time, shortens it to the next tiered flush if appropriate, sleeps in at-most-one-second chunks while `opts->running`, and tells the caller when to run `flush_tier`. `testutil_tiered_flush_complete` schedules the next flush. `testutil_tiered_storage_configuration` only supports `dir_store`, builds the extension string, computes bucket paths, optionally creates the bucket directory, and emits empty config when tiered storage is disabled.

## State, dependencies, and integration
This file depends on `test_util.h`, WiredTiger time/sleep helpers through `testutil_time_us`, the `DIR_STORE` macros, and the extension config macros. It integrates with command-line parsing from `parse_opts.c`, connection opening in `misc.c`, and test loops that periodically call `flush_tier`.

## Risks and test signals
Risks include path-buffer limits, `mkdir` failure if the bucket exists unexpectedly, `do_flush_tier` being dereferenced even though the function only conditionally checks it earlier, and strict support for `dir_store` only. Signals include tiered tests opening the storage source extension, bucket directory creation, periodic flush scheduling, and no repeated flush attempts while a previous flush is still considered incomplete.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/tiered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/util_modify.c -->
# sources/storage-engines/wiredtiger/test/utility/util_modify.c

## Purpose
`util_modify.c` provides `testutil_modify_apply`, a deliberately simple independent implementation of WiredTiger modify operations. It is used by tests as an oracle against the production modify algorithm.

## Important APIs and functions
The sole exported function is `testutil_modify_apply(WT_ITEM *value, WT_ITEM *workspace, WT_MODIFY *entries, int nentries, uint8_t pad_byte)`. It consumes a starting value buffer, a workspace buffer, an ordered list of modify entries, and a byte used to fill gaps when a modify offset extends beyond the current size.

## Control flow and behavior
The function first estimates a pessimistic maximum output size from current value size, modify offsets, and replacement sizes, then grows both buffers with `__wt_buf_grow`. It poisons unused capacity with `0xff` for debugging clarity. For each modify entry it copies leading bytes or pad bytes, appends replacement bytes, copies trailing bytes after the replaced span, asserts the new size is bounded, and swaps source/workspace buffers. If the final result resides in the workspace, it swaps the `WT_ITEM` structs back so the caller receives the result in `value`.

## State, dependencies, and integration
The function mutates both `WT_ITEM` buffers, including `mem`, `memsize`, `size`, and `data`. It depends on WiredTiger buffer growth and the shared test assertion/check macros. It is integrated into tests that compare modify behavior and need a straightforward reference implementation independent of internal optimized paths.

## Risks and test signals
The implementation assumes entries are applied in the caller-provided order and that the pessimistic size calculation covers all later swaps. It may be inefficient for large modify lists, which is acceptable for test use. Test signals include exact byte-for-byte equality with WiredTiger modify results, coverage of offsets beyond EOF with padding, zero-length replacements, replacement deletion spans, multi-entry modifies, and buffer ownership remaining valid after final swaps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/util_modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/util_random.c -->
# sources/storage-engines/wiredtiger/test/utility/util_random.c

## Purpose
`util_random.c` wraps WiredTiger's random number state for tests, giving callers simple random generation, deterministic seeding from a numeric seed, seeding one generator from another, and default seed creation with returned seed values for reproduction.

## Important APIs and functions
The exported functions are `testutil_random`, `testutil_random_from_random`, `testutil_random_from_seed`, and `testutil_random_init`. They operate on `WT_RAND_STATE` and seed pointers stored in `TEST_OPTS` by the option parser.

## Control flow and behavior
`testutil_random` uses the caller-provided state when available; otherwise it initializes a local state from WiredTiger's random initializer and returns one number. `testutil_random_from_random` advances a source generator and seeds the destination from that value. `testutil_random_from_seed` splits a 64-bit seed into lower and upper 32-bit halves and sets both internal generator components to nonzero values, borrowing from the other half when one half is zero. `testutil_random_init` generates a compact 24-bit seed when `*seedp` is zero, shifted by `n % 4` so multiple initializations close in time still diverge.

## State, dependencies, and integration
The functions mutate caller-owned `WT_RAND_STATE` and `uint64_t` seed storage. They depend on `__wt_random_init` and `__wt_random`, and are called by `parse_opts.c` to initialize data and extra random streams. Tests can print or pass `-PS` seeds to reproduce behavior.

## Risks and test signals
Risks include limited entropy for auto-generated seeds by design, repeated values if callers misuse the `n` index, and non-cryptographic random behavior. Signals include deterministic sequences from explicit seeds, distinct data/extra streams from default initialization, correct handling of seeds below `2^32`, and reproducible failure command lines including `TESTUTIL_SEED_FORMAT`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/utility/util_random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/windows/CMakeLists.txt

## Purpose
This CMake file builds the Windows test compatibility shim as a static library named `windows_shim`. The target packages POSIX-like APIs needed by WiredTiger tests and examples on Windows.

## Important APIs and targets
The only source is `windows_shim.c`. The target exports `${CMAKE_SOURCE_DIR}/test/windows` as a public include directory so consumers can include `windows_shim.h`, and privately includes generated build/config headers plus `src/include`. It applies `${COMPILER_DIAGNOSTIC_C_FLAGS}` to keep diagnostics consistent with the rest of the project.

## Control flow and behavior
CMake declares a `sources` list, creates `add_library(windows_shim STATIC ${sources})`, then attaches include directories and compile options. There is no conditional logic here; higher-level CMake decides when this directory participates in the build.

## State, dependencies, and integration
The static library is consumed by Windows test/example targets through `test_util.h`, which includes `windows_shim.h` under `_WIN32`. It depends on build-generated WiredTiger headers and source include paths because the shim calls some internal helpers such as error mapping and formatting.

## Risks and test signals
Risks are mainly build-graph related: missing public include exposure would break Windows test compilation, while missing private include directories would break references to `wt_internal.h`. Signals are successful Windows CMake configuration, `windows_shim` static-library compilation, and downstream test targets resolving POSIX compatibility symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/windows_shim.c -->
# sources/storage-engines/wiredtiger/test/windows/windows_shim.c

## Purpose
`windows_shim.c` implements POSIX-style functions and pthread read-write lock behavior needed by WiredTiger tests on Windows. It bridges time, sleep, globbing, read-write locks, and Windows error formatting for code that otherwise assumes Unix APIs.

## Important APIs and functions
Implemented functions are `sleep`, `usleep`, `gettimeofday`, `glob`, `globfree`, `pthread_rwlock_destroy`, `pthread_rwlock_init`, `pthread_rwlock_unlock`, `pthread_rwlock_tryrdlock`, `pthread_rwlock_rdlock`, `pthread_rwlock_trywrlock`, `pthread_rwlock_wrlock`, and `last_windows_error_message`. `glob` fills the shim `glob_t` from `FindFirstFileA`/`FindNextFileA`, and the rwlock functions wrap Windows `SRWLOCK`.

## Control flow and behavior
Sleep helpers convert seconds or microseconds to Windows milliseconds, rounding microsecond sleeps up to at least one millisecond. `gettimeofday` converts Windows `FILETIME` from the 1601 epoch to Unix seconds/microseconds. `glob` rejects unsupported flags, special-cases `"."`, dynamically grows the path vector, and calls an optional error function for find-next failures. `globfree` releases every allocated path. RW lock unlock chooses exclusive versus shared release based on `exclusive_locked`.

## State, dependencies, and integration
The code depends on `windows_shim.h`, Windows APIs, WiredTiger error/formatting helpers, and thread-local storage for the last error message buffer. It integrates with Windows builds of test utilities, examples, and any test code using POSIX-like functions through the shim header.

## Risks and test signals
Risks include incomplete `glob` flag support, returned glob path names being file names rather than full matched paths, coarse `usleep` precision, and `exclusive_locked` not tracking recursive/ownership semantics beyond the thread id marker. Signals are successful Windows test runs using glob/sleep/time/rwlock APIs, leak-free `globfree`, readable `last_windows_error_message`, and no deadlocks around SRWLOCK-backed readers/writers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/windows_shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/windows_shim.h -->
# sources/storage-engines/wiredtiger/test/windows/windows_shim.h

## Purpose
`windows_shim.h` declares the Windows compatibility surface for WiredTiger tests. It supplies missing constants, aliases, POSIX-like structs, type definitions, function prototypes, and macro mappings so Unix-oriented test code can compile under MSVC.

## Important APIs and types
The header defines `R_OK`, `X_OK`, `strcasecmp`, `PATH_MAX`, `mkdir`, `S_ISDIR`, `struct timeval`, `pid_t`, `glob_t`, `useconds_t`, pthread-like mutex/condition/rwlock/thread typedefs, and wrappers for `lseek`, `read`, and `write`. It declares `gettimeofday`, `glob`, `globfree`, `sleep`, `usleep`, pthread creation/join/rwlock functions, and `last_windows_error_message`.

## Control flow and behavior
There is no runtime control flow in the header. Its behavior is compile-time adaptation: older MSVC versions map `snprintf` to `__wt_snprintf`, `_mkdir` backs `mkdir`, `_read`/`_write`/`_lseek` back POSIX names, and the `rwlock_wrapper` embeds an `SRWLOCK` plus an exclusive-owner marker.

## State, dependencies, and integration
The header includes `wt_internal.h`, `<sys/utime.h>`, and `<direct.h>`, and is included by `test_util.h` only under `_WIN32`. It is paired with the `windows_shim` static library from the Windows CMake file.

## Risks and test signals
Risks include semantic gaps from POSIX emulation, especially pthread behavior and filesystem mode handling. Macro remapping can also hide portability problems if code depends on Unix-only semantics. Signals include clean Windows compilation, tests resolving all declared shim symbols, correct include visibility from CMake, and no conflicting declarations with MSVC or Windows SDK headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/windows/windows_shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/wt_hang_analyzer/wt_hang_analyzer.py -->
# sources/storage-engines/wiredtiger/test/wt_hang_analyzer/wt_hang_analyzer.py

## Purpose
`wt_hang_analyzer.py` is a standalone diagnostic tool for collecting debugger output, and optionally core/minidump files, from interesting WiredTiger test processes during timeouts. It was designed for Evergreen-style hang investigation and supports Linux primarily, with Windows and LLDB/Darwin code paths present but Darwin intentionally disabled.

## Important APIs and classes
Important helpers include `LoggerPipe`, `call`, `callo`, `find_program`, `get_process_logger`, `get_hang_analyzers`, `check_dump_quota`, `pname_match`, `avoid_asan_dump`, and `main`. Platform adapters are `WindowsDumper`, `WindowsProcessList`, `LLDBDumper`, `DarwinProcessList`, `GDBDumper`, and `LinuxProcessList`. Command-line options select process-name contains/exact filters, explicit PIDs, core dumping, maximum dump size, and debugger output destinations.

## Control flow and behavior
`main` logs Python/OS/user context, parses options, chooses process and debugger adapters, enumerates processes, filters out itself, and iterates targets. For each process it tries to reduce ASAN-heavy core mappings through `/proc/<pid>/coredump_filter`, builds a per-process logger, and runs the platform dumper. Linux invokes `gdb` with batch commands for shared libraries, thread lists, all backtraces, scheduler locking, optional `gcore`, and quit. Windows invokes `cdb`; LLDB writes commands to a temporary file and sources them.

## State, dependencies, and integration
The script writes debugger logs named `debugger_<process>_<pid>.log` when file output is enabled and dump files named by process/pid/extension when core dumping is enabled. It depends on platform tools (`ps`, `gdb`, `cdb`, `lldb`), Python stdlib process/logging/threading modules, and Windows `pywin32` imports on Windows. It integrates with Evergreen or manual timeout triage workflows.

## Risks and test signals
Risks include debugger attach permissions, deprecated `platform.linux_distribution`, broad default matching that includes Python/test processes, command failures propagating as trapped exceptions, and Linux-specific `/proc` logic in `avoid_asan_dump`. Signals are useful per-process backtraces, nonzero exit when debugger invocations fail, quota-limited core creation, missing PID warnings, unsupported-platform warnings, and no subprocess pipe deadlocks due to `LoggerPipe`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/wt_hang_analyzer/wt_hang_analyzer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/wtperf/test_conf_dump.py -->
# sources/storage-engines/wiredtiger/test/wtperf/test_conf_dump.py

## Purpose
`test_conf_dump.py` is an executable regression test that verifies `wtperf` writes `WT_TEST/CONFIG.wtperf` matching the effective input configuration. It specifically checks precedence and append behavior across defaults/config files, `-o`, `-C`, and `-T`.

## Important APIs and functions
The script defines `generate_conf_file`, `execute_wtperf`, `build_dict_from_conf`, `extract_config_from_file`, `extract_config_from_opt_o`, and `run_test`. Constants include `OP_FILE`, `TMP_CONF`, `WTPERF_BIN`, and `CONF_NOT_PROVIDED`. It accepts `--wtperf_dir` and optional `--config`.

## Control flow and behavior
The script changes into the wtperf binary directory, generates a temporary config unless one was provided, runs `wtperf -O <conf>`, then parses both the input and dumped config into dictionaries. `conn_config` and `table_config` values are appended when repeated, while other keys are replaced by later sources. `run_test` validates that dumped values include `conn_config` and `table_config` fragments in precedence order and that all other keys match exactly. It runs once without options and once with representative `-o`, `-C`, and `-T` overrides, then removes `WT_TEST` and the generated config.

## State, dependencies, and integration
The test writes `__tmp.wtperf` and `WT_TEST/CONFIG.wtperf` under the wtperf directory, and removes them through shell commands. It depends on a built `./wtperf` binary, Python `argparse`, `re`, and `subprocess`. It integrates with the wtperf test suite to lock down config dumping semantics.

## Risks and test signals
Risks include `shell=True` command construction, simple comma splitting that can be fragile for nested config values, assumptions that quoted values start/end in a particular way, and cleanup through shell `rm`. Signals are process exit `0` plus `All tests succeeded`, and failure messages identifying missing keys, mismatched values, or incorrect append ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/wtperf/test_conf_dump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/build_and_push_containers.sh -->
# sources/storage-engines/wiredtiger/tools/antithesis/build_and_push_containers.sh

## Purpose
This shell script builds and pushes Antithesis Docker images for WiredTiger `test/format` workloads. It is intended for CI environments with task metadata and registry credentials in environment variables.

## Important commands and variables
Key variables are `task_name`, `is_patch`, `antithesis_image_tag`, `branch_name`, `build_id`, `revision`, and `antithesis_repo_key`. The script writes `../../cmake_build/VERSION`, builds `wt-test-format:$tag` from `test_format.dockerfile`, rewrites `docker-compose.yaml` from `wt-latest` to the tag, builds `wt-test-format-config:$tag` from `config.docker`, logs in to `us-central1-docker.pkg.dev`, tags both images into the MongoDB repository path, pushes them, and logs out.

## Control flow and behavior
With `errexit` and verbose shell mode, any failing command aborts. The tag defaults to `${task_name}-latest`, changes to `${task_name}-patch` for patch builds, and is overridden by `antithesis_image_tag` when present. Registry credentials are written temporarily to `mongodb.key.json`, piped to `docker login`, then removed.

## State, dependencies, and integration
The script mutates the local compose file via `sed -i`, writes a version file in the build directory, creates local Docker images, and pushes remote registry tags. It depends on `sudo docker`, the Antithesis Dockerfiles, `docker-compose.yaml`, CI metadata, and Google Artifact Registry credentials.

## Risks and test signals
Risks include in-place compose-file mutation, credentials touching disk, reliance on `sudo`, unquoted environment expansion in some paths, and stale tags if CI variables are absent. Signals include successful image builds, registry login/push output, expected image tags in Artifact Registry, and a version file containing branch/build/revision metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/build_and_push_containers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/docker-compose.yaml -->
# sources/storage-engines/wiredtiger/tools/antithesis/docker-compose.yaml

## Purpose
This Compose file defines the Antithesis test environment for a single WiredTiger `test/format` container. It gives the workload a fixed network identity, bind-mounted configuration, and persistent local data directory.

## Important services and fields
The `wiredtiger` service uses container name and hostname `wiredtiger`, image `wt-test-format:wt-latest`, and command `/bin/bash /opt/bin/test.sh -c CONFIG.antithesis -h /data/RUNDIR -T bulk,txn,retain=50`. It mounts `./data/wiredtiger` to `/data/` and binds local `CONFIG.antithesis` over `/opt/bin/test/format/CONFIG.antithesis`. The `antithesis-net` bridge network uses subnet `10.20.20.0/24` and assigns the container `10.20.20.6`.

## Control flow and behavior
Compose itself starts the service with the provided command. The image tag is rewritten by `build_and_push_containers.sh` during CI packaging, changing `wt-latest` to the selected Antithesis tag.

## State, dependencies, and integration
State persists in `./data/wiredtiger` on the host. The file depends on a built/pushed `wt-test-format` image and a local `CONFIG.antithesis` file. It integrates with Antithesis fault-injection assumptions by using a static low IPv4 address and comments that addresses `10.20.20.130` or higher are ignored by the fault injector.

## Risks and test signals
Risks include the mutable image tag, fixed container name/address collisions, host-directory permissions, and Compose version compatibility. Signals are container startup, `/data/RUNDIR` workload state, successful bind mount of `CONFIG.antithesis`, and reproducible network addressing for Antithesis orchestration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/docker-compose.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/launch_gdb.sh -->
# sources/storage-engines/wiredtiger/tools/antithesis/launch_gdb.sh

## Purpose
`launch_gdb.sh` is a developer helper for opening a WiredTiger `test/format` core file inside the Antithesis Docker image. It ensures the image exists, mounts the core at the expected location, and runs `gdb t core`.

## Important commands and variables
The script requires being run from `tools/antithesis`. It checks for a `wt-test-format` image with `sudo docker image ls | grep`, builds `wt-test-format:latest` from `test_format.dockerfile` if absent, resolves the first argument to an absolute source path, sets `T_DIR=/opt/bin/test/format`, and runs a temporary interactive container with `--mount type=bind,src=$SRC,dst=$T_DIR/core`.

## Control flow and behavior
The working-directory guard exits with a clear message if invoked from the wrong folder. If the image check fails, the script builds the image from the repository root. Then it launches an interactive container and changes to the test directory before invoking GDB on executable `t` and mounted core file `core`.

## State, dependencies, and integration
The script depends on Docker, sudo privileges, `test_format.dockerfile`, and a core path argument. It integrates with the same image used by Antithesis test runs, which helps match libraries and binaries during postmortem debugging.

## Risks and test signals
Risks include brittle image detection via grep, unquoted path handling, no explicit argument validation, and required interactive TTY/sudo access. Signals are an interactive GDB session with symbols and executable `t` resolved, or a locally built image when none existed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/launch_gdb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/test.sh -->
# sources/storage-engines/wiredtiger/tools/antithesis/test.sh

## Purpose
`test.sh` is the container entrypoint wrapper for running WiredTiger `test/format` inside the Antithesis image. It sets runtime library paths, starts the workload, and prints a bounded GDB backtrace if the workload leaves a core after failure.

## Important commands and variables
The script exports `LD_LIBRARY_PATH=/opt/bin:/opt/tools/voidstar/lib:$LD_LIBRARY_PATH`, changes to `./bin/test/format`, runs `./t "$@" 2>&1 &`, waits for the child PID, stores the return code, and on nonzero status invokes `gdb --batch` with `thread apply all backtrace 30` against `t *core*`.

## Control flow and behavior
The workload runs in the background so the script can capture and wait on its PID. The exit status is propagated after optional debugging output. All arguments passed to the script are forwarded to `./t`.

## State, dependencies, and integration
The script depends on the container filesystem layout, dynamic libraries in `/opt/bin` and `/opt/tools/voidstar/lib`, GDB, and the `test/format` executable `t`. It integrates with `docker-compose.yaml`, which calls it with `CONFIG.antithesis` and workload flags.

## Risks and test signals
The shebang is `/bin/sh` but the script uses `[[ ... ]]`, which requires a shell that supports Bash/Ksh syntax; this is a portability risk unless `/bin/sh` is Bash-compatible in the image. `gdb t *core*` is also glob-dependent and may fail or choose unexpectedly with zero/multiple cores. Signals are test stdout/stderr, preserved exit code, and GDB backtraces on nonzero failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/antithesis/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/backup_analysis.py -->
# sources/storage-engines/wiredtiger/tools/backup_analysis.py

## Purpose
`backup_analysis.py` compares two WiredTiger backup directories and reports how many bytes and incremental-backup granularity blocks changed between them. It classifies files into MongoDB-oriented categories to summarize replication, oplog, local, and system table change patterns.

## Important APIs and functions
Core functions include `get_metadata`, `get_checkpoint_time`, `older_dir`, `compute_type`, `check_backup`, `compare_file`, `print_summary`, `compare_backups`, and `backup_analysis`. `TypeStats` accumulates per-category bytes, changed blocks, file counts, changed-file counts, granularity-block counts, small-change counts, large-change counts, and single-block-file counts.

## Control flow and behavior
The script validates two distinct backup directories containing `WiredTiger.backup`, determines which is older from `WiredTigerHS.wt` checkpoint metadata, compares `.wt` and `.wti` files common to both directories, and reports files created/dropped between backups. `compare_file` reads common file prefixes in 4096-byte chunks, rolls differences into caller-specified granularity blocks, prints verbose or terse per-file output, and updates global type statistics. `print_summary` aggregates totals and per-type percentages.

## State, dependencies, and integration
State is held in module globals `compare_size`, `pct20`, `pct80`, and `typestats`. The script depends on backup metadata format, MongoDB naming conventions (`collection`, `index`, oplog metadata), POSIX file paths, Python stdlib modules, and readable backup data files. It is a diagnostic command-line tool, not part of WiredTiger runtime.

## Risks and test signals
Risks include brittle metadata parsing, assertions instead of graceful errors for missing metadata or type mismatches, division by zero for unusual empty inputs, only overlapping bytes being compared, and integer-only granularity. Signals are per-file change reports, created/dropped file messages, summary percentages, correct category classification, and exit after `backup_analysis(opts)` with status `0`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/backup_analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/callgraph -->
# sources/storage-engines/wiredtiger/tools/callgraph

## Purpose
`tools/callgraph` is a Perl analysis tool for building and querying WiredTiger C call graphs. It can render filtered Graphviz graphs, find shortest or all call paths, compute crosslink statistics, trace possible return values, grep/tag function bodies, merge DOT files, and run as an interactive server for repeated queries.

## Important APIs and modes
Major modes are `--graph`, `--path-1`, `--path-all`, `--crosslink-stats`, `--ret`, `--retl`, `--retll`, `--merge`, `--mergeflat`, and `--server`. Key helpers include argument parsing (`parseArgs`, `postProcessArgs`, `split_args`, `argv_redirect`), source loading (`read_all`), module inference (`fname_to_module`, `name_to_module`), parsing/tagging (`parse_retvals`, tag handlers), output formatting (`printPathText`, `formatNodeDot`, `printPathDot`, `pan_js`), filtering hooks (`filterEdge`, `filterNode`), graph merging, and server dispatch (`start_server`).

## Control flow and behavior
The script reads all `src`, `ext`, and optional `build` C/header files into one stream with `#line` markers, strips comments, joins selected continued lines, discovers function definitions and function-like macros, optionally records assigned function-pointer references, and scans function bodies for calls. It builds forward and reverse adjacency maps, file/module maps, return-expression maps, and tag annotations. Query modes then either traverse paths breadth/depth first with depth/prune/grow/exclude filters, emit graph nodes/edges, summarize internal/external cross-module calls, recursively expand return values, or merge preexisting DOT input.

## State, dependencies, and integration
The script uses many global hashes for graph state (`%funcs`, `%calls`, `%rcalls`, `%edges`, `%func2file`, `%func2mod`, `%funcmarks`, `%func2ret`). It depends on Perl 5.26, `Getopt::Long`, `IO::File`, Git for repo-root discovery, Unix shell commands for source collection, and Graphviz/`column` for some output modes. It is WiredTiger-specific through module aliases, function naming conventions, return macros, and cursor static initializer parsing.

## Risks and test signals
Risks include regex-based C parsing limitations, global mutable state, eval-powered custom hooks and tag substitutions, shell interpolation in source reading, temp-file/fork complexity in server mode, and output filters that depend on external tools. Signals are correct function lists for known files, plausible path results such as eviction-to-hazard examples, valid DOT/SVG/HTML output, crosslink tables, useful return-code expansion, and server commands reusing parsed source without reparsing the graph unless grep/tag metadata is requested.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/callgraph -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/checksum_bitflip/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/tools/checksum_bitflip/CMakeLists.txt

## Purpose
This CMake file declares the `checksum_bitflip` diagnostic executable for WiredTiger. It uses the project helper `create_test_executable` and lists `checksum_bitflip.c` as the only source.

## Important APIs and targets
The important build API is `create_test_executable(checksum_bitflip SOURCES checksum_bitflip.c)`. Build properties, include directories, and link libraries are inherited from the helper rather than spelled out locally.

## Control flow and behavior
There is no conditional build logic. If the containing directory is included by the parent CMake configuration, the executable target is created.

## State, dependencies, and integration
The file depends on the parent WiredTiger CMake infrastructure defining `create_test_executable`. The generated binary integrates with developer diagnostics for checksum mismatch investigation.

## Risks and test signals
Risks are limited to build-system integration: if helper semantics change, the tool may miss internal include paths or libraries needed for `test_util.h` and checksum helpers. Signals are successful target generation and compilation of `checksum_bitflip.c`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/checksum_bitflip/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/checksum_bitflip/checksum_bitflip.c -->
# sources/storage-engines/wiredtiger/tools/checksum_bitflip/checksum_bitflip.c

## Purpose
`checksum_bitflip.c` implements a diagnostic command that tests whether a target checksum matches a file as-is or after flipping any single bit. It helps investigate checksum mismatches that may be caused by hardware bit flips in memory.

## Important APIs and functions
The program only defines `main`. It uses `strtol` to parse a hex checksum, POSIX `open`/`fstat`/`read`/`close` to read the input file, test utility allocation/assertion helpers, and WiredTiger `__wt_checksum_sw` to compute checksums.

## Control flow and behavior
`main` validates `argc`, parses the checksum as a 32-bit value, reads the entire file into memory, first checks the original checksum, then iterates every byte and bit. For each bit it toggles the bit, computes the checksum, reports the matching byte/bit if found, then toggles it back. It exits `0` on a match and `1` for usage errors, invalid checksum width, or no match.

## State, dependencies, and integration
State is transient: one heap buffer containing the file and local loop variables. The tool depends on `test_util.h`, `__wt_checksum_sw`, and a build environment that exposes WiredTiger internals. The CMake file builds it as a test executable.

## Risks and test signals
The brute-force algorithm is `O(file_size * 8 * checksum_cost)`, so large files can be expensive. It reads the whole file into memory and does not free before process exit, which is acceptable for a short-lived tool. Signals are output saying checksum matches without flipping bits, output identifying the bit and byte that produce the target checksum, or `No checksum match` with exit `1`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/checksum_bitflip/checksum_bitflip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/__init__.py -->
# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/__init__.py

## Purpose
`__init__.py` marks `tools/gdb/gdb_scripts` as a Python package so GDB loader code can import the individual helper scripts by module name.

## Important APIs and functions
The file defines no runtime API, functions, classes, or state. Its only functional content is the package marker behavior.

## Control flow and behavior
There is no control flow. Importing `gdb_scripts` succeeds because this file exists.

## State, dependencies, and integration
It integrates with `load_gdb_scripts.py`, which appends the build directory to `sys.path` and imports `gdb_scripts.hazard_pointers` and `gdb_scripts.dump_insert_list`. It has no external dependencies beyond Python package loading.

## Risks and test signals
Risk is minimal; deleting or renaming it can break imports in environments that still require explicit package markers. Signals are successful `source load_gdb_scripts.py` inside GDB and import of sibling modules without `ModuleNotFoundError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/dump_insert_list.py -->
# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/dump_insert_list.py

## Purpose
`dump_insert_list.py` registers a custom GDB command for walking a WiredTiger `WT_INSERT_HEAD` skip list and dumping bottom-level insert entries to `dump.txt`. It is meant for debugging large insert lists without flooding the terminal.

## Important APIs and classes
The helper class `insert` stores a decoded key, address, and next-pointer array and can print itself. The GDB command class `dump_insert_list` registers command name `dump_insert_list`, tracks `key_format`, and implements `usage`, `decode_key`, `get_key`, `walk_level`, and `invoke`.

## Control flow and behavior
When invoked with `WT_INSERT_HEAD,key_format`, the command clears previous inserts, opens `dump.txt`, parses the expression through `gdb.parse_and_eval`, walks `head[0]`, decodes each key using the insert key offset/size, records up to ten next pointers or until `0x0`, writes one line per insert, and reports completion. Supported key formats are `S`, `u`, and `i`, with `S` decoded as bytes-to-string.

## State, dependencies, and integration
The command uses GDB's Python API, `gdb.selected_inferior().read_memory`, and WiredTiger structure layout knowledge for `WT_INSERT`. It is imported by `load_gdb_scripts.py` and can also be sourced manually in GDB. Output state is `dump.txt` in the current GDB working directory.

## Risks and test signals
Risks include fragile argument splitting on a comma, no validation for missing arguments before indexing, key decoding assumptions, hardcoded next-pointer inspection up to ten levels, and dependence on exact debug type/layout information. Signals are `dump.txt` containing ordered bottom-level entries, correct key decoding for `S`, `u`, and `i`, and no GDB Python exceptions for valid `WT_INSERT_HEAD` expressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/dump_insert_list.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/hazard_pointers.py -->
# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/hazard_pointers.py

## Purpose
`hazard_pointers.py` registers GDB commands for inspecting WiredTiger hazard pointers across threads. It helps identify active sessions holding references that can block eviction or page lifecycle transitions.

## Important APIs and classes
Module-level aliases `SESSION_IMPL_PTR` and `CONN_IMPL_PTR` resolve GDB types. `find_sessions` walks all inferior threads and stack frames looking for an argument named `session`. Command classes `dump_hazard_pointers` and `find_hazard_pointer_for` register `dump_hazard_pointers` and `find_hazard_pointers_for`.

## Control flow and behavior
`find_sessions` saves the original frame, switches through every thread, walks older frames until `info arg session` returns a pointer-like value, records the thread global number and session pointer, then restores the original frame. `dump_hazard_pointers` prints every non-null hazard pointer for active sessions. `find_hazard_pointers_for` validates a single hex pointer argument and prints threads/sessions whose hazard array has a matching `ref`.

## State, dependencies, and integration
The script depends on GDB Python APIs and WiredTiger debug types `WT_SESSION_IMPL` and `WT_CONNECTION_IMPL`. It assumes session frames expose an argument named `session` and that session hazard fields are named `active`, `hazards.inuse`, and `hazards.arr`. It is imported by `load_gdb_scripts.py`.

## Risks and test signals
Risks include GDB command parsing via text output from `info arg session`, stale type/field names after WiredTiger structure changes, and frame restoration failures if GDB state changes unexpectedly. Signals are command registration, session/thread listings, hazard pointer dumps for active sessions, and precise identification of holders for a target `WT_REF` address.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/hazard_pointers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/wt_debug_script_update.py -->
# sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/wt_debug_script_update.py

## Purpose
`wt_debug_script_update.py` is an exploratory GDB Python script for dumping WiredTiger data handles, pages, insert lists, and update chains, including optional BSON decoding for MongoDB values. It predates the command-class style used by the other scripts and exposes helper functions directly in the GDB Python environment.

## Important APIs and functions
Important helpers include `dbg`, `walk_wt_list`, `get_data_handle`, `get_btree_handle`, `dump_update_chain`, `dump_insert_list`, `dump_skip_list`, `dump_modified`, `dump_disk`, `dump_leaf_page`, `dump_int_page`, and `dump_handle`. It initializes `conn_impl_ptr`, parses `session->iface->connection`, and dereferences it as a `WT_CONNECTION_IMPL`.

## Control flow and behavior
On import, the script prints/debugs type and connection information. Users call `get_data_handle(conn, handle_name, checkpoint_name)` to locate a handle in the connection's data-handle queue, then `dump_handle` to inspect the Btree root. Internal-page dumping recurses through page indexes; leaf-page dumping prints disk bytes and modified update/insert state. Update-chain dumping skips value reads for zero-size tombstone/reserve entries and attempts BSON decoding when type indicates a standard update.

## State, dependencies, and integration
The script depends on GDB Python, `bson`, WiredTiger debug types and field layout, and an in-scope `session` symbol in GDB. It is not imported by `load_gdb_scripts.py` in the current loader; it is likely sourced manually during deep debugging.

## Risks and test signals
Risks are high because the script executes work at import time, assumes `session` exists, uses broad `except` around BSON decoding, has hardcoded page/block header sizes, and contains older TODO/FIXME notes. Signals are successful handle discovery, readable root/internal/leaf page dumps, decoded BSON where applicable, and absence of GDB exceptions on known page structures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/gdb_scripts/wt_debug_script_update.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/load_gdb_scripts.py -->
# sources/storage-engines/wiredtiger/tools/gdb/load_gdb_scripts.py

## Purpose
`load_gdb_scripts.py` is the entrypoint that loads WiredTiger's custom GDB debugging helpers. It is designed for manual `source` use and for automatic GDB loading when copied beside a shared library as `<library>-gdb.py`.

## Important APIs and commands
The script imports `gdb`, `sys`, and `os`, prints a loading message, computes `build_dir = os.path.dirname(__file__)`, appends it to `sys.path`, imports `gdb_scripts.hazard_pointers` and `gdb_scripts.dump_insert_list`, and executes `source {build_dir}/gdb_scripts/dump_row_int.gdb` for a Scheme/GDB script.

## Control flow and behavior
Execution is linear. Importing the Python modules registers their GDB command classes at import time. The final `gdb.execute` loads the row-internal-page dump script. There is no error recovery; import or source failures surface directly in GDB.

## State, dependencies, and integration
The loader depends on being located in a directory that also contains `gdb_scripts`, plus copied build-directory packaging when shared-library auto-load is enabled. It integrates with GDB's objfile `-gdb.py` auto-load mechanism and with build steps that copy/rename the loader.

## Risks and test signals
Risks include GDB auto-load safe-path restrictions, missing `gdb_scripts` package files in the build directory, missing `dump_row_int.gdb`, and import-time failures if WiredTiger debug types are unavailable. Signals are the "Loading custom WiredTiger gdb scripts..." message and availability of `dump_hazard_pointers`, `find_hazard_pointers_for`, and `dump_insert_list` commands in GDB.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/gdb/load_gdb_scripts.py -->
