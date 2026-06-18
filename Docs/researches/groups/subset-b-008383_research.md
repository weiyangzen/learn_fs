# subset-b-008383 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/mako.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/mako.cpp

## Purpose
`mako.cpp` is the executable driver for FoundationDB's C/C++ Mako benchmark tool. It parses command-line workload configuration, configures the FDB C API, forks worker and statistics processes, runs synchronous or Boost.Asio-based asynchronous workloads, collects shared-memory counters, and prints human-readable and JSON reports. It supports `clean`, `build`, `run`, and `report` modes.

## Important APIs, Types, and Functions
- `ThreadArgs` packages process/thread ids, parent pid, immutable `Arguments`, shared-memory access, and the assigned `fdb::Database`.
- `createNewTransaction`, `setTransactionOptionsIfEnabled`, `cleanupNormalKeyspace`, `populate`, `runOneTransaction`, and `runWorkload` form the transaction execution path.
- `workerThread`, `runAsyncWorkload`, and `workerProcessMain` bridge workload logic to thread/process orchestration.
- `Arguments::Arguments`, `parseArguments`, `parseTransaction`, `Arguments::setGlobalOptions`, `Arguments::validate`, and `usage` define the CLI contract.
- `printStats`, `aggregateWorkerStats`, `maybeCaptureWarmupSnapshot`, `printWorkerStats`, `loadSample`, `printReport`, `statsProcessMain`, and `mergeSketchReport` define reporting and DDSketch merge behavior.

## Control Flow
`main` parses arguments, applies defaults, validates mode-specific invariants, handles report-only merging, creates POSIX shared memory, initializes a `shared_memory::Access` layout, then forks `num_processes` workers plus one stats process. Workers call `workerProcessMain`, select/set up the FDB API, launch one FDB network thread per process, create configured databases, and run either native worker threads or async workflow states. The parent waits for `readycount`, flips the shared `signal` from `SIGNAL_OFF` to `SIGNAL_GREEN`, later flips to `SIGNAL_RED` for timed or completed runs, and waits for children.

In run mode, `runWorkload` throttles per-thread TPS, creates a transaction per iteration, applies timeout/GRV-delay options, optionally tags or traces transactions, and delegates the configured operation sequence to `runOneTransaction`. `runOneTransaction` walks `opTable`, waits on futures, updates error counters, retries through `on_error` paths, commits when needed, and records sampled latency for operations, commits, and whole transactions. Build mode uses `populate` to partition rows across process/thread workers and commit batches.

## State and Persistence Behavior
The file writes no durable application data beyond benchmark operations in the target FDB cluster. It creates transient POSIX shared memory named `mako<pid>`, temp DDSketch files under `/tmp/makoTemp<pid>`, optional JSON reports, and optional exported sketch JSON. Shared-memory state includes signal, readiness, stop counts, throttle factor, worker counters, thread timers, and process timers. Cleanup guards unlink shared memory and remove temp sample directories after report generation.

## Dependencies and Integration Points
It depends on the local C++ wrapper `fdb_api.hpp`, Mako headers (`operations`, `stats`, `shm`, `utils`, `async`, `future`, `admin_server`, `logger`), POSIX `fork`/`mmap`/`shm_open`, Boost.Asio, fmt, RapidJSON, and the FDB client network APIs. It integrates with FoundationDB tracing, TLS, knobs, distributed tracer selection, client bypass/multi-version-client options, transaction timeouts, database-level timeouts, read-your-writes disabling, and transaction tag throttling.

## Risks
The driver has several operational risks: manual shared-memory layout must stay synchronized with `shm.hpp`; process failure paths rely on guards and `_exit`; temporary sketch loading silently skips malformed JSON; `strcpy`/`memcpy` option parsing is bounded mostly by validation and fixed arrays but still sensitive to oversized inputs; optional-argument parsing mutates `optarg`; `goto transaction_begin` and retry handling make transaction state transitions subtle; and async mode has a different worker-count interpretation than synchronous mode. Some JSON report writing is hand-assembled and can break if string fields contain unexpected quotes.

## Test Signals
This file is itself a benchmark/test utility rather than a unit test. Useful signals are successful execution of `mako --mode build`, `--mode run`, `--mode clean`, and `--mode report`; correct nonzero per-op counters; DDSketch export/import round trips; timeout tests for `--transaction_timeout_tx`/`--transaction_timeout_db`; async vs sync runs; and trace/tagging runs that confirm client options are accepted.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/mako.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/mako.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/mako.hpp

## Purpose
`mako.hpp` is the central public configuration header for the Mako benchmark. It defines benchmark modes, CLI option ids, operation ids, workload specification storage, default limits, and the `Arguments` structure shared by parser, worker, and reporting code.

## Important APIs, Types, and Functions
- `MODE_INVALID`, `MODE_CLEAN`, `MODE_BUILD`, `MODE_RUN`, and `MODE_REPORT` define executable behavior.
- `ArgKind` maps long-only command-line options to `getopt_long` values.
- `OpKind` defines operation ids used as indexes in `WorkloadSpec`, `opTable`, and statistics arrays.
- `WorkloadSpec::ops[MAX_OP][3]` stores per-operation count, range, and reverse flags.
- `Arguments` contains all run configuration: FDB API version, concurrency, mode, row/key/value sizing, TPS controls, transaction spec, cluster/database arrays, tracing/TLS/auth fields, JSON/export paths, timeout settings, and GRV queue delay.
- `setTransactionOptionsIfEnabled` applies transaction timeout and max GRV queue delay to an `fdb::Transaction`.

## Control Flow
The header is included by parser, workload, operations, and stats code. `Arguments` is initialized once in the main process, then copied through forked children where it is treated as immutable. `parseArguments` fills fields, `Arguments::validate` enforces cross-field invariants, `Arguments::setGlobalOptions` applies network-level FDB settings before network setup, and worker paths use the values to partition work and build transactions.

## State and Persistence Behavior
The header owns no runtime storage directly, but it defines fixed-size buffers that become process-local state after parsing. The most persistent effect is indirect: fields such as `json_output_path`, `stats_export_path`, `tracepath`, `cluster_files`, and report file arrays control external file or cluster interactions.

## Dependencies and Integration Points
It includes the FDB C++ wrapper `fdb_api.hpp`, POSIX/PThread types, and `limit.hpp` for path sizes. The operation ids are a hard contract with `operations.cpp`, `stats.hpp`, and report formatting.

## Risks
Many fields are plain `int` or fixed char arrays, so parser and validation code must maintain bounds. `MAX_OP` must remain last because arrays and loops depend on it. Adding an operation requires updating this enum, `operations.cpp`, parser strings, stats/report logic, and tests together.

## Test Signals
The best validation is building all Mako translation units and running parser smoke tests across modes, operation specs, timeout options, TLS paths, tracing, and report export. Operation additions should be caught by tests that confirm `MAX_OP`-indexed arrays and `opTable` stay aligned.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/mako.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/operations.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/operations.cpp

## Purpose
`operations.cpp` defines the executable operation table for Mako workloads. Each `OpKind` maps to a display name, one or two steps, a step kind, a callable that performs the C++ FDB operation, an optional post-step result decoder, and a flag indicating whether the operation requires a later commit.

## Important APIs, Types, and Functions
- `opTable` is a `std::array<Operation, MAX_OP>` and is the central dispatch table consumed by `runOneTransaction`.
- Read operations include `GRV`, `GET`, `GETRANGE`, `SGET`, `SGETRANGE`, and `STATUSJSON`.
- Write operations include `UPDATE`, `INSERT`, `INSERTRANGE`, `OVERWRITE`, `CLEAR`, `SETCLEAR`, `CLEARRANGE`, and `SETCLEARRANGE`.
- Abstract entries `COMMIT` and `TRANSACTION` exist for measurement only.

## Control Flow
`runOneTransaction` gets the current `Operation` and invokes `stepFunction(step)`. Immediate writes return an empty `Future`; reads return typed futures erased to a generic `Future`; commit steps call `tx.commit()`. Post-step functions decode futures to force result materialization. Multi-step operations such as `UPDATE`, `SETCLEAR`, and `SETCLEARRANGE` use the first step to read or commit setup state and the second step to mutate using preserved keys.

## State and Persistence Behavior
The table itself is immutable process state. It drives FDB transaction mutations and reads. Some operations mutate the provided reusable key/value buffers. Write operations persist data only if the containing transaction later commits or if their step kind commits immediately.

## Dependencies and Integration Points
It depends on `operations.hpp`, `mako.hpp`, `logger.hpp`, `utils.hpp`, the `fdb` wrapper, and operation ids from `mako.hpp`. Key generation relies on `randomString`, `numericWithFill`, and `KEY_PREFIX`. Range reads use `args.streaming_mode` and transaction spec range/reverse flags.

## Risks
The `opTable` order must match `OpKind` exactly. A visible bug risk is that `SGETRANGE` checks `args.txnspec.ops[OP_GETRANGE][OP_REVERSE]` instead of `OP_SGETRANGE`, which may make snapshot range reverse settings inconsistent. Multi-step writes rely on key buffer preservation across steps and retries. Range insertion uses asserts for positive range rather than runtime errors.

## Test Signals
Transaction-spec tests should cover every operation token, forward/reverse range reads, snapshot reads, multi-step set/clear operations, commit-needed operations, and report stats for abstract commit/transaction rows. A targeted regression should check `sgr` reverse behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/operations.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/operations.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/operations.hpp

## Purpose
`operations.hpp` declares the data model and iterator helpers for Mako's operation dispatch table. It lets the benchmark express a transaction as a sequence of counted operations, each with one or more steps.

## Important APIs, Types, and Functions
- `StepKind` classifies steps as `NONE`, `IMM`, `READ`, `COMMIT`, or `ON_ERROR`.
- `isAbstractOp` identifies stats-only `OP_COMMIT` and `OP_TRANSACTION`.
- `StepFunction` and `PostStepFunction` define operation callback signatures.
- `Step` stores a kind and function pointers.
- `Operation` exposes `name`, `stepKind`, `stepFunction`, `postStepFunction`, `steps`, and `needsCommit`.
- `OpIterator`, `OpEnd`, `getOpBegin`, and `getOpNext` traverse `Arguments::txnspec`.

## Control Flow
`getOpBegin` skips abstract operations and zero-count operations, returning the first concrete step. `getOpNext` first advances within a multi-step operation, then advances the operation count, then scans for the next enabled operation. Consumers stop at `OpEnd`.

## State and Persistence Behavior
The header stores no mutable state. Iteration state is an `OpIterator` value copied through transaction execution. It indirectly controls persistent FDB changes by determining whether write steps are run and whether a commit is required.

## Dependencies and Integration Points
It depends on `fdb_api.hpp`, `mako.hpp`, and the force-inline macro. `opTable` is defined in `operations.cpp`; all stats and parser code rely on the same `MAX_OP`/`OpKind` ordering.

## Risks
The table supports only two steps per operation, so future multi-step operations require structure changes. `getOpNext` assumes valid, non-abstract current iterators and uses asserts, so malformed internal state can crash debug builds. Step function pointers can be null only for abstract rows that should never be executed.

## Test Signals
Unit-level tests can validate iterator sequences for mixed counts and multi-step operations without connecting to FDB. Integration tests should ensure transaction specs execute in declared order and stop exactly at the configured operation counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/operations.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/process.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/process.hpp

## Purpose
`process.hpp` defines the process role enum used by Mako logging and process branching.

## Important APIs, Types, and Functions
- `enum class ProcKind { MAIN, WORKER, STATS, ADMIN }` names the process categories used by the benchmark and admin server components.

## Control Flow
`mako.cpp` initializes `ProcKind::MAIN`, changes children to `WORKER` or `STATS` after fork, and uses the role to choose the worker or stats entry point. Other headers use distinct tag types for logger construction, while this enum represents high-level process identity.

## State and Persistence Behavior
The file has no state or persistence behavior. Runtime state is a simple enum value in each process.

## Dependencies and Integration Points
It is intentionally dependency-free. Its values integrate with process orchestration in `mako.cpp` and conceptually with `admin_server`/logging.

## Risks
The enum is small but central enough that adding a role requires checking every process switch and logger mapping. There is no default behavior encoded here.

## Test Signals
Build coverage and Mako process smoke tests are sufficient. Any new process role should be accompanied by a fork-path or admin-path test.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/process.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/shm.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/shm.hpp

## Purpose
`shm.hpp` defines Mako's shared-memory protocol between the parent, worker processes, worker threads, async workflows, and stats process. It provides a safer accessor around a manually packed POSIX shared-memory buffer.

## Important APIs, Types, and Functions
- `SIGNAL_RED`, `SIGNAL_GREEN`, and `SIGNAL_OFF` coordinate lifecycle.
- `shared_memory::Header` stores atomic signal, ready count, throttle factor, and stop count.
- `storageSize` computes required bytes for header, worker `WorkflowStatistics`, `ThreadStatistics`, and `ProcessStatistics`.
- `shared_memory::Access` wraps base pointer and dimensions, placement-news statistics objects, and exposes array/slot accessors.

## Control Flow
`mako.cpp` creates and maps shared memory, constructs `Access`, calls `initMemory`, then passes the accessor by value into children and threads. Workers increment readiness, check signal state, update stats slots, and increment stop count. The stats process reads arrays and throttle signal; the parent writes lifecycle signals.

## State and Persistence Behavior
All state is transient shared memory. Objects are placement-constructed in a contiguous layout and are never explicitly destroyed before unmapping, which is acceptable for process-local benchmark termination but important because contained vectors in `WorkflowStatistics` are copied into shared memory.

## Dependencies and Integration Points
It depends on `stats.hpp` and atomics. Layout alignment relies on `alignas(64)` in stats classes and on all processes using the same binary ABI. `storageSize` must match `Access` pointer arithmetic exactly.

## Risks
Manual layout arithmetic is fragile. `storageSize` asserts only minimal positive dimensions and does not validate overflow. Objects containing non-trivial members in shared memory are safe after fork in this single-binary model but would not be a general cross-process ABI. Async mode passes `num_workers = async_xacts` while thread timer storage still uses `num_threads`, so callers must supply consistent dimensions.

## Test Signals
Stress runs with multiple processes, multiple threads, and async workflows are the practical tests. Sanitizer or debug builds should verify no slot overruns. Unit tests for `storageSize` and slot address monotonicity would reduce risk.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/shm.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/stats.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/stats.hpp

## Purpose
`stats.hpp` implements Mako's metrics containers: operation counts, conflicts, errors, timeouts, latency DDSketches, JSON serialization, and CPU utilization timers for worker threads, worker processes, and FDB network threads.

## Important APIs, Types, and Functions
- `DDSketchMako` serializes/deserializes `DDSketch<uint64_t>` fields to RapidJSON.
- `WorkflowStatistics` stores per-operation counters, latency sample counts/totals, and sketches. It supports `combine`, increment methods, `addLatency`, warmup `subtractCounters`, file serialization, and sketch replacement.
- `operator<<` and `operator>>` serialize/deserialize full workflow stats.
- `CPUUtilizationTimer`, `ThreadStatistics`, and `ProcessStatistics` measure wall duration and CPU time using `flow/Platform.h` helpers.

## Control Flow
Workers mutate their own `WorkflowStatistics` slots as operations complete. Periodic stats aggregate all worker slots. At final report time, Mako loads per-thread sketch files, merges sketches, updates the aggregate stats with merged latency distributions, and prints percentile/mean/min/max metrics.

## State and Persistence Behavior
`WorkflowStatistics` is mutable in memory and also persists to JSON for exported sketch reports or temp per-op sample files. The warmup subtraction only subtracts counters, not latency sketches, so report text explicitly notes latency still includes warmup.

## Dependencies and Integration Points
It depends on `mako.hpp` for `MAX_OP`, `operations.hpp` for names and abstract op detection, `time.hpp`, `ddsketch.hpp`, RapidJSON, and platform CPU-time helpers. Shared memory embeds these classes in `shm.hpp`.

## Risks
Serialization assumes all expected JSON members exist. `operator>>` deserializes a sketch for every op name, which can fail if exported files omit empty op sketches. `combine` increments `total_errors` and `total_timeouts` by per-op errors while also combining other fields; this is fine for fresh aggregates but repeated combine into a non-fresh target must be intentional. Vectors inside shared-memory objects are process-private allocations after fork and should not be treated as portable shared-memory containers.

## Test Signals
Tests should cover DDSketch serialize/deserialize round trips, combining multiple workers, warmup counter subtraction, percentile reporting after temp-file merge, and report mode merging multiple exported sketch files.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/stats.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/time.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/time.hpp

## Purpose
`time.hpp` provides lightweight chrono aliases and stopwatch utilities for Mako latency, throttling, warmup, and duration reporting.

## Important APIs, Types, and Functions
- `steady_clock`, `timepoint_t`, and `timediff_t` standardize monotonic timing.
- `toDoubleSeconds`, `toIntegerSeconds`, and `toIntegerMicroseconds` convert chrono durations for reports and counters.
- `StartAtCtor` tags immediate-start stopwatch construction.
- `Stopwatch` records start/stop timepoints, supports starting from an existing time, setting stop manually, restarting from stop, and computing `diff`.

## Control Flow
Mako creates stopwatches around whole transactions, individual operations, commits, populate runs, throttling windows, and trace intervals. The stopwatch is intentionally passive: callers must call `stop` or `setStop` before `diff`.

## State and Persistence Behavior
State is two in-process monotonic timepoints. There is no file or cluster persistence.

## Dependencies and Integration Points
It depends only on `<chrono>` and is included by stats and Mako driver code. `WorkflowStatistics::addLatency` converts stopwatch diffs to microseconds through this header.

## Risks
Default-constructed `Stopwatch` has zero-initialized timepoints, so using `diff` before start/stop is a caller bug. Integer conversions truncate fractional units. There is no overflow guard for extremely long durations converted to unsigned integer units.

## Test Signals
Simple unit tests can assert conversion behavior and stopwatch monotonicity. Integration signal comes from nonzero latencies and stable TPS throttling in Mako runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/time.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/utils.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/utils.cpp

## Purpose
`utils.cpp` provides the non-template implementations for Mako utility helpers declared in `utils.hpp`.

## Important APIs, Types, and Functions
- `computeThreadPortion` divides a total value across process/thread partitions, distributing remainders to lower global worker indexes and returning `-1` when the base interval is zero and the current worker receives no portion.
- `digits` returns the decimal digit count for a positive integer-like input.

## Control Flow
`computeThreadPortion` is used through `computeThreadTps` and `computeThreadIters`. Validation in `mako.cpp` tries to ensure per-thread portions are positive for configured throttling/iteration runs. `digits` is used during argument initialization and key formatting.

## State and Persistence Behavior
The file has no mutable global state and no persistence. It performs deterministic arithmetic based on inputs.

## Dependencies and Integration Points
It includes `utils.hpp`, `mako.hpp`, C library headers, and fmt. Its results feed row partitioning, TPS throttling, and iteration limits in the main workload driver.

## Risks
`digits(0)` returns 0, which is acceptable for current callers because `rows` is validated positive, but it is not a general decimal-width helper for zero. `computeThreadPortion` uses integer division and returns `-1` as a sentinel that callers must handle.

## Test Signals
Unit tests should cover exact division, remainder distribution, too-small totals, and digit counts for boundary row values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/utils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/utils.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/utils.hpp

## Purpose
`utils.hpp` contains inline and template helpers for random data, key generation, row partitioning, RAII guards, and fixed-width terminal output used throughout Mako.

## Important APIs, Types, and Functions
- Random helpers: `urand`, `nextKey`, `randomAlphanumString`, and `randomString`.
- Key helpers: `insertBegin`, `insertEnd`, `numericWithFill`, `genKey`, and `prepareKeys`.
- Partition helpers: declarations for `computeThreadPortion`, `computeThreadTps`, and `computeThreadIters`.
- RAII helpers: `ExitGuard` and `FailGuard`.
- Formatting helpers: `putTitle`, `putTitleRight`, `putTitleBar`, `putField`, `putFieldBar`, and `putFieldFloat`.

## Control Flow
Workload execution calls `prepareKeys` once per operation's first step, generating row keys using either uniform or Zipfian distribution. Build mode uses `insertBegin`/`insertEnd` to assign disjoint row ranges. Cleanup and stats printing use the formatting helpers. Guards are used in `mako.cpp` to reset stopwatches, reset transactions, join/stop network threads, and clean resources at scope exit.

## State and Persistence Behavior
Most helpers are stateless. Random helpers consume the process-global C `rand()` state seeded in `main`; Zipf selection consumes the FDB zipfian generator state. Key generation only mutates caller-provided buffers.

## Dependencies and Integration Points
It depends on `mako.hpp`, `macro.hpp`, `fdbclient/zipf.h`, fmt, and C/C++ standard headers. It is a low-level dependency of operations and the Mako driver.

## Risks
`rand()` is process-global and not high-quality; worker threads call these helpers concurrently, so randomness may be implementation-dependent. Key buffer lengths rely on prior validation. `ExitGuard` always executes and is non-copy-protected, so accidental copies would double-run callbacks. Formatting helpers print directly to stdout.

## Test Signals
Tests should verify key layout with and without prefix padding, range endpoint generation, Zipf/uniform selection bounds, and partition coverage with no gaps or overlaps across process/thread combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/utils.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/performance_test.c -->
# sources/storage-engines/foundationdb/bindings/c/test/performance_test.c

## Purpose
`performance_test.c` is a C API benchmark program that measures local-client throughput for common FoundationDB operations and writes KPI/error results through `test.h`.

## Important APIs, Types, and Functions
- Globals configure `numKeys`, `keySize`, generated `keys`, `valueSize`, and `valueStr`.
- `waitError`, `run`, `runTest`, and `runTestDb` provide retry and median-measurement harnesses.
- Setup helpers `clearAll`, `insertRange`, and `insertData` prepare the keyspace.
- Benchmarks include `futureLatency`, `clear`, `clearRange`, `set`, `parallelGet`, `alternatingGetSet`, `serialGet`, `getRange`, `getKey`, `getSingleKeyRange`, and `writeTransaction`.
- `runTests` opens the database/network, loads data, runs all KPIs, and stops the network.

## Control Flow
`main` selects the API version, allocates a fixed value buffer and one million generated keys, runs the benchmark suite, writes a result JSON file, and frees resources. Each benchmark is run 25 times; the median throughput is recorded. Most transaction benchmarks execute inside `run`, which retries via `fdb_transaction_on_error` and commits if the operation function succeeds.

## State and Persistence Behavior
The benchmark clears the entire database keyspace and loads one million keys, so it is destructive to the target cluster. Some mutation benchmarks reset the transaction before commit to avoid changing loaded data. Results are persisted as `fdb-c_result-<random>.json`.

## Dependencies and Integration Points
It uses the FoundationDB C API, generated options, pthread-based network thread helpers from `test.h`, and C heap allocation. The KPI names are consumed by surrounding performance infrastructure.

## Risks
The test is destructive because `clearAll` clears `["", "\xff")`. Error paths in some loops destroy only the current future and can leak other allocated futures. Large key allocation and one-million-key load make runtime and memory cost high. The benchmark uses wall-clock timing and `rand()`, so results are noisy.

## Test Signals
Successful output includes KPIs for each named operation and no errors in the result file. Correctness checks in range benchmarks validate expected counts and no extra pages for exact single-key range reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/performance_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/ryw_benchmark.c -->
# sources/storage-engines/foundationdb/bindings/c/test/ryw_benchmark.c

## Purpose
`ryw_benchmark.c` measures read-your-writes cache performance in a single FoundationDB C transaction after loading keys into the transaction's local state.

## Important APIs, Types, and Functions
- `insertData` clears the keyspace and sets `numKeys + 1` keys in one transaction.
- `runTest` runs a transaction-local benchmark 25 times and records median keys/sec.
- Benchmarks include `getSingle`, `getManySequential`, `getRangeBasic`, `singleClearGetRange`, `clearRangeGetRange`, and `interleavedSetsGets`.
- `runTests` opens the database, creates one transaction, obtains a read version, populates local mutations, runs benchmarks, and tears down.

## Control Flow
Unlike `performance_test.c`, benchmarks generally reuse one transaction and rely on the transaction's local RYW cache. Range benchmarks validate returned counts after local clears and clear ranges, then repopulate transaction state with `insertData`.

## State and Persistence Behavior
The test mutates a transaction's local state heavily. It does not explicitly commit after `insertData`, so most measured behavior is transaction-local rather than durable cluster state. It still issues a full clear and sets inside the transaction, and results are persisted through `writeResultSet`.

## Dependencies and Integration Points
It depends on the FDB C API, `test.h` result/network helpers, and generated key arrays. It is part of C binding benchmark coverage for RYW cache behavior.

## Risks
Several error paths return without destroying the current future, and `getRangeBasic` does not destroy futures in the success path. The code expects exact range counts from local mutations and may be sensitive to API semantics. `insertData` iterates `<= numKeys`, which relies on `generateKeys` allocating `numKeys + 1`.

## Test Signals
Result JSON should contain six RYW KPI names and no errors. Count checks in range benchmarks are direct correctness signals for local clear and clear-range visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/ryw_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/shim_lib_tester.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/shim_lib_tester.cpp

## Purpose
`shim_lib_tester.cpp` is a command-line utility for validating FoundationDB C shim library configurations, including local client override, external client library, external client directory, disabled local client, and capped API version selection.

## Important APIs, Types, and Functions
- `TesterOptions` stores parsed CLI values.
- `TesterOptionDefs`, `parseArgs`, `processArg`, and `processIntOption` implement SimpleOpt parsing.
- `applyNetworkOptions` maps options to FDB network options or rejects invalid combinations.
- `testBasicApi` creates a database/transaction, sets a timeout, writes `key1=val1`, commits with retry handling, and exits on timeout.
- `testNewOnlyApi` is a placeholder for future shim compatibility probes.

## Control Flow
`main` parses options, optionally calls `fdb_shim_set_local_client_library_path` before any FDB API call, selects the requested capped API version, applies network options, sets up and runs the network on a thread, performs a basic write test, optionally flushes deferred cleanup under ASAN, stops the network, and joins.

## State and Persistence Behavior
The test writes one key/value pair to the configured cluster. It has no result file. Process exit code communicates success/failure to higher-level tests.

## Dependencies and Integration Points
It uses `test/fdb_api.hpp` C++ wrappers, `foundationdb/fdb_c_shim.h`, SimpleOpt, fmt, FDB error definitions, and network options for multi-version/external clients. It is likely invoked by Python shim tests.

## Risks
`fdb_check` accepts an expected-error parameter but ignores it. Invalid external-client configurations intentionally fail by timeout/exit, so calling tests must interpret exit codes carefully. The basic API test mutates a fixed key. ASAN-specific flushing depends on native C API calls.

## Test Signals
Exit code 0 after a commit validates the selected shim configuration. Negative tests should verify invalid library paths, disabled local client without external library, old API versions, and external-client directory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/shim_lib_tester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/test.h -->
# sources/storage-engines/foundationdb/bindings/c/test/test.h

## Purpose
`test.h` is a header-only helper library for C binding tests and benchmarks. It supplies timing, deterministic key generation, median calculation, KPI/error result collection, JSON result writing, error handling, network thread startup, and database opening.

## Important APIs, Types, and Functions
- `getTime`, `writeKey`, `generateKeys`, `freeKeys`, `median`.
- `RunResult` and `RES` standardize benchmark function return values.
- `Kpi`, `Error`, and `ResultSet` form linked-list result storage.
- `newResultSet`, `addKpi`, `addError`, `writeResultSet`, and `freeResultSet` manage result lifecycle.
- `getError`, `checkError`, `logError`, and `maybeLogError` handle C API errors.
- `runNetwork` and `openDatabase` set up the FDB network thread and create a default database.

## Control Flow
Benchmarks include this header, create a `ResultSet`, select the API version, call `openDatabase`, add KPIs/errors while running, and call `writeResultSet`. Fatal errors write and free the result set before exiting.

## State and Persistence Behavior
`writeResultSet` persists a randomly named `fdb-c_result-<id>.json` file in the current directory. Other state is heap-owned linked lists and generated key arrays. `openDatabase` starts global FDB network state in a pthread.

## Dependencies and Integration Points
It depends on the FoundationDB C API and generated options, POSIX time, pthreads, sockets byte-order headers, and standard C allocation/IO. Multiple C test programs include it directly, so function definitions are emitted into each translation unit.

## Risks
There are no include guards, though each test likely includes it once. JSON output is hand-escaped and will break if KPI or error strings contain quotes or control characters. `freeKeys` frees only `0..numKeys-1` even though `generateKeys` allocates `numKeys + 1`, leaking the sentinel key. `runNetwork` signature omits a `void*` parameter expected by pthread start routines.

## Test Signals
Any benchmark using this header should produce a result JSON file with expected KPI names and an empty error array. Memory tooling would catch the sentinel key leak and result-list cleanup issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/txn_size_test.c -->
# sources/storage-engines/foundationdb/bindings/c/test/txn_size_test.c

## Purpose
`txn_size_test.c` verifies that `fdb_transaction_get_approximate_size` grows as mutations are added to a transaction.

## Important APIs, Types, and Functions
- `getSize` issues `fdb_transaction_get_approximate_size`, waits, extracts the int64 result, and destroys the future.
- `runTests` creates a database and transaction, applies set, set, clear, and clear-range mutations, records approximate sizes, and asserts strict growth.
- `main` selects the API version, generates keys, runs tests, and frees resources.

## Control Flow
The test starts the FDB network via `openDatabase`, creates a transaction, performs each mutation in sequence without commit, queries approximate size after each mutation, and asserts `sizes[j] < sizes[j + 1]`.

## State and Persistence Behavior
The transaction is not committed, so no durable database mutation is expected. Runtime state includes generated keys, a fixed static value buffer, and a local `sizes` array. It does not write a result set unless `checkError` fails.

## Dependencies and Integration Points
It uses `test.h`, the FDB C API, pthread network setup, and generated options. It targets the C API's transaction-size accounting.

## Risks
`memset(sizes, 0, numKeys * sizeof(uint32_t))` uses `uint32_t` size for an `int64_t` array, though only the first few entries are used and initialized before comparison. The database and transaction are not explicitly destroyed/stopped in the shown success path, relying on process exit. The strict monotonic assertion may be sensitive to changes in approximate-size accounting granularity.

## Test Signals
Success prints four increasing sizes and `Test passed!`. Failure indicates either API error or non-monotonic approximate transaction size after mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/txn_size_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/disconnected_timeout_tests.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/unit/disconnected_timeout_tests.cpp

## Purpose
`disconnected_timeout_tests.cpp` is a doctest suite for C API transaction and database timeout behavior when connected to an unavailable cluster file.

## Important APIs, Types, and Functions
- `fdb_check`, `fdb_open_database`, and `wait_future` wrap C API error handling.
- `validateTimeoutDuration` asserts actual timeout duration is at least expected and less than double expected.
- Test cases cover transaction timeout before/after operations, timeout replacement, database timeout, database vs transaction precedence, reset behavior, reset/destruction cancellation, and repeated timeout setup/destruction.
- `main` handles unavailable cluster file, optional external client library, doctest context, network setup/run/stop, and global DB handles.

## Control Flow
The program selects the latest API, optionally configures an external client, starts the FDB network, opens two database handles against an unavailable cluster, runs doctest cases, destroys handles, stops network, and returns doctest status.

## State and Persistence Behavior
No database persistence is expected because the cluster is unavailable. State consists of global `FDBDatabase*` handles and futures that should timeout or be canceled. The tests intentionally block until timeout/cancel readiness.

## Dependencies and Integration Points
It uses the FDB C API directly and the local unit `fdb_api.hpp` RAII wrappers for futures/transactions. It depends on doctest and C++ threading/chrono.

## Risks
Wall-clock assertions can be flaky on very slow or overloaded machines. Error-code checks use numeric constants `1031` and `1025` rather than named constants. Tests require a genuinely unavailable cluster file; an accidentally reachable cluster changes behavior. Database timeout is set on a shared `timeoutDb`, so tests depend on set/reset semantics across transaction creation.

## Test Signals
Passing doctest output validates timeout duration, precedence, reset cancellation, destruction cancellation, and external-client timeout support. Failures are strong signals for C API timeout regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/disconnected_timeout_tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.cpp

## Purpose
`unit/fdb_api.cpp` implements RAII C++ wrappers around selected FoundationDB C API futures, results, database management functions, and transaction methods for use in unit tests.

## Important APIs, Types, and Functions
- `Future` destructor destroys `FDBFuture`; methods wrap readiness, blocking, callbacks, error retrieval, memory release, and cancellation.
- Typed futures implement `get` methods for int64, double, key, value, string array, key-value array, mapped key-value array, and key-range array.
- `Result` and `KeyValueArrayResult` manage `FDBResult`.
- `Database` static methods wrap administrative futures.
- `Transaction` constructor/destructor manage `FDBTransaction`; methods wrap options, read version, approximate size, costs, reads, ranges, mapped ranges, watch, commit, on_error, mutations, committed version, and conflict ranges.

## Control Flow
Tests create wrapper objects on the stack. Constructors allocate C API handles; destructors clean them up. Methods return typed future wrappers by value so future cleanup is tied to object lifetime. Fatal transaction construction errors print and abort.

## State and Persistence Behavior
Wrappers own native handles. Transaction methods can read or mutate database state depending on caller commits. Future/result objects own C API memory and release on destruction.

## Dependencies and Integration Points
It depends on `fdb_api.hpp`, the FoundationDB C API, and iostream for fatal construction errors. Unit tests such as disconnected timeout tests use these wrappers to avoid repetitive destroy calls.

## Risks
Wrappers are copyable by default because copy/move constructors are not deleted; copying a `Future`, `Result`, or `Transaction` could double-destroy native handles. Return-by-value relies on copy elision/move behavior but explicit copy remains dangerous. Constructor aborts instead of returning errors, which is acceptable for tests but not library-grade.

## Test Signals
Wrapper use in unit tests exercises common paths. Additional compile/runtime tests should forbid copying and cover every typed getter with a real or mocked future result.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.hpp

## Purpose
`unit/fdb_api.hpp` declares the RAII wrapper classes implemented in `fdb_api.cpp`. It provides typed future wrappers and a transaction wrapper to make C API unit tests shorter and safer.

## Important APIs, Types, and Functions
- `Future` base class declares destructor and common future methods.
- Typed future classes declare result-specific `get` methods and restrict constructors to friend classes.
- `Result` and `KeyValueArrayResult` wrap newer `FDBResult` APIs.
- `Database` declares static administrative wrappers.
- `Transaction` declares wrappers for transaction lifecycle, options, reads, ranges, mapped ranges, watches, commits, error handling, mutations, committed version, and conflict ranges.

## Control Flow
Tests include this header, select/setup the FDB API separately, create a `Transaction` from an `FDBDatabase*`, call methods returning typed futures, block/get results, and rely on destructors for cleanup.

## State and Persistence Behavior
The declarations define ownership of raw `FDBFuture*`, `FDBResult*`, and `FDBTransaction*`. Persistence is indirect through transaction commit and database admin operations.

## Dependencies and Integration Points
It defines `FDB_USE_LATEST_API_VERSION`, includes `foundationdb/fdb_c.h`, and uses `std::string_view` for key/value parameters. It is test-local and distinct from the production `bindings/c/test/fdb_api.hpp` wrapper used by Mako/shim tests.

## Risks
The header does not delete copy constructors or assignment operators, which undermines unique ownership. The base destructor is pure virtual but implemented in the cpp. `KeyValueArrayResult` comment has a typo but behavior is unaffected. The wrapper is broad enough that API changes require updating declaration and implementation together.

## Test Signals
Compilation of all unit tests using this header is the first signal. Runtime tests should validate automatic cleanup and typed getters for representative C API futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/fdb_api.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/setup_tests.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/unit/setup_tests.cpp

## Purpose
`setup_tests.cpp` is a doctest unit test for C API setup and network initialization invariants.

## Important APIs, Types, and Functions
- `fdb_check` aborts on unexpected C API errors.
- The single `TEST_CASE("setup")` checks API version selection errors/success, max API version, network setup idempotence, network-thread completion hook registration, network run/stop, and hook invocation.

## Control Flow
Doctest provides `main`. The test first verifies selecting an excessive API version fails, selects the current API, verifies selecting again fails, sets up the network, verifies setup again fails, registers a completion hook, starts `fdb_run_network` on a thread, stops the network, joins, and checks the hook fired.

## State and Persistence Behavior
No database state is touched. The test mutates global FDB API process state, so it must run in a fresh process where API version and network are not already selected/setup.

## Dependencies and Integration Points
It uses the FDB C API, doctest, iostream, and C++ threads. It is part of C binding unit coverage for setup semantics.

## Risks
Because the API version and network state are global, this test cannot be safely composed with other tests in the same process. It assumes `FDB_API_VERSION` is valid and that network stop completes promptly.

## Test Signals
Passing the test validates correct errors for invalid/double setup calls and confirms completion hooks run after the network thread exits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/setup_tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/trace_partial_file_suffix_test.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/unit/trace_partial_file_suffix_test.cpp

## Purpose
`trace_partial_file_suffix_test.cpp` verifies that FDB trace files use a configured partial-file suffix while the network is running and that the suffix is removed on shutdown, including for a simulated stray partial file from an earlier crash.

## Important APIs, Types, and Functions
- `fdb_check` aborts on C API errors.
- `set_net_opt` wraps `fdb_network_set_option` for string options.
- `file_exists` checks file presence.
- `main` configures tracing, creates a simulated stray `.tmp` trace file, runs the network, opens a database to initialize logging, waits for a new trace file, stops the network, checks rename behavior, and removes files.

## Control Flow
The test selects the API version, builds a random file identifier, creates a fake trace file ending in `.tmp`, enables tracing and sets file identifier/suffix, starts the network, opens/destroys a database using `argv[1]`, loops over current-directory files until a real trace file appears with the suffix, stops the network, asserts both partial files were renamed without the suffix, then deletes them.

## State and Persistence Behavior
The test creates and deletes trace files in the current working directory. It does not intentionally mutate database contents, but it opens a database to trigger trace initialization.

## Dependencies and Integration Points
It uses the FDB C API, `flow/Platform.h` for directory listing, C++ file/thread/random utilities, and process current-directory trace behavior.

## Risks
The wait loop has no timeout and can hang if tracing does not create a file. It assumes `argv[1]` exists. File name matching is current-directory based and could collide, though the random identifier lowers risk. Assertions are active because `NDEBUG` is undefined.

## Test Signals
Success proves partial trace suffix configuration, startup trace creation, shutdown rename, stray partial-file cleanup, and cleanup deletion. Failure indicates trace lifecycle or file naming regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/unit/trace_partial_file_suffix_test.cpp -->
