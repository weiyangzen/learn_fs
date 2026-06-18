# subset-b-008956 Research

Grouped research for the WiredTiger wtperf benchmark sources and CMake build configuration files in subset B. Each section preserves the original source path and is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf.c

## Purpose
`wtperf.c` is the executable driver for WiredTiger's `wtperf` benchmark. It parses command-line and file options, builds connection/table configuration strings, creates and populates benchmark tables, runs mixed workload threads, starts optional background backup/checkpoint/flush/scan/monitor activity, reports throughput and latency, and tears the database down when configured.

## Important APIs, Types, And Functions
The file operates around `WTPERF`, `WTPERF_THREAD`, `WORKLOAD`, and `TRACK` from `wtperf.h`. Key functions are `main`, `start_all_runs`, `start_run`, `execute_populate`, `execute_workload`, `worker`, `populate_thread`, `monitor`, `backup_worker`, `checkpoint_worker`, `flush_tier_worker`, `scan_worker`, `create_tables`, `create_uris`, `close_reopen`, `wtperf_rand`, and `run_mix_schedule`. It uses the WiredTiger C API heavily: `wiredtiger_open`, connection/session creation, cursors, transactions, checkpoints, backup cursors, `wiredtiger_calc_modify`, and session truncate.

## Control Flow
`main` initializes defaults, processes `-C`, `-h`, `-m`, `-O`, `-o`, and `-T`, appends derived connection/table config, validates with `config_sanity`, recreates homes when `create=true`, writes `CONFIG.wtperf`, then calls `start_all_runs`. A single database runs directly through `start_run`; multiple databases clone `WTPERF` and execute each home in a thread. `start_run` opens the connection, creates URIs/tables, optionally launches monitor, populates records, closes/reopens for workload isolation or readonly mode, starts background workers, runs `execute_workload`, prints final counters and latencies, and joins all helper threads.

## State And Persistence Behavior
Persistent state is the WiredTiger home directory, table data, optional backup directories, monitor output files, and `CONFIG.wtperf`. Shared in-memory state includes atomic insert/log counters, per-thread `TRACK` counters, volatile stop/error/activity flags, the truncate stone queue, and open connection/session/cursor handles. The code intentionally leaks some thread-owned structures after join because monitor and summary code may still read counters. Reopen uses `final_flush=true`, while `close_conn=false` intentionally skips a clean close and may lose data.

## Dependencies And Integration Points
This file depends on `wtperf_config.c` for option parsing, `wtperf_misc.c` for logging/index/backup helpers, `wtperf_throttle.c` for throttling, `wtperf_truncate.c` for truncate steering, WiredTiger test utilities, extension build macros, and system threading/sleep/file APIs. It integrates with WiredTiger backup, tiered storage, compression extensions, statistics logging, table/index creation, and random cursor support.

## Risks
Important risks are concurrency around volatile flags and unsynchronized counters, division by zero in final summary if `total_ops` or `testsec` is zero, mixed workload percentage rounding that can eliminate low-ratio operations, complex transaction rollback paths when side tables are enabled, and fragile assumptions around truncate being single-table/single-thread. `wtperf_rand` must avoid invalid ranges when populate is disabled or when insert threads are still catching up.

## Test Signals
Useful signals include successful compile under strict C warnings, smoke runs with populate-only, read-only reopen, mixed insert/read/update, `modify` with `ops_per_txn`, `random_range`, scan tables, backup, tiered flush, and truncate workloads. Runtime artifacts to inspect are `CONFIG.wtperf`, `*.stat`, `monitor`, `monitor.json`, final operation summaries, latency histograms, and failures from `lprintf`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf.h -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf.h

## Purpose
`wtperf.h` is the shared contract for the wtperf benchmark. It defines extension paths, workload operation codes, benchmark state structs, time conversion macros, tracking structures, exported helper prototypes, and key encode/decode helpers used across the wtperf C files.

## Important APIs, Types, And Functions
Important types are `WORKLOAD`, `TRUNCATE_CONFIG`, `TRUNCATE_QUEUE_ENTRY`, `THROTTLE_CONFIG`, `WTPERF`, `TRACK`, and `WTPERF_THREAD`. `WTPERF` owns connection-level state, URIs, config, thread arrays, counters, volatile lifecycle flags, and truncate queue head. `WTPERF_THREAD` owns per-thread buffers, RNG state, throttle/truncate config, random cursor, and per-operation `TRACK` counters. Inline helpers include `generate_key`, `extract_key`, and `die`.

## Control Flow
The header does not execute logic directly, but it shapes all call boundaries: `wtperf.c` drives lifecycle, `wtperf_config.c` fills `CONFIG_OPTS` and workload arrays, `wtperf_misc.c` logs/backs up/indexes, `wtperf_throttle.c` consumes `THROTTLE_CONFIG`, and `wtperf_truncate.c` consumes the truncate queue/config.

## State And Persistence Behavior
State here is purely structural. Persistent effects are mediated by fields such as `home`, `monitor_dir`, table URIs, and connection/table configuration strings. The header documents intentionally shared counters and volatile flags but does not provide synchronization beyond callers' use of atomics for selected counters.

## Dependencies And Integration Points
The header includes `test_util.h`, `<math.h>`, and `config_opt.h`, and exposes WiredTiger API types such as `WT_CONNECTION`, `WT_SESSION`, and `WT_CURSOR`. Compression and tiered extension constants integrate command-line options with dynamic extension loading or built-in extension builds.

## Risks
The biggest risk is that this header is a broad shared mutable contract. Changes to struct layout or option-derived buffer sizing affect multiple files and thread paths. `volatile bool` flags are lifecycle hints, not full synchronization primitives. Buffer sizes rely on `key_sz` and `value_sz_max` being validated before thread startup.

## Test Signals
Compile coverage across all wtperf C files is the primary signal. Runtime tests should exercise all declared helpers: backup, config parsing, latency aggregation, truncate, throttling, index-like table operations, and idle table cycling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_config.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_config.c

## Purpose
`wtperf_config.c` implements wtperf option management. It expands the option list generated from `wtperf_opt_inline.h`, initializes defaults, parses config files and command-line option strings, parses workload thread groups, validates combinations, logs the effective config, and prints usage.

## Important APIs, Types, And Functions
Public functions are `config_opt_init`, `config_opt_cleanup`, `config_opt_file`, `config_opt_str`, `config_opt_name_value`, `config_sanity`, `config_opt_log`, `config_opt_print`, `config_opt_usage`, and `config_reopen`. Internal functions include `config_unescape`, `config_threads`, `config_opt`, `config_consolidate`, and `pretty_print`. The file uses WiredTiger's `WT_CONFIG_PARSER` to parse both top-level option strings and nested `threads=((...))` groups.

## Control Flow
Initialization copies the generated default struct and duplicates default strings so cleanup can free all string fields uniformly. `config_opt_file` reads lines, handles whitespace, comments, continuations, and overflow checks, then passes joined options to `config_opt_str`. `config_opt_str` scans `key=value` pairs, applies `config_opt`, and records each processed pair in `config_head`. `threads` values are delegated to `config_threads`, which builds `WORKLOAD` entries and sets global grow/shrink/truncate flags. `config_sanity` enforces cross-option rules before the benchmark runs.

## State And Persistence Behavior
The file mutates `CONFIG_OPTS`, `WTPERF.workload`, `workload_cnt`, `workers_cnt`, and wtperf flags. It persists the final processed configuration via `config_opt_log`, consolidating duplicate keys and concatenating repeated `conn_config` or `table_config` entries.

## Dependencies And Integration Points
It depends on `config_opt.h`, `wtperf_opt_inline.h`, WiredTiger config parsing, test utility allocation helpers, and `lprintf`. Its output feeds `wtperf.c` connection/table creation, workload scheduling, random selection, transactions, truncate, backup, scan, tiered, and monitoring behavior.

## Risks
Thread configuration is dense and rejects malformed values through a shared `goto err` path, so diagnostics can be coarse. Config queue recording happens after parsing each pair and can preserve implicit command order in ways tests may depend on. `CONFIG_STRING_TYPE` appends values while `STRING_TYPE` replaces, so changing an option's type changes user-visible semantics.

## Test Signals
Test config files with comments, continuations, escaped characters, repeated config keys, nested thread groups, invalid unknown options, invalid truncate mixes, readonly write workloads, scan table coupling, and grow/shrink value bounds. Verify `CONFIG.wtperf` consolidation and usage output after option list changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_misc.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_misc.c

## Purpose
`wtperf_misc.c` contains small operational helpers for wtperf: index-like table key generation/deletion, log file setup, formatted logging, and source-side backup file reading.

## Important APIs, Types, And Functions
Public functions are `delete_index_key`, `generate_index_key`, `setup_log_file`, `lprintf`, and `backup_read`. Internal `create_index_key` formats synthetic index keys as `index_value:key`. `WT_BACKUP_COPY_SIZE` controls backup read buffer size.

## Control Flow
Index deletion probes every possible historical multiplier for a main-table key and removes any matching index-like entries. Workload index inserts use `generate_index_key`, with populate fixed at `INDEX_POPULATE_MULT` and workload updates randomized across multiplier space. `setup_log_file` creates `<monitor_dir>/<table_name>.stat` when verbosity is enabled. `lprintf` writes normal messages to the stat file and sometimes stdout, while errors also go to stderr and `WT_PANIC` aborts. `backup_read` opens a WiredTiger backup cursor, iterates filenames, opens each source file from `home`, and reads it in chunks.

## State And Persistence Behavior
The log helper persists the `.stat` file and line-buffers it. Backup read does not create backup files; it measures source-side backup read pressure. Index helpers mutate the optional index-like table when called from populate or workload transactions.

## Dependencies And Integration Points
This file integrates with `wtperf.c` worker/populate/backup paths, WiredTiger backup cursors, POSIX `open`, `read`, `stat`, and `close`, and test utility error/allocation helpers.

## Risks
`delete_index_key` scans a fixed multiplier range, so changing index multiplier constants must keep deletion in sync. `backup_read` ignores some open failures after `error_sys_check` style calls and may produce benchmark-specific behavior rather than a complete backup. `lprintf` assumes `logf` exists for normal verbose logging when verbosity is enabled.

## Test Signals
Exercise index-like workloads through populate and update paths, verify `.stat` creation and stdout/stderr behavior for verbosity levels, run source-side backup mode, and inject backup cursor `EBUSY` to confirm retry behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_opt_inline.h -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_opt_inline.h

## Purpose
`wtperf_opt_inline.h` is an X-macro option catalog for wtperf. It is included multiple times with different macro definitions to generate the `CONFIG_OPTS` struct fields, option descriptors, default initializer, and doxygen-style option documentation.

## Important APIs, Types, And Functions
The file defines `DEF_OPT_AS_BOOL`, `DEF_OPT_AS_CONFIG_STRING`, `DEF_OPT_AS_STRING`, and `DEF_OPT_AS_UINT32` under mode macros such as `OPT_DECLARE_STRUCT`, `OPT_DEFINE_DESC`, `OPT_DEFINE_DEFAULT`, and `OPT_DEFINE_DOXYGEN`. It lists options for backup, checkpoint, connection/session/table config, compression, population, table counts, indexing, logging, latency/throughput checks, random distributions, scans, tiered storage, transactions, truncate, and value sizing.

## Control Flow
There is no direct execution. The include mode determines whether each entry becomes a struct member, descriptor row, initializer value, or documentation row. `wtperf_config.c` depends on descriptor order matching the default struct layout.

## State And Persistence Behavior
This file defines default benchmark state such as `conn_config`, `table_config`, `icount`, `run_time`, `sample_rate`, `value_sz`, and `threads`. These defaults are copied into each `CONFIG_OPTS` instance and later written to `CONFIG.wtperf` only when processed through config parsing or derived option appends.

## Dependencies And Integration Points
It is tightly coupled to `config_opt.h`, `wtperf_config.c`, and every place that reads `CONFIG_OPTS` fields. `CONFIG_STRING` options append new configuration while `STRING` options replace values, so option classification is part of the public behavior.

## Risks
Adding, reordering, or retyping options can break struct initialization, usage output, or parser semantics. Defaults are intentionally tiny for fast basic runs, so tests that assume production-sized workloads must override them explicitly.

## Test Signals
Regenerate/compile all include modes, run `wtperf -?` or usage paths, parse each option type, and verify new options appear in defaults, descriptors, and config logging.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_opt_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_throttle.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_throttle.c

## Purpose
`wtperf_throttle.c` implements per-worker operation throttling so a workload can cap operations per second.

## Important APIs, Types, And Functions
The public functions are `setup_throttle` and `worker_throttle`. Both operate on `WTPERF_THREAD.throttle_cfg`, which stores the last refill timestamp, remaining operation count, operations per increment, and microseconds per increment.

## Control Flow
`setup_throttle` maps a configured per-thread throttle into an operation bucket. Very low rates use one operation with a larger interval, ordinary rates target `THROTTLE_OPS` operations per interval, and high rates use 100 microsecond increments with more operations per increment. The main worker loop decrements `ops_count` after each operation and calls `worker_throttle` when it reaches zero. `worker_throttle` sleeps for the remaining interval or refills proportionally when the worker is behind.

## State And Persistence Behavior
All state is per-thread and in-memory. There is no persistent output except indirect effects on benchmark throughput and monitor logs.

## Dependencies And Integration Points
It depends on time conversion macros from `wtperf.h`, WiredTiger time helpers `__wt_epoch` and `WT_TIMEDIFF_US`, and `usleep`. The `worker` loop in `wtperf.c` is the sole consumer.

## Risks
Throttle zero is handled by callers; this file assumes nonzero throttle. Integer division can make low rates coarse, and scheduler sleep granularity can dominate small intervals. Refilling based on elapsed time intentionally lets delayed workers catch up, which may create short bursts.

## Test Signals
Run workloads with throttle below 100 ops/sec, midrange rates, and high rates; compare monitor ops/sec to configured caps and verify no divide-by-zero when throttle is disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_throttle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_truncate.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/wtperf_truncate.c

## Purpose
`wtperf_truncate.c` implements the special wtperf truncate workload. It creates and consumes "truncate stones" so the table is periodically reduced to a target record count while insert activity may continue.

## Important APIs, Types, And Functions
Public functions are `setup_truncate`, `run_truncate`, and `cleanup_truncate_config`. Internal `decode_key` converts string keys to numeric positions. The file uses `TRUNCATE_CONFIG` and `TRUNCATE_QUEUE_ENTRY` from `wtperf.h`.

## Control Flow
`setup_truncate` opens the single benchmark table, finds first and last keys, computes a stone gap and needed stones from `truncate_count` and `truncate_pct`, and preloads the global stone queue when existing data is large enough. `run_truncate` updates expected total rows from summed inserts, adjusts a catch-up multiplier when behind, adds stones until the queue reaches the target, pops one stone, and either removes records one-by-one or calls `WT_SESSION.truncate` up to the stone cursor.

## State And Persistence Behavior
In-memory truncate state tracks expected table size, last key, catch-up multiplier, and queued stones. Persistent effects are deletes/truncates in the WiredTiger table. `cleanup_truncate_config` drains any remaining queue entries during `WTPERF` cleanup.

## Dependencies And Integration Points
The file integrates with the `worker` loop's truncate operation, key formatting from `generate_key`, operation counters from `sum_insert_ops`, and WiredTiger cursor/session truncate APIs. It assumes wtperf validation has restricted truncate to one table and one truncate worker.

## Risks
Queue state is stored in `WTPERF.stone_head`, so truncate is only safe under the single-thread invariant. Initial setup assumes the table has data and uses `testutil_check` on cursor navigation. Catch-up multiplier changes benchmark behavior dynamically and can create larger-than-expected truncate spans.

## Test Signals
Run truncate with both `truncate_single_ops=false` and true, verify validation rejects random-range or multi-table truncate, check table size trends toward `truncate_count`, and test cleanup of queued stones on early stop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/wtperf_truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/base.cmake -->
# sources/storage-engines/wiredtiger/cmake/configs/base.cmake

## Purpose
`base.cmake` defines WiredTiger's central build configuration options and default values. It chooses defaults from build type, platform, and discovered libraries, exposes cache options through helper macros, and applies derived flag/config relationships.

## Important APIs, Types, And Functions
It uses `config_choice`, `config_bool`, and `config_string` from `helpers.cmake` to define architecture, OS, diagnostics, error logging, ref tracking, call log, unit tests, coverage, static/shared builds, PIC, strict mode, Python/SWIG, spinlock type, compression/encryption/storage extensions, cppsuite/model/PALite/LazyFS/LLVM, debug info, SQLite, optimization level, and version strings.

## Control Flow
The file computes defaults, probes Python, disables Python under selected sanitizers, maps built-in extension availability to default external extension options, forces Windows static defaults, declares all cache options, then applies derived relationships: diagnostics enables debug info/ref tracking/error log, unit-test asserts require unit tests, Windows chooses CRT mode, optimization flags replace prior `-O`/`/O` flags, GNU gets `-fno-strict-aliasing`, and Antithesis adds sanitizer coverage instrumentation.

## State And Persistence Behavior
It mutates CMake cache variables such as `ENABLE_SHARED`, `HAVE_DIAGNOSTIC`, `WT_ARCH`, `WT_OS`, `CC_OPTIMIZE_LEVEL`, `WT_OPTIMIZE_FLAGS_SAVED`, and `WT_DEBUG_FLAGS_INITIALIZED`. These values persist in a build directory and flow into generated headers and target flags.

## Dependencies And Integration Points
It includes `cmake/helpers.cmake` and `cmake/configs/version.cmake`, consumes library discovery variables such as `HAVE_LIBLZ4`, and relies on compiler identity variables established by `modes.cmake`. It feeds `wiredtiger_config.h.in`, library target definitions, extension builds, tests, and install metadata.

## Risks
Cache persistence is a major risk: once initialized, debug/optimization flags are guarded by internal variables and may not update unless cache variables change as expected. Dependency errors intentionally fail hard for explicit extension requests. Platform defaults can surprise cross-builds if `WT_OS`/`WT_ARCH` are not set before this file.

## Test Signals
Configure Debug, Release, sanitizer, Windows, and POSIX builds; toggle each extension with and without required libraries; verify generated `wiredtiger_config.h`, compile flags, and cache variables. Reconfigure after changing `CC_OPTIMIZE_LEVEL` to ensure replacement logic works.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/base.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/modes.cmake -->
# sources/storage-engines/wiredtiger/cmake/configs/modes.cmake

## Purpose
`modes.cmake` defines available WiredTiger build types and compiler/linker flags for default, sanitizer, and coverage configurations.

## Important APIs, Types, And Functions
The key function is `define_build_mode(mode ...)`, which accepts C/CXX compiler flags, link flags, libraries, and dependency expressions. It sets `BUILD_MODES`, compiler family variables (`MSVC_C_COMPILER`, `CLANG_C_COMPILER`, `GNU_C_COMPILER`, and CXX variants), and cache variables like `CMAKE_C_FLAGS_ASAN`.

## Control Flow
The file detects compiler families, defines `define_build_mode`, constructs frame-pointer, ASan, UBSan, MSan, TSan, and Coverage flags, validates compiler support using `check_c_compiler_flag` and `check_cxx_compiler_flag`, initializes cache flags once per build type, and rejects unavailable `CMAKE_BUILD_TYPE` values.

## State And Persistence Behavior
Build modes and their flags are persisted in the CMake cache. Per-mode initialization is guarded by `WT_BUILD_MODE_<MODE>_FLAGS_INITIALIZED`, preventing repeated re-seeding from overwriting user edits in the same build directory.

## Dependencies And Integration Points
It includes `CheckCCompilerFlag`, `CheckCXXCompilerFlag`, and `helpers.cmake` for dependency evaluation. `base.cmake` later depends on `BUILD_MODES` and compiler family variables for debug and optimization flag logic.

## Risks
Flag checks are only as good as the active compiler/linker environment; unsupported sanitizer libraries may still fail later at link or runtime. The file uses `MSVC` in dependency expressions even though compiler booleans are also defined separately, so CMake's own `MSVC` variable must be reliable.

## Test Signals
Configure each build type (`Debug`, `Release`, `RelWithDebInfo`, `ASan`, `UBSan`, `MSan`, `TSan`, `Coverage`) under Clang/GCC/MSVC where applicable and verify invalid build types fail at configure time.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/modes.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/version.cmake -->
# sources/storage-engines/wiredtiger/cmake/configs/version.cmake

## Purpose
`version.cmake` is the generated CMake version source for WiredTiger.

## Important APIs, Types, And Functions
It sets `WT_VERSION_MAJOR`, `WT_VERSION_MINOR`, `WT_VERSION_PATCH`, and `WT_VERSION_STRING`.

## Control Flow
There is no branching. The file is included by `base.cmake`, which exposes these values as configurable version strings.

## State And Persistence Behavior
The values become CMake variables and may be copied into cache-backed `VERSION_*` settings and generated headers/pkg-config metadata.

## Dependencies And Integration Points
It is generated by `dist/s_version` and consumed by build configuration, install metadata, and runtime version strings.

## Risks
Manual edits are explicitly discouraged. If the generated version drifts from source release metadata, package names, `wiredtiger.pc`, and `WIREDTIGER_VERSION_STRING` consumers can disagree.

## Test Signals
Run the version-generation path and configure CMake; verify generated headers and pkg-config report `12.0.0` and the full version string.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/version.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/wiredtiger_config.h.in -->
# sources/storage-engines/wiredtiger/cmake/configs/wiredtiger_config.h.in

## Purpose
`wiredtiger_config.h.in` is the CMake template for WiredTiger's generated compile-time configuration header.

## Important APIs, Types, And Functions
It uses `#cmakedefine` for build toggles such as diagnostics, error logging, built-in extensions, call log, unit tests, memkind, Antithesis, RCpc, CRC disable, spinlock type, endian, and standalone build. It also defines POSIX feature availability by target preprocessor macros and sets `VERSION`.

## Control Flow
CMake substitutes cache variables into the template. At C compile time, platform preprocessor checks define availability for POSIX, Linux-only, x86, and ARM intrinsic features.

## State And Persistence Behavior
The generated header is a persistent build artifact under the build include directory. It directly controls compiled code paths throughout WiredTiger.

## Dependencies And Integration Points
It depends on `base.cmake` values and platform compiler macros. It is included by WiredTiger source through generated include paths and is installed indirectly through generated public headers.

## Risks
Template mistakes can silently alter broad compile-time behavior. Platform feature checks are preprocessor-based and may not capture unusual libc/kernel combinations. The `SPINLOCK_TYPE` substitution must match a valid mutex implementation macro.

## Test Signals
Configure representative Linux, macOS, NetBSD, Windows, x86_64, and aarch64 builds; inspect generated header; build with toggles for diagnostics, built-in extensions, unit tests, and RCpc.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/configs/wiredtiger_config.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/define_libwiredtiger.cmake -->
# sources/storage-engines/wiredtiger/cmake/define_libwiredtiger.cmake

## Purpose
`define_libwiredtiger.cmake` centralizes creation of `libwiredtiger` CMake library targets so static and shared variants receive consistent properties, include directories, compile flags, and dependencies.

## Important APIs, Types, And Functions
The macro `define_wiredtiger_library(target type SOURCES ... PUBLIC_INCLUDES ... PRIVATE_INCLUDES ...)` validates arguments, calls `add_library`, attaches includes, applies diagnostic C flags, sets output name/properties, and links system and optional third-party libraries.

## Control Flow
After argument parsing and source validation, the macro defines the target, attaches include paths, applies `COMPILER_DIAGNOSTIC_C_FLAGS`, sets `OUTPUT_NAME` to `wiredtiger`, `NO_SYSTEM_FROM_IMPORTED`, and `C_STANDARD 11`, then links `Threads::Threads`, `${CMAKE_DL_LIBS}`, Linux `rt`, memkind, built-in compressors/encryption, IAA support, accel-config, and key provider as enabled.

## State And Persistence Behavior
The macro creates build-system target state. The output library name is deliberately the same for each flavor, so call sites must avoid conflicting variants in the same output context.

## Dependencies And Integration Points
It integrates with options from `base.cmake`, third-party targets from `cmake/third_party`, and installation in `install.cmake`. It is the main target-definition hook for WiredTiger library builds.

## Risks
Because this is a macro, variables are evaluated in caller scope and naming conflicts are possible. Optional dependency flags must stay aligned with discovery modules and pkg-config private library generation. Multiple targets with the same output name can collide if build directories are not configured correctly.

## Test Signals
Configure shared-only, static-only, built-in extension, memkind, IAA, Linux, and non-Linux builds; verify target link lines and final library names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/define_libwiredtiger.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/gdb_autoloader_setup.cmake -->
# sources/storage-engines/wiredtiger/cmake/gdb_autoloader_setup.cmake

## Purpose
`gdb_autoloader_setup.cmake` installs build-directory GDB helper scripts for Linux shared-library builds.

## Important APIs, Types, And Functions
The function `setup_gdb_autoloader` creates `copy-autoload-script` and `copy-runtime-files` custom targets when `WT_LINUX` and `ENABLE_SHARED` are true.

## Control Flow
On eligible builds, it copies `tools/gdb/load_gdb_scripts.py` to a GDB-recognized name based on `libwiredtiger.so.<version>-gdb.py`, and copies the `tools/gdb/gdb_scripts` directory into the build directory. Otherwise it emits a status message and does nothing.

## State And Persistence Behavior
It creates build artifacts in the binary directory, not installed artifacts. The copied file names must match the shared library version for GDB auto-loading.

## Dependencies And Integration Points
It depends on version variables, `WT_LINUX`, `ENABLE_SHARED`, CMake custom targets, and the source tree's `tools/gdb` directory. It is invoked by the top-level build to improve debugging.

## Risks
The function assumes Linux has GDB and that the shared library versioned filename matches the copied autoload script. Static or non-Linux builds do not get these scripts.

## Test Signals
Configure Linux shared and static builds; verify copy targets exist only for shared Linux and that GDB auto-loads the generated script when loading the built library.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/gdb_autoloader_setup.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/helpers.cmake -->
# sources/storage-engines/wiredtiger/cmake/helpers.cmake

## Purpose
`helpers.cmake` provides shared CMake utility functions for dependency evaluation, cache-backed configuration options, third-party library discovery, filelist parsing, and compile-flag manipulation.

## Important APIs, Types, And Functions
Public helper functions are `eval_dependency`, `config_string`, `config_choice`, `config_bool`, `wt_find_library`, `parse_filelist_source`, `add_cmake_flag`, and `replace_compile_options`.

## Control Flow
`eval_dependency` evaluates dependency expressions. `config_string`, `config_choice`, and `config_bool` parse their mini-DSLs, set/unset cache variables, track disabled states, and optionally fail on unmet dependencies. `wt_find_library` tries `find_package`, pkg-config, then raw library/header search and creates `wt::` aliases. `parse_filelist_source` reads `dist/filelist` style entries and filters by selected architecture/platform groups. The flag helpers append or replace whole flags in cache strings.

## State And Persistence Behavior
Most helpers intentionally write to the CMake cache. Disabled-state variables such as `<name>_DISABLED` preserve transitions across reconfigure. `wt_find_library` writes `HAVE_LIB*` internal cache variables and imported target aliases.

## Dependencies And Integration Points
This file is included by build mode, base config, third-party discovery, and source-list generation scripts. It integrates CMake's parser, package discovery, pkg-config, imported targets, and platform options such as `WT_X86`, `WT_LINUX`, and `WT_WIN`.

## Risks
Dependency strings are evaluated as CMake expressions, so malformed or user-controlled expressions can fail configure. Cache persistence can hide changed defaults unless disabled-state logic is correct. `parse_filelist_source` must stay aligned with filelist group names; unsupported arch/OS combinations can silently omit platform files.

## Test Signals
Configure with dependency-enabled and dependency-disabled options, explicit missing-library requests, package/pkg-config/raw library discovery, source filelist filters for every supported arch/OS, and repeated reconfigure after toggling dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/helpers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/install/install.cmake -->
# sources/storage-engines/wiredtiger/cmake/install/install.cmake

## Purpose
`install.cmake` defines install rules for WiredTiger public headers, library targets, and POSIX pkg-config metadata.

## Important APIs, Types, And Functions
It uses `install(FILES ...)`, builds the `wt_targets` list from `ENABLE_SHARED` and `ENABLE_STATIC`, installs targets to library/archive destinations, computes `PRIVATE_PKG_LIBS`, runs `configure_file` for `wiredtiger.pc.in`, and installs the generated `.pc` file.

## Control Flow
The file always installs generated `wiredtiger.h` and source `wiredtiger_ext.h`. It conditionally appends `wiredtiger_shared` and/or `wiredtiger_static` to install targets. On POSIX builds it composes private library flags for pthread/dl/rt and enabled built-in dependencies, then configures and installs `wiredtiger.pc`.

## State And Persistence Behavior
Install state is expressed in CMake's install graph. `wiredtiger.pc` is generated in the binary directory from current version, install paths, and private dependency flags.

## Dependencies And Integration Points
It depends on `GNUInstallDirs`-style variables, library targets created elsewhere, config flags from `base.cmake`, and `wiredtiger.pc.in`. It integrates with downstream consumers through headers, libraries, and pkg-config.

## Risks
If no library flavor is enabled, `install(TARGETS ${wt_targets})` may be empty or invalid depending on CMake behavior. Private library flags must stay synchronized with `define_libwiredtiger.cmake`; drift can break static/pkg-config consumers.

## Test Signals
Run install for shared-only, static-only, POSIX, Linux, and extension-enabled builds; inspect installed headers, libraries, and `wiredtiger.pc` `Libs.private`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/install/install.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/install/wiredtiger.pc.in -->
# sources/storage-engines/wiredtiger/cmake/install/wiredtiger.pc.in

## Purpose
`wiredtiger.pc.in` is the pkg-config template for installed WiredTiger development metadata.

## Important APIs, Types, And Functions
It defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package name/description, version, linker flags, compiler flags, and `Libs.private`.

## Control Flow
`install.cmake` substitutes CMake install directories, version numbers, and `PRIVATE_PKG_LIBS` using `configure_file(... @ONLY)`.

## State And Persistence Behavior
The generated `wiredtiger.pc` is installed under `${CMAKE_INSTALL_LIBDIR}/pkgconfig` on POSIX builds and is consumed by downstream builds.

## Dependencies And Integration Points
It integrates with pkg-config consumers and the install rules. `Libs.private` is composed from the same optional libraries that libwiredtiger links privately.

## Risks
Incorrect private libs or install directories can break static linking or cross-prefix installs. The empty `Requires:` field means dependency propagation relies on explicit linker flags.

## Test Signals
After install, run `pkg-config --cflags --libs wiredtiger` and `pkg-config --static --libs wiredtiger` for baseline and extension-enabled builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/install/wiredtiger.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/aarch64.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/arch/aarch64.cmake

## Purpose
`aarch64.cmake` applies ARM64-specific compiler options for WiredTiger.

## Important APIs, Types, And Functions
It includes `CheckCCompilerFlag` and `cmake/rcpc_test.cmake`, reads `HAVE_RCPC`, calls `add_compile_options`, checks `-moutline-atomics`, and unsets the temporary cache result.

## Control Flow
If the RCpc compile test succeeds, it adds `-march=armv8.2-a+rcpc+crc`; otherwise it adds `-march=armv8-a+crc`. It then checks compiler support for `-moutline-atomics` and adds it when available.

## State And Persistence Behavior
This file mutates global compile options for the build directory. The `HAVE_RCPC` result can also flow into the generated config header.

## Dependencies And Integration Points
It depends on the RCpc probe and ARM compiler flag support. It is selected by architecture platform setup when `WT_ARCH` is aarch64.

## Risks
Forcing `-march` may conflict with user-provided CPU flags or cross-compiler defaults. `-moutline-atomics` support detection is compiler-version dependent and can affect runtime compatibility/performance.

## Test Signals
Configure native and cross aarch64 builds with and without RCpc support, inspect compile flags, and compile atomic/checksum code paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/aarch64.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/riscv64.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/arch/riscv64.cmake

## Purpose
`riscv64.cmake` sets the baseline RISC-V 64-bit compiler ABI and ISA flags for WiredTiger.

## Important APIs, Types, And Functions
It contains a single `add_compile_options(-march=rv64imafdc -mabi=lp64d)` call.

## Control Flow
There is no branching. All selected riscv64 builds receive the same ISA/ABI options.

## State And Persistence Behavior
It mutates global compile options in the build directory.

## Dependencies And Integration Points
It is selected by architecture platform setup and depends on a compiler accepting `rv64imafdc` and `lp64d`.

## Risks
The hard-coded ISA/ABI may not match every RISC-V target, particularly reduced-extension or different ABI environments.

## Test Signals
Configure and compile with the intended RISC-V toolchain; verify emitted flags and ABI compatibility with linked libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/riscv64.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/s390x.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/arch/s390x.cmake

## Purpose
`s390x.cmake` enables assembly support required for z/Architecture-specific WiredTiger sources.

## Important APIs, Types, And Functions
It calls `enable_language(ASM)`.

## Control Flow
There is no branching; selecting s390x enables CMake's ASM language.

## State And Persistence Behavior
It changes the configured language set for the build directory, allowing assembly sources such as zseries CRC code to compile.

## Dependencies And Integration Points
It integrates with filelist-selected `src/checksum/zseries/crc32le-vx.S` and the active assembler/toolchain.

## Risks
If the assembler is missing or incompatible, configuration or compilation fails. Enabling ASM globally may expose toolchain issues earlier than C-only configurations.

## Test Signals
Configure s390x builds and verify assembly source compilation and checksum tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/arch/s390x.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/darwin.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/os/darwin.cmake

## Purpose
`darwin.cmake` applies macOS-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON`, disables `ENABLE_CPPSUITE`, and adds `${CMAKE_SOURCE_DIR}/oss/apple` as a system include directory.

## Control Flow
There is no branching. macOS builds are treated as POSIX, exclude cppsuite, and include Apple portability headers.

## State And Persistence Behavior
It writes cache values and include-directory state that persist for the build directory.

## Dependencies And Integration Points
It integrates with POSIX feature config, build option dependency evaluation, and portable futex headers under `oss/apple`.

## Risks
Disabling cppsuite here can hide macOS regressions in C++ test coverage. The system include path can mask warnings from portability shims.

## Test Signals
Configure and build on macOS; verify POSIX code paths, futex shim includes, and absence of cppsuite targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/darwin.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/linux.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/os/linux.cmake

## Purpose
`linux.cmake` applies Linux-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON` and adds `_GNU_SOURCE` as a compile definition.

## Control Flow
There is no branching. Linux builds always expose POSIX configuration and GNU/Linux extension APIs.

## State And Persistence Behavior
The file persists `WT_POSIX` in the cache and adds a global compile definition for all targets configured after it.

## Dependencies And Integration Points
It enables Linux feature declarations used by source code, such as `pthread_setname_np`, and drives POSIX dependency options in `base.cmake`.

## Risks
Global `_GNU_SOURCE` can change libc header behavior and should stay consistent across all translation units. Missing it can cause compile failures for GNU extension use.

## Test Signals
Configure Linux builds and verify `_GNU_SOURCE` appears on compile lines and POSIX/Linux feature macros are set in generated config.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/linux.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/netbsd.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/os/netbsd.cmake

## Purpose
`netbsd.cmake` marks NetBSD as a POSIX WiredTiger platform.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON` in the CMake cache.

## Control Flow
There is no branching or additional setup.

## State And Persistence Behavior
The POSIX cache flag persists for the build directory and affects option dependencies and install/pkg-config behavior.

## Dependencies And Integration Points
It integrates with generated POSIX feature macros in `wiredtiger_config.h.in` and general POSIX build paths.

## Risks
The minimal file assumes no NetBSD-specific flags are required. If source code grows platform-specific needs, this file may under-configure the build.

## Test Signals
Configure and build on NetBSD, verifying POSIX feature macros and linked libraries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/netbsd.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/windows.cmake -->
# sources/storage-engines/wiredtiger/cmake/platform/os/windows.cmake

## Purpose
`windows.cmake` applies Windows/MSVC-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX OFF`, forces `SPINLOCK_TYPE=msvc`, enables static and disables shared builds, enables PIC, adds MSVC compile options, constructs `win_link_flags`, and appends them to `CMAKE_EXE_LINKER_FLAGS`.

## Control Flow
There is no branching. All Windows builds receive static-library defaults and MSVC warning/optimization/linker compatibility flags.

## State And Persistence Behavior
It mutates cache values and global compile/link flags. These settings persist in the CMake build directory and influence target creation in `define_libwiredtiger.cmake`.

## Dependencies And Integration Points
It integrates with `base.cmake` Windows CRT selection, spinlock configuration, and generated config headers. The forced static build supports producing a `.lib`; shared DLL production is expected through additional DEF-file handling elsewhere.

## Risks
Forcing shared off can surprise users expecting DLL builds. Flags are MSVC-specific and unsuitable for non-MSVC Windows toolchains unless guarded by upstream platform selection. Global warning suppressions can hide portability issues.

## Test Signals
Configure Windows/MSVC builds; verify static target generation, spinlock macro, runtime library selection, and linker flags `/DYNAMICBASE` and `/NXCOMPAT`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/platform/os/windows.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/rcpc_test.cmake -->
# sources/storage-engines/wiredtiger/cmake/rcpc_test.cmake

## Purpose
`rcpc_test.cmake` probes whether an ARM compiler/target supports RCpc load-acquire instructions.

## Important APIs, Types, And Functions
It includes `CheckCSourceCompiles`, defines `rcpc_test`, sets `CMAKE_REQUIRED_FLAGS` to `-march=armv8.2-a+rcpc+crc`, and calls `check_c_source_compiles` with an inline `ldapr` assembly snippet, setting `HAVE_RCPC`.

## Control Flow
The function-scoped test avoids leaking required flags. It compiles the snippet and treats switch-conflict warnings as failures via `FAIL_REGEX`. After calling the function, it emits a debug message when `HAVE_RCPC` is true.

## State And Persistence Behavior
The probe writes `HAVE_RCPC` into the CMake cache/check state, which architecture setup and generated headers consume.

## Dependencies And Integration Points
It is included by `platform/arch/aarch64.cmake`, which chooses ARM compile options based on the result.

## Risks
Inline assembly syntax and `-march` flag behavior are compiler-specific. User-provided CPU flags can conflict with the probe, which is why failure regex handling matters.

## Test Signals
Configure aarch64 builds with compilers/targets that support and do not support RCpc; verify `HAVE_RCPC` and selected `-march` flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/rcpc_test.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/cl_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/cl_strict.cmake

## Purpose
`cl_strict.cmake` selects strict diagnostic flags for MSVC C compilation.

## Important APIs, Types, And Functions
It includes `strict_flags_helpers.cmake`, calls `get_cl_base_flags(cl_flags C)`, and sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
There is no branching beyond helper behavior. The file collects common CL flags and exposes them as the C diagnostic flag list.

## State And Persistence Behavior
It sets a CMake variable consumed later by target definitions, especially `define_wiredtiger_library`.

## Dependencies And Integration Points
It depends on strict flag helper definitions and is selected when strict mode is enabled for MSVC C.

## Risks
Any missing or overly aggressive helper flag affects every strict C target. This file has no local overrides for C-specific suppressions.

## Test Signals
Configure MSVC strict C builds and inspect `COMPILER_DIAGNOSTIC_C_FLAGS` on targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/cl_strict.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clang_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/clang_strict.cmake

## Purpose
`clang_strict.cmake` selects strict diagnostic flags for Clang C compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_clang_base_flags(clang_flags C)`, appends C-specific flags such as `-Weverything`, `-Wjump-misses-init`, `-Wmissing-prototypes`, and several suppressions, then sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
The only conditional disables `-Wunused-function` during code coverage builds because inline functions may not be inlined.

## State And Persistence Behavior
The resulting list is stored in `COMPILER_DIAGNOSTIC_C_FLAGS` for targets configured with strict Clang C diagnostics.

## Dependencies And Integration Points
It is consumed by target definition macros and depends on `CODE_COVERAGE_MEASUREMENT` from `base.cmake`.

## Risks
`-Weverything` is intentionally broad and can break builds when Clang adds new warnings. Suppressions must be maintained as code style or compiler versions change.

## Test Signals
Run Clang strict builds with and without coverage enabled; verify warning flags and successful compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clang_strict.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clangxx_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/clangxx_strict.cmake

## Purpose
`clangxx_strict.cmake` selects strict diagnostic flags for Clang C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_clang_base_flags(clangxx_flags CXX)`, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
There are no local C++-specific additions in this file; helper-provided flags define the behavior.

## State And Persistence Behavior
It sets the CMake variable used by C++ targets that opt into strict diagnostics.

## Dependencies And Integration Points
It is used by the broader strict-mode build setup and depends on helper flag definitions.

## Risks
Because there are no local overrides, all C++ warning policy comes from the shared helper. C++ targets may need future targeted suppressions as Clang evolves.

## Test Signals
Configure Clang C++ strict builds and verify C++ unit/model/cppsuite targets compile with the helper flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clangxx_strict.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clxx_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/clxx_strict.cmake

## Purpose
`clxx_strict.cmake` selects strict diagnostic flags for MSVC C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_cl_base_flags(clxx_flags CXX)`, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
There is no branching and no local C++ flag extension beyond helper output.

## State And Persistence Behavior
The file sets a CMake variable that is consumed by strict C++ target setup.

## Dependencies And Integration Points
It depends on `strict_flags_helpers.cmake` and MSVC C++ target configuration.

## Risks
Shared CL helper changes affect both C and C++ strict behavior. Lack of local overrides may make it hard to handle C++-only warnings without editing helpers.

## Test Signals
Configure MSVC C++ strict builds and compile C++ tests/tools that consume `COMPILER_DIAGNOSTIC_CXX_FLAGS`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/clxx_strict.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/gcc_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/gcc_strict.cmake

## Purpose
`gcc_strict.cmake` selects strict diagnostic flags for GNU C compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_gnu_base_flags(gcc_flags C)`, appends common and C-specific warnings, conditionally enables `-Wunsafe-loop-optimizations` for GCC 4.7, 5, and 6, conditionally suppresses unused inline functions for coverage, and sets `COMPILER_DIAGNOSTIC_C_FLAGS`.

## Control Flow
Compiler-version checks gate the noisy unsafe-loop warning. Coverage builds add `-Wno-unused-function`.

## State And Persistence Behavior
The resulting flag list is stored in a CMake variable and applied by target definitions.

## Dependencies And Integration Points
It depends on `CMAKE_C_COMPILER_VERSION`, `CODE_COVERAGE_MEASUREMENT`, and helper-provided GNU base flags. It feeds the library and executable target compile options.

## Risks
Version comparisons use exact major/minor forms and may not catch all older GCC variants. Aggressive warning flags can break builds when code or compiler diagnostics change.

## Test Signals
Compile strict GNU C builds across supported GCC versions and coverage mode; verify expected warning set and no unexpected warning failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/gcc_strict.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/gxx_strict.cmake -->
# sources/storage-engines/wiredtiger/cmake/strict/gxx_strict.cmake

## Purpose
`gxx_strict.cmake` selects strict diagnostic flags for GNU C++ compilation.

## Important APIs, Types, And Functions
It includes strict helpers, calls `get_gnu_base_flags(gxx_flags CXX)`, optionally appends `-Wno-unused-function` for coverage, and sets `COMPILER_DIAGNOSTIC_CXX_FLAGS`.

## Control Flow
Coverage mode is the only local conditional, suppressing warnings caused by non-inlined inline functions.

## State And Persistence Behavior
It sets the CMake variable consumed by C++ strict target configuration.

## Dependencies And Integration Points
It depends on `CODE_COVERAGE_MEASUREMENT` and shared GNU strict flag helpers. It affects C++ tests, tools, and model components when strict mode is enabled.

## Risks
The helper carries most warning policy, so C++-specific issues require helper or local updates. Coverage suppression may mask unused helper functions beyond the intended inline-function case.

## Test Signals
Configure GNU C++ strict builds with and without coverage; compile C++ targets and inspect resulting warning flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/cmake/strict/gxx_strict.cmake -->
