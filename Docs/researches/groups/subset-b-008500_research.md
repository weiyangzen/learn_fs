# Research Group subset-b-008500

This grouped report covers Flow benchmark, runtime support, serialization, Swift interop, actor utility, and core header files from `sources/storage-engines/foundationdb/flow`. Each file section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCoroChooseRace.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchCoroChooseRace.cpp

Purpose: defines Google Benchmark microbenchmarks comparing Flow C++ coroutine `Choose()` selection against `race()` for two-result futures. It measures both side-effect-only selection and value-returning selection with `std::variant<int,double>`.

Important APIs/types/functions: internal enums `Impl` and `Scenario`; helpers `consumeReady`, `consumeAfter`, `selectReadyAsValue`, `selectAfterAsValue`; actor benchmarks `benchChooseRaceActor`, `benchChooseRaceValueActor`, and `benchChooseRaceConstructPendingActor`; wrappers run work through `onMainThread(...).blockUntilReady()`.

Control flow: each benchmark constructs ready, never-ready, or promise-completed futures and dispatches compile-time branches for `Choose` versus `race`. The pending-construction benchmark resumes timing only around selector construction and pauses before cancellation to isolate registration overhead.

State/persistence: no persistent state. Local `sink` variables prevent optimization. Promises and futures are per-iteration or per-actor local; pending futures are explicitly cancelled after timed construction.

Dependencies/integration: relies on `benchmark/benchmark.h`, Flow coroutine support from `flow/genericactors.actor.h`, and main-thread execution via `flow/ThreadHelper.actor.h`. Registered benchmark names group results under `coro_choose`, `coro_race`, and construct/value variants.

Risks: assertions assume synchronously ready futures after promise send or ready inputs; semantic changes in `Choose`, `race`, cancellation, or ready future propagation will break benchmark assumptions. The value-selection `Choose` path uses an extra `Promise<Result>`, intentionally measuring a different adaptation cost.

Test signals: the registered benchmark matrix covers ready-first, ready-second, after-first, value-returning, and pending construction cases, with `ReportAggregatesOnly(true)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCoroChooseRace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCoroutineOverhead.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchCoroutineOverhead.cpp

Purpose: measures baseline overhead of Flow C++ coroutine futures for immediate `co_return` and immediate `co_await` on ready values.

Important APIs/types/functions: `returnReadyInt`, `returnReadyVoid`, `benchCreateReadyIntActor`, `benchCreateReadyVoidActor`, `benchAwaitReadyIntActor`, `benchAwaitReadyVoidActor`, and non-actor benchmark wrappers that execute on the Flow main thread.

Control flow: create benchmarks repeatedly call a coroutine that returns an already-ready `Future<T>`, assert readiness, consume the result where applicable, and use `DoNotOptimize`. Await benchmarks keep a prebuilt ready `Future<int>` or `Future<Void>` and repeatedly `co_await` it inside the benchmark actor.

State/persistence: only local counters and ready futures. There is no durable state or heap ownership beyond normal future frames.

Dependencies/integration: depends on Google Benchmark, `flow/flow.h`, and `ThreadHelper.actor.h`. Benchmark registration names use `coroutine_overhead/...`, providing a focused signal for Flow coroutine implementation changes.

Risks: because all inputs are ready, results are sensitive to compiler optimization, coroutine ABI behavior, and future fast-path changes. Assertions hard-code that these coroutines complete synchronously.

Test signals: benchmark registrations cover ready int/void creation and ready int/void await; `SetItemsProcessed` is not used, so timing is per benchmark iteration only.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchCoroutineOverhead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchHash.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchHash.cpp

Purpose: benchmarks hashing throughput for Flow key-sized buffers using `hashlittle2`, CRC32C, and XXH3.

Important APIs/types/functions: enum `HashType`; template specializations `hash<HashLittle2>`, `hash<CRC32C>`, `hash<XXHash3>`; benchmark body `bench_hash`; helper `getString` from `BenchSupport.h`.

Control flow: each benchmark selects a byte length from `DenseRange(2, 18)` as `1 << range`, creates a deterministic `StringRef`, and repeatedly invokes the selected hash implementation with `DoNotOptimize` on results.

State/persistence: no persistent state. Data is generated once per benchmark state and then reused for all iterations.

Dependencies/integration: integrates Flow hash utilities (`flow/Hash3.h`, `flow/xxhash.h`), CRC32C, and Google Benchmark. Output is registered as template benchmarks for all three hash algorithms.

Risks: only measures single-buffer repeated hashing, so cache effects are favorable. The empty primary template would compile to no-op if accidentally used with an unhandled `HashType`.

Test signals: benchmark ranges span 4 bytes through 256 KiB and set item count to iterations, enabling comparative timing rather than byte-throughput counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchHash.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMain.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchMain.cpp

Purpose: provides the executable entry point for `flow_bench`.

Important APIs/types/functions: `main(int argc, char** argv)` delegates directly to `runBenchmarks` from `flow/BenchMain.h`.

Control flow: all initialization, network setup, benchmark thread handling, and shutdown semantics live in the included harness; this file is intentionally minimal.

State/persistence: no local state beyond command-line arguments.

Dependencies/integration: depends only on `flow/BenchMain.h`, tying the binary target built by the bench CMake file to the shared benchmark harness.

Risks: any extra initialization must be added through `runBenchmarks` or an alternate entry point; this file provides no error handling beyond the harness return code.

Test signals: executable behavior is validated indirectly by running any registered Google Benchmark from the `flow_bench` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMain.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMem.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchMem.cpp

Purpose: simple baseline benchmarks for standard `memcmp` and `memcpy` over 10,000-byte buffers.

Important APIs/types/functions: `bench_memcmp` and `bench_memcpy`, each registered with `BENCHMARK`.

Control flow: `bench_memcmp` allocates two buffers, zeroes both, changes the last byte of the second, and repeatedly compares the full range. `bench_memcpy` allocates source and destination buffers and repeatedly copies the fixed length.

State/persistence: all buffers are `std::unique_ptr<char[]>` local to each benchmark state. No durable state exists.

Dependencies/integration: uses `<cstring>`, `<memory>`, and Google Benchmark. It is separate from the more detailed `BenchMemcpy.cpp` matrix.

Risks: fixed-size, hot-cache behavior may not represent production memory patterns. `bench_memcpy` does not initialize the destination before use, which is fine for copy timing but not validation.

Test signals: basic benchmark names `bench_memcmp` and `bench_memcpy` provide coarse regression signals for libc or Flow memcpy override behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMem.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMemcpy.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchMemcpy.cpp

Purpose: builds a detailed benchmark matrix comparing `rte_memcpy_noinline` and `std::memcpy` across sizes, cache locality modes, and alignment cases.

Important APIs/types/functions: enums `CopyFunction`, `CacheMode`, `CopyAlignment`; constants for small/large buffers, alignment, address count, and tested sizes; `AlignedBuffer`, `MemcpyBuffers`, `copy`, `benchMemcpy`, and registration helpers.

Control flow: global static registration creates variable-size and constant-size benchmarks for both copy implementations, four cache modes, and aligned/unaligned addresses. `MemcpyBuffers` preallocates 100 MiB large read/write buffers and 8 KiB small read/write buffers, fills deterministic read data, and precomputes randomized large offsets.

State/persistence: `memcpyBuffers()` owns a process-static buffer set reused by all benchmarks. Per-iteration state is an address index cycling through randomized offsets.

Dependencies/integration: uses Flow platform aligned allocation/free, deterministic random, `rte_memcpy_noinline` from `flow.cpp`, and Google Benchmark counters for bytes/items processed.

Risks: large static buffers affect process memory footprint and benchmark startup. Cache-mode simulation depends on buffer size and randomized offsets rather than explicit cache flushes. Constant-size template paths intentionally expose compiler specialization behavior.

Test signals: benchmark names are hierarchical under `Memcpy/<function>/<alignment>/<cache_mode>/variable|constant/<size>` with `MinTime(0.01)` and byte counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchMemcpy.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNet2.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchNet2.cpp

Purpose: C++20 coroutine benchmark version for Flow net2 scheduling patterns, intended to compare with actor-style equivalents.

Important APIs/types/functions: coroutine `increment`, `getRandomTaskPriority`, `benchNet2Actor`, `benchDelayLoop`, `benchYieldLoop`, and benchmark wrappers `coroutine_net2`, `coroutine_delay_bench`, `coroutine_yield_bench`.

Control flow: net2 benchmark creates `actorCount` delayed increment futures at deterministic priorities, waits for all, and consumes the sum. Delay/yield benchmarks first populate the run-loop priority queue with random future timers, then repeatedly `co_await delay(0)` or `yield()`.

State/persistence: no persistent state. Random seed is captured once per benchmark actor to make priority selection repeatable within the run.

Dependencies/integration: uses Flow `delay`, `yield`, `waitForAll`, network/task priority definitions, deterministic random, platform random seed, and `onMainThread`.

Risks: comments note a GCC coroutine issue that led to separate delay/yield functions. Results are scheduler-sensitive and depend on timer queue population rather than real network I/O.

Test signals: registered ranges cover actor counts or timer counts from 1/0 up to `1 << 16`, with aggregate reporting and items processed counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNet2.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNet2Actor.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchNet2Actor.cpp

Purpose: actor-named benchmark file for net2 scheduling, delay, and yield overhead; current implementation uses coroutine syntax while preserving actor benchmark naming/shape.

Important APIs/types/functions: `increment`, `getRandomTaskPriority`, `benchNet2Actor`, `populateTimers`, `benchDelayLoop`, `benchYieldLoop`, template wrapper `bench_delay`.

Control flow: mirrors `BenchNet2.cpp`: spawn delayed increments, wait for all, or populate timers and repeatedly await `delay(0)`/`yield()`. `bench_delay` dispatches between delay and yield via a compile-time boolean.

State/persistence: local vectors hold outstanding timers or increment futures. No durable state is kept.

Dependencies/integration: Flow network and scheduling primitives, deterministic random, `ThreadHelper.actor.h`, and Google Benchmark. It registers `bench_net2` and template `bench_delay` variants.

Risks: the file name and comments imply ACTOR comparison, but the visible implementation is coroutine-based; researchers should confirm whether generated `.actor.g.cpp` or historical versions supply additional actor-only behavior elsewhere. Timer futures are intentionally retained only to keep the queue populated.

Test signals: benchmark ranges exercise `Range(1, 1 << 16)` for net2 and `Range(0, 1 << 16)` for delay/yield.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNet2Actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNoThrowOnCancel.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchNoThrowOnCancel.cpp

Purpose: benchmarks coroutine cancellation with normal exception unwinding versus `NoThrowOnCancel` frame destruction.

Important APIs/types/functions: `CleanupCounter`, `cancelWithThrow`, `cancelWithoutThrow`, enums `CancelImpl` and `CancelScenario`, `makeCancelFuture`, `benchNoThrowOnCancelActor`, and wrapper `benchNoThrowOnCancel`.

Control flow: construct-and-cancel repeatedly creates one pending future on an unsent promise and cancels it. Batch-cancel pauses timing to build a vector of pending futures, resumes timing to cancel them, then pauses to assert cancellation results. The no-throw path uses a sentinel catch block that should not run.

State/persistence: local counters track RAII cleanup and caught cancellation exceptions. No persisted state.

Dependencies/integration: uses Flow futures, `NoThrowOnCancel`, cancellation error codes, `ThreadHelper.actor.h`, and Google Benchmark.

Risks: correctness assertions are embedded in benchmarks; changes to cancellation readiness/error representation can fail runs. Batch scenario times only cancellation, so construction costs are intentionally excluded.

Test signals: four registered benchmarks cover throwing/no-throw and construct/batch scenarios; cleanup count must equal cancellation count, and caught count distinguishes implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchNoThrowOnCancel.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchPriorityMultiLock.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchPriorityMultiLock.cpp

Purpose: benchmarks `PriorityMultiLock` handoff behavior under active and inactive priority sets.

Important APIs/types/functions: coroutine `benchPriorityMultiLock`, wrapper `bench_priorityMultiLock`, `PriorityMultiLock::Lock`, and `makeReference<PriorityMultiLock>`.

Control flow: builds priority levels at multiples of ten, sets concurrency to ten times priority count, fills a deque with lock waiters for active priorities, waits for all initial locks, then repeatedly replaces one future with a new waiter and awaits the old one. Priority and deque index rotate each iteration.

State/persistence: the benchmark owns one lock and deque of futures for the benchmark state. No external persistence.

Dependencies/integration: depends on Flow `PriorityMultiLock`, futures, `waitForAll`, `ThreadHelper.actor.h`, and Google Benchmark.

Risks: comments contain a typo ("buy" for "by") but behavior is clear. The test assumes initial concurrency saturates but remains serviceable. Inactive priorities are included in lock configuration but not actively requested.

Test signals: benchmark ranges vary active priorities 1-64 and inactive priorities 0-128, with an explicit `{5,0}` argument and aggregate reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchPriorityMultiLock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchRandom.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchRandom.cpp

Purpose: measures throughput of Flow's thread-local deterministic RNG `random01()`.

Important APIs/types/functions: `bench_random` and `deterministicRandom()->random01()`.

Control flow: each iteration calls `random01()` and uses `benchmark::DoNotOptimize` to retain the call.

State/persistence: relies on Flow's thread-local deterministic RNG state initialized elsewhere. The benchmark itself has no stored state.

Dependencies/integration: includes `flow/IRandom.h` and Google Benchmark. It exercises the global RNG accessor defined in `flow.cpp`.

Risks: benchmark timing includes accessor cost as well as random generation. Because RNG state is global/thread-local, prior tests can influence sequence position but not the cost model materially.

Test signals: one aggregate benchmark with item count set to iteration count.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchRandom.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchRef.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchRef.cpp

Purpose: compares allocation, destruction, and copy overhead for raw pointers, `unique_ptr`, `shared_ptr`, Flow `Reference`, and thread-safe Flow `Reference`.

Important APIs/types/functions: empty reference-counted types `Empty` and `EmptyTSRC`; enum `RefType`; specialized `Factory` templates; benchmarks `bench_ref_create_and_destroy` and `bench_ref_copy`.

Control flow: create/destroy benchmarks construct one object per iteration and invoke type-specific cleanup. Copy benchmarks create one pointer-like object before timing and repeatedly copy it.

State/persistence: no persistent state. Allocations are per benchmark iteration for creation tests and one per benchmark state for copy tests.

Dependencies/integration: uses Flow `FastAlloc`, `FastRef`, standard smart pointers, and Google Benchmark.

Risks: raw pointer cleanup is manual and only safe because the benchmark calls `Factory::cleanup`. Copy benchmarks do not include `unique_ptr` because it is noncopyable.

Test signals: registrations cover creation/destruction for all five pointer styles and copy for raw, shared, Flow reference, and thread-safe Flow reference.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchStream.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchStream.cpp

Purpose: benchmarks `PromiseStream<StringRef>` send/receive throughput for different item counts and payload sizes.

Important APIs/types/functions: `benchStreamActor`, `bench_stream`, `getString`, `PromiseStream<StringRef>`, and `stream.getFuture()`.

Control flow: each iteration sends `items` copies of a prebuilt `StringRef` into the stream, then awaits and consumes the same number of futures.

State/persistence: one local stream is reused for the benchmark actor. Payload memory comes from `getString(size)` and is held for the actor lifetime.

Dependencies/integration: uses Flow streams/futures, network main-thread execution, TLS/network includes, and Google Benchmark.

Risks: producer and consumer are in the same coroutine and same thread, so results reflect in-memory stream buffering rather than cross-actor contention. The benchmark sends borrowed `StringRef` values, so payload lifetime must outlive receives, which it does locally.

Test signals: two-dimensional benchmark ranges cover item count and string size from 1 to `1 << 16`, with item count processed per iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchStream.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchSupport.h -->
# sources/storage-engines/foundationdb/flow/bench/BenchSupport.h

Purpose: provides small shared helpers for Flow benchmark data generation.

Important APIs/types/functions: inline `getString(int length)`, which returns a `Standalone<StringRef>` filled with random bytes from `deterministicRandom()`.

Control flow: allocates a standalone mutable string of the requested length, fills it through `mutateString`, and returns the owning standalone value.

State/persistence: generated data owns its bytes through the `Standalone<StringRef>` arena. The RNG state comes from Flow's deterministic random singleton.

Dependencies/integration: includes `flow/Arena.h`, `flow/IRandom.h`, and `flow/flow.h`. Used by hash and stream benchmarks to avoid duplicated buffer setup.

Risks: generated bytes depend on the current deterministic RNG state and therefore are deterministic per process seed but not content-fixed by this helper alone. Returned `StringRef` must not be separated from its `Standalone` owner.

Test signals: indirect; correctness is visible through benchmarks that use the generated string without lifetime errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchSupport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchTimeout.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchTimeout.cpp

Purpose: compares actor-based `timeout` from `genericactors.actor.h` with coroutine-based `generic_coro::timeout`.

Important APIs/types/functions: enums `TimeoutImpl` and `TimeoutScenario`; template actor `benchTimeoutActor`; wrapper `benchTimeout`; overloads returning a timed-out value.

Control flow: ready scenario repeatedly wraps a ready future with zero timeout and awaits the result. construct-pending scenario measures construction of a timeout race on a never-ready future with a one-second timer, pauses timing, and cancels the pending result.

State/persistence: local sink for ready values and local never/ready futures. No durable state.

Dependencies/integration: Flow generic actor helpers, `genericcoros.h`, main-thread execution, and Google Benchmark.

Risks: ready scenario includes await cost after wrapper construction; pending scenario explicitly excludes cancellation cleanup. Semantics depend on timeout implementation preserving ready fast paths and cancellation behavior.

Test signals: four benchmarks cover actor/coroutine implementations in ready and pending construction modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchTimeout.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchTimer.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchTimer.cpp

Purpose: benchmarks Flow platform time accessors.

Important APIs/types/functions: `bench_timer` calls `timer()` and `bench_timer_monotonic` calls `timer_monotonic()`.

Control flow: each benchmark repeatedly invokes the selected clock function and prevents optimization of the result.

State/persistence: no local or persistent state.

Dependencies/integration: includes `flow/Platform.h` and Google Benchmark. These functions are low-level timing sources used broadly in Flow and simulation code.

Risks: results are platform-dependent and sensitive to clock implementation, syscall/vDSO behavior, and CPU frequency settings.

Test signals: two aggregate benchmark registrations set item count to iterations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchTimer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchWaitForAllReady.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchWaitForAllReady.cpp

Purpose: compares actor and coroutine implementations of `waitForAllReady` over already-completed futures, including success and error futures.

Important APIs/types/functions: enums `WaitForAllReadyImpl` and `WaitForAllReadyScenario`; `makeResults`; `benchWaitForAllReadyActor`; wrapper `benchWaitForAllReady`.

Control flow: prebuilds a vector of ready `Future<int>` objects or futures already set to `operation_failed()`, then repeatedly invokes actor `::waitForAllReady` or `generic_coro::waitForAllReady` and awaits completion.

State/persistence: immutable vector of futures for a benchmark state. No durable state.

Dependencies/integration: uses Flow generic actor helpers, `genericcoros.h`, main-thread execution, and Google Benchmark.

Risks: only covers all-ready inputs, so it isolates iteration and error-suppression overhead, not asynchronous fan-in latency. Error scenario assumes the implementation waits for readiness without propagating errors.

Test signals: four registered benchmark series cover actor/coroutine and ready/error cases with ranges 1 to 4096 futures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchWaitForAllReady.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchZstd.cpp -->
# sources/storage-engines/foundationdb/flow/bench/BenchZstd.cpp

Purpose: benchmarks raw and streaming Zstandard compression/decompression when `ZSTD_LIB_SUPPORTED` is enabled.

Important APIs/types/functions: helpers `compress`, `compress2`, `decompress`, `compressAsStream`, `decompressAsStream`, `genUncompressedData`, `genCompressedData`; benchmark functions for compress, compress2, stream compress, decompress, and stream decompress.

Control flow: test data comes from `BM_ZSTD_DATA` if set or a deterministic 1 MiB alphanumeric string. Static globals hold uncompressed data and compressed data at levels 1, 3, and 9. Benchmarks iterate through chunks using selected chunk size/level, track compression ratio counters, and set bytes processed.

State/persistence: process-static `UNCOMPRESSED` and `COMPRESSED` cache benchmark inputs. Compression contexts/streams are created per benchmark function invocation and freed where implemented.

Dependencies/integration: Google Benchmark, Flow deterministic random, and zstd C API under conditional compilation.

Risks: several helper calls do not check `ZSTD_isError`, so failed compression/decompression can be misinterpreted. `compress2` creates a `ZSTD_CCtx` without visible free, and stream reuse semantics may carry state if not reset per chunk as expected by the API.

Test signals: registered argument matrix covers chunk sizes from 4 KiB to 8 MiB and levels 1/3/9, plus decompression by level.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/BenchZstd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/CMakeLists.txt -->
# sources/storage-engines/foundationdb/flow/bench/CMakeLists.txt

Purpose: defines the `flow_bench` executable target and its benchmark source files.

Important APIs/types/functions: CMake commands `add_executable`, `target_link_libraries`, and `target_include_directories`.

Control flow: target construction lists benchmark `.cpp` sources and the shared `BenchMain.cpp`. The target links against `flow`, Google Benchmark, and required platform libraries.

State/persistence: build-system metadata only; no runtime state.

Dependencies/integration: integrates Flow benchmark sources into the repository build. It also adds the local bench directory as an include path so files can include `BenchSupport.h`.

Risks: adding a new benchmark source requires updating this list or using a broader source collection elsewhere. Conditional library support such as zstd affects source behavior but this file still compiles the benchmark file.

Test signals: successful CMake generation/build of `flow_bench` and execution of benchmark filters validate the target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/bench/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/clock_support.swift -->
# sources/storage-engines/foundationdb/flow/clock_support.swift

Purpose: exposes Flow network time and delay as a Swift `Clock` implementation.

Important APIs/types/functions: `FlowClock`, nested `FlowClock.Instant`, `.flow` clock extension, `now`, `minimumResolution`, `sleep(until:tolerance:)`, `sleep(for:)`, `InstantProtocol` methods, and `Swift.Duration` unit conversion helpers.

Control flow: `now` reads `flow_gNetwork_now()` and converts the `Double` seconds value into `Swift.Duration`. `sleep` computes duration to a deadline and awaits `flow_gNetwork_delay(...).value()` with `TaskPriority.DefaultDelay`.

State/persistence: `Instant` stores a `Swift.Duration` value. No persistent global state beyond Flow network state accessed through imported Flow functions.

Dependencies/integration: imports `Flow` and relies on Swift interop wrappers for Flow future `.value()`. It bridges Swift concurrency timing to Flow's event loop.

Risks: `sleep` currently ignores nanoseconds in the computed delay (`nanosDouble = 0` TODO), so sub-second precision may be wrong. Duration conversions can saturate to `.max` on overflow. Behavior depends on `gNetwork` availability.

Test signals: no local tests. Swift async code using `Task.sleep(..., clock: .flow)` is the integration signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/clock_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/config.h.cmake -->
# sources/storage-engines/foundationdb/flow/config.h.cmake

Purpose: CMake-generated configuration header template for Flow/FoundationDB compilation flags and build paths.

Important APIs/types/functions: `#cmakedefine` entries for allocation instrumentation, debug/release, IDE mode, sanitizers, GCOV, Valgrind, DTrace, aligned allocation, and jemalloc; path macros `FDB_SOURCE_DIR` and `FDB_BINARY_DIR`; Windows target macros.

Control flow: CMake substitutes configured options into preprocessor definitions. `FDB_RELEASE` implies `FDB_CLEAN_BUILD`; sanitizer defines combine into `USE_SANITIZER`; `USE_VALGRIND` defines `VALGRIND`.

State/persistence: build-time generated configuration only.

Dependencies/integration: included by compiled sources to choose platform features and instrumentation. Values depend on top-level CMake cache and platform.

Risks: path macros embed build/source directories in binaries. Incorrect sanitizer or Windows target substitution can change ABI/platform behavior.

Test signals: generated `config.h` inspection and successful compilation under configured build variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/config.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/coveragetool/Program.cs -->
# sources/storage-engines/foundationdb/flow/coveragetool/Program.cs

Purpose: command-line tool that scans source files for Flow coverage macros and writes an XML inventory of coverage cases.

Important APIs/types/functions: `CoverageCase`, `ParseException`, `Main`, `ParseOutput`, `WriteOutput`, `ParseSource`, and `FindComment`.

Control flow: `Main` validates args, reads existing output when input list matches, detects changed files by modification time, reuses unchanged cases, parses changed sources, and writes XML. `ParseSource` uses a regex to find `TEST`, `INJECT_FAULT`, and `SHOULD_INJECT_FAULT` invocations outside `#define` lines, then requires each case to have a unique non-empty trailing `//` comment.

State/persistence: persists cases and input paths in the XML output file. Incremental behavior depends on output timestamp and input list equality.

Dependencies/integration: C#/.NET LINQ, XML, regex, file I/O. It supports FoundationDB code coverage/probe tooling by enforcing comment uniqueness.

Risks: regex parsing is shallow and can miss multiline or unusual macro invocations. Incremental reuse trusts timestamps. Duplicate detection is per parsed changed file batch, not obviously global across reused unchanged cases.

Test signals: exit code `0` on success, `1` on parse validation failure, `100` on usage error; verbose output is controlled by `VERBOSE`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/coveragetool/Program.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/coveragetool/Properties/AssemblyInfo.cs -->
# sources/storage-engines/foundationdb/flow/coveragetool/Properties/AssemblyInfo.cs

Purpose: .NET assembly metadata for the `coveragetool` project.

Important APIs/types/functions: assembly attributes for title, company, product, copyright, COM visibility, GUID, and version.

Control flow: no runtime control flow; attributes are consumed by the compiler and runtime metadata systems.

State/persistence: static assembly metadata embedded into the built artifact.

Dependencies/integration: uses `System.Reflection`, `System.Runtime.CompilerServices`, and `System.Runtime.InteropServices`.

Risks: metadata copyright year differs from most source headers and may need maintenance. `ComVisible(false)` prevents COM exposure by default.

Test signals: successful C# project compilation and inspection of assembly metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/coveragetool/Properties/AssemblyInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/error_support.swift -->
# sources/storage-engines/foundationdb/flow/error_support.swift

Purpose: adds Swift convenience behavior for Flow errors.

Important APIs/types/functions: extension `Flow.Error.isEndOfStream`.

Control flow: property compares `self.code()` to `error_code_end_of_stream`.

State/persistence: no state.

Dependencies/integration: imports `Flow` and uses generated/imported Flow error constants. It is intended for Swift callers consuming Flow streams or futures.

Risks: only covers one error classification. Any change to generated symbol names or error code bridging breaks compilation.

Test signals: Swift code can branch on `error.isEndOfStream` instead of manually comparing codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/error_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flat_buffers.cpp -->
# sources/storage-engines/foundationdb/flow/flat_buffers.cpp

Purpose: implements and heavily unit-tests Flow flat-buffer vtable generation, vtable set reuse, serialization/deserialization compatibility, and support for special container/value cases.

Important APIs/types/functions: `detail::swapWithThreadLocalGlobal`, `detail::generate_vtable`, `string_serialized_traits<Void>`, unit-test context types, many serializable structs (`Nested`, `Root`, `Y1`, `Y2`, `X`), and helper `print_buffer`.

Control flow: `generate_vtable` sorts non-empty members by size descending, aligns offsets, stores vtable size/object size, and returns member offsets relative to object data. Tests serialize objects with `detail::save`, `save_members`, `ObjectWriter`, `ObjectReader`, and `ArenaObjectReader`, then load and compare fields.

State/persistence: thread-local vector `gWriteToOffsetsMemory` serves reusable serializer scratch memory. Test arenas own temporary serialized/deserialized data.

Dependencies/integration: depends on `flow/flat_buffers.h`, `FileIdentifier`, `Arena`, serializer traits, object serializer/reader, deterministic random, and unit-test macros.

Risks: alignment and vtable layout are compatibility-critical. Tests note Arenas are ignored by the wire protocol and must appear after owned refs. Several tests are meant to catch heap overflows under ASAN/Valgrind.

Test signals: numerous `TEST_CASE`s cover empty/non-empty vtables, nested serialization, members, variants, vector bool, schema evolution, tuples, file identifiers, `VectorRef`, `Standalone`, void, empty strings/vectors/sets, and non-empty unordered sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flat_buffers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow.cpp -->
# sources/storage-engines/foundationdb/flow/flow.cpp

Purpose: provides core Flow runtime globals, deterministic randomness helpers, UID/string utilities, formatting helpers, OpenSSL deterministic RNG binding, memcpy override glue, and unit tests for serialization and utility functions.

Important APIs/types/functions: globals `g_network`, `startSampling`, lineage references, RNG references, `randLog`, `noUnseed`; functions `setThreadLocalDeterministicRandomSeed`, `debugRandom`, `deterministicRandom`, `nondeterministicRandom`, `UID::toString/fromString/fromStringThrowsOnFailure/shortString`, `parse_with_suffix`, `parseDuration`, `vsformat`, `format`, `strinc`, `addVersionStampAtEnd`, `bindDeterministicRandomToOpenssl`, `nChooseK`, and `rte_memcpy_noinline`.

Control flow: RNG access lazily initializes thread-local deterministic generators from platform seeds. UID parsing validates fixed 32-character hex strings. Suffix parsing converts storage/duration units. OpenSSL binding installs a `RAND_METHOD` that draws from Flow deterministic random and asserts simulation when `g_network` exists.

State/persistence: owns process/thread globals for network, RNG, lineage, and debug tokens. No durable on-disk persistence.

Dependencies/integration: OpenSSL/BoringSSL, fmt, Flow platform, errors, deterministic random, unit tests, serialization. The optional AVX/Linux memcpy override exports a default `memcpy` symbol using `rte_memcpy`.

Risks: global state is central and ordering-sensitive. Overriding `memcpy` is platform/compiler/sanitizer gated and high blast radius. `strinc` asserts non-all-0xff input. OpenSSL deterministic binding should only be used in simulation.

Test signals: unit tests cover `ErrorOr`, `Optional`, `Standalone`, noSim presence, `ErrorOr::map/flatMap`, and human-readable byte/duration formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_future_support.swift -->
# sources/storage-engines/foundationdb/flow/flow_future_support.swift

Purpose: placeholder Swift extension file for Flow future conformances shared by Flow-importing modules.

Important APIs/types/functions: commented examples for `FlowCallbackForSwiftContinuationCInt`, `FutureCInt`, `FlowCallbackForSwiftContinuationVoid`, and `FutureVoid` conforming to protocols from `future_support.swift`.

Control flow: no active executable declarations beyond `import Flow`.

State/persistence: no state.

Dependencies/integration: intended to sit beside generated C++/Swift interop future types and add conformances once those types can be extended cleanly.

Risks: because conformances are commented out, Swift future awaitability depends on other files/generated bindings. Stale comments can hide missing type coverage.

Test signals: compile-only; additional Swift future types should add active conformances here and be validated through `.value()` await usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_future_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_optional_support.swift -->
# sources/storage-engines/foundationdb/flow/flow_optional_support.swift

Purpose: bridges Flow C++ optional-like types into Swift `Optional`.

Important APIs/types/functions: protocol `FlowOptionalProtocol` with associated `Wrapped`, `present()`, and unsafe getter; `Swift.Optional.init(cxxOptional:)`.

Control flow: initializer checks `present()`. If false, it assigns `nil`; otherwise it reads the pointed-to wrapped value from `__getUnsafe().pointee`.

State/persistence: no state. It copies the pointed value into a Swift optional.

Dependencies/integration: imports `Flow`; C++ optional bridge types must conform to `FlowOptionalProtocol`.

Risks: explicitly uses `__getUnsafe` with a FIXME, so lifetime and pointer validity are caller/type dependent. Missing conformances mean the generic initializer is unavailable.

Test signals: Swift code constructing `Optional(cxxOptional:)` from Flow optional wrappers; compile and runtime memory safety are key checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_optional_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_stream_support.swift -->
# sources/storage-engines/foundationdb/flow/flow_stream_support.swift

Purpose: adds Swift async stream protocol conformances for Flow `FutureStream` bridge types.

Important APIs/types/functions: extension `FutureStreamCInt: FlowStreamOps` and extension `FlowSingleCallbackForSwiftContinuation_CInt: FlowSingleCallbackForSwiftContinuationProtocol`; associated types `Element`, `SingleCB`, and `AsyncIterator`.

Control flow: no runtime logic in this file; it wires generated Flow C++ interop types into generic Swift stream machinery.

State/persistence: no state.

Dependencies/integration: imports `Flow` and depends on protocol definitions from the Swift support layer. Commented-out Void stream conformance indicates planned or blocked additional coverage.

Risks: currently only active for `CInt`; other element types need explicit conformance. Type names are generated/interop-sensitive.

Test signals: Swift async iteration over `FutureStreamCInt` should compile and use `FlowStreamOpsAsyncIteratorAsyncIterator`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/flow_stream_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/future_support.swift -->
# sources/storage-engines/foundationdb/flow/future_support.swift

Purpose: defines generic Swift protocols and await support for Flow future bridge types.

Important APIs/types/functions: `FlowCallbackForSwiftContinuationT`, `FlowFutureOps`, `FlowFutureOps.value()`, internal async property `waitValue`, and a `Flow.Void` specialization with `@discardableResult`.

Control flow: `.value()` awaits `waitValue`. If the future is already ready, it checks `isError`, throws `GeneralFlowError` for errors, asserts `canGet`, and returns `__getUnsafe().pointee`. If not ready, it creates a callback object and uses `withCheckedThrowingContinuation`, passing raw continuation and callback pointers to the C++ bridge callback `set`.

State/persistence: stack/local callback object and continuation wrapper are used during suspension. No durable state.

Dependencies/integration: imports `Flow` and requires concrete future/callback types to conform through associated types.

Risks: comments mark incomplete ready-error/cancellation handling and unsafe getter usage. Raw pointer handoff to C++ callback must preserve lifetime until continuation resumes.

Test signals: Swift `try await flowFuture.value()` for ready and pending futures; cancellation/error behavior needs explicit coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/future_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/genericactors.actor.cpp -->
# sources/storage-engines/foundationdb/flow/genericactors.actor.cpp

Purpose: implements generic Flow actor/coroutine utilities and unit tests for async listeners, quorum helpers, wait-most behavior, and coroutine equivalents in `genericcoros.h`.

Important APIs/types/functions: `allTrue`, actor `anyTrue`, `cancelOnly`, `timeoutWarningCollector`, `waitForMost`, `quorumEqualsTrue`, `shortCircuitAny`, `orYield`, `returnIfTrue`, `lowPriorityDelay`, `delayAfterCleared`, `lowPriorityDelayAfterCleared`, plus test helpers.

Control flow: utilities compose futures with ACTOR `choose`, `wait`, `waitForAny`, `quorum`, and coroutine awaits. `waitForMost` maps `ErrorOr<Void>` futures to success booleans, waits for quorum, optionally waits longer for slow futures, and throws configured error on insufficient success.

State/persistence: actor state variables track counters, timers, vectors, and previous async-var values. No disk persistence.

Dependencies/integration: includes Flow core, unit tests, `genericcoros.h`, and actor compiler last. It exposes general helpers used throughout FoundationDB actor code.

Risks: actor/coroutine interop and cancellation behavior are subtle. `lowPriorityDelay` loop count depends on knobs. `shortCircuitAny` handles a race between final completion and short-circuit path.

Test signals: unit tests cover `IAsyncListener`, `waitForMost`, and generic coroutine helpers for error transformation, tracing, timeout, delayed propagation, trigger, and wait-for-all-ready.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/genericactors.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/genericcoros.h -->
# sources/storage-engines/foundationdb/flow/genericcoros.h

Purpose: header-only C++20 coroutine implementations of common Flow future combinators.

Important APIs/types/functions: namespace `generic_coro`; templates `traceAfter`, `stopAfter`, `throwErrorOr`, `transformErrors`, `transformError`, `waitForAllReady`, `timeout` overloads, `timeoutError`, `delayed`, `trigger`, `uncancellable`, `holdWhile`, and `store`.

Control flow: functions use `co_await`, `race`, `delay`, and `coro::errorOr` to mimic actor utilities. Error handling preserves actor cancellation in transform paths, optionally logs trace events, and returns optional/timed-out values when delay wins.

State/persistence: no global state. `stopAfter` calls `g_network->stop()` after completion/error. `uncancellable` uses an intermediate promise to shield the underlying future.

Dependencies/integration: includes `flow/Coroutines.h` and `flow/flow.h`; benchmark and unit-test files compare these helpers with actor implementations.

Risks: templates are instantiated broadly and are sensitive to `Future<T>` move/copy semantics. `waitForAllReady` ignores result errors intentionally by awaiting `errorOr(ignore(result))`. `timeout` races may cancel losers depending on Flow race behavior.

Test signals: tests in `genericactors.actor.cpp` and benchmarks in `BenchTimeout.cpp`/`BenchWaitForAllReady.cpp`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/genericcoros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ActorCollection.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ActorCollection.h

Purpose: declares `actorCollection` and convenience wrappers for managing dynamically added actor futures.

Important APIs/types/functions: `actorCollection`, `ActorCollectionNoErrors`, `ActorCollection`, and `SignalableActorCollection`.

Control flow: declared `actorCollection` consumes a `FutureStream<Future<Void>>`, cancels child futures deterministically on cancellation, returns errors immediately, and optionally returns when the collection empties. Wrappers send futures through `PromiseStream` and expose size/result/signal operations.

State/persistence: wrappers hold `PromiseStream`, result future, optional count, and stop promise. No durable persistence.

Dependencies/integration: includes `flow/flow.h`; used by higher-level actor systems that need dynamic supervision.

Risks: lifecycle is cancellation-sensitive. `ActorCollectionNoErrors` assumes child actors report errors themselves. `SignalableActorCollection` uses a stop future to force emptying and reset/collapse semantics that callers must understand.

Test signals: indirect through actor supervision tests and production actor cancellation/error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ActorCollection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ActorContext.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ActorContext.h

Purpose: declares actor context tracking and dump APIs when `WITH_ACAC` is enabled, with no-op-compatible types otherwise.

Important APIs/types/functions: `ActorIdentifier`, `ActorID`, `ActiveActor`, `ActorExecutionContext`, `ActiveActorHelper`, `ActorExecutionContextHelper`, `ActorContextDumpType`, `encodeActorContext`, `dumpActorCallBacktrace`, `DecodedActorContext`, and `decodeActorContext`.

Control flow: enabled builds can register/unregister active actors through RAII helpers, track block execution context, dump actors, encode current context, and decode serialized context. Disabled builds typedef identifiers and provide minimal structs/helpers.

State/persistence: enabled mode implies global actor context state managed outside this header; serialized context strings can be persisted in traces/logs.

Dependencies/integration: Flow random/UID, FastAlloc/FastRef, mutex/vector/ostream in enabled mode. It integrates with actor compiler instrumentation and debugging.

Risks: disabled mode changes functionality substantially while preserving compile compatibility. Actor IDs and context dumps must be thread-safe in implementation.

Test signals: build variants with and without `WITH_ACAC`; runtime actor context dumps and decode round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ActorContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Arena.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Arena.h

Purpose: defines Flow's arena allocator and core arena-owned reference types, especially `StringRef`, `Standalone<T>`, `VectorRef<T>`, and `SmallVectorRef<T>`.

Important APIs/types/functions: `TrackIt`, `NonCopyable`, `Arena`, `ArenaBlock`, placement `operator new` overloads, `WipeAfterUse`, `Standalone<T>`, `StringRef`, string helpers (`makeString`, `mutateString`, `concatenateStrings`, `_sr` literal), `commonPrefixLength`, `flow_ref`, `VectorRefPreserializer`, `VectorRef`, `SmallVectorRef`, and serialization/trace/hash traits.

Control flow: `Arena` allocates by bumping within `ArenaBlock`s and frees by releasing the whole block graph. `dependsOn` links arena lifetimes. `StringRef` is a non-owning pointer/length view with arena-copy constructors and lexicographic helpers. `Standalone<T>` combines an arena with a value copied into that arena. `VectorRef` stores arena-backed contiguous elements, optionally deep-copying Flow ref types, and supports flat-buffer or string serialization strategies.

State/persistence: `ArenaBlock` reference counts and block trees own memory. `StringRef` and `VectorRef` usually borrow arena-owned memory and can dangle if owners are lost. Serialization traits define wire behavior for arena values, optional values, strings, and vectors.

Dependencies/integration: central dependency for Flow serialization, tracing, hashing, Swift support, object serializers, and many storage/server data structures.

Risks: lifetime discipline is critical. Mutation helpers cast away const and are safe only for uniquely owned mutable buffers. `VectorRef` copies share data, so mutating copied vectors is warned against. `commonPrefixLength` uses word loads that may rely on platform tolerance for unaligned reads. Secure memory wiping depends on `IsSecureMem`.

Test signals: broad indirect coverage across flat-buffer tests, serialization tests, StringRef/vector users, ASAN/Valgrind, and any workload using arena-owned protocol data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Arena.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ArgParseUtil.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ArgParseUtil.h

Purpose: helper for extracting normalized command-line argument keys with a specific prefix.

Important APIs/types/functions: `extractPrefixedArgument(std::string prefix, std::string arg)`.

Control flow: verifies `arg` starts with `prefix`, has an extra separator character, and that separator is `-` or `_`. It then strips the prefix plus separator and converts all hyphens in the remaining key to underscores.

State/persistence: no state.

Dependencies/integration: includes `flow/Arena.h` for `Optional<std::string>`. Intended for command-line parsing such as prefixed knobs.

Risks: function is defined in a header without `inline`, which can risk ODR/link issues if included in multiple translation units unless usage/build avoids it. Prefix matching is literal and case-sensitive.

Test signals: unit tests or callers should verify `--prefix-key`, `--prefix_key`, too-short strings, and nonmatching prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ArgParseUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/AsioReactor.h -->
# sources/storage-engines/foundationdb/flow/include/flow/AsioReactor.h

Purpose: declares the Boost.Asio-backed reactor used by Flow net2.

Important APIs/types/functions: namespace `N2`; classes `ASIOReactor`, Linux nested `EventFD`, abstract `Task`, `OrderedTask`, and globals/types `Net2`, `Peer`, `Connection`, `g_net2`.

Control flow: `ASIOReactor` owns an `io_service`, work guard, first timer, and wake/react/sleep APIs implemented elsewhere. Linux `EventFD` opens an `eventfd`, wraps it in an Asio stream descriptor, and returns Flow `Future<int64_t>` from async reads through a promise.

State/persistence: reactor owns Asio event-loop state. `EventFD` owns a file descriptor and read buffer until destruction.

Dependencies/integration: Boost.Asio, Linux `eventfd`, Flow futures, `g_network->global(INetwork::enEventFD)`, and net2 internals.

Risks: async read handler captures a pointer to `fdVal`; object lifetime must outlive pending reads. `sd.close()` is assumed to close the fd. EventFD is Linux-only; other platforms use different wake mechanisms.

Test signals: net2 event-loop tests, wake/read behavior on Linux, and network benchmark scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/AsioReactor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/AutoCPointer.h -->
# sources/storage-engines/foundationdb/flow/include/flow/AutoCPointer.h

Purpose: RAII wrapper for C pointers that must be released by a matching C free function.

Important APIs/types/functions: template `AutoCPointer<T, R>` deriving protected from `std::unique_ptr<T, R (*)(T*)>`, constructor overloads, `operator bool`, `release`, `reset`, and implicit `operator T*`.

Control flow: construction stores pointer and deleter; destruction invokes the deleter through `unique_ptr`; `release` transfers ownership without freeing.

State/persistence: owns one C pointer in process memory.

Dependencies/integration: intended for OpenSSL and similar C APIs where functions accept raw `T*`. Implicit conversion reduces `.get()` noise.

Risks: implicit raw pointer conversion can hide ownership/lifetime mistakes. Deleter type must match exactly and tolerate null where applicable.

Test signals: compile-time use with C APIs and leak/error-path testing around reset/release.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/AutoCPointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/BenchMain.h -->
# sources/storage-engines/foundationdb/flow/include/flow/BenchMain.h

Purpose: shared benchmark executable harness that initializes Flow, runs Google Benchmark on a separate thread, and stops the network cleanly.

Important APIs/types/functions: `stopNetworkAfter(Future<Void>)` and `runBenchmarks(int,char**, std::function<void()>)`.

Control flow: initializes Google Benchmark and rejects unknown args, calls `platformInit`, `Error::init`, creates `g_network = newNet2(TLSConfig())`, runs optional extra init, starts a benchmark thread, signals completion back to the main Flow thread with `onMainThreadVoid`, awaits `benchmarksDone`, stops `g_network`, runs the network event loop, joins the thread, and returns.

State/persistence: assigns the global `g_network`; local promise coordinates thread completion.

Dependencies/integration: Google Benchmark, Flow platform/errors/network/TLS/thread helper. Used by `BenchMain.cpp`.

Risks: benchmark functions that require Flow main-thread work rely on this dual-thread/event-loop structure. Exceptions in `stopNetworkAfter` still stop the network and rethrow.

Test signals: running `flow_bench --benchmark_filter=...` successfully starts and stops net2.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/BenchMain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/BooleanParam.h -->
# sources/storage-engines/foundationdb/flow/include/flow/BooleanParam.h

Purpose: provides strong-ish typed boolean parameter wrappers to avoid ambiguous raw bool arguments.

Important APIs/types/functions: class `BooleanParam`; macros `FDB_DECLARE_BOOLEAN_PARAM`, `FDB_DEFINE_BOOLEAN_PARAM`, and `FDB_BOOLEAN_PARAM`.

Control flow: derived parameter classes wrap a bool and expose `True`/`False` static constants. Conversion to bool is constexpr.

State/persistence: each parameter object stores one bool. Static constants are inline definitions when macro-defined.

Dependencies/integration: used throughout Flow, including `FastInaccurateEstimate` and `IsSecureMem` in `Arena.h`.

Risks: implicit conversion back to bool means it prevents call-site ambiguity more than it enforces type safety internally. Macro use for nested classes requires correct fully qualified definitions.

Test signals: compile-time usability in APIs expecting named boolean params.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/BooleanParam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Buggify.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Buggify.h

Purpose: implements deterministic probabilistic fault-injection gates for simulation/testing.

Important APIs/types/functions: `P_EXPENSIVE_VALIDATION`, `BuggifySection`, `BuggifySectionHash`, generated general/client buggify globals and functions, `_buggify`, macros `EXPENSIVE_VALIDATION`, `CLIENT_BUGGIFY_WITH_PROB`, `CLIENT_BUGGIFY`, `buggify`, and Swift bridging helpers.

Control flow: each source file/line section is activated once based on deterministic random and cached in a map. If enabled and activated, individual calls fire based on another probability. Activation is added to `g_traceBatch` and dumped when `g_network` exists.

State/persistence: inline global probabilities and section maps store process-wide buggify state. Swift bridging uses a `std::map` keyed by string/line.

Dependencies/integration: deterministic random, Trace batching, global `g_network`, Swift bridging namespace. Used pervasively in simulation to inject rare behavior.

Risks: `BuggifySection` hashes/equality compare `const char*` file pointer identity, not string contents, while Swift uses string keys. Header inline globals are process-global and not thread-protected. Probabilities are mutable globals.

Test signals: simulation runs with general/client buggify enabled and trace batch records of activated sections.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Buggify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ChaosMetrics.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ChaosMetrics.h

Purpose: declares chaos/fault injection metrics and control singletons for disk, bit-flip, and S3 simulated faults.

Important APIs/types/functions: `ChaosMetrics`, `DiskFailureInjector`, `BitFlipper`, and `S3FaultInjector`.

Control flow: `ChaosMetrics` can clear counters and emit trace fields. `DiskFailureInjector` computes stall/throttle/disk delay from configured intervals and periods. `BitFlipper` stores a bit flip percentage. `S3FaultInjector` stores rates and operation multipliers for S3 errors/throttles/delays/corruptions.

State/persistence: singleton-style injectors hold process-wide chaos configuration. Metrics hold counters and start time.

Dependencies/integration: forward-declared `TraceEvent`; implementations elsewhere connect to simulation and tracing.

Risks: comments note a FIXME to clarify relation to broader simulation chaos. Rates are simple doubles without visible range enforcement in the header. Singleton mutable state needs disciplined reset between tests.

Test signals: trace fields from `ChaosMetrics`, simulation fault injection behavior, and explicit configuration of disk/S3/bit flip settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ChaosMetrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CodeProbe.h -->
# sources/storage-engines/foundationdb/flow/include/flow/CodeProbe.h

Purpose: defines FoundationDB code coverage probes, annotations, registration, tracing, and the `CODE_PROBE` macro.

Important APIs/types/functions: namespace `probe`; enums `AnnotationType`, `ExecutionContext`; context annotations `net2`, `sim2`; assertion annotations `NoSim`, `SimOnly` and boolean combinators; decoration `Rare`; functional `Deduplicate`; template `CodeProbeAnnotations`; interface `ICodeProbe`; template `CodeProbeImpl`; `registerProbe`, `functionNameFromInnerType`, and `CODE_PROBE` macro stack.

Control flow: `CODE_PROBE(condition, comment, annotations...)` defines compile-time string wrapper types, and when condition is true, obtains a singleton `CodeProbeImpl` and calls `hit()`. First hit traces covered state; annotations may assert context, suppress tracing, decorate trace events, or mark deduplication/context expectations.

State/persistence: each probe singleton owns atomic hit count and annotations. Registered probes form global coverage inventory in implementation files. Trace events persist coverage signals externally.

Dependencies/integration: Flow knobs and trace system; coveragetool scans `CODE_PROBE`/related macros. Used in simulation coverage reporting.

Risks: macro-generated types depend on line numbers and `COMPILATION_UNIT`. Assertion annotations can abort if probes fire in unexpected contexts. Static registration order must be handled safely by implementation.

Test signals: `printProbesXML/JSON`, missed-probe tracing, coveragetool output, and simulation/Joshua coverage runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CodeProbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CodeProbeUtils.h -->
# sources/storage-engines/foundationdb/flow/include/flow/CodeProbeUtils.h

Purpose: declares helper utilities for reporting code probes that were expected but not hit.

Important APIs/types/functions: `probe::traceMissedProbes(Optional<ExecutionContext> context)`.

Control flow: implementation elsewhere likely iterates registered probes and emits trace events for misses, optionally filtered by execution context.

State/persistence: no state in the header; depends on global probe registry from `CodeProbe.h`.

Dependencies/integration: includes `flow/CodeProbe.h` and `flow/Arena.h` for `Optional`.

Risks: behavior is only declared here; correctness depends on implementation matching annotation/context semantics in `CodeProbe.h`.

Test signals: simulation or net2 coverage runs that call `traceMissedProbes` and verify missed probe trace output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CodeProbeUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CompressedInt.h -->
# sources/storage-engines/foundationdb/flow/include/flow/CompressedInt.h

Purpose: defines an order-preserving compressed signed integer serialization wrapper.

Important APIs/types/functions: template `CompressedInt<IntType>` with `value` and `serialize(Ar&)`.

Control flow: deserialization reads a sign/unary-length header, inverts bytes for negative encodings, reconstructs value bytes, and reinverts negative values. Serialization flips negative values, writes nonzero value bytes, computes bit length and encoded length, sets sign/unary header bits, optionally bit-flips the encoded bytes for negatives, and writes bytes through `ar.serializeBytes`.

State/persistence: encoded form is persisted by archives; wrapper stores one integer value in memory.

Dependencies/integration: depends on archive serializer APIs and integer byte operations. Used where sorted binary encodings of signed integers are needed.

Risks: assumes `IntType` supports signed comparison to zero; unsigned instantiations may behave unexpectedly. The GCC diagnostic suppression hints at compiler warning sensitivity around buffer manipulation. Boundary values need careful testing.

Test signals: round-trip serialization tests, bytewise ordering tests for negative/zero/positive values, and max/min integer coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/CompressedInt.h -->
