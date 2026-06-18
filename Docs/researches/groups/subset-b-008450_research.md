# Research Report: subset-b-008450

This grouped report covers fdbrpc replication utilities, simulated external connectivity, stats and trace helpers, actor fuzzing, benchmarks, actor DSL tests, async file wrappers, transport-facing headers, monitoring headers, and allow-list utilities. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationUtils.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/ReplicationUtils.cpp

## Purpose
`ReplicationUtils.cpp` implements helper algorithms and randomized test scaffolding for FoundationDB replication policies. It evaluates policy selection fairness, finds reduced locality subsets that still satisfy a policy, validates combinations against policy constraints, builds synthetic locality maps, generates static and random policies, and exposes a unit test for the replication policy machinery.

## Important APIs, Types, and Functions
Key production-facing helpers include `ratePolicy`, `findBestPolicySet`, `findBestUniquePolicySet`, `validateAllCombinations`, `filterLocalityDataForPolicyDcAndProcess`, and the overloaded `filterLocalityDataForPolicy` variants. Test helpers include `createTestLocalityMap`, `getStaticPolicies`, `randomAcrossPolicy`, `testPolicy`, and `testReplication`. The code operates on `LocalitySet`, `LocalityMap<repTestType>`, `LocalityGroup`, `LocalityData`, `LocalityEntry`, and `IReplicationPolicy` implementations such as `PolicyOne`, `PolicyAcross`, and `PolicyAnd`.

## Control Flow
`findBestPolicySet` specializes the common `One` and `Across(zoneid, One)` shapes, then falls back to `findBestPolicySetExpensive`, which repeatedly samples policy solutions, adds random extras, restricts the locality set, rates the restricted set with repeated selections, and keeps the lowest mode concentration. `findBestUniquePolicySet` follows the same sample/rate structure while excluding entries that share the configured uniqueness key. `validateAllCombinations` clones an existing locality group, appends candidate items, enumerates bitmask combinations, and checks whether policy selection returns empty/non-empty results according to the requested validity expectation. `testReplication` reads `REPLICATION_*` environment controls, builds a synthetic locality map, chooses static or random policies, samples included servers, and either runs `findBestPolicySet` or validates `testPolicy`.

## State and Persistence Behavior
The file is mostly stateless aside from deterministic random use, `g_replicationdebug`, environment variables, policy caches from `getStaticPolicies`, and cached locality-set internals reset during tests. It does not persist cluster data. It mutates passed `LocalitySet` entries during randomized selection and strips fields from `LocalityData` in the filter helpers.

## Dependencies and Integration Points
It depends on `fdbrpc/ReplicationUtils.h`, `ReplicationPolicy.h`, `Replication.h`, `flow/Hash3.h`, `flow/Platform.h`, and `flow/UnitTest.h`. It integrates with the unit-test runner through `TEST_CASE("/fdbrpc/Replication/test")`, with simulation via `g_network->isSimulated()` assertions comparing simple and expensive algorithms, and with data-distribution style callers that need locality data reduced to policy-relevant keys.

## Risks and Edge Cases
`findBestPolicySetSimple` resizes `randomizedEntries` and then also pushes vectors, leaving leading empty vectors; the loop still works only because it cycles until enough entries are collected, but the extra empties are inefficient and fragile. The expensive search is randomized and can be costly for large policy/test counts. `filterLocalityDataForPolicyDcAndProcess` inserts dc/process keys but then calls `filterLocalityDataForPolicy(policy->attributeKeys(), ld)` instead of the augmented key set, so the function name and local inserts appear inconsistent. `validateAllCombinations` enumerates combinations exponentially and assumes `selectReplicas` succeeds.

## Test Signals
The direct signal is `/fdbrpc/Replication/test`, which forces validation and stop-on-error, then expects `testReplication()` to return zero errors. Benchmarks in this subset also call `createTestLocalityMap` and `PolicyAcross::selectReplicas`, providing performance signals for selected policy shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ReplicationUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.cpp

## Purpose
`SimExternalConnection.cpp` implements an `IConnection` adapter that lets simulated FoundationDB processes connect to real TCP endpoints through Boost.Asio. It is used for external-client style simulation tests, DNS resolution tests, and hostname resolution behavior while preserving Flow `Future` APIs.

## Important APIs, Types, and Functions
The file defines a static Boost `io_service`, `SimExternalConnectionImpl::connect`, `SimExternalConnectionImpl::onReadable`, all `SimExternalConnection` `IConnection` overrides, blocking and asynchronous `resolveTCPEndpoint` helpers, and three unit tests: `fdbrpc/SimExternalClient`, `fdbrpc/MockDNS`, and `/fdbrpc/Hostname/hostname`. `forceLinkSimExternalConnectionTests` ensures the object file is linked for tests.

## Control Flow
`connect` jitter-delays, converts `NetworkAddress` to a Boost endpoint, synchronously connects a socket, and returns either an invalid reference or a `SimExternalConnection`. `write` sends packet bytes via `SendBufferIterator`, sleeps briefly, reads all currently available echoed bytes into `readBuffer`, and triggers waiters if the buffer was previously empty. `onReadable` waits for jitter and then blocks on `onReadableTrigger` only if the local buffer is empty. DNS resolution uses Boost resolver synchronously, converts IPv4/IPv6 endpoints to public `NetworkAddress` values, adds them to the DNS cache, and reports failures as `lookup_failed`.

## State and Persistence Behavior
Connection state is per object: a Boost TCP socket, debug UID, a deque-backed read buffer, and an async readable trigger. DNS state is persisted only in the provided `DNSCache` and in mock endpoint registrations owned by `INetworkConnections`. There is no durable storage.

## Dependencies and Integration Points
The implementation depends on Boost.Asio, `flow/IConnection.h`, `flow/Net2Packet.h`, `SendBufferIterator`, `Hostname`, `UnitTest`, and `INetworkConnections::net()`. It integrates with simulation by providing a real external connection implementation and mock DNS handling inside the network abstraction.

## Risks and Edge Cases
Most socket operations are synchronous and can block the simulation thread. `write` assumes data becomes readable after a fixed `threadSleep(0.1)` and asserts on errors, making it test-oriented rather than production tolerant. `hasTrustedPeer` always returns true, which is appropriate for this test adapter but bypasses peer-auth semantics. The test echo server binds a fixed port `8000`, so parallel runs or occupied ports can fail.

## Test Signals
`fdbrpc/SimExternalClient` starts a local echo server, connects through `INetworkConnections`, writes random bytes, reads the echo, and asserts equality. `fdbrpc/MockDNS` verifies mock endpoint add/remove behavior. The hostname test verifies async, blocking, and retry resolution against a mock endpoint in simulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.h -->
# sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.h

## Purpose
`SimExternalConnection.h` declares the `SimExternalConnection` concrete `IConnection` used by simulation to communicate with external TCP services.

## Important APIs, Types, and Functions
`SimExternalConnection` inherits `IConnection` and `ReferenceCounted<SimExternalConnection>`. It exposes `close`, handshake methods, readability/writability futures, `read`, `write`, peer/debug accessors, `getSocket`, static endpoint resolution helpers, and static `connect`.

## Control Flow
The header establishes the interface contract; implementation is in the `.cpp`. Construction is private and only available to `makeReference` and `SimExternalConnectionImpl`, ensuring sockets are moved into reference-counted connection objects through the factory path.

## State and Persistence Behavior
The object owns a Boost TCP socket, debug UID, buffered read deque, and an `AsyncTrigger` for readability. State is in-memory and connection-scoped.

## Dependencies and Integration Points
It depends on Flow reference counting, `flow/network.h`, `flow/flow.h`, `flow/IConnection.h`, and Boost.Asio. It plugs into `INetworkConnections` implementations that need an `IConnection` reference.

## Risks and Edge Cases
The header exposes the raw Boost socket through `getSocket`, so callers can bypass `IConnection` sequencing. The trusted-peer answer is implemented as unconditional in the `.cpp`, so auth-sensitive callers should not mistake this adapter for a secure transport.

## Test Signals
The companion `.cpp` unit tests exercise construction, connect, read/write, DNS resolution, and hostname resolution through this declared interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Stats.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/Stats.cpp

## Purpose
`Stats.cpp` implements counter collections, periodic trace emission, latency bands, and latency samples for fdbrpc/Flow metrics. It bridges internal counters to `TraceEvent`, optional OpenTelemetry metrics, and StatsD message generation.

## Important APIs, Types, and Functions
Core methods include `Counter::operator+=`, `getRate`, `getRoughness`, `resetInterval`, `clear`, `CounterCollection::logToTraceEvent`, `CounterCollection::traceCounters`, `LatencyBands::addThreshold`, `LatencyBands::addMeasurement`, `LatencyBands::clearBands`, `LatencySample::addMeasurement`, and `LatencySample::logSample`.

## Control Flow
Counters accumulate interval deltas and squared inter-event timings. `traceCounters` delays once for initialization, resets all counters, then loops forever creating a trace event, logging every counter, applying a decorator, optionally tracking latest, and waiting the configured interval. `LatencyBands` lazily creates a `CounterCollection` when the first threshold is added, installs an infinity band and filtered counter, then places each measurement into the first upper-bound band. `LatencySample` records measurements in a DDSketch and periodically emits count, elapsed, min/max, mean, and percentiles, then clears the sketch.

## State and Persistence Behavior
All state is process-local and interval-based: counters, last event times, sketch buckets, event-cache tracking keys, random metric IDs, and recurring actor futures. No durable state is written. Emission mutates global metric collections when configured.

## Dependencies and Integration Points
The file depends on `fdbrpc/Stats.h`, `flow/IRandom.h`, `Knobs`, `OTELMetrics`, `TDMetric`, `Trace`, and `network`. It integrates with `MetricCollection::getMetricCollection`, `createStatsdMessage`, `createOtelGauge`, `TraceEvent::trackLatest`, and `g_network->getLocalAddress`.

## Risks and Edge Cases
`Counter` assumes non-empty names for capitalization. `Counter::getRoughness` can report negative sentinel values when no elapsed time exists. StatsD attribute vectors are currently built but not passed into message creation, so endpoint labels may be absent for StatsD. `LatencySample` labels `p50` using `sketch.mean()` while also logging `Median` as that value, which is semantically surprising. Periodic actors capture `this`, so owners must clear futures before destruction.

## Test Signals
Benchmarks in `BenchSamples.cpp` exercise `LatencyBands`, DDSketch-backed latency samples indirectly, and histogram sampling. Runtime trace output, OTEL histogram/gauge entries, and StatsD messages are the main integration signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/Stats.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/TraceFileIO.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/TraceFileIO.cpp

## Purpose
`TraceFileIO.cpp` provides optional debug-only tracking of file writes, reads, and truncates for a named file. In normal builds it compiles to no-op functions.

## Important APIs, Types, and Functions
The externally relevant functions are `debugFileCheck`, `debugFileSet`, and `debugFileTruncate`. When enabled, helpers include `debugFileSetup`, `debugFileTrim`, and `debugFileIsSet`, plus global maps for tracked data, masks, and regions.

## Control Flow
With `CENABLED(0, NOT_IN_CLEAN)` enabled, setup allocates memory for configured file regions and a page-sized all-ones mask. `debugFileSet` copies overlapping written bytes into the in-memory region and marks the mask. `debugFileCheck` compares a read buffer with fully or partially known bytes and emits warning trace events on mismatch. `debugFileTruncate` clears mask bytes after the truncation point. The compiled default path defines empty functions.

## State and Persistence Behavior
Enabled mode holds global heap buffers keyed by file-region offset and tracks only the hard-coded `debugFileName`. It does not write persistent diagnostics; it emits `TraceEvent`s. Default mode has no state.

## Dependencies and Integration Points
It depends on `fdbrpc/TraceFileIO.h` and Flow trace/assert utilities through included headers. `AsyncFileNonDurable` calls these hooks around simulated writes, reads, and truncates.

## Risks and Edge Cases
The enabled branch allocates large buffers and never frees them. It is manually configured by editing globals, so it is easy to track the wrong file or region. It is not thread-safe and uses assertions for internal assumptions. The disabled default can hide accidental dependence on these functions because all calls become no-ops.

## Test Signals
There are no direct unit tests here. Signals are trace events such as `DebugFileFail`, `DebugFileUnsetCheck`, and `DebugFileSkipping*` when a developer enables the debug branch and runs file I/O simulations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/TraceFileIO.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/actorFuzz.py -->
# sources/storage-engines/foundationdb/fdbrpc/actorFuzz.py

## Purpose
`actorFuzz.py` generates `ActorFuzz.actor.cpp`, a randomized suite of Flow actor control-flow tests. It creates actor functions with loops, waits, throws, returns, breaks, continues, try/catch blocks, and range-for loops, then computes expected output by interpreting the generated structure in Python.

## Important APIs, Types, and Functions
Generation state lives in `Context`; interpretation state lives in `ExecContext`. AST-like node classes include `hashF`, `compoundF`, `loopF`, `rangeForF`, `ifF`, `tryF`, `breakF`, `continueF`, `waitF`, `throwF`, `throwF2`, `throwF3`, and `returnF`. `fuzzCode` chooses node types, and `randomActor` builds one complete actor and expected-output list.

## Control Flow
The script opens `ActorFuzz.actor.cpp`, writes a header, includes `ActorFuzz.h`, skips Windows, generates 30 actors, and writes `actorFuzzTests()` that calls `testFuzzActor` for each generated actor with the expected outputs. `randomActor` retries on interpreted infinite loops, appends a fallback return, evaluates the AST against an infinite input sequence, and records final return or error code output.

## State and Persistence Behavior
The script persists one generated C++ file in the current working directory. Randomness is not seeded explicitly, so generated content changes across invocations. Class attributes such as `Context.tok`, `Context.indent`, and `ExecContext.iterationsLeft` are overridden per instance where needed.

## Dependencies and Integration Points
It depends only on Python `random` and `copy`. The generated C++ depends on Flow actor syntax and `fdbrpc/ActorFuzz.h`, and is consumed by `dsltest.actor.cpp` through `actorFuzzTests()`.

## Risks and Edge Cases
Unseeded generation makes diffs non-reproducible unless callers control Python randomness externally. The output path is relative, so running from the wrong directory writes the generated file elsewhere. The interpreter is a model of actor behavior, not the actor compiler itself; mismatches can reflect either compiler bugs or generator-model bugs. Python 3 style is mostly used, but the script has no command-line contract or deterministic manifest.

## Test Signals
The generated `actorFuzzTests()` returns passed/total counts. `dsltest()` prints the count and exercises each actor five times with different input/error timing through `testFuzzActor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/actorFuzz.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchAsyncFileWriteCheckerLRU.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchAsyncFileWriteCheckerLRU.cpp

## Purpose
This benchmark measures the update, remove, and truncate workload of `AsyncFileWriteChecker::LRU`, approximating random page tracking for a large file.

## Important APIs, Types, and Functions
The file defines `lru_test(benchmark::State&)` and registers it with `BENCHMARK(lru_test)`. It uses `AsyncFileWriteChecker::LRU`, `AsyncFileWriteChecker::WriteInfo`, deterministic random numbers, and a `std::set<uint32_t>` of existing pages.

## Control Flow
For each benchmark iteration, the test performs 10,000 operations. If the known set is small or a random draw is above 0.5, it updates a random page with a changing timestamp. If the random draw is below 0.45, it removes a random existing page. Otherwise it truncates to a random page in the first half and erases the local set tail.

## State and Persistence Behavior
State is in-memory inside the benchmark process: the LRU object and the local page set. It models a file up to `150000000` pages but does not touch disk.

## Dependencies and Integration Points
It depends on Google Benchmark, `AsyncFileWriteChecker.h`, and Flow deterministic random support. It integrates with the `fdbrpc_bench` target.

## Risks and Edge Cases
The local `exist` set persists across benchmark iterations, so later iterations benchmark a warmed and growing structure. Random `std::advance` over `std::set` is linear and contributes overhead that is not part of the LRU implementation. The comment says 600GB, which assumes 4KB pages.

## Test Signals
The signal is benchmark throughput and aggregate timing, not correctness assertions. Crashes or assertion failures in the LRU implementation are secondary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchAsyncFileWriteCheckerLRU.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchIONet2.actor.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchIONet2.actor.cpp

## Purpose
`BenchIONet2.actor.cpp` benchmarks Flow actor scheduling under mixed task priorities while also performing a small async file write and sync through the Net2 filesystem.

## Important APIs, Types, and Functions
Key functions are actor `increment`, `getRandomTaskPriority`, actor `benchIONet2Actor`, and benchmark wrapper `bench_ionet2`. The benchmark is registered over actor counts from 1 to 65536.

## Control Flow
Each benchmark loop resets a counter, creates `actorCount` `increment` actors with deterministic random priorities, opens `/tmp/__test-benchmark-file__` with atomic create/readwrite flags, writes 4096 zero bytes, syncs the file, and reports items processed. `increment` waits on a zero-delay at the chosen priority, performs CPU work with deterministic random values, prevents optimization, and increments the shared sum.

## State and Persistence Behavior
The benchmark writes a fixed temporary file path under `/tmp` and recreates or overwrites it during iterations. Actor state and random seeds are in-memory. The file may remain after benchmark execution depending on filesystem behavior.

## Dependencies and Integration Points
It depends on Flow actor compiler, `ThreadHelper.actor.h`, `IAsyncFile`, `flow/network.h`, and Google Benchmark. `bench_ionet2` enters the Flow main thread with `onMainThread`.

## Risks and Edge Cases
The fixed temp path can collide with concurrent runs. Opening and syncing a file inside each benchmark iteration mixes scheduler and filesystem costs. `sum` is shared by actors on the Flow thread; if execution assumptions change, it would need synchronization.

## Test Signals
Benchmark throughput across actor counts is the main signal. Successful execution also indicates the benchmark main initialized Net2 filesystem correctly and the Flow scheduler can process the actor burst.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchIONet2.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchMain.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchMain.cpp

## Purpose
`BenchMain.cpp` is the entry point for fdbrpc benchmarks. It initializes the Net2 filesystem and delegates command-line handling to the shared Flow benchmark runner.

## Important APIs, Types, and Functions
The file defines `initializeNet2FileSystem` and `main`. Initialization registers `Net2FileSystem::stop` as a network stop callback and installs a new Net2 filesystem.

## Control Flow
`main` calls `runBenchmarks(argc, argv, initializeNet2FileSystem)`. The benchmark runner owns benchmark registration, argument parsing, network setup, and execution; this file provides fdbrpc-specific filesystem setup.

## State and Persistence Behavior
It mutates process-global `g_network` callbacks and the global `IAsyncFileSystem` implementation. It does not persist data directly.

## Dependencies and Integration Points
It depends on `fdbrpc/Net2FileSystem.h` and `flow/BenchMain.h`. It is linked into the `fdbrpc_bench` executable built by the bench CMake file.

## Risks and Edge Cases
Benchmarks that assume a different filesystem implementation will inherit Net2. Stop-callback ordering matters if other benchmark initialization also registers filesystem or network cleanup.

## Test Signals
Successful startup and benchmark discovery indicate that Net2 filesystem initialization and benchmark registration are wired correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchMain.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSamples.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSamples.cpp

## Purpose
`BenchSamples.cpp` benchmarks sampling and histogram primitives used by fdbrpc metrics: DDSketch variants, `ContinuousSample`, `LatencyBands`, and Flow `Histogram`.

## Important APIs, Types, and Functions
Benchmarks include `bench_ddsketchUnsigned`, `bench_ddsketchInt`, `bench_ddsketchDouble`, `bench_ddsketchLatency`, `bench_continuousSampleInt`, `bench_continuousSampleLatency`, `bench_latencyBands`, `bench_histogramInt`, `bench_histogramPct`, and `bench_histogramTime`. `InputGenerator<T>` supplies precomputed random inputs.

## Control Flow
Each benchmark constructs the target sampler and an input generator, then loops over Google Benchmark iterations adding one sample per iteration. DDSketch benchmarks run at several error guarantees; continuous sample benchmarks run at different reservoir sizes; latency bands create thresholds before measurement.

## State and Persistence Behavior
All state is in-memory inside sampler objects. Histograms are obtained through `Histogram::getHistogram`, which may use process-global histogram registries. No durable output is produced.

## Dependencies and Integration Points
It depends on Google Benchmark, `BenchSupport.h`, `fdbrpc/Stats.h`, `fdbrpc/DDSketch.h`, `ContinuousSample.h`, `flow/Histogram.h`, and deterministic random support. It exercises the metric data structures used by runtime tracing and telemetry.

## Risks and Edge Cases
Precomputed random input avoids measuring random generation in the hot loop but uses deterministic global random during setup. Some benchmarks reuse the same sampler across all iterations, so bucket growth or saturation is part of the measurement. `bench_latencyBands` passes `false` as the third argument to `addMeasurement`, relying on bool conversion to the `Filtered` enum/type.

## Test Signals
Signals are throughput, aggregate timing, and successful execution without sampler assertions. They are performance tests rather than accuracy tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSamples.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSelectReplicas.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSelectReplicas.cpp

## Purpose
`BenchSelectReplicas.cpp` benchmarks `IReplicationPolicy::selectReplicas` for simple rack-across policies over synthetic locality maps.

## Important APIs, Types, and Functions
The central helper is `bench_select_replicas(int repCount, benchmark::State&)`, wrapped by `bench_select_replicas_tripple` and `bench_select_replicas_double`. It uses `PolicyAcross`, `PolicyOne`, `createTestLocalityMap`, `LocalityGroup`, and `LocalityEntry`.

## Control Flow
The benchmark constructs a rack policy, pre-warms `depth()` and `maxdepth()`, creates a synthetic locality map, copies entries into a vector sized by benchmark argument, and repeatedly clears the results vector before timing `policy->selectReplicas`. It registers triple-replica benchmarks with 4 and 8 servers and double-replica benchmarks with 2 and 8 servers.

## State and Persistence Behavior
State is in-memory and deterministic-random-derived through locality map creation. No persistent data is written.

## Dependencies and Integration Points
It depends on `fdbrpc/ReplicationPolicy.h`, `Replication.h`, `ReplicationUtils.h`, Flow arena support, and Google Benchmark. It directly reuses the replication utility test-map builder from this subset.

## Risks and Edge Cases
The synthetic topology is narrow and may not represent production locality diversity. The wrapper name `tripple` is misspelled but harmless. `SetItemsProcessed` is called inside the benchmark loop rather than after it, which is unusual for Google Benchmark usage.

## Test Signals
The main signal is measured `selectReplicas` throughput for fixed simple policies. Crashes or policy assertion failures indicate correctness issues in the selection path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSelectReplicas.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSupport.h -->
# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSupport.h

## Purpose
`BenchSupport.h` provides a small reusable `InputGenerator<T>` for fdbrpc benchmark files that need deterministic precomputed input values.

## Important APIs, Types, and Functions
`InputGenerator<T>` has a default constructor, a generator constructor taking `n` and a callable, and `next()` returning a const reference to the next precomputed value.

## Control Flow
The constructor reserves `n` values and fills the vector by repeatedly calling the supplied generator. `next()` increments `lastIndex`, wraps to zero at the end, and returns the current element.

## State and Persistence Behavior
State is process-local: a vector of generated values and the last returned index. It does not persist output.

## Dependencies and Integration Points
It depends on `flow/flow.h` for `ASSERT` and is included by `BenchSamples.cpp`.

## Risks and Edge Cases
The default constructor leaves `lastIndex` uninitialized, so callers must not call `next()` before constructing with data. `next()` assumes `data` is non-empty; only the generator constructor asserts `n > 0`.

## Test Signals
Benchmark success in `BenchSamples.cpp` exercises the generator's wrap-around behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/BenchSupport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbrpc/bench/CMakeLists.txt

## Purpose
This CMake file builds the `fdbrpc_bench` executable from all sources in the benchmark directory.

## Important APIs, Types, and Functions
It uses `include(FDBBenchmark)`, `fdb_find_sources(FDBRPC_BENCH_SRCS)`, `add_flow_target`, `fdb_setup_googlebenchmark`, `target_include_directories`, and `target_link_libraries`.

## Control Flow
CMake discovers benchmark sources, creates an executable target, sets up Google Benchmark, adds local include paths, and links threads, `fdb_google_benchmark`, `flow`, and `fdbrpc`.

## State and Persistence Behavior
It contributes build-system state only. Generated build artifacts are owned by the selected CMake build directory.

## Dependencies and Integration Points
It integrates with FoundationDB's CMake helpers and the shared Flow/fdbrpc libraries. The local include paths allow benchmark files to include `BenchSupport.h` and adjacent fdbrpc headers.

## Risks and Edge Cases
`fdb_find_sources` will include any new source dropped into the directory, which is convenient but can accidentally add experimental files. Include path `"${CMAKE_CURRENT_SOURCE_DIR}/include"` may be redundant unless a bench-local include directory exists.

## Test Signals
Successful configuration and build of `fdbrpc_bench` are the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/bench/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/dsltest.actor.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/dsltest.actor.cpp

## Purpose
`dsltest.actor.cpp` is a broad Flow actor DSL, future/promise, allocator, arena, async map, and microbenchmark test harness. It validates actor compiler control-flow behavior, generated actor fuzz cases, promise/stream primitives, and several low-level Flow utilities.

## Important APIs, Types, and Functions
Important functions include `testFuzzActor`, actor templates `addN`, `switchTest`, `chooseTest`, `achain`, `chain2`, `cycle`, and many actor control-flow tests `actorTest1` through `actorTest10`. Utility tests include `fastAllocTest`, `arenaTest`, `asyncMapTest`, `introPromiseFuture`, `introActor`, `chainTest`, `cycleTime`, `sleeptest`, `copyTest`, and top-level `dsltest`. Local types include `TestBuffer`, `FastKey`, `TestB`, `AddReply`, and `AddRequest`.

## Control Flow
`dsltest` seeds deterministic random state, runs async map checks, a 1000-node stream cycle, introductory promise/actor examples, actor control-flow cases, generated actor fuzz tests, many promise/future/stream performance loops, arena serialization/allocation tests, choose/add examples, switch tests, fast allocator tests, and optional thread-safety tests when `FLOW_THREAD_SAFE` is enabled. `testFuzzActor` drives a generated actor five times with varied input/error timing and compares all outputs against the Python-generated oracle.

## State and Persistence Behavior
State is almost entirely transient and printed to stdout. Some routines allocate large in-memory objects, mutate global deterministic random state, increment `fastKeyCount`, and create actor futures. Disabled `#if 0` blocks contain older memory and thread tests but do not run.

## Dependencies and Integration Points
The file depends on `fdbrpc/simulator.h`, `fdbrpc/ActorFuzz.h`, Flow actor compiler, deterministic random, thread helpers, `FastRef`, arenas, serialization, promises, streams, and async maps. It integrates with generated `ActorFuzz.actor.cpp` via `actorFuzzTests()`.

## Risks and Edge Cases
The file contains many microbenchmarks and old disabled experiments rather than clean unit tests. It prints heavily and uses blocking `.get()` patterns, so it is best suited to local test binaries rather than production paths. Some actor calls are made without awaiting returned futures, relying on immediate behavior and side effects. The TODO near the top questions whether the file is still needed.

## Test Signals
Signals are stdout messages, assertions, fuzz pass counts, and absence of actor compiler/runtime failures. Actor control-flow digits `1` through `10`, `AsyncMap: OK`, and actor fuzz passed/total counts are key visible markers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/dsltest.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/fdbrpc_test.cpp -->
# sources/storage-engines/foundationdb/fdbrpc/fdbrpc_test.cpp

## Purpose
`fdbrpc_test.cpp` is the main function for the fdbrpc unit-test executable.

## Important APIs, Types, and Functions
It defines `initializeSimulation()` and `main`. It uses `FDB_BOOLEAN_PARAM` declarations for `IsSimulated` and `Randomize`, `resetFlowKnobs`, `startUnitTestSimulator`, and `runUnitTests`.

## Control Flow
`main` calls `runUnitTests` with a `UnitTestRunnerConfig` named `fdbrpc` and an initialization function. Initialization resets Flow knobs for randomized simulation and starts the unit-test simulator.

## State and Persistence Behavior
It mutates global Flow knobs and starts simulator state for the process. It does not persist data directly.

## Dependencies and Integration Points
It depends on `fdbrpc/simulator.h`, `flow/Knobs.h`, `flow/UnitTestRunner.h`, and boolean parameter helpers. It is the executable entry point for the `TEST_CASE` definitions in fdbrpc sources.

## Risks and Edge Cases
All tests launched through this binary run under simulated/randomized knobs, so tests requiring real networking or non-simulated behavior need explicit guards. Initialization failure blocks the entire suite.

## Test Signals
The process exit code from `runUnitTests` is the primary signal. Individual fdbrpc `TEST_CASE` functions register into this runner.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/fdbrpc_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ActorFuzz.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ActorFuzz.h

## Purpose
`ActorFuzz.h` declares the interface between generated actor fuzz tests and the Flow actor DSL test harness.

## Important APIs, Types, and Functions
It defines inline `throw_operation_failed`, declares `testFuzzActor` with a signature adjusted for `OPEN_FOR_IDE`, and declares `actorFuzzTests()` returning passed and total counts.

## Control Flow
The header has no runtime control flow except `throw_operation_failed`, which throws `operation_failed()`. Generated actors include this helper to test actor compiler handling of throwing callees.

## State and Persistence Behavior
There is no persistent or mutable state.

## Dependencies and Integration Points
It depends on `flow/flow.h` and `std::vector`. `actorFuzz.py` generates a source file that includes this header, and `dsltest.actor.cpp` implements `testFuzzActor` and calls `actorFuzzTests()`.

## Risks and Edge Cases
The IDE signature differs from the compiled signature because actor compiler transformations handle references differently. Consumers must keep generated actor signatures aligned with this header and `dsltest.actor.cpp`.

## Test Signals
Successful compilation of generated `ActorFuzz.actor.cpp` and correct `actorFuzzTests()` pass counts are the direct signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/ActorFuzz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileCached.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileCached.h

## Purpose
`AsyncFileCached.h` declares and largely implements an `IAsyncFile` wrapper that adds an in-memory page cache with random or LRU eviction, dirty-page flushing, zero-copy reads, truncate ordering, metrics, and shared open-file tracking.

## Important APIs, Types, and Functions
Core types are `EvictablePage`, `EvictablePageCache`, `AsyncFileCached`, and `AFCPage`. Important APIs include `AsyncFileCached::open`, `read`, `write`, `readZeroCopy`, `releaseZeroCopy`, `truncate`, `changeFileSize`, `sync`, `flush`, `quiesce`, and template `read_write_impl`. `AFCPage` provides `evict`, `orphan`, `write`, `read`, `readZeroCopy`, `releaseZeroCopy`, `readThrough`, `writeThrough`, `flush`, `quiesce`, and `truncate`.

## Control Flow
`open` deduplicates by filename using `openFiles`, opens an uncached/unbuffered underlying file, records size, and returns a cached wrapper. Reads and writes are split into pages by `read_write_impl`; page reads either hit valid cached data or start/merge underlying reads. Writes mark pages dirty, read missing partial pages when needed, and can orphan buffers when zero-copy readers still hold them. `flush` writes dirty pages through, respecting optional rate control. `truncate_impl` serializes truncates and makes writes that extend past the in-flight truncate wait.

## State and Persistence Behavior
Persistent storage remains the wrapped `IAsyncFile`; cache state is in-memory. `AsyncFileCached` tracks file length, previous length, page map, flushable page list, current truncate future/size, rate control, orphaned zero-copy buffers, and many metric handles. `EvictablePageCache` tracks allocated pages globally for a cache instance and evicts randomly or via intrusive LRU.

## Dependencies and Integration Points
It depends on Boost intrusive lists, Flow futures, `IAsyncFile`, knobs, metrics, deterministic random, and network simulation flags. It integrates with the filesystem layer as an `IAsyncFile` implementation and with telemetry through `Int64MetricHandle`.

## Risks and Edge Cases
Correctness depends on careful coordination of `notReading`, `notFlushing`, dirty flags, zero-copy ref counts, and orphaned pages. Eviction may exceed limits if pages are not immediately evictable. `openFiles` is a static weak-future map keyed only by filename and must be erased on open errors. Partial-page writes require valid read-through data, so read failures can poison subsequent waits. LRU intrusive hooks require pages to be removed consistently before destruction.

## Test Signals
Signals include async-file tests elsewhere in the repository, cache metric counters, trace events such as `AFCUnderlyingOpen*`, and the LRU benchmark in this subset for eviction-related support code.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileCached.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileEncrypted.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileEncrypted.h

## Purpose
`AsyncFileEncrypted.h` declares an `IAsyncFile` wrapper for AES-256-GCM encrypted append-only files with read-only and append-only modes.

## Important APIs, Types, and Functions
`AsyncFileEncrypted` exposes `Mode { APPEND_ONLY, READ_ONLY }`, constructor `AsyncFileEncrypted(Reference<IAsyncFile>, Mode, int)`, reference counting overrides, `read`, `write`, `zeroRange`, `truncate`, `sync`, `flush`, `size`, `getFilename`, zero-copy methods, and `debugFD`. Private helpers include `getIV`, `writeLastBlockToFile`, and `initialize`.

## Control Flow
The header declares the control surface; implementation elsewhere initializes encryption state, derives IVs per block, buffers append data, writes encrypted blocks, and decrypts reads. Append-only mode maintains current block and offset; read-only mode serves decrypted reads over the wrapped file.

## State and Persistence Behavior
Durable bytes are stored encrypted in the wrapped file. In-memory state includes the first block IV, mode, cached file size, encryption stream cipher, current block number, offset within the encryption block, write buffer, and encryption block size.

## Dependencies and Integration Points
It depends on `flow/IAsyncFile.h`, Flow reference counting, deterministic random support, and `flow/StreamCipher.h`. It integrates with any FoundationDB code that can consume an `IAsyncFile` while requiring encryption at rest.

## Risks and Edge Cases
Append-only semantics mean random writes, truncation, and zeroing need strict mode enforcement. IV derivation and block-boundary handling are security-critical. The header exposes zero-copy methods but encrypted data generally cannot be returned as stable raw underlying buffers without decryption ownership handling.

## Test Signals
Relevant signals are encryption wrapper tests, round-trip read/write checks, append boundary tests, sync/flush behavior, and failure of unsupported mutation methods in read-only mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileEncrypted.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileNonDurable.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileNonDurable.h

## Purpose
`AsyncFileNonDurable.h` implements simulation-only async file wrappers that model shutdown, process detachment, delayed writes, non-durable sync, dropped writes, corrupted sectors, dropped truncates, and power-failure behavior.

## Important APIs, Types, and Functions
Helpers include `sendOnProcess`, `sendErrorOnProcess`, `waitShutdownSignal`, and template `sendErrorOnShutdown`. `AsyncFileDetachable` wraps a file that can detach on shutdown. `AsyncFileNonDurable` implements `open`, `read`, `write`, `truncate`, `sync`, `size`, `kill`, `removeOpenFile`, and close handling. Internal actors include `checkKilled`, `onRead`, delayed `write`, delayed `truncate`, `onSync`, `sync`, `onSize`, and `closeFile`.

## Control Flow
Public writes and truncates create promises that are completed once the operation has logically started, while internal actors delay actual underlying I/O according to disk parameters and simulation speed. Pending modification ranges are tracked so reads wait for overlapping writes/truncates. `sync(true)` forces pending operations to finish durably and syncs the wrapped file. `kill()` calls `sync(false)`, signals pending operations to stop delaying, and may write correctly, drop data, corrupt sectors, drop truncates, or sometimes sync depending on randomized kill mode and prior sync state.

## State and Persistence Behavior
The wrapped file holds durable data; `AsyncFileNonDurable` overlays in-memory pending modifications, approximate size, lower-bound size after modifications, killed/killComplete promises, sync trigger promise, disk parameters, `hasBeenSynced`, kill mode, and actor collection. It also has static `filesBeingDeleted` and open-file map interactions.

## Dependencies and Integration Points
It depends on Flow actors, `IAsyncFile`, simulator APIs, `TraceFileIO`, `RangeMap`, disk parameter helpers, knobs, and process switching through `g_simulator`. It integrates into simulation file systems to test storage recovery under non-durable writes.

## Risks and Edge Cases
This code is intentionally fault-injecting, so callers must expect injected `io_error`s and corruption. Pending range tracking must remain consistent with `minSizeAfterPendingModifications`; bugs can allow reads before overlapping writes settle. `delref` starts asynchronous close/delete behavior and must avoid using object fields after kill completion can delete the wrapper. AIO mode asserts page-aligned writes.

## Test Signals
Simulation storage tests that reboot or kill processes are the main signals. Trace events such as `AsyncFileNonDurable_BadWrite`, `DroppedWrite`, `DroppedTruncate`, and debug file checks show injected behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileNonDurable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileReadAhead.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileReadAhead.h

## Purpose
`AsyncFileReadAhead.h` implements a read-only `IAsyncFile` wrapper that reads larger blocks, prefetches blocks ahead of the requested range, caches block futures, and limits concurrent underlying reads.

## Important APIs, Types, and Functions
The main type is `AsyncFileReadAheadCache` with nested `CacheBlock`. Key methods are static `readBlock`, static `read_impl`, `read`, unsupported `write`/`truncate`, `sync`, `flush`, `size`, unsupported `readZeroCopy`, `releaseZeroCopy`, `debugFD`, and `getFilename`.

## Control Flow
`read_impl` validates the requested range against file size, clips reads at EOF, computes the block range, starts needed block reads plus configured read-ahead blocks, stores futures in `m_blocks`, waits for needed blocks, copies requested byte ranges into the caller buffer, and evicts unpinned cache entries if the cache exceeds the block limit. `readBlock` takes a `FlowLock` permit, reads into a `CacheBlock`, and releases the permit on success or error.

## State and Persistence Behavior
The wrapped file remains the source of persistent data. The wrapper stores block size, read-ahead count, cache limit, concurrency lock, and a map from block number to future `CacheBlock`s. The destructor cancels cached block futures.

## Dependencies and Integration Points
It depends on Flow futures, `IAsyncFile`, and `FlowLock`. It can wrap any read-only async file where sequential or near-sequential reads benefit from prefetch.

## Risks and Edge Cases
The cache is ordered by block number, not LRU, so eviction favors low block numbers when over limit. Future reference counts are used to determine pinned blocks; misuse could retain large blocks longer than expected. `readZeroCopy` is explicitly unsupported. Errors in cached futures cause a block to be restarted on later reads.

## Test Signals
Read-ahead behavior is signaled by correct read results across block boundaries, EOF clipping, concurrent read limiting, and absence of `ReadZeroCopyNotSupported` except when that unsupported API is intentionally called.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileReadAhead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/DDSketch.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/DDSketch.h

## Purpose
`DDSketch.h` implements approximate quantile sketches for non-negative values, including fast floating-point, slow logarithmic, and fixed-accuracy unsigned integer variants.

## Important APIs, Types, and Functions
`fastLogger` provides `fastlog` and `reverseLog`. `DDSketchBase<Impl,T>` implements sample insertion, `mean`, `median`, `percentile`, `min`, `max`, `getSum`, `clear`, `getPopulationSize`, `getErrorGuarantee`, `getBucketSize`, `getSamples`, and `mergeWith`. Concrete implementations are `DDSketch<T>`, `DDSketchSlow<T>`, and `DDSketchFastUnsigned`.

## Control Flow
Adding a sample updates min/max/sum/population, counts near-zero samples separately, maps positive samples into a bucket through the implementation's `getIndex`, and increments that bucket. Percentile lookup computes a zero-based target rank, handles zero samples, then scans buckets upward for lower percentiles or downward for upper percentiles and converts the chosen bucket back to an estimated value. Merging asserts compatible error guarantees and bucket sizes, then adds bucket populations and summary fields.

## State and Persistence Behavior
Sketch state is in-memory: error guarantee, zero population, bucket vector, min, max, sum, and total population. No persistence is built in, but `getSamples` exposes bucket counts for telemetry export.

## Dependencies and Integration Points
It depends on standard math/vector algorithms and Flow `ASSERT`/unit-test support. `Stats.cpp` uses `DDSketch<double>` for latency samples and transport peers use sketches for ping/connect latencies.

## Risks and Edge Cases
The base class treats values below `1e-18` as zero and asserts huge values stay within allocated buckets. `DDSketch<T>` static-asserts little-endian systems. Bucket counters are `uint32_t`, so extremely long-lived sketches can overflow per bucket. `DDSketchSlow` references `DDSketch<T>::EPS` in its offset expression, which is equivalent through the base constant but visually odd.

## Test Signals
`BenchSamples.cpp` benchmarks all three major usage patterns. Accuracy tests elsewhere should check percentile error bounds, merge behavior, zero handling, and min/max/sum after clear.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/DDSketch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FailureMonitor.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FailureMonitor.h

## Purpose
`FailureMonitor.h` defines the failure-monitoring abstraction used by FoundationDB components to track unavailable addresses, missing endpoints, unauthorized endpoints, disconnects, and wait conditions for failure state changes.

## Important APIs, Types, and Functions
`FailureStatus` wraps a failed/available boolean and serializes it. `IFailureMonitor` declares state queries for endpoints and addresses, endpoint failure notifications, unauthorized notification, state-change futures, disconnect futures, permanent/endpoint-only/unauthorized checks, `notifyDisconnect`, `setStatus`, `onStateEqual`, `onFailed`, `onFailedFor`, and static `failureMonitor`. `SimpleFailureMonitor` implements the interface with address maps, endpoint maps, and async triggers.

## Control Flow
Transport and clients call `setStatus`, `endpointNotFound`, `unauthorizedEndpoint`, and `notifyDisconnect` as network events occur. Callers query current state or wait for futures such as `onStateChanged`, `onDisconnectOrFailure`, and `onFailedFor` before retrying or reconfiguring. New endpoints on healthy addresses are treated optimistically unless endpoint-specific failure is known.

## State and Persistence Behavior
State is process-local: address statuses, endpoint-known-failed async map, disconnect triggers, and endpoint failure reasons. It is resettable and not durable.

## Dependencies and Integration Points
It depends on Flow futures/maps, `FlowTransport.h` for `Endpoint`, and network globals. It integrates directly with `FlowTransport`, load balancing, data distribution, and callers using `g_network->failureMonitor()`.

## Risks and Edge Cases
The monitor is intentionally local and reactive, not an active failure detector. It can report temporary false failures or optimistic availability. Endpoint failures and address failures have different semantics, so callers must distinguish `onlyEndpointFailed` from full address failure. Future behavior depends on implementation in the companion source.

## Test Signals
Tests should cover address status transitions, endpoint-not-found behavior, unauthorized endpoints, disconnect triggers, `onFailedFor` timing, and reset behavior. Transport tests that close connections provide integration signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FailureMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowGrpc.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowGrpc.h

## Purpose
`FlowGrpc.h` declares optional gRPC backend globals and server management for FoundationDB when `FLOW_GRPC_ENABLED` is defined.

## Important APIs, Types, and Functions
`FlowGrpc` provides singleton access through `g_network` globals, `init`, `server`, `serverCreds`, and `clientCreds`. `GrpcServer` declares service registration, role-owned service registration/deregistration, `run`, `stopServer`, `shutdown`, `onRunning`, `onNextStart`, `onStop`, TLS checks, `hasStarted`, and test counter `numStarts`.

## Control Flow
`FlowGrpc::init` configures credentials and optionally creates a server for a local address. `GrpcServer::run` starts a server and returns a future that completes after shutdown; service-list changes trigger restarts after a short debounce. Workers register services under their UID and deregister them on restart or termination.

## State and Persistence Behavior
State is process-global through `g_network->global(INetwork::enGrpcState)`. `GrpcServer` stores address, async task executor, run actor, triggers, registered service map, underlying `grpc::Server`, credential provider, state enum, and start count. No durable state is stored.

## Dependencies and Integration Points
It depends on Flow futures/network/TLS, gRPC service/server types, async gRPC client/task executor, and credential providers. It integrates with worker roles that expose gRPC services and with TLS configuration refresh.

## Risks and Edge Cases
The entire header is conditional; callers must guard usage when gRPC is disabled. Server restart on service change can disrupt active clients. Stop methods may block synchronously in destructors or sync variants. Service ownership is by UID, so stale or reused IDs can affect deregistration behavior.

## Test Signals
Signals include server start count, `onRunning`/`onStop` futures, TLS-enabled checks, successful service registration/deregistration, and client calls against registered services in gRPC-enabled builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowGrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowTransport.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowTransport.h

## Purpose
`FlowTransport.h` declares the core fdbrpc transport interface: endpoint identity/serialization, message receivers, peer state, reliable/unreliable sending, endpoint registration, connection management, metrics, health, compatibility, peer trust, and public key support.

## Important APIs, Types, and Functions
Key types are `Endpoint`, `NetworkMessageReceiver`, `Peer`, `PeerCompatibilityPolicy`, and `FlowTransport`. Important APIs include endpoint construction/well-known tokens/serialization, `FlowTransport::createInstance`, `bind`, local address getters, peer reference management, endpoint registration/removal, `sendReliable`, `cancelReliable`, `sendUnreliable`, degraded/incompatible peer access, protocol-version async vars, `loadedEndpoint`, `loadedDisconnect`, `healthMonitor`, peer trust/current peer accessors, and public key load/watch methods.

## Control Flow
Endpoints carry address lists and tokens; deserialization adjusts primary address for TLS/secondary-address preferences. `FlowTransport` owns local endpoints and peers, binds listeners, sends packets reliably or unreliably, tracks peer references for streams and requests, and exposes transport-global state through `g_network`. `Peer` stores unsent/reliable queues, connection actors/triggers, ping/connect latency sketches, byte counters, compatibility state, and disconnect promise.

## State and Persistence Behavior
Transport state is process-global through `g_network`. Peer and endpoint state is in-memory: queues, counters, futures, protocol versions, health monitor, and public keys loaded from JWKS files. Public key files are read from disk by declared methods but key state is held in memory.

## Dependencies and Integration Points
It depends on `DDSketch`, `HealthMonitor`, Flow actors/network/protocol/packet/arena/public-key support, and `IPAllowList`. It is foundational for fdbrpc request/reply streams, failure monitoring, authorization, TLS address choice, and protocol compatibility.

## Risks and Edge Cases
Endpoint equality and hashing combine token and primary address, so address adjustment matters. Reliable packet lifetime must be explicitly cancelled. Compatibility and peer protocol state can change asynchronously. `Endpoint::isLocal` calls the global transport and requires an initialized instance. Public key file watching introduces filesystem and parsing failure modes in transport setup.

## Test Signals
Signals include transport unit/simulation tests for endpoint serialization, reliable delivery, missing/unauthorized endpoint handling, connection reset, incompatible peer tracking, peer metrics, and authorization token validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowTransport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HTTP.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HTTP.h

## Purpose
`HTTP.h` declares lightweight HTTP request/response parsing, writing, client request execution, proxy CONNECT support, and simulation HTTP server registration primitives used by fdbrpc components such as blob storage integrations.

## Important APIs, Types, and Functions
The namespace defines status code constants, verb constants, case-insensitive `Headers`, URL/URI encoding helpers, MD5 helpers, `HTTPData<T>`, request/response base templates, `IncomingRequest`, `OutgoingRequest`, `IncomingResponse`, `OutgoingResponse`, `doRequest`, `proxyConnect`, `registerAlwaysFailHTTPHandler`, `IRequestHandler`, `SimRegisteredHandlerContext`, and `SimServerContext`.

## Control Flow
Incoming request/response types read from an `IConnection`; outgoing responses write to one. `doRequest` sends an outgoing request to a connection under optional send/receive rate controls and parses the incoming response. `proxyConnect` establishes a tunnel through an HTTP proxy. Simulation server contexts register handlers, bind listeners, and route incoming requests to cloned request handlers.

## State and Persistence Behavior
HTTP data is per request/response. Simulation server contexts store handler registration, DNS addresses, listener futures, actor collections, and running state. There is no durable persistence.

## Dependencies and Integration Points
It depends on Flow networking, `IConnection`, rate control, packet queues, actor collections, and network addresses. It integrates with simulated HTTP servers, blob-store clients, and proxy-aware outbound connections.

## Risks and Edge Cases
Header handling is case-insensitive but still string-based. Content length and MD5 validation depend on implementation in the corresponding source. Handler cloning must avoid sharing per-instance mutable state, as documented. `isHeaderOnlyResponse` treats DELETE and CONNECT as header-only, which must match caller expectations.

## Test Signals
Signals include HTTP parser/writer tests, blob-store request tests, proxy CONNECT tests, MD5 verification behavior, and simulation handlers receiving expected requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HTTP.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HealthMonitor.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HealthMonitor.h

## Purpose
`HealthMonitor.h` declares a small peer health tracker that records recently closed connections and flags peers with too many closures.

## Important APIs, Types, and Functions
`HealthMonitor` exposes `reportPeerClosed`, `tooManyConnectionsClosed`, `closedConnectionsCount`, and `getRecentClosedPeers`. Private state is maintained by `purgeOutdatedHistory`, `peerClosedHistory`, and `peerClosedNum`.

## Control Flow
Callers report a closed peer address. Query methods purge outdated history, count recent closures, and return either a threshold decision, a per-peer count, or the set of peers with recent closures.

## State and Persistence Behavior
State is in-memory: a deque of timestamp/address pairs and a map of address to recent close count. No state persists across process restart.

## Dependencies and Integration Points
It depends on Flow time/network address types and standard containers. `FlowTransport` exposes a `healthMonitor()` accessor and likely uses this to inform connection health/degradation logic.

## Risks and Edge Cases
The thresholds and history window are hidden in implementation, so callers must treat results as heuristic. The data structure is not inherently thread-safe. If purge is only called on queries, inactive monitors can retain stale history until queried.

## Test Signals
Tests should report repeated closes for one peer, verify count and threshold behavior, then advance time or purge to confirm old entries expire.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HealthMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/IPAllowList.h -->
# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/IPAllowList.h

## Purpose
`IPAllowList.h` declares subnet parsing and IP-address allow-list checks used to restrict trusted peers by IPv4 or IPv6 subnet.

## Important APIs, Types, and Functions
`AuthAllowedSubnet` stores a base address and address mask, constructs from strings, builds bit masks, matches `IPAddress` values through `operator()`, returns netmask/netmask weight, and has debug printing. `IPAllowList` stores subnet entries, exposes `addTrustedSubnet` overloads, `subnets`, and `operator()` for allow checks.

## Control Flow
Callers add trusted subnets as strings or parsed subnet objects. A check returns true for all addresses when the list is empty, otherwise it iterates subnets and returns true on the first match. IPv4 and IPv6 masks are kept separate; mismatched address families never match.

## State and Persistence Behavior
State is an in-memory vector of allowed subnets. There is no persistence, though callers may construct it from config files or command-line options.

## Dependencies and Integration Points
It depends on Flow `IPAddress`, `network.h`, and arena includes. `FlowTransport` accepts an `IPAllowList const*` during instance creation, making it part of transport authentication/trust decisions.

## Risks and Edge Cases
An empty allow list means allow all, which is convenient but security-sensitive. Correctness depends on robust `fromString` parsing and netmask validation in the implementation. Address-family mismatches are rejected, so dual-stack deployments need both IPv4 and IPv6 entries when appropriate.

## Test Signals
Tests should cover IPv4 and IPv6 CIDR parsing, boundary mask weights, empty-list allow-all behavior, nonmatching families, and multiple subnet ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/IPAllowList.h -->
