# Research Group subset-b-008503

This grouped report covers FoundationDB Flow public headers under `sources/storage-engines/foundationdb/flow/include/flow`. Each section is delimited for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TreeBenchmark.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TreeBenchmark.h

## Purpose
`TreeBenchmark.h` is a small benchmarking harness for ordered tree-like containers. It compares a target tree implementation against a standard-map-shaped API by generating deterministic random keys, measuring insert/find/bounds/scan/erase throughput, and asserting basic ordering correctness.

## Important APIs, Types, And Functions
`opTimer` records `timer()` at construction and prints Kops/sec at destruction. `timedRun(name, t, f)` applies a callable to every element in a range while timing. `MapHarness<K>` adapts `std::map<K, int>` to the expected tree interface with `insert`, `find`, `not_found`, `begin`, `end`, `lower_bound`, `upper_bound`, and `erase`. `treeBenchmark(T& tree, F generateKey)` is the main benchmark driver. `randomStr(Arena&)` and `randomInt()` are canned key generators using `deterministicRandom()`.

## Control Flow
`treeBenchmark` creates one million keys, times insertion and lookup-style operations, sorts and uniquifies keys, scans from the first lower bound while checking every key matches the iterator sequence, shuffles keys, erases all keys, and finally asserts the tree is empty. Timers are scoped so each phase prints when its `opTimer` destructs.

## State And Persistence Behavior
All state is in-memory benchmark state: generated keys, an arena for random strings supplied by callers, and the tested container. There is no persistent state. Deterministic randomness makes simulation and repeated benchmark runs reproducible, subject to the caller's random seed.

## Dependencies And Integration Points
It depends on `flow/flow.h` for `timer`, `ASSERT`, `StringRef`, `Arena`, and deterministic RNG. The target tree must expose `key_type` and a map-like ordered iterator API. It is suitable for Redwood/IndexedSet-style data-structure tests rather than production runtime paths.

## Risks And Edge Cases
The benchmark assumes all generated keys can be inserted and later found; duplicate keys are only removed after the initial lookup/bounds phases, so containers with non-unique behavior or different duplicate semantics can fail. `upper_bound` is not asserted, only executed. The scan starts at `*keys.begin()`, so an empty key set would be invalid, though current key count prevents that.

## Test Signals
Useful signals are successful assertions for find, lower-bound, scan order, sorted find, and final empty state, plus stable throughput output across runs. For new tree implementations, failures in the scan phase usually point to ordering or iterator increment bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TreeBenchmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TxnCounters.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TxnCounters.h

## Purpose
`TxnCounters.h` declares a tiny transaction-counter bundle used to expose started, committed, and aborted counts through Flow's `SimpleCounter` infrastructure.

## Important APIs, Types, And Functions
`TxnCounters` stores three `SimpleCounter<int64_t>*` fields: `started`, `committed`, and `aborted`. `makeCounters(const char* prefix)` allocates the bundle and creates counters named `<prefix>/started`, `<prefix>/committed`, and `<prefix>/aborted`.

## Control Flow
The header is allocation-only. Callers pass a metric prefix, receive a heap-allocated `TxnCounters`, and increment the returned counters elsewhere as transaction lifecycle events occur.

## State And Persistence Behavior
The counters are process-local metrics. They are not durable database state. `makeCounters` uses `new` and returns raw pointers with no ownership wrapper, so the intended lifetime is effectively process/global metric lifetime.

## Dependencies And Integration Points
It depends on `flow/SimpleCounter.h`. Integration points are components that want standardized transaction lifecycle counters without repeating metric names.

## Risks And Edge Cases
The ownership model is the main risk: repeated calls with dynamic prefixes can leak `TxnCounters` and counter objects. Counter naming collisions are possible if multiple subsystems reuse a prefix.

## Test Signals
Tests should verify metric names and that lifecycle code increments the right counter. Because this file has no behavior beyond construction, most coverage is indirect through metrics emitted by transaction-serving components.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TxnCounters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TypeTraits.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TypeTraits.h

## Purpose
`TypeTraits.h` provides small compile-time helpers for manipulating `std::variant` types in template-heavy Flow code.

## Important APIs, Types, And Functions
`variant_concat_t<L, R>` concatenates two `std::variant` type lists. `variant_concat<L, R>` is the alias for its `type`. `variant_map_t<T, Fun>` maps a unary type-template over each alternative of a variant, and `variant_map<T, Fun>` is the alias.

## Control Flow
All behavior is compile-time type transformation. There is no runtime control flow, storage, or function dispatch.

## State And Persistence Behavior
No state is held and nothing is persisted. The impact is on template instantiation and ABI of code that uses the produced variant types.

## Dependencies And Integration Points
It depends only on `<variant>`. It integrates with serialization, RPC, and generic code that builds variant alternatives programmatically.

## Risks And Edge Cases
The file warns that template metaprogramming can increase compile times, especially when used from common headers. It only handles exactly `std::variant` inputs; passing non-variant types gives template errors rather than graceful diagnostics.

## Test Signals
Compile-time tests using `static_assert(std::is_same_v<...>)` are enough: concat should preserve left-to-right order, and map should transform every alternative exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TypeTraits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/UnitTest.h -->
# sources/storage-engines/foundationdb/flow/include/flow/UnitTest.h

## Purpose
`UnitTest.h` defines Flow's lightweight unit-test registration framework. It supports synchronous and actor-based `Future<Void>` tests, optional randomized tests, and named parameters for test execution.

## Important APIs, Types, And Functions
`UnitTestParameters` stores string parameters and an optional data directory, with setters and typed getters for strings, integers, and doubles. `UnitTest` records a test name, source file, line, function pointer, and linked-list `next`. `UnitTestCollection` holds the global list head `g_unittests`. `TEST_CASE(name)` registers a static `UnitTest` unless `FLOW_DISABLE_UNIT_TESTS` is defined. `ACTOR_TEST_CASE(actorname, name)` is generated by the actor compiler for actor test bodies. `noUnseed` disables RNG-state checking after simulation runs.

## Control Flow
Static initialization constructs `UnitTest` objects and links them into `g_unittests`. Test runners iterate the list and invoke each registered `Future<Void> (*)(const UnitTestParameters&)`. In `.actor.cpp` files, the actor compiler rewrites `TEST_CASE` bodies into actor-compatible functions and emits `ACTOR_TEST_CASE`.

## State And Persistence Behavior
Registration state is process-global and non-durable. `UnitTestParameters::dataDir` points tests at per-run persistent scratch directories, but this header only stores the directory name.

## Dependencies And Integration Points
It depends on `flow/flow.h`. Integration points include `UnitTestRunner`, `UnitTestWorkload`, fdbserver/fdbclient unit-test mains, and many `TEST_CASE` declarations across Flow, fdbrpc, fdbclient, and fdbserver.

## Risks And Edge Cases
Static registration depends on link inclusion, so unlinked translation units silently omit tests. Tests can mutate global Flow state and the comments explicitly warn that tests that pass under `fdbserver -r unittests` can still break simulation. `FLOW_DISABLE_UNIT_TESTS` keeps function declarations but suppresses registration.

## Test Signals
Signals include test discovery by path, parameter parsing, data-directory propagation, actor test registration after actor compilation, RNG-state checking in simulation, and clean behavior when tests are disabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/UnitTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/UnitTestRunner.h -->
# sources/storage-engines/foundationdb/flow/include/flow/UnitTestRunner.h

## Purpose
`UnitTestRunner.h` declares the common executable-side interface for running Flow unit tests with suite-specific configuration and optional simulation initialization.

## Important APIs, Types, And Functions
`UnitTestRunnerConfig` stores a source subdirectory/suite name and an optional `SimulationInitializer` callback returning `Future<Void>`. It exposes `suiteName()`, `dataDir()`, `traceName()`, `supportsSimulation()`, and `initializeSimulation()`. `runUnitTests(int argc, char** argv, const UnitTestRunnerConfig& config)` is the public entry point.

## Control Flow
Unit-test main programs construct a config, optionally supply simulation initialization, and call `runUnitTests`. The implementation parses CLI arguments, selects registered tests from `g_unittests`, sets up traces/data directories, and invokes the simulation initializer when requested.

## State And Persistence Behavior
The config stores string views and callback state only. Runtime persistence is limited to test data directories and trace files created by the runner implementation, not by this header.

## Dependencies And Integration Points
It depends on `flow/flow.h` and standard functional/string headers. It integrates with fdbserver and fdbclient unit-test binaries and the global registration surface from `UnitTest.h`.

## Risks And Edge Cases
`sourceSubDir` is stored as `std::string_view`, so callers must pass storage with sufficient lifetime, usually a string literal. Suites without a simulation initializer must report `supportsSimulation() == false` to avoid invalid simulation setup.

## Test Signals
Signals include correct suite naming, trace/data directory naming, command-line filtering, simulation initialization only for supported suites, and successful execution through representative unit-test mains.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/UnitTestRunner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Util.h -->
# sources/storage-engines/foundationdb/flow/include/flow/Util.h

## Purpose
`Util.h` contains small generic utilities used across Flow and storage tooling: text key/value parsing, vector removal, scoped counters, and human-readable formatting helpers for bytes, durations, progress, throughput, ETA, elapsed time, and UTC timestamps.

## Important APIs, Types, And Functions
`keyValueReader<K,V>(istream, consumer)` reads line-oriented key/value pairs and stops when the consumer returns false. `swapAndPop(C*, int)` removes an element without preserving order. `Hold<T>` increments a pointed counter on construction and decrements on destruction or `release()`, with move support. Formatting helpers include `formatBytesHumanReadable`, `formatDurationHumanReadable`, `formatBytesProgress`, `formatThroughputLine`, `formatETALine`, `formatElapsedTimeLine`, and `formatTimeISO8601`.

## Control Flow
`keyValueReader` loops line by line, resets a `stringstream`, attempts `operator>>` extraction for key and value, ignores parse failures and trailing text, and invokes the consumer until it returns false. `Hold` is RAII control flow around a counter. Formatting functions branch on units and return preformatted strings.

## State And Persistence Behavior
The only stateful type is `Hold`, which mutates an external counter. There is no persistence; formatting output is transient display text.

## Dependencies And Integration Points
It depends on standard algorithms, strings, streams, time, and formatting C APIs. It is included by generic actors and can be used in CLI/status output, progress reporting, bulk operation output, and simple parsers.

## Risks And Edge Cases
`keyValueReader` reuses `key` and `value`; callers should treat consumer inputs as values for the current successful parse only. `swapAndPop` changes order and assumes a valid index. `Hold` is not copyable and is not atomic; it should not be used for unsynchronized cross-thread counters. Formatting functions use fixed buffers and integer casts; very large values should be reviewed.

## Test Signals
Tests should cover malformed key/value lines, early consumer stop, swap/pop order behavior, move and release behavior for `Hold`, and formatting thresholds at bytes/KB/MB/GB/TB, duration boundaries, optional totals, and UTC timestamp output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/Util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WatchFile.h -->
# sources/storage-engines/foundationdb/flow/include/flow/WatchFile.h

## Purpose
`WatchFile.h` provides an actor helper that polls a file's last-write time and triggers an `AsyncTrigger` when the file changes or becomes stat-able again after an I/O-style stat error.

## Important APIs, Types, And Functions
`watchFileForChanges(std::string filename, AsyncTrigger* fileChanged, const int* intervalSeconds, const char* errorType)` is the only API. It uses `IAsyncFileSystem::filesystem()->lastWriteTime`, `TraceEvent`, `delay`, and `AsyncTrigger`.

## Control Flow
An empty filename waits forever. Otherwise the actor records the first observed modification time, then loops: stat the file asynchronously, trigger when the timestamp differs or a prior stat error was seen, log warning events for `io_error`, and delay for `*intervalSeconds`.

## State And Persistence Behavior
The actor keeps `firstRun`, `statError`, and `lastModTime` in memory. It does not persist state and does not read file contents. It observes filesystem metadata only.

## Dependencies And Integration Points
It depends on `IAsyncFile.h` and `genericactors.actor.h`. The comments indicate use for certificate/config-style file watching, where losing access should warn loudly without necessarily crashing if previously loaded data remains usable.

## Risks And Edge Cases
`intervalSeconds` and `fileChanged` are raw pointers that must outlive the actor. Timestamp resolution can miss rapid repeated writes. All `io_error` causes are grouped together, including permission and missing-file cases. Non-`io_error` exceptions propagate and stop the actor.

## Test Signals
Tests should simulate initial stat, file modification, missing/inaccessible files, recovery after stat errors, empty filename never firing, and cancellation. Integration signals are reload triggers for TLS/config file changes and warning trace emission on stat failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WatchFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WipedString.h -->
# sources/storage-engines/foundationdb/flow/include/flow/WipedString.h

## Purpose
`WipedString.h` defines `WipedString`, a restricted string wrapper for sensitive data. It stores bytes in wipe-after-use arena memory and ensures serialized buffers containing its content are marked for wiping when the serialization context supports that hook.

## Important APIs, Types, And Functions
`detail::WipedStringSerdesWrapper` wraps a `StringRef` only for custom serialization traits. The `is_wipe_enabled` concept detects `context.markForWipe(uint8_t*, size_t)`. `dynamic_size_traits<WipedStringSerdesWrapper>` copies bytes, calls `markForWipe`, and tracks wiped areas under the keepalive allocator used by tests. `WipedString` offers constructors from `StringRef`, optional external `Arena`, copy/move defaults, conversion to `StringRef`, `contents()`, and `serialize(Archive&)`.

## Control Flow
Construction copies input bytes into an arena allocation tagged `WipeAfterUse`. Serialization wraps the internal `StringRef` and delegates to `serializer`; saving copies bytes to the output buffer and marks that output range for wiping if supported. Loading delegates to `StringRef` dynamic-size loading.

## State And Persistence Behavior
State is an `Arena` plus a `StringRef` into wipe-enabled memory. The class is designed to minimize sensitive data lifetime in memory, but the header notes deserialized `WipedString` currently does not make the deserialized instance wipe on destruction because there is no need for that path.

## Dependencies And Integration Points
It depends on Flow serialization traits, `Arena`, `StringRef`, file identifiers, and object serializer traits. It integrates with FlatBuffers/BinaryWriter/ObjectWriter contexts that honor wipe marks for serialized output buffers.

## Risks And Edge Cases
Implicit conversion to `StringRef` can still expose sensitive bytes to APIs that copy them into non-wiping memory. The wrapper intentionally avoids inheriting `StringRef`; bypassing it would lose wipe behavior. External arena construction assigns the arena after allocation and must preserve ownership expectations.

## Test Signals
Test signals include construction copying bytes, serialization round trips, output buffer wipe marking, keepalive allocator tracking of wiped areas, empty-string behavior, and verification that normal `StringRef` traits are not used for `WipedString`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WipedString.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WriteOnlySet.h -->
# sources/storage-engines/foundationdb/flow/include/flow/WriteOnlySet.h

## Purpose
`WriteOnlySet.h` declares lock-free sampling data structures used when `ENABLE_SAMPLING` is enabled. They allow concurrent insertion/removal/replacement of reference-counted objects and weakly consistent copying of current contents.

## Important APIs, Types, And Functions
`WriteOnlySet<T, IndexType, CAPACITY>` exposes `insert`, `erase`, `replace`, and `copy`. It stores atomic pointer words in `_set`, free indexes in a boost lock-free queue, and deferred refcount cleanup in `freeList`. `WriteOnlyVariable<T, IndexType>` is a capacity-one wrapper with `get()` and `replace()`. `ActorLineageSet` is an extern-instantiated `WriteOnlySet<ActorLineage, unsigned, 1024>`.

## Control Flow
Insert obtains an index from `freeQueue`, stores a reference-counted pointer, and returns the index or `npos` if full. Erase removes a pointer and either decrements its refcount immediately or defers it if a copy operation has locked the pointer by setting the low bit. Copy traverses atomics, locks stable pointer values, increments references, and drains deferred frees.

## State And Persistence Behavior
All state is process-local sampling state. It is not durable. Correctness depends on pointer alignment because the low pointer bit is used as a lock flag.

## Dependencies And Integration Points
It depends on Flow `Reference`, `FastRef`, `Error`, `Trace`, and `boost::lockfree::queue`. It integrates with actor lineage sampling through `INetwork::getActorLineageSet()` and profiling tools.

## Risks And Edge Cases
The API is compiled out unless `ENABLE_SAMPLING` is defined. Capacity is fixed; inserts can fail gracefully with `npos`. The copy contract is intentionally weak and is not a snapshot. Pointer alignment and atomic lock-freedom are hard requirements; violating either breaks memory management.

## Test Signals
Tests should cover full-capacity insert failure, erase and replace refcount behavior, copy during concurrent erase/replace, deferred free-list cleanup, capacity-one variable replacement, and actor lineage sampling under concurrent activity.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/WriteOnlySet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/actorcompiler.h -->
# sources/storage-engines/foundationdb/flow/include/flow/actorcompiler.h

## Purpose
`actorcompiler.h` supplies macros and guard declarations used by FoundationDB's actor compiler and IDE tooling. It makes actor syntax readable before compilation and prevents accidental runtime use of `wait` APIs after actor compilation.

## Important APIs, Types, And Functions
Under `POST_ACTOR_COMPILER`, deleted overloads of `wait(Future<T>)`, `wait(Never)`, and `waitNext(FutureStream<T>)` ensure these constructs were rewritten by the actor compiler. Without `POST_ACTOR_COMPILER`, it forward-declares `Future`, `Never`, and `FutureStream`; for IntelliSense it defines `ACTOR`, `SWIFT_ACTOR`, `state`, `UNCANCELLABLE`, `choose`, `when`, and placeholder wait functions. It also defines `loop`, `THIS`, `THIS_ADDR`, and no-op Valgrind macros when Valgrind is absent.

## Control Flow
The header changes compile-time interpretation of actor source depending on preprocessor state. Actor source includes it last; the actor compiler rewrites actor constructs and then post-compiled C++ sees deleted wait functions, catching missed rewrites.

## State And Persistence Behavior
There is no runtime state or persistence. The file controls source transformation and compile-time safety.

## Dependencies And Integration Points
It integrates tightly with `.actor.h`/`.actor.cpp` files, generated `.actor.g.h` outputs, `unactorcompiler.h`, Flow coroutine shims, and IDE parsing. Valgrind macro definitions allow actor code to compile without conditional sections inside actors.

## Risks And Edge Cases
The comments note `#ifdef` cannot be used inside actors, so macro behavior must remain simple. Defining common names like `wait`, `state`, and `loop` can collide if included in the wrong context. The deleted post-compiler functions are important safety rails; weakening them could let uncompiled actor syntax run incorrectly.

## Test Signals
Signals include successful actor compilation, failure when raw `wait` remains after compilation, IDE parseability without `NO_INTELLISENSE`, and Flow actor tests that validate line numbers, cancellation, and generated callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/actorcompiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/error_definitions.h -->
# sources/storage-engines/foundationdb/flow/include/flow/error_definitions.h

## Purpose
`error_definitions.h` is the central X-macro list of FoundationDB error names, numeric codes, and user-facing messages. It is included with `ERROR` defined to generate enums, factories, mappings, and bindings.

## Important APIs, Types, And Functions
There are no normal functions; the API is the `ERROR(name, code, message)` stream. Codes are grouped by purpose: success/normal operational failures around `0` and `1xxx`, platform errors in `15xx`, client/API errors in `2xxx`, backup/restore and task errors in `23xx`, snapshot and encryption errors in `25xx`/`27xx`, internal errors in `4xxx`, auth errors in `6xxx`, and gRPC in `7000`.

## Control Flow
Consumers define `ERROR`, include the file, and then the header expands every error entry before undefining `ERROR`. Removed code comments preserve gaps and compatibility history.

## State And Persistence Behavior
The list defines durable protocol/API semantics: numeric error codes cross process boundaries, client bindings, logs, and sometimes persisted metadata. Names and messages are not persistent state, but numeric changes are compatibility-sensitive.

## Dependencies And Integration Points
It integrates with `flow/Error.h`, client bindings, RPC serialization, retry logic, API error reporting, simulation, storage engines, backup/restore, encryption, special keys, bulk load/dump, and operational tooling.

## Risks And Edge Cases
The top comment warns that distinct errors should exist only when code can sensibly react to them. Reusing, renumbering, or deleting codes can break clients and compatibility. Some comments mark dangerous catch behavior, such as recruitment/worker removal errors whose handling can delete server data.

## Test Signals
Tests should verify generated factories and code/name/message maps, client binding visibility, retryability classification, serialization across protocol versions, and workload behavior for specific catchable errors such as conflict, timeout, maybe-delivered, authorization, storage corruption, and backup/restore failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/error_definitions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/flat_buffers.h -->
# sources/storage-engines/foundationdb/flow/include/flow/flat_buffers.h

## Purpose
`flat_buffers.h` implements FoundationDB's trait-driven FlatBuffers-compatible object serialization layer. It maps Flow's `serializer(ar, ...)` style into FlatBuffer tables, vectors, unions, structs, dynamic byte fields, vtables, and file identifiers.

## Important APIs, Types, And Functions
Public helpers include `save_members`, `load_members`, `read_file_identifier`, and `EnsureTable<T>`. Trait specializations cover scalar types, `std::tuple` as struct-like, `std::pair`, standard vectors/deques/arrays/maps/sets/unordered containers, `boost::container::flat_map`, and `std::string`. Internals include `RelativeOffset`, `PrecomputeSize`, `WriteToBuffer`, `VTableSet`, `SaveVisitorLambda`, `LoadMember`, `LoadSaveHelper`, `FakeRoot`, and vtable generation helpers.

## Control Flow
Serialization is two-pass. First `PrecomputeSize` traverses the object graph, computes buffer size, dynamic payload placement, vtable offsets, and write locations. Then `WriteToBuffer` repeats traversal and copies bytes from the end-relative layout into the allocated buffer, fixing relative offsets. Deserialization starts from table offsets, reads vtables, checks field presence, and loads members through the same trait categories.

## State And Persistence Behavior
The output buffer is persistent serialized data suitable for RPC/object storage. Thread-local vtable caches and precompute scratch vectors are process-local performance state. File identifiers are embedded near the root so readers can validate object identity.

## Dependencies And Integration Points
It depends on `FileIdentifier`, `ObjectSerializerTraits`, container traits, and Flow serializer conventions. `flow.h` uses it for `ErrorOr`, `CachedSerialization`, and `EnsureTable`, and the wider codebase uses it for RPC payloads and object serialization.

## Risks And Edge Cases
The code assumes little-endian-style byte copies for scalar layout and FlatBuffers alignment rules. Nested struct-like structs are explicitly unsupported. Union alternatives are capped at 254 because FlatBuffers reserves zero for empty. `serialize_raw` paths bypass normal table generation. Missing fields default-construct members, which is useful for compatibility but can hide schema drift if defaults are unsafe.

## Test Signals
Strong tests include round trips for every supported container, maps/sets preserving contents, empty-vector offset reuse, `vector<bool>`, unions and vectors of unions, missing-field compatibility, file identifier checks, raw serialization paths, alignment/padding checks, and cross-version object serialization used by RPC and persisted metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/flat_buffers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/flow.h -->
# sources/storage-engines/foundationdb/flow/include/flow/flow.h

## Purpose
`flow.h` is the central Flow async runtime header. It defines core value types, error/value wrappers, cached serialization, futures/promises, streams, actor callback state, actor lineage sampling hooks, and convenience wrappers over the active `INetwork`.

## Important APIs, Types, And Functions
Important exports include parsing/formatting helpers, `concatenate`, `Void`, `Never`, `ErrorOr<T>`, `CachedSerialization<T>`, `Callback<T>`, `SingleCallback<T>`, `ActorLineage`, `LineageReference`, `LocalLineage`, `SAV<T>`, `Future<T>`, `StrictFuture<T>`, `Promise<T>`, `NotifiedQueue<T>`, `FutureStream<T>`, `PromiseStream<T>`, `Actor<ReturnValue>`, `ActorCallback`, `ActorSingleCallback`, `now`, `delay`, `orderedDelay`, `delayUntil`, `delayJittered`, `yield`, and `check_yield`.

## Control Flow
`Promise` owns producer references to `SAV`; `Future` owns consumer references. Sending a value, `Never`, or error transitions the single-assignment state and fires registered callbacks. Dropping the last promise before setting sends `broken_promise` to remaining futures; dropping futures can cancel producers. Streams use `NotifiedQueue` with a single callback waiter and queued values/errors. Actor compiler output derives from `Actor` and callback types to resume actors on future readiness.

## State And Persistence Behavior
Most state is in-memory async scheduling state. Serialization-related types can produce binary/object payloads using the current network protocol version. Actor lineage is optional sampling/debug state, protected by mutexes and reference counting. Delays and yields are scheduled through global `g_network`.

## Dependencies And Integration Points
It pulls in Arena, errors, random, network, serialization, Swift bridging, coroutines, and generic actors. Nearly every Flow, fdbrpc, fdbclient, and fdbserver actor or RPC interface depends on this header.

## Risks And Edge Cases
Reference counts and callback rings are delicate: wrong add/drop/clear behavior can leak, double-fire, or lose cancellation. `CachedSerialization` has comments about direct ObjectWriter caching limitations. `Future::get()` throws stored errors. `PromiseStream::getReply` has at-least-once delivery semantics, not exactly-once semantics. Sampling code is conditional and should not affect non-sampling builds.

## Test Signals
Key signals are Flow actor cancellation tests, trivial future tests, networked future tests, quorum tests, broken-promise propagation, stream end/error behavior, serialization round trips for `ErrorOr` and cached objects, Swift continuation integration, and simulation determinism around `delayJittered`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/genericactors.actor.h -->
# sources/storage-engines/foundationdb/flow/include/flow/genericactors.actor.h

## Purpose
`genericactors.actor.h` provides reusable Flow actor utilities: future transformations, timeouts, stream adapters, change-notification containers, quorum/wait aggregation, locks, recurring tasks, weak future references, and simulation-friendly singleton helpers.

## Important APIs, Types, And Functions
Important APIs include `traceAfter`, `stopAfter`, `errorOr`, `throwErrorOr`, `transformErrors`, `timeout`, `timeoutError`, `delayed`, `uncancellable`, `holdWhile`, `store`, `map`, `mapAsync`, `waitForAll`, `waitForAny`, `waitForMost`, `getAll`, `appendAll`, `waitForFirst`, `tag`, `orYield`, `recurring`, `recurringAsync`, `brokenPromiseToNever`, `FlowMutex`, `FlowLock`, `BoundedFlowLock`, `AsyncMap`, `YieldedAsyncMap`, `AsyncVar`, `AsyncTrigger`, `Debouncer`, `IAsyncListener`, `UnsafeWeakFutureReference`, and `FlowSingleton`.

## Control Flow
The header uses both actor-compiler syntax and C++ coroutines. Aggregation helpers attach callbacks to futures or single-consumer `AsyncResult`s and complete on quorum, all-success, or first error while detaching/cancelling unused producers. `AsyncVar` swaps its next-change promise before setting values so waiters observe changes. `FlowLock` queues waiters when permits are exhausted and yields after acquisition to avoid running arbitrary waiter code on the release stack.

## State And Persistence Behavior
State is process-local runtime coordination: maps of async values, promises, wait queues, permits, counters, debounce workers, and singleton maps keyed by simulated local address. There is no direct durable state, but these primitives coordinate durable subsystems such as storage engines and server roles.

## Dependencies And Integration Points
It depends on `flow.h`, task priorities, knobs, indexed sets, actor compiler macros, and utility helpers. It is included broadly by Flow and server/client actor code for common async patterns.

## Risks And Edge Cases
Cancellation ownership is subtle, especially for `AsyncResult` aggregation because results are single-consumer and vectors must be passed by rvalue. `FlowLock` is not thread-safe and intentionally allows an oversized request when `active == 0`. `AsyncMap` cleanup relies on promise reference counts. `UnsafeWeakFutureReference` can dangle if users outlive the referenced object.

## Test Signals
Existing test signals include `/flow/genericactors/AsyncListener`, `/flow/genericactors/WaitForMost`, generic coroutine tests for trace/timeout/delayed/trigger/error transforms, Flow quorum tests, and storage-engine tests that exercise `FlowLock` throttling. Additional tests should stress cancellation, fail-fast aggregation, and lock release on cancelled acquisition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/genericactors.actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/network.h -->
# sources/storage-engines/foundationdb/flow/include/flow/network.h

## Purpose
`network.h` declares the abstract Flow network/event-loop interface and associated metrics/state. It is the seam between Flow actors and either the real Net2 runtime or simulation.

## Important APIs, Types, And Functions
`NetworkMetrics` tracks slow events, disk stall/submit timing, active priority trackers, run-loop busyness, and starvation trackers. `NetworkInfo` holds metrics, alternatives failure timestamps, TLS connection throttling state, and a handshake `FlowLock`. `IEventFD` abstracts eventfd-style readiness. `INetwork` exposes clocks, delay/yield scheduling, task priority, global slots, stop callbacks, simulation/main-thread checks, thread creation, TLS initialization, disk byte queries, local address lookup, actor lineage set access under sampling, and `protocolVersion()`. Globals include `g_network` and `newNet2`.

## Control Flow
Actors call inline wrappers in `flow.h`, which dispatch into `g_network`. Implementations run the event loop, schedule timers and yields, maintain globals, and stop when requested. Static helpers retrieve local network addresses through function pointers stored in network globals.

## State And Persistence Behavior
All state is process runtime state. Metrics may be exported to monitoring, but this header does not persist them. `protocolVersion()` influences serialization compatibility for RPC and object encoding.

## Dependencies And Integration Points
It depends on protocol versioning, Swift annotations, network addresses, task priorities, random support, and `WriteOnlySet` for sampling. It is implemented by Net2/simulation runtimes and used by all Flow actors through `g_network`.

## Risks And Edge Cases
`g_network` is a global singleton and many helpers assume it is initialized. `global(id)` uses untyped `void*` slots, so enum ordering and casts must remain consistent. The destructor is protected/non-public by convention; deleting through `INetwork` is forbidden. Metrics copy assignment must handle atomic fields explicitly.

## Test Signals
Signals include event-loop startup/shutdown, delay ordering, yield priority behavior, simulated vs real clocks, TLS init sequencing, disk byte reporting, local address helpers, protocol-version propagation, and metrics/starvation tracking under load.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/network.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ppc-asm.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ppc-asm.h

## Purpose
`ppc-asm.h` provides PowerPC assembly convenience definitions imported from GCC. It names registers, handles ABI-specific function labels/descriptors, defines CFI directives when building inside GCC, and marks GNU stack metadata on Linux.

## Important APIs, Types, And Functions
The header defines register-number macros for general, condition, floating-point, Altivec, and VSX registers. Token glue helpers `XGLUE` and `GLUE` support label construction. ABI-dependent macros include `FUNC_NAME`, `JUMP_TARGET`, `FUNC_START`, `HIDDEN_FUNC`, and `FUNC_END`. Optional CFI macros include `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_OFFSET`, `CFI_DEF_CFA_REGISTER`, and `CFI_RESTORE`.

## Control Flow
There is no C++ runtime flow. Assembly files include this header so a single source can expand function prologue/label directives correctly for ELFv2, older ppc64 descriptor ABIs, AIX descriptor mode, PIC, or default labels.

## State And Persistence Behavior
No state is held or persisted. It affects generated object-file symbols, unwind metadata, and executable-stack notes.

## Dependencies And Integration Points
It is architecture-specific support for PowerPC assembly, likely paired with CRC or low-level optimized routines. It complements `ppc-opcode.h`, which defines instruction encodings for opcodes assemblers may not know.

## Risks And Edge Cases
The header defines very broad macro names such as `r0`, `sp`, and `toc`; include scope must be tightly limited to assembly-oriented code. ABI conditionals are fragile and must match compiler flags such as `_CALL_ELF`, `_CALL_AIXDESC`, PIC, VSX, and Altivec.

## Test Signals
Signals are build/link success on supported PowerPC targets, correct exported/hidden symbols, valid unwind info when CFI is enabled, no executable stack warnings on Linux, and passing low-level assembly routine tests such as CRC correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ppc-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ppc-opcode.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ppc-opcode.h

## Purpose
`ppc-opcode.h` defines raw PowerPC VSX/crypto opcode encodings for assemblers that may not have mnemonic support for selected instructions.

## Important APIs, Types, And Functions
Register field helpers include `__PPC_RA`, `__PPC_RB`, `__PPC_XA`, `__PPC_XB`, `__PPC_XS`, and `__PPC_XT`. `VSX_XX3` and `VSX_XX1` assemble operand fields. Instruction constants include `PPC_INST_VPMSUMW`, `PPC_INST_VPMSUMD`, `PPC_INST_MFVSRD`, and `PPC_INST_MTVSRD`. Macros `VPMSUMW`, `VPMSUMD`, `MFVRD`, and `MTVRD` emit `.long` encoded instructions.

## Control Flow
Assembly code expands these macros inline into numeric instruction words. There is no C++ runtime flow.

## State And Persistence Behavior
No state is held or persisted. The macros affect emitted machine code.

## Dependencies And Integration Points
It is used with PowerPC assembly code, commonly for accelerated checksum/CRC routines needing carryless multiply or VSX register moves. It pairs with `ppc-asm.h` register naming and function-label helpers.

## Risks And Edge Cases
Encoding bugs produce invalid or wrong machine instructions. Operand ranges are masked but not semantically validated. The macros assume GNU assembler `.long` syntax and appropriate CPU feature availability at runtime.

## Test Signals
Signals include successful assembly on target toolchains, runtime CPU feature gating where needed, CRC/checksum known-answer tests, and disassembly confirming emitted opcodes match intended instructions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ppc-opcode.h -->
