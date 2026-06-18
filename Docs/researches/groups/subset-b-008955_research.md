# Research Group: subset-b-008955

This grouped report covers WiredTiger benchmark and workgen files from `bench/workgen`, `bench/wtperf`, and `bench/wt2853_perf`. Each source section is wrapped with reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen.cpp -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen.cpp

## Purpose
`workgen.cpp` implements the C++ runtime behind WiredTiger's Python/SWIG workgen benchmark API. It turns Python-facing `Context`, `Table`, `Operation`, `Thread`, `Transaction`, and `Workload` objects into live WiredTiger sessions, cursors, worker threads, optional monitor output, timestamp advancement, background compaction, and dynamic table create/drop activity.

## Important APIs, Types, and Functions
The main public behavior is implemented through methods declared in `workgen.h` and internal types from `workgen_int.h`. `Workload::run` creates a `WorkloadRunner`; `WorkloadRunner::run` validates options, opens report output, initializes RNG state, calls `create_all`, `open_all`, `ThreadRunner::cross_check`, and `run_all`. `ThreadRunner::create_all`, `open_all`, `run`, `op_run_setup`, `op_kv_gen`, and `op_run` are the operation execution core. `Operation::init_internal` maps operation types to internal strategy objects such as `CheckpointOperationInternal`, `TableOperationInternal`, `SleepOperationInternal`, `RTSOperationInternal`, and `VerifyOperationInternal`. `Track`, `Stats`, `Monitor`, and `Throttle` implement statistics, latency histograms, sampled reporting, and per-thread throttling.

## Control Flow
Workload setup assigns thread names, connects each `ThreadRunner` to shared context/runtime state, opens a WiredTiger session per runner, computes key/value buffer sizes, and opens static table cursors indexed by table integer (`tint`). `run_all` registers signal handlers, starts worker pthreads, then conditionally starts monitor, timestamp, idle-table-cycle, dynamic table create, dynamic table drop, and background compaction activity. Worker threads loop over their root operation until `run_time` ends or stop is requested. `op_run_setup` throttles, resolves dynamic random-table selection when needed, generates keys/values, and delegates to `op_run`. `op_run` selects a stat track, opens or reuses cursors, applies transaction semantics, performs WiredTiger cursor/session/connection operations, handles `WT_ROLLBACK`, updates latency counters, recursively runs operation groups, and closes per-operation cursors.

## State and Persistence Behavior
Persistent benchmark side effects include WiredTiger tables, dynamically created tables tagged in `app_metadata`, mirror-table metadata, report files under the WT home, monitor JSON, and latency/sample data. Runtime-only state includes static table maps, dynamic table maps, max record numbers, `_pending_delete`, `_in_use`, per-thread table assignments, and timestamp mutex state. Dynamic table recovery is metadata-driven: `ContextInternal::create_all` scans `metadata:` for `workgen_dynamic_table=true`, reconstructs mirror/base relationships, and drops leftover tables whose mirror is missing. Record number allocation uses atomic counters and is intentionally approximate under races; reads may observe not-found keys and record that separately.

## Dependencies and Integration Points
The file depends on WiredTiger public APIs (`WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`) plus test/internal utilities exposed through `workgen_func.c` and `test_util.h`. It uses POSIX pthreads, `std::filesystem`, C++ streams, and `workgen_time.h` time helpers. It integrates with Python through SWIG-exposed classes in `workgen.h`, with workgen runner scripts, and conceptually overlaps wtperf's idle-table-cycle benchmark behavior.

## Risks and Edge Cases
Only one `Context` is supported; attempts to create more throw. Dynamic table handling relies on shared locks plus atomics, but there are deliberate races around max recno visibility and table selection. `op_run` assumes random-table operations selected a valid table before decrementing `_in_use`; error paths around dynamic table cursor open or mirror groups can be sensitive. `Track::min_latency` starts at zero, so interval minimum behavior can under-report until populated. `Stats::subtract` subtracts `other.truncate` from `rts`, which looks like a likely copy/paste defect. `WorkloadOptions` copy constructor omits many newer fields, so copying workloads can silently reset dynamic-table and timestamp options. `VerifyOperationInternal::run` opens a new session but does not close it before returning. Signal state and `stop_timestamp_thread` are static process state and can affect repeated runs in one process.

## Test Signals
Useful signals are workgen Python runner workloads, SWIG import tests, wtperf translation tests via `wtperf.py`, dynamic table/mirror restart tests that inspect metadata recovery, and workloads using `sample_interval_ms` to validate monitor CSV/JSON output. Stress should include rollback-heavy transactions, mirrored dynamic tables, create/drop under checkpoint, timestamp lag options, and copy-construction of workloads/options.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen.h -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen.h

## Purpose
`workgen.h` is the public C++ header for the workgen benchmark API and the contract exposed to Python by SWIG. It defines the user-visible model for creating tables, operations, threads, transactions, workloads, and for reading benchmark statistics.

## Important APIs, Types, and Functions
Key exported types are `OptionsList`, `Track`, `Stats`, `Context`, `TableOptions`, `Table`, `ParetoOptions`, `Key`, `Value`, `Operation`, `ThreadOptions`, `ThreadListWrapper`, `Thread`, `Transaction`, `WorkloadOptions`, and `Workload`. `Operation::OpType` covers checkpoint, insert, log flush, none/noop, remove, search, sleep, update, rollback-to-stable, and verify. Constructors encode common operation shapes: table-key-value operations, table-key operations, table-only operations, random-table operations, and config-string internal operations. `Workload::run(WT_CONNECTION *)` is the public execution entry point.

## Control Flow
Python scripts create `Context`, `Table`, `Operation`, and `Thread` objects, compose threads through SWIG-side operators backed by `ThreadListWrapper`, then construct `Workload` and call `run`. During execution, the private pointers declared here (`ContextInternal`, `TableInternal`, `OperationInternal`) are populated by `workgen.cpp` and drive actual WiredTiger calls. `Track` and `Stats` are both public data containers and runtime aggregation objects.

## State and Persistence Behavior
The public objects intentionally carry a mix of declarative and runtime state. `Table` has stable URI/options plus an internal table-id pointer. `Operation` can own config, key/value/table descriptions, transaction pointer, group pointer, dynamic table assignment vector, timing/repeat settings, and random-table behavior. `WorkloadOptions` includes persistent output names (`report_file`, `sample_file`) and runtime controls for timestamps, dynamic table creation/deletion, mirrored tables, background compaction, and latency sampling.

## Dependencies and Integration Points
The header is intentionally light: C++ STL containers and forward declarations keep it usable by SWIG. It integrates with `workgen.cpp` for implementation, `workgen_int.h` for private runtime state, WiredTiger through the `WT_CONNECTION *` parameter, and Python runner/helper code that relies on stable field names.

## Risks and Edge Cases
Because SWIG exposes fields directly, renaming or changing field types is API-breaking for benchmark scripts. Ownership is split: Python manages operation groups and transactions, while C++ manages internal pointers, so shallow copies are deliberate but risky. The header prevents assignment for `Track`/`Stats` except explicit methods, but many other copy operations preserve runtime pointers or internal IDs. Options must remain synchronized with `workgen.cpp` constructors and SWIG typemaps.

## Test Signals
SWIG build/import tests, Python examples in `bench/workgen/runner`, and workload composition tests are primary signals. API compatibility tests should instantiate every constructor shape, inspect help text, copy objects, and run a minimal workload against a temporary WiredTiger home.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen/__init__.py -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen/__init__.py

## Purpose
This package initializer makes the generated workgen extension modules look like one Python namespace. It appends the package directory to `sys.path`, imports `workgen` and `workgen_util`, and copies symbols from imported module objects into the package module.

## Important APIs, Types, and Functions
There are no declared functions or classes. The important state is `me = sys.modules[__name__]`, followed by dynamic `setattr(me, name, value)` for every symbol found in each imported module.

## Control Flow
On import, Python executes the file once, mutates `sys.path`, imports SWIG-generated support modules, iterates over `workgen`, then re-exports each discovered attribute into the package namespace. Runner scripts can then use `from workgen import *` without knowing the generated module layout.

## State and Persistence Behavior
The file mutates process-global import state by appending the package directory to `sys.path`. It also mutates the package module object. No filesystem state is persisted.

## Dependencies and Integration Points
It depends on generated modules named `workgen` and `workgen_util` being importable from the package directory. It is consumed by workgen runner scripts, `wtperf.py` generated programs, and benchmark examples that import `Context`, `Table`, `Operation`, and other SWIG-visible names.

## Risks and Edge Cases
The loop `for module in workgen:` assumes the imported `workgen` object is iterable or list-like; if SWIG generation changes to a normal module, import will fail. Appending to `sys.path` can alter import resolution for later imports. Wild re-export can overwrite package attributes and makes static analysis weak.

## Test Signals
A minimal `python -c 'import workgen; from workgen import Context, Operation'` from the built tree is the key signal. Tests should run under Python 3 and from a current working directory outside the package to catch path assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_func.c -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen_func.c

## Purpose
`workgen_func.c` is a C bridge that lets C++ workgen code call selected WiredTiger internal helper functions without including broad internal headers directly in C++. It wraps atomics, clocks, epoch time, random state, zero-filled number formatting, and version string construction.

## Important APIs, Types, and Functions
The file defines the opaque `workgen_random_state` around `WT_RAND_STATE` and exports `workgen_atomic_add32`, `workgen_atomic_add64`, `workgen_atomic_sub32`, `workgen_clock`, `workgen_epoch`, `workgen_random`, `workgen_random_alloc`, `workgen_random_free`, `workgen_u64_to_string_zf`, and `workgen_version`. It also declares `WT_PROCESS __wt_process` so workgen links in cases where WiredTiger's common symbol is otherwise unresolved.

## Control Flow
Callers allocate RNG state with a `WT_SESSION`, use it repeatedly through `workgen_random`, then free it. Time and atomic wrappers delegate directly to `__wt_*` primitives. `workgen_version` writes `workgen-` plus `WIREDTIGER_VERSION_STRING` into a caller-provided buffer.

## State and Persistence Behavior
The only owned heap state is the RNG wrapper allocated by `malloc` and released by `free`. The random seed/state is initialized from a WiredTiger session implementation. No files are persisted.

## Dependencies and Integration Points
It depends on `wiredtiger.h`, `test_util.h`, and WiredTiger internal functions/macros such as `__wt_atomic_add_uint32`, `__wt_clock`, `__wt_epoch`, `__wt_random_init`, and `u64_to_string_zf`. `workgen.cpp` and `workgen_int.h` consume these wrappers through `workgen_func.h`.

## Risks and Edge Cases
The file casts public `WT_SESSION *` to `WT_SESSION_IMPL *`, so it is tightly coupled to WiredTiger internals. `workgen_version` uses `strncpy` in a way that may not null-terminate when the destination is very small. RNG allocation failure returns `ENOMEM`, so callers must not use an uninitialized state.

## Test Signals
Build/link tests are important because this bridge exists largely to satisfy linkage and C/C++ compatibility. Runtime smoke can allocate random state from a session, generate values, format a key string, and confirm version prefix output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_func.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_func.h -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen_func.h

## Purpose
`workgen_func.h` declares the C bridge functions used by workgen C++ code to access WiredTiger internal utilities safely across the C/C++ boundary.

## Important APIs, Types, and Functions
It forward-declares `struct workgen_random_state` and declares wrappers for 32/64-bit atomics, monotonic clock, epoch time, random allocation/use/free, zero-filled uint64 formatting, and version formatting.

## Control Flow
Consumers include this header under `extern "C"` from C++ internal headers, then call the functions implemented in `workgen_func.c`. The RNG lifecycle is explicit: allocate with a `WT_SESSION`, use, free.

## State and Persistence Behavior
The header defines no state. It exposes an opaque handle so callers cannot depend on `WT_RAND_STATE` layout directly.

## Dependencies and Integration Points
The declarations require WiredTiger types, particularly `WT_SESSION`, to be visible before inclusion. It is included by `workgen_int.h` and implemented by `workgen_func.c`.

## Risks and Edge Cases
Because it is a low-level bridge, signature drift from `workgen_func.c` or missing WiredTiger type declarations will break builds. The opaque random state prevents misuse but also requires strict lifecycle discipline.

## Test Signals
Compile tests covering both C and C++ translation units are the main signal. Link tests should verify every declared wrapper has exactly one implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_func.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_int.h -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen_int.h

## Purpose
`workgen_int.h` declares private runtime structures for workgen. It separates SWIG-visible API declarations from implementation-only execution state such as thread runners, monitors, operation internals, dynamic table runtime, throttling, and timestamp helpers.

## Important APIs, Types, and Functions
Important types include `tint_t`, `WorkgenTimeStamp`, `WorkgenException`, `Throttle`, `ThreadRunner`, `Monitor`, `TableRuntime`, `ContextInternal`, `OperationInternal` and subclasses, `TableInternal`, and `WorkloadRunner`. `ThreadRunner` owns per-thread session/cursor/RNG/buffer/stat state. `WorkloadRunner` owns the run-level thread vector, report stream, WT home path, start time, and stop flag.

## Control Flow
`WorkloadRunner` coordinates setup and execution. `ThreadRunner` methods prepare operations, generate keys/values, run operations, and maintain stats. `OperationInternal` subclasses parse operation config and implement non-table operations. `Monitor` periodically formats sampled stats. `Throttle` sleeps to enforce per-thread operation rates. `WorkgenTimeStamp` generates monotonic microsecond timestamps and sleeps fractional seconds.

## State and Persistence Behavior
Most state is runtime-only. `ContextInternal` maps URI strings to table IDs for static and dynamic tables, stores max record numbers, dynamic table in-use/delete flags, and mutexes. `TableRuntime` records mirror relationships that correspond to persisted table metadata created by `workgen.cpp`.

## Dependencies and Integration Points
The header depends on pthread-compatible types through implementation includes, WiredTiger C wrappers from `workgen_func.h`, time helpers from `workgen_time.h`, STL containers, and C math/unistd. It is the private contract between `workgen.cpp`, `workgen.h`, and C wrapper functions.

## Risks and Edge Cases
The private API exposes many raw pointers and manual ownership rules. `WorkgenTimeStamp::get_timestamp` is thread-local monotonic, so timestamps are monotonic per thread, not globally unless protected by external mutex use. `ContextInternal` has explicit single-context assumptions. Dynamic-table structures require correct shared-mutex discipline and atomic counter updates.

## Test Signals
Coverage should come through workgen runtime tests: multi-thread workloads, throttled workloads, timestamped transactions, dynamic table create/drop, mirrored table operations, and monitor sampling. Static analysis is useful for raw pointer ownership and lock discipline.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_time.h -->
# sources/storage-engines/wiredtiger/bench/workgen/workgen_time.h

## Purpose
`workgen_time.h` provides inline time conversion macros and `timespec` operators used by workgen scheduling, throttling, monitoring, and reporting.

## Important APIs, Types, and Functions
It defines constants for thousand/million/billion, nanosecond/microsecond/millisecond/second conversion macros, `operator<<`, `operator-`, `operator+`, comparison operators, `operator+=`, `operator-=`, `ts_add_ms`, `ts_assign`, `ts_clear`, `ts_sec`, `ts_ms`, `ts_us`, and `secs_us`.

## Control Flow
The helpers normalize common arithmetic on `timespec`: subtract with nanosecond borrow, add whole seconds, add milliseconds with carry, compare by seconds then nanoseconds, and convert to scalar durations. Workgen uses these functions to compute run deadlines, report intervals, throttle divisions, synchronized sleep deadlines, and elapsed times.

## State and Persistence Behavior
The file has no state and performs no persistence. All behavior is inline computation on caller-provided values.

## Dependencies and Integration Points
It requires `timespec` and C++ streams to be visible in the including translation unit. It is included by `workgen_int.h` and indirectly used throughout `workgen.cpp`.

## Risks and Edge Cases
The conversion macros do not guard overflow. `ts_add_ms` loops while `tv_nsec > NSEC_PER_SEC`; equality to exactly `NSEC_PER_SEC` is not normalized, which can leave an invalid `timespec` boundary value. `operator+(timespec,int)` only handles whole seconds. `secs_us(double)` truncates fractional microseconds through `uint64_t` return conversion.

## Test Signals
Unit tests should exercise subtraction borrow, millisecond carry including exact one-second boundaries, comparisons, zero handling, and fractional second conversion. Throttle and synchronized sleep tests indirectly validate the helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/workgen_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/wtperf.py -->
# sources/storage-engines/wiredtiger/bench/workgen/wtperf.py

## Purpose
`wtperf.py` is a partial translator and runner for `.wtperf` configuration files. It emits Python source using the workgen API, optionally prints that source, or executes it to emulate selected wtperf workloads through workgen.

## Important APIs, Types, and Functions
`Translator` owns parsing and translation. Important methods include `set_opt`, typed getters, `split_assign`, `split_config_parens`, `translate_table_create`, `translate_populate`, `parse_threads`, `calc_throttle`, and `translate_inner`. `OptionValue` tracks filename/line for diagnostics, `TranslateException` controls fatal parse exits, and the script-level loop handles `--python`, `--verbose`, `--pydebug`, and `.wtperf` arguments.

## Control Flow
The translator reads a config file, strips comments, parses `key=value`, forwards directly supported workload options, stores other supported options, validates combinations, and builds a Python program string. Generated code opens WiredTiger via workgen context helpers, creates tables, optionally populates data, builds thread operations, runs workload, writes latency output, closes the connection, and copies the original config plus generated `RUN.py` into `WT_TEST` after execution.

## State and Persistence Behavior
The script persists generated runtime artifacts under `WT_TEST`: `CONFIG.wtperf` and `RUN.py`. During normal execution it creates a temporary Python file, runs it, then removes it. It mutates translator state (`opts_map`, `opts_used`, `options`) while parsing.

## Dependencies and Integration Points
It depends on Python standard libraries plus built workgen, wiredtiger Python bindings, and the `bench/workgen/runner` package. It consumes `.wtperf` files used by benchmark suites and is an integration bridge between wtperf-style configs and workgen execution.

## Risks and Edge Cases
It supports only a known subset of wtperf options and intentionally errors on unknown options. Some generated strings are built by concatenation, so unusual quoting in config values can break generated Python. `split_assign` references `line` in an error path where it is not in scope. The `readonly` branch under `reopen_connection` contains a bare string expression instead of appending to `conn_config`, so readonly reopen appears ineffective. Divisibility requirements for multi-table population are strict and fatal.

## Test Signals
Useful tests include `--python` golden output for representative configs, execution of small `.wtperf` files, unsupported-option diagnostics with file/line numbers, multi-table/range partition validation, populate transaction behavior, checkpoint thread generation, and translated latency file production.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/wtperf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/bench/wt2853_perf/CMakeLists.txt

## Purpose
This CMake file wires the WT-2853 performance regression test into the WiredTiger build.

## Important APIs, Types, and Functions
It checks `WT_POSIX` and returns early on non-POSIX systems. On supported platforms it calls `create_test_executable(test_wt2853_perf SOURCES main.c)`.

## Control Flow
Configure-time logic skips the target on Windows/non-POSIX builds. Otherwise, the test executable is compiled from `main.c` using repository CMake helper macros.

## State and Persistence Behavior
No runtime state is managed here. It affects generated build files and whether the test binary exists.

## Dependencies and Integration Points
It depends on the repository's CMake helper `create_test_executable`, POSIX support, and `main.c`. The companion `smoke.sh` expects the resulting binary name `test_wt2853_perf`.

## Risks and Edge Cases
The early return means CI coverage is platform-dependent. If helper macro behavior or binary naming changes, `smoke.sh` can drift from the build target.

## Test Signals
CMake configure/build on POSIX should produce `test_wt2853_perf`; non-POSIX configure should skip it without error. `smoke.sh` validates row and column table modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/main.c -->
# sources/storage-engines/wiredtiger/bench/wt2853_perf/main.c

## Purpose
`main.c` is a standalone WT-2853 performance regression workload. It creates a table with multiple indices, runs concurrent insert/update and read/index traversal threads, detects long progress gaps, and writes a small performance JSON summary.

## Important APIs, Types, and Functions
Important types are `SHARED_OPTS` for index URIs and row/column mode and `THREAD_ARGS` for per-thread arguments and counters. Key functions are `main`, `thread_insert`, `thread_get`, and `create_perf_json`. Constants define record counts, insert count, thread counts, gap warning threshold, and 1KB payload.

## Control Flow
`main` parses test options, recreates the home, opens WiredTiger with statistics logging, creates the table and `post`, `bal`, and `flag` indices, inserts one seed row, starts insert and get threads, waits for inserts, signals readers to stop, prints counts/warnings, writes JSON, and cleans up. Insert threads repeatedly choose random keys, begin a transaction, set indexed values, insert/update rows, handle `WT_ROLLBACK`, commit, and report elapsed gaps. Get threads repeatedly begin a transaction, search the `post` index, walk matching entries, validate invariants against both index and primary table reads, reset cursors, rollback, and record long gaps.

## State and Persistence Behavior
The test persists a WiredTiger home during execution, statistics logs through WT config, and `wt2853_perf.json` with metrics for cursor joins and gap warnings. Table/index contents are temporary and cleaned by `testutil_cleanup`.

## Dependencies and Integration Points
It uses `test_util.h`, WiredTiger sessions/cursors/transactions, pthreads, and WiredTiger internal random/time helpers. It is built by the local CMake file and exercised by `smoke.sh` in row and column-store modes.

## Risks and Edge Cases
The test is performance-sensitive and explicitly allows gap warnings on slow hosts. `done` is a plain int shared between threads without atomic/locking, which is typical for this test but data-racy in strict terms. It treats insert conflicts as acceptable rollback, but other errors assert. Runtime is sizable (`N_INSERT` is one million), so smoke execution can be expensive.

## Test Signals
Primary signals are successful completion, nonzero cursor join count, low or zero gap warnings, and valid `wt2853_perf.json`. Running both `-t r` and `-t c` covers row and column table key paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/smoke.sh -->
# sources/storage-engines/wiredtiger/bench/wt2853_perf/smoke.sh

## Purpose
`smoke.sh` runs the WT-2853 performance test binary in both row-store and column-store modes as part of check-style test runs.

## Important APIs, Types, and Functions
The script has no functions. It resolves `test_bin` from the first argument or from `${binary_dir:-dirname $0}/test_wt2853_perf`, then invokes `$TEST_WRAPPER $test_bin -t r` and `$TEST_WRAPPER $test_bin -t c`.

## Control Flow
`set -e` makes either test failure abort the script. The optional argument path supports direct invocation with a custom binary. The default path supports CMake syncing the script into a build directory.

## State and Persistence Behavior
The script itself persists no state. The invoked binary creates and cleans its WiredTiger test home and writes its performance JSON.

## Dependencies and Integration Points
It depends on `test_wt2853_perf` and optional `TEST_WRAPPER`. It is coupled to the binary name generated by the CMake file and to `testutil_parse_opts` supporting `-t r`/`-t c`.

## Risks and Edge Cases
If `TEST_WRAPPER` is unset, the command still works in POSIX shells because it expands to empty. If the script is not run from a synced build directory and no argument is supplied, binary lookup can fail.

## Test Signals
Exit status is the signal. Successful row and column invocations validate both table types.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wt2853_perf/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/bench/wtperf/CMakeLists.txt

## Purpose
This CMake file builds the `wtperf` benchmark executable and registers a small-btree smoke variant for CTest/check.

## Important APIs, Types, and Functions
It constructs `wt_perf_flags` based on enabled compression libraries, passing compile definitions for Snappy, LZ4, Zlib, and Zstd extension paths. It calls `create_test_executable(wtperf SOURCES ...)` with wtperf implementation files and `define_test_variants(wtperf ...)` for `small_btree`.

## Control Flow
Configure-time branches append flags when compressor options are enabled. The executable includes config parsing, idle table cycle, misc helpers, tracking, main workload, throttle, and truncate modules. The test variant runs `wtperf -O runners/small-btree.wtperf -o run_time=20`.

## State and Persistence Behavior
No direct runtime state. It controls build graph state, compile flags, and test registration.

## Dependencies and Integration Points
It depends on repository CMake helper macros, compressor build options, all listed C sources, and runner config files. It integrates `wtperf` into CI labels `check` and `wtperf`.

## Risks and Edge Cases
Compile-time extension path definitions must match installed/built extension layout. The smoke variant relies on source directory paths and helper macro quoting. Missing optional compressors should not define stale paths.

## Test Signals
Successful build of `wtperf` and a passing `small_btree` CTest variant are the main signals. Compressor-enabled builds should verify the corresponding flags appear in compile commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/config_opt.h -->
# sources/storage-engines/wiredtiger/bench/wtperf/config_opt.h

## Purpose
`config_opt.h` defines wtperf's configuration option metadata and runtime option struct shape.

## Important APIs, Types, and Functions
It declares `CONFIG_OPT_TYPE` with bool, config-string, int, string, and uint32 types. `CONFIG_OPT` describes one option name, description, default string, type, and struct offset. `CONFIG_QUEUE_ENTRY` stores raw config strings in a tail queue. `CONFIG_OPTS` is generated by including `wtperf_opt_inline.h` under `OPT_DECLARE_STRUCT`, then adds `config_head`.

## Control Flow
`wtperf_config.c` includes this header and re-includes `wtperf_opt_inline.h` under different macros to generate descriptors, defaults, parsing, logging, and usage behavior from one option list.

## State and Persistence Behavior
`CONFIG_OPTS` is the central in-memory configuration state for a wtperf run. The `config_head` queue preserves config strings for later output/logging.

## Dependencies and Integration Points
It depends on queue macros and `wtperf_opt_inline.h`. It is included by wtperf implementation files through `wtperf.h`.

## Risks and Edge Cases
The X-macro pattern requires every option macro mode in `wtperf_opt_inline.h` to stay synchronized. Offset-based parsing is sensitive to type mismatches. Adding a new option without updating all macro modes can cause compile or runtime parsing defects.

## Test Signals
Config parser tests, `wtperf -?` usage output, default config logging, and overrides via `-o`/`-O` validate this header indirectly. Compile failures are common when option macro modes drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/config_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/idle_table_cycle.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/idle_table_cycle.c

## Purpose
`idle_table_cycle.c` implements wtperf's optional helper thread that repeatedly creates, opens, closes, and drops idle tables while measuring whether those metadata operations exceed a configured threshold.

## Important APIs, Types, and Functions
Key functions are `check_timing`, `cycle_idle_tables`, `start_idle_table_cycle`, and `stop_idle_table_cycle`. It uses `WTPERF`, `CONFIG_OPTS`, `WT_SESSION`, `WT_CURSOR`, `wt_thread_t`, and `lprintf`.

## Control Flow
`start_idle_table_cycle` returns immediately when `max_idle_table_cycle` is zero. Otherwise it sets `idle_cycle_run`, creates a thread, and stores its ID. The worker opens a session, then while enabled sleeps one second, creates a new derived table URI, times create, opens/closes a cursor, times cursor open/close, drops with `force,checkpoint_wait=false` retrying `EBUSY`, and times drop. `stop_idle_table_cycle` clears the run flag and joins the thread.

## State and Persistence Behavior
The thread creates transient WiredTiger tables using `wtperf->uris[0]` as a prefix and drops them before the next cycle completes. Runtime state includes `wtperf->idle_cycle_run` and `wtperf->error`. Logs are emitted through wtperf logging.

## Dependencies and Integration Points
It depends on `wtperf.h`, WiredTiger sessions/cursors, `__wt_clock`, `WT_CLOCKDIFF_SEC`, `__wt_sleep`, thread helpers, and wtperf config fields. It mirrors similar behavior in workgen's idle table cycle.

## Risks and Edge Cases
The worker returns without closing the session on many error paths. It retries `EBUSY` on drop indefinitely until success or process shutdown. Performance thresholds can false-positive on slow or overloaded hosts. The URI buffer assumes generated names fit.

## Test Signals
Set `max_idle_table_cycle` in a wtperf config and verify no threshold warnings under normal load, errors when threshold is intentionally tiny/fatal, and clean thread shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/idle_table_cycle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/get_ckpt.py -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/get_ckpt.py

## Purpose
`get_ckpt.py` converts checkpoint messages from wtperf output into simple comma-separated time/state data suitable for plotting checkpoint activity.

## Important APIs, Types, and Functions
It has no functions. It reads stdin, tracks cumulative `time`, and prints `time,state` pairs. Lines ending in `secs` advance time; lines starting with `Finished checkpoint` emit start and stop points.

## Control Flow
The script starts with `0,0`. For each input line, if the stripped line ends with `secs`, it adds field 8 (`split(' ')[7]`) to cumulative seconds. If a checkpoint completion line appears, it converts field 4 milliseconds to seconds with rounding, prints `(time-duration,1)`, then `(time,0)`.

## State and Persistence Behavior
Only in-memory cumulative time is maintained. Output is written to stdout; callers redirect it to `.ckpt` files.

## Dependencies and Integration Points
It depends on wtperf textual output format used by `wtperf_ckpt.sh`. It uses only Python standard `sys`.

## Risks and Edge Cases
Parsing is positional and fragile: minor output wording changes break field indexes. Python 3 division returns floats, but `%d` formatting truncates/raises depending value type; in current code `(int + 500) / 1000` is a float under Python 3 and `%d` expects integer-like, so this path may need `//` for strict Python 3 compatibility.

## Test Signals
Feed representative wtperf checkpoint logs and verify generated on/off intervals. Include Python 3 execution in CI because the shebang uses `python`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/get_ckpt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/update-btree.json -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/update-btree.json

## Purpose
This JSON file defines three wtperf runner variants for update-btree-style workloads, each emphasizing a different operation by throttling the others.

## Important APIs, Types, and Functions
The file is an array of objects. Each object has `arguments`, a list containing a `-o threads=...` override, and `operations`, a list of metric names expected from the run.

## Control Flow
A runner harness reads each object, invokes wtperf with the listed thread override, and records the named operations. The first case leaves reads unthrottled and records read/load; the second leaves updates unthrottled; the third leaves inserts unthrottled.

## State and Persistence Behavior
No state is modified by the file itself. It defines benchmark matrix metadata consumed by external scripts.

## Dependencies and Integration Points
It depends on wtperf accepting `-o threads=((...))` syntax and on the runner interpreting `operations` names such as `read`, `load`, `update`, and `insert`.

## Risks and Edge Cases
JSON is valid but shell-like argument strings require the consuming harness to preserve quoting. Operation names must match downstream parser expectations. Thread counts and throttle values are benchmark policy and can become stale as hardware changes.

## Test Signals
Run the consuming wtperf runner over this file and verify all three cases execute and produce the requested metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/update-btree.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/update-checkpoint.json -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/update-checkpoint.json

## Purpose
This JSON file defines update/checkpoint benchmark variants analogous to `update-btree.json`, but with one insert thread in each thread mix, likely to pair update-heavy workloads with checkpoint-sensitive profiles.

## Important APIs, Types, and Functions
The schema is an array of objects with `arguments` and `operations`. Each argument is a wtperf `-o threads=...` override. Operation metric groups are `read`/`load`, `update`, and `insert`.

## Control Flow
An external runner iterates entries, passes the override to wtperf, and extracts requested metrics. Throttles shift the performance focus between reads, updates, and inserts.

## State and Persistence Behavior
The file has no direct runtime state. It configures benchmark invocations and expected metric extraction.

## Dependencies and Integration Points
It depends on wtperf option parsing and runner harness JSON support. It is part of the `bench/wtperf/runners` workload catalog.

## Risks and Edge Cases
As with other runner JSON, argument quoting and metric-name compatibility are the main fragility. The lower insert thread count compared with `update-btree.json` is intentional benchmark policy but should be documented in consuming dashboards to avoid miscomparison.

## Test Signals
Execute all entries through the benchmark harness and confirm metric files contain read/load, update, and insert outputs as declared.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/update-checkpoint.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_ckpt.sh -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_ckpt.sh

## Purpose
`wtperf_ckpt.sh` automates wtperf checkpoint performance analysis. It can create/reuse a populated database, run checkpoint workloads, collect stack traces with `pmp`, and post-process result files into operation and checkpoint timelines.

## Important APIs, Types, and Functions
The script has option parsing for binary dir, root dir, optfile, debug/gdb, reuse, short run, verbose, and workload mode. Key variables are `WTPERF`, `DB_HOME`, `OUT_DIR`, `SHARED_OPTS`, `CREATE_OPTS`, and `RUN_OPTS`.

## Control Flow
It validates the wtperf binary, optionally creates a reusable database and tarball, creates a results directory, runs one checkpoint configuration, optionally samples `pmp` output every second while wtperf runs, copies `test.stat`, then extracts per-second read/insert/update lines and checkpoint on/off data using `get_ckpt.py`.

## State and Persistence Behavior
It deletes and recreates `WT_TEST`, `WT_TEST.tgz`, and `results`. It writes `.trace`, `.res`, `.out`, and `.ckpt` files. In reuse mode it restores database state from the tarball.

## Dependencies and Integration Points
It depends on local `wtperf`, `tar`, `pmp`, shell utilities, optional `gdb`, and companion `get_ckpt.py`. It assumes wtperf output format and `test.stat` naming.

## Risks and Edge Cases
The script is destructive to `WT_TEST` and `results` under `ROOT_DIR`. Some options concatenate without spaces (`-O$OPTARG`) and rely on wtperf parsing. `VERBOSE` is set to `0` even for `-v`, likely a bug. `pmp` may be unavailable. Result names are sanitized but still derived from option text.

## Test Signals
Run short mode (`-s`) against a built wtperf and verify `results` contains trace/res/out/ckpt artifacts. Reuse mode should avoid repopulation and still run workload successfully.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_ckpt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_run.sh -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_run.sh

## Purpose
`wtperf_run.sh` runs a wtperf benchmark repeatedly on Jenkins, filters out min/max outliers, averages remaining metrics, and writes normalized results to `wtperf.out`.

## Important APIs, Types, and Functions
Shell functions `getval` and `isstable` compute min/max and 3% stability. Arrays track `avg`, `max`, `min`, `sum`, current metrics, operation names, and output labels. The script parses required config path and run count plus optional wtperf args and `NOCREATE`.

## Control Flow
For each run, it optionally recreates `WT_TEST`, runs `./wtperf -O <config> <args>` with tcmalloc preload and library path extension, archives selected artifacts with `rsync`, extracts load time and operation counts from `WT_TEST/test.stat`, updates min/max/sum, and after three runs may stop early if all metrics are stable. It then computes averages, optionally subtracting min/max, and appends labeled results to `wtperf.out`.

## State and Persistence Behavior
It deletes/recreates `WT_TEST`, writes `wtperf.out`, and creates timestamped backup directories named from the workload, run number, and epoch. It relies on `test.stat` output from wtperf.

## Dependencies and Integration Points
It depends on bash arrays, `bc`, `expr`, `grep`, `cut`, `rsync`, tcmalloc at `/usr/local/lib/libtcmalloc.so`, local `./wtperf`, and Jenkins/perf dashboard parsers expecting labels such as `Insert count:`.

## Risks and Edge Cases
`if test "$numruns" -eq "0"; then $numruns=1; fi` is invalid assignment and can try to run a command named by the value. The initial `avg/max/min/sum` arrays are sized inconsistently before assigning `loadindex=6`, leaving an unused gap. `LD_PRELOAD` hard-coding can fail on systems without tcmalloc. Arithmetic mixes integer `expr` and floating `bc`. Argument logging prints parsed `$#` after shifting, not original count.

## Test Signals
Run with a small wtperf config and 1-3 iterations, with and without `NOCREATE`, and verify `wtperf.out` labels plus archived artifacts. Shellcheck would catch several assignment/quoting issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_track.sh -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_track.sh

## Purpose
`wtperf_track.sh` records Jenkins wtperf metrics over time and emits warnings when short-term or mid-term trends regress against longer baselines.

## Important APIs, Types, and Functions
Functions include `Usage`, `GetValues`, `MinValues`, `AvgValues`, `CheckValues`, `GetCpuLoadAverage`, and `GetDiskLoadAverage`. Required Jenkins environment variables are `JENKINS_HOME`, `JOB_NAME`, and `BUILD_ID`. Options select time (`-t`, lower better), count (`-c`, higher better), and percent threshold (`-p`).

## Control Flow
The script validates environment and arguments, appends a row to `${STATE_DIR}/${JOB_NAME}.${NAME}.csv`, computes `v3` as best of last 3, `v20` as average best 10 of last 20, and `v100` as average best 50 of last 100. It prints current/baseline values and calls `CheckValues` for short and long trends. Warning output is intended for Jenkins to mark instability; final nonzero exit is disabled.

## State and Persistence Behavior
Persistent state lives in `/home/jenkins/wtperf_track/*.csv`, with columns build id, timestamp, value, load average, and disk average. The file grows indefinitely unless managed externally.

## Dependencies and Integration Points
It depends on Jenkins variables, bash/sh utilities, `bc`, `sort`, `tail`, `cut`, `date`, `uptime`, and `df`. Jenkins job configuration consumes warning text.

## Risks and Edge Cases
The warning message uses `$type` while the global variable is initialized as `TYPE`; later `type=time/count` creates a lowercase variable, which works but is confusing. The usage text has typos. `AvgValues` divides by word count; empty input would fail, though recent appended row usually prevents that. Disk load is stubbed to `0.0`.

## Test Signals
Run in a fake Jenkins environment with temporary `STATE_DIR` after patching or overriding path, append enough values to validate v3/v20/v100 logic, and assert warning behavior for time and count metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_track.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_xray.sh -->
# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_xray.sh

## Purpose
`wtperf_xray.sh` runs a wtperf workload under LLVM XRay instrumentation and produces profiling reports, stack summaries, call graph SVG, and optionally a flame graph.

## Important APIs, Types, and Functions
There are no shell functions. Key variables are `xray_home`, output paths for account/stack/graph/flame files, `XRAY_OPTIONS`, `XRAY_BINARY`, and `FLAME_GRAPH_PATH`.

## Control Flow
The script checks for `./wtperf`, validates arguments, infers the WT home from `-h` if present, verifies the binary has an `xray_instr_map` section, creates the home directory, removes old XRay outputs, runs `./wtperf -O "$@"` with XRay enabled, locates the single `xray-log.wtperf.*`, selects `llvm-xray` or `XRAY_BINARY`, then runs `account`, `stack`, and `graph` subcommands. It pipes graph output through `unflatten` and `dot`; flame graph generation is conditional.

## State and Persistence Behavior
It writes profiling artifacts into the wtperf home: `wtperf_account.txt`, `wtperf_stack.txt`, `wtperf_graph.svg`, and optionally `wtperf_flame.svg`. It also creates/removes `xray-log.wtperf.*` in the current directory.

## Dependencies and Integration Points
It depends on a wtperf binary compiled with `-fxray-instrument`, `objdump`, LLVM XRay tools, Graphviz (`unflatten`, `dot`), optional FlameGraph, and wtperf runner configs. It assumes invocation from the directory containing `wtperf`.

## Risks and Edge Cases
`rm xray-log.wtperf.* ...` without `--` is acceptable but glob behavior can be shell-dependent; errors are redirected. Multiple XRay logs abort. Argument handling `./wtperf -O "$@"` treats the first user argument as the `-O` value and passes the rest, matching usage but sensitive to quoting. Graphviz/llvm tools may be absent.

## Test Signals
Build wtperf with XRay instrumentation, run a short config, and verify all requested output files are non-empty. Also test missing instrumentation and missing `FLAME_GRAPH_PATH` paths for clear diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_xray.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/smoke.sh -->
# sources/storage-engines/wiredtiger/bench/wtperf/smoke.sh

## Purpose
`smoke.sh` provides a minimal manual/check smoke command for wtperf using the small-btree workload.

## Important APIs, Types, and Functions
It has no functions. It invokes `./wtperf -O \`dirname $0\`/runners/small-btree.wtperf -o "run_time=20"`.

## Control Flow
The script resolves the runner config relative to the script path and runs local `./wtperf` for 20 seconds. There is no `set -e`, but the final command exit status becomes the script exit status.

## State and Persistence Behavior
The invoked wtperf process creates its default WT home and output files such as `test.stat`, monitor data, and latency files depending on config defaults.

## Dependencies and Integration Points
It depends on the current directory containing `wtperf`, and the source/build layout containing `runners/small-btree.wtperf` relative to the script.

## Risks and Edge Cases
Running from a directory without `./wtperf` fails. Backtick command substitution and unquoted path can fail for paths with spaces. CMake's registered smoke variant is more robust than this script for build-tree execution.

## Test Signals
A successful zero exit after a 20-second small-btree run is the main signal. Confirm expected wtperf output files appear in the default home.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/track.c -->
# sources/storage-engines/wiredtiger/bench/wtperf/track.c

## Purpose
`track.c` aggregates wtperf operation counts and latency measurements across worker, populate, checkpoint, backup, scan, and flush threads. It also writes latency distribution files for insert, modify, read, and update operations.

## Important APIs, Types, and Functions
Count functions include `sum_pop_ops`, `sum_backup_ops`, `sum_ckpt_ops`, `sum_flush_ops`, `sum_scan_ops`, `sum_insert_ops`, `sum_modify_ops`, `sum_read_ops`, `sum_truncate_ops`, and `sum_update_ops`. Latency functions include `latency_insert`, `latency_modify`, `latency_read`, `latency_update`, `latency_print`, plus static helpers `sum_ops`, `latency_op`, `sum_latency`, and `latency_print_single`.

## Control Flow
Count helpers choose relevant thread arrays and sum `TRACK.ops` fields, often using `offsetof(WTPERF_THREAD, field)` to share logic. `latency_op` computes interval latency by comparing cumulative latency counters against `last_latency*` snapshots, resets min/max for the next interval, and returns average/min/max. Per-operation latency wrappers preserve the last nonzero values to avoid graph discontinuities. `latency_print` builds aggregate latency histograms per operation and writes CSV-like files.

## State and Persistence Behavior
The file mutates `TRACK.last_latency_ops`, `last_latency`, `min_latency`, and `max_latency` while sampling intervals. Static variables inside each latency wrapper remember last displayed values across calls. `latency_print_single` persists files named `latency.insert`, `latency.modify`, `latency.read`, and `latency.update` under `monitor_dir`.

## Dependencies and Integration Points
It depends on `wtperf.h`, `CONFIG_OPTS`, `WTPERF`, `WTPERF_THREAD`, `TRACK`, time conversion macros, and `lprintf`. Monitor/report code in `wtperf.c` calls these helpers to produce periodic metrics and final latency artifacts.

## Risks and Edge Cases
Sampling reads counters concurrently with worker updates; values are approximate by design. Static last latency values are process-global per operation, so multiple wtperf instances in one process would cross-contaminate. `latency_print_single` skips zero buckets and starts millisecond/second loops at 1, so bucket boundary interpretation must match insertion logic. It logs but continues on file-open failure.

## Test Signals
Run workloads with known operation mixes and verify summed counts match `test.stat`. Enable latency tracking, then confirm latency files exist, have headers, monotonic cumulative counts, and plausible total operation counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/wtperf/track.c -->
