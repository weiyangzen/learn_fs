# subset-b-008495 Research

Grouped research for the FoundationDB files assigned to `subset-b-008495`. Each section preserves the original source path and is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/WriteDuringRead.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/WriteDuringRead.cpp

## Purpose
`WriteDuringRead.cpp` defines the `WriteDuringRead` simulation workload, a self-checking stress test for `ReadYourWritesTransaction` behavior while reads, writes, commits, watches, resets, conflict ranges, and timeouts overlap. It keeps an in-memory model of expected transactional state and compares live FoundationDB reads against that model under many randomized option combinations.

## Important APIs, Types, and Functions
The central type is `WriteDuringReadWorkload : TestWorkload`, registered through `WorkloadFactory<WriteDuringReadWorkload>`. Public workload hooks are `setup`, `start`, `check`, and `getMetrics`. Important helpers include `memoryGetKey`, `memoryGetRange`, and `memoryGet`, which model FDB read semantics over `std::map<Key, Value>`; `getKeyAndCompare`, `getRangeAndCompare`, `getAndCompare`, and `watchAndCompare`, which issue asynchronous reads or watches and verify results; `commitAndUpdateMemory`, which commits and moves the model from pending to committed state; `writeBarrier`, which prevents cancelled write-only transactions from reordering after the next run; and `randomTransaction`, the main randomized operation driver.

## Control Flow
Only client 0 runs the workload. `loadAndRun` repeatedly initializes the database in batches, records `lastCommittedDatabase`, then runs randomized transactions until duration or write-budget limits are reached. `randomTransaction` configures transaction options, seeds a conflict range, schedules a random mix of reads, range reads, key-selector reads, commits, clear operations, atomic operations, watches, delays, resets, and conflict-range additions, then waits for outstanding operations and validates watch outcomes. Errors such as `not_committed`, `commit_unknown_result`, size errors, watch limits, and timeout paths roll the in-memory model back to the last committed state before retrying the outer loop.

## State and Persistence Behavior
Persistent state is ordinary FDB key-value data under a generated prefix, optionally system-key prefixed when `ACCESS_SYSTEM_KEYS` is enabled. The workload keeps volatile mirror state in `memoryDatabase`, `lastCommittedDatabase`, `changeCount`, and `addedConflicts`. Successful commits update the durable store and then assign `lastCommittedDatabase` to the committed in-memory snapshot. Unknown or rejected commits reset volatile state and let the initialization loop reestablish a consistent baseline.

## Dependencies and Integration Points
The file depends on `NativeAPI.actor.h`, `ReadYourWrites`, atomic mutation helpers, `ActorCollection`, `ApiVersion`, and workload tester infrastructure. It exercises FDB transaction options such as `READ_YOUR_WRITES_DISABLE`, `SNAPSHOT_RYW_DISABLE`, `READ_AHEAD_DISABLE`, `PRIORITY_BATCH`, `ACCESS_SYSTEM_KEYS`, `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`, and `TIMEOUT`. In simulation it can target an extra simulated database.

## Risks and Edge Cases
Risk centers on the fidelity of the in-memory model versus real FDB semantics, especially with system keys, byte-limited range reads, key-size truncation for conflict ranges, versionstamped keys, concurrent commit use, and timeout injection. The workload intentionally tolerates `used_during_commit` and cancellation races. A subtle risk is that expected conflict ranges must match the transaction's internal write conflict map exactly when RYW is enabled.

## Test Signals
Failures surface as `TraceEvent(SevError, ...)` records such as `WDRGetWrongResult`, `WDRGetRangeWrongResult`, `WDRGetKeyWrongResult`, `WDRWatchWrongResult`, and conflict range errors. Metrics expose transaction and retry counts. `check` returns the accumulated `success` flag.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/WriteDuringRead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/WriteTagThrottling.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/WriteTagThrottling.cpp

## Purpose
`WriteTagThrottling.cpp` implements the `WriteTagThrottling` workload, which validates tag-based write throttling by comparing "bad" actors that concentrate writes and clears on hot ranges against "good" actors that use random keys.

## Important APIs, Types, and Functions
The main type is `WriteTagThrottlingWorkload : KVWorkload`, registered as `WriteTagThrottling`. Configuration includes actor counts, reads/writes/clears per transaction, `badOpRate`, `hotRangeRate`, `writeThrottle`, `populateData`, `keyCount`, and transaction pacing. `clientActor` runs the read/write workload. `throttledTagUpdater` polls `ThrottleApi::getThrottledTags`, and `recordThrottledTags` accumulates observed throttled tags. `generateKey`, `generateRange`, and `generateVal` produce transaction data.

## Control Flow
`setup` first checks transaction tag knob capacity and can fast-succeed when tags are unsupported. `_setup` optionally bulk-loads data and enables automatic throttling on client 0. `_start` launches good and bad actors plus a tag polling actor and runs them until `testDuration`. Each client actor paces transactions with `poisson`, tags transactions when `writeThrottle` is enabled, runs clear, set, and get operations, commits, records latency, and retries with `tr.onError`.

## State and Persistence Behavior
The workload persists only generated KV data and transaction mutations. Runtime metrics are in member counters and `DDSketch` latency samplers. Bad actors target deterministic per-actor hot ranges derived from client and actor id, making throttling attribution stable across the run.

## Dependencies and Integration Points
It integrates with tester `KVWorkload`, `BulkSetup`, FDB `Transaction`, `TransactionTag`, `FDBTransactionOptions::AUTO_THROTTLE_TAG`, and `ThrottleApi`. It depends on client knobs `MAX_TAGS_PER_TRANSACTION` and `MAX_TRANSACTION_TAG_LENGTH`.

## Risks and Edge Cases
The `check` method is intentionally more diagnostic than strict. If no throttling occurs it logs a warning, and it fails only when observed throttled tags exclude the bad tag. Average latency metrics divide by transaction counts, so configurations that produce zero transactions can make metric output fragile. Hot-range sizing also depends on `badActorPerClient`; zero bad actors skips range division but removes the intended bad-client signal.

## Test Signals
Metrics include bad/good transaction counts, retries, throttle retries, too-old and commit-failed retries, and latency summaries. Warnings `NoThrottleTriggered` and `IncorrectThrottle` signal likely configuration or behavior issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/WriteTagThrottling.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.cpp

## Purpose
`pubsub.cpp` implements the storage and transactional behavior for a small FoundationDB-backed pub/sub model declared in `pubsub.h`. It provides feeds, inboxes, subscriptions, message posting, inbox cache maintenance, and feed/inbox message listing.

## Important APIs, Types, and Functions
The exported methods are `PubSub::createFeed`, `createInbox`, `createSubscription`, `postMessage`, `listInboxMessages`, and `listFeedMessages`. Helper key builders create lexicographic key families for inboxes, subscriptions, stale feeds, inbox caches, feeds, subscribers, feed messages, watchers, global messages, and dispatch entries. `uInt64ToValue` and `valueToUInt64` encode ids as fixed-width hex strings. Core actors include `_createFeed`, `_createInbox`, `_createSubscription`, `_postMessage`, `updateFeedWatchers`, `singlePassInboxCacheUpdate`, `updateInboxCache`, `getFeedLatestAtOrAfter`, `getMessage`, `_listInboxMessages`, and `_listFeedMessages`.

## Control Flow
Creation methods pick random ids and retry transactions until an unused feed or inbox key is found. Subscription creation validates both endpoints, updates inbox and feed indexes, increments counters, and registers the inbox as a watcher on the feed. Posting first reserves a decreasing global message id and dispatch entry, then in a second transaction updates feed message indexes, stale inbox markers for all watchers, the message payload, and clears the dispatch marker. Inbox listing refreshes stale feed cache entries, reads cached per-feed latest messages, adjusts for the pagination cursor, checks dispatch entries for ordering gaps, and merges feed streams by message id.

## State and Persistence Behavior
All state lives in FDB keys using textual prefixes. Feeds store metadata, subscriber count, message count, latest message id, per-feed message ids, subscribers, and watchers. Inboxes store metadata, subscription count, subscription keys, stale-feed markers, cache-by-message-id, and cache-by-feed entries. Global message ids are assigned in reverse order so smaller keys represent newer messages.

## Dependencies and Integration Points
The file depends on `NativeAPI.actor.h`, `Transaction`, `RangeResult`, `TraceEvent`, actor retries with `tr.onError`, and the types from `pubsub.h`. It is a workload/demo component rather than a production FDB subsystem.

## Risks and Edge Cases
The implementation contains several "SOMEDAY" notes: id allocation is random instead of atomic, global ordering is only approximated, and frequently updated feeds can cause repeated stale-cache passes. There is a likely key bug in `_createSubscription`: it writes `keyForFeedSubscriberCount(inbox)` instead of `keyForFeedSubscriberCount(feed)` when incrementing feed subscriber count. Several `.get()` calls assume count/latest keys exist once metadata exists.

## Test Signals
There are no local unit tests in this file. Runtime signals are trace events such as `PubSubCreateFeed`, `PubSubCreateInbox`, `PubSubCreateSubscription`, `PubSubPost`, `PubSubListInbox`, and `PubSubListFeed`; correctness is otherwise observable through API return values and stored key consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.h

## Purpose
`pubsub.h` declares a simple FoundationDB-backed pub/sub abstraction used by workload code. Its header comment explains the intended data model and operational assumptions for feeds, inboxes, messages, watcher lists, stale lists, and inbox caches.

## Important APIs, Types, and Functions
The file aliases `Feed`, `Inbox`, and `MessageId` to `uint64_t`. `Message` contains `originatorFeed`, `messageId`, and arena-backed `data`, and provides a serializer. `PubSub` owns a `Database` handle and exposes asynchronous methods to create feeds and inboxes, create subscriptions, post messages, and list feed or inbox messages.

## Control Flow
The header itself contains no implementation, but it defines the expected flow: posting appends a message to a feed and marks watcher inboxes dirty; listing inbox messages updates dirty feed caches and merges recent messages from subscribed feeds. `cursor` defaults to `0` for list calls, matching the implementation's descending/global id scheme.

## State and Persistence Behavior
No state is stored in the header except the `Database cx` member. The declared API implies all persistent state is externalized to FDB key ranges managed by `pubsub.cpp`. `Message::data` is a `Standalone<StringRef>`, so returned messages carry their arena lifetime with the value bytes.

## Dependencies and Integration Points
It includes `fdbclient/NativeAPI.actor.h` for `Database`, `Future`, `Standalone`, and `StringRef`. It is consumed by `pubsub.cpp` and any workload or test code that wants a compact pub/sub API.

## Risks and Edge Cases
The model assumes retroactive subscriptions and warns that paging can look odd when subscriptions are added during reads. There are no explicit namespaces or include guards in this header, which relies on project include patterns and can be fragile if included repeatedly.

## Test Signals
No tests are defined in the header. Testability comes through the asynchronous `PubSub` API and message serialization round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/pubsub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ActorCollection.actor.cpp -->
# sources/storage-engines/foundationdb/flow/ActorCollection.actor.cpp

## Purpose
`ActorCollection.actor.cpp` implements the actor backing `ActorCollection`, a utility for dynamically adding `Future<Void>` actors, tracking their count, propagating errors, and optionally returning when the collection drains.

## Important APIs, Types, and Functions
`Runner` owns a handler future and is stored in a Boost intrusive `RunnerList`. `RunnerListDestroyer` guarantees list cleanup when the actor frame is destroyed. `runnerHandler` waits on one task and sends either its iterator to a completion stream or its error to an error stream. `actorCollection` is the main actor and is declared in the corresponding header. The file also defines `Traceable<std::pair<T, U>>` and `forceLinkActorCollectionTests`.

## Control Flow
`actorCollection` chooses among new actor arrivals, task completions, and task errors. New futures allocate a `Runner`, start a handler, and increment the external or internal count. Completion decrements the count, updates optional timing accumulators, optionally returns when empty, and erases the runner. Error events are thrown from the collection actor, causing the collection to become failed.

## State and Persistence Behavior
All state is in memory: the intrusive runner list, completion and error streams, count pointer, and optional activity timing pointers. There is no persistence. The destroyer is critical because actor cancellation must clear outstanding runner handlers and delete their allocations.

## Dependencies and Integration Points
The file depends on Flow actors, `ActorCollection.h`, `IndexedSet.h`, `UnitTest.h`, Boost intrusive lists, and the actor compiler. Workloads such as `WriteDuringRead` use `ActorCollection` to track concurrent commit futures.

## Risks and Edge Cases
The implementation relies on Flow `choose` behavior that promise fulfillment from one branch does not synchronously fire another branch in the same choose block. Reinitializing an `ActorCollection` is safer than just clearing it when the underlying add stream may contain queued futures.

## Test Signals
Unit tests cover choose behavior, cancellation of added actors on `clear`, and cancellation of actors queued in the promise stream after a failure and reinitialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ActorCollection.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ActorContext.cpp -->
# sources/storage-engines/foundationdb/flow/ActorContext.cpp

## Purpose
`ActorContext.cpp` implements optional actor context tracking behind `WITH_ACAC`. It records active actors, their execution stack, and spawn relationships, and can serialize actor context dumps for diagnostics.

## Important APIs, Types, and Functions
Important globals are `g_currentExecutionContext` and `g_activeActors`. `ActiveActor` stores identifier, id, spawn time, and spawner id. `ActiveActorHelper` registers/unregisters active actors. `ActorExecutionContextHelper` pushes/pops execution context. Public functions include `dumpActors`, `dumpActorCallBacktrace`, `encodeActorContext`, and `decodeActorContext`.

## Control Flow
Instrumentation helpers only mutate global tracking state on the main actor thread. Actor construction assigns a thread-local incremental actor id and records the current actor as spawner. Execution-context helpers maintain a stack of active blocks. Encoding writes a dump type, current actor id, and either full active-actor state, current stack, or current call backtrace to a `BinaryWriter`, then base64-encodes the binary payload.

## State and Persistence Behavior
State is process-local diagnostic state and is not durable. Encoded dumps are portable strings carrying a snapshot of selected actor metadata. `decodeActorContext` reads that string back into a `DecodedActorContext`.

## Dependencies and Integration Points
The file depends on `ActorContext.h`, `flow.h`, libb64, Flow serialization, and `g_network`. It contains special logic for Sim2 versus Net2 main-thread detection because simulation may not set Net2 thread state in the same way.

## Risks and Edge Cases
The globals are not guarded by the included mutex, so correctness depends on the main-thread check. Missing actor ids during backtrace currently stop traversal with TODOs. Stack underflow in `ActorExecutionContextHelper` destructor aborts the process, which is appropriate for instrumentation corruption but high impact.

## Test Signals
No local unit tests are defined. Observable signals are emitted diagnostic dumps and crashes on context-stack corruption when `WITH_ACAC` instrumentation is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ActorContext.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ApiVersion.h.cmake -->
# sources/storage-engines/foundationdb/flow/ApiVersion.h.cmake

## Purpose
`ApiVersion.h.cmake` is a configured header template that generates `flow/ApiVersion.h`. It centralizes FoundationDB client API-version feature gates.

## Important APIs, Types, and Functions
The main type is `ApiVersion`, a constexpr wrapper around an integer version. It exposes `LATEST_VERSION`, `isValid`, `version`, comparison operators, and generated feature helpers. The `API_VERSION_FEATURE(v, x)` macro defines a feature marker struct, `hasX()` predicate, and `withX()` constructor for each feature.

## Control Flow
CMake substitutes placeholders such as `@FDB_AV_LATEST_VERSION@` and individual `@FDB_AV_*@` values from `ApiVersions.cmake`. Runtime code can then compare an `ApiVersion` against the feature's introduction version without string parsing or generated lookup tables.

## State and Persistence Behavior
There is no mutable or persistent state. The generated header embeds API-version constants into compiled code. `noBackwardsCompatibility` defines the lower valid bound.

## Dependencies and Integration Points
It includes `flow/Trace.h` and `<cstdint>`. `flow/CMakeLists.txt` configures this file into the build include directory. Client and binding code can use `hasFeature` methods to guard behavior by selected API version.

## Risks and Edge Cases
Feature constants must not exceed `LATEST_VERSION`; the macro enforces this with `static_assert`. Any missing semicolon in macro uses can affect generated C++ syntax; one feature line intentionally lacks a visible semicolon because the macro expands to declarations.

## Test Signals
Compile-time generation and compilation are the primary tests. Feature behavior is indirectly tested anywhere client API-version gates are exercised.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ApiVersion.h.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ApiVersions.cmake -->
# sources/storage-engines/foundationdb/flow/ApiVersions.cmake

## Purpose
`ApiVersions.cmake` is the authoritative CMake data file for FoundationDB API-version constants consumed by `ApiVersion.h.cmake`.

## Important APIs, Types, and Functions
It defines `FDB_AV_LATEST_VERSION`, `FDB_AV_LATEST_BINDINGS_VERSION`, and one `FDB_AV_*` variable per API feature, including snapshot RYW, persistent options, trace file identifiers, blob range APIs, tenant API milestones, total cost, tag throttled duration, future double/bool APIs, client status, and tenant id.

## Control Flow
The file is included by `flow/CMakeLists.txt`, which then runs `configure_file` to replace matching placeholders in `ApiVersion.h.cmake`. There is no procedural control flow beyond CMake `set` commands.

## State and Persistence Behavior
The file stores build-time constants only. Changing it changes generated headers and therefore compiled API-gating behavior.

## Dependencies and Integration Points
Its direct integration point is `FDB_API_VERSION_FILE` in `flow/CMakeLists.txt`. Bindings and client behavior depend on the generated constants being synchronized with released API semantics.

## Risks and Edge Cases
A wrong value can expose a feature to too-old API versions or hide it from versions that should support it. `LATEST_BINDINGS_VERSION` must remain compatible with language binding release expectations.

## Test Signals
Build success verifies placeholder availability. Behavioral tests for API-version-gated features provide indirect validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ApiVersions.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Arena.cpp -->
# sources/storage-engines/foundationdb/flow/Arena.cpp

## Purpose
`Arena.cpp` implements Flow's arena-backed memory primitives, including `Arena`, `ArenaBlock`, `StringRef` formatting helpers, dependency tracking, secure wipe support, allocator metrics, and unit tests for arena-related container helpers.

## Important APIs, Types, and Functions
Key APIs include `Arena::Arena`, `dependsOn`, `allocate4kAlignedBuffer`, `getSize`, and `hasFree`; `ArenaBlock::allocate`, `create`, `dependOn`, `dependOn4kAlignedBuffer`, `destroy`, `destroyLeaf`, `totalSize`, `estimatedTotalSize`, `wipeUsed`, and reference-count methods; plus `StringRef::toHexString` and `toFullHexStringPlain`. Internal helpers integrate with Valgrind or ASAN memory poisoning.

## Control Flow
Arena allocation reuses the current block when possible, otherwise creates a larger block and links it to prior blocks. Tiny allocations can use 32 or 64 byte fast allocators; larger blocks use size buckets up to 8192 bytes or huge allocation. Dependencies are stored as `ArenaBlockRef` records inside a block; destruction walks referenced blocks iteratively to avoid recursive stack overflow and frees 4K-aligned buffers separately.

## State and Persistence Behavior
State is heap memory with reference-counted arena blocks. There is no durable persistence. Secure allocations mark blocks and trigger `wipeUsed` before release. `totalSizeEstimate` caches approximate tree size and can be corrected by accurate traversal.

## Dependencies and Integration Points
This file is a foundational dependency for Flow strings, vectors, serialization, futures, and FDB data structures. It integrates with `FastAllocator`, keepalive allocation, sanitizer/Valgrind hooks, `SimpleCounter`, and allocation tracing globals.

## Risks and Edge Cases
Memory poisoning must be correctly paired around header reads and writes. Dependency graphs can share blocks and become cyclic; `totalSize` uses a visited set. Huge arena logging is disabled during secure-wipe tests because sampling can disturb allocation assumptions. The conditional spelling `ADDRESS_SANITZER` appears inconsistent with `ADDRESS_SANITIZER`, making ASAN-specific helpers worth checking against build definitions.

## Test Signals
Unit tests cover `VectorRef`, `SmallVectorRef`, optional hashing, boost hashing, size estimates, self-dependency, `StringRef::eat`, `StringRef(const char*)`, optional map/flatMap variants, and secure wipe behavior over varied allocation sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Arena.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CMakeLists.txt -->
# sources/storage-engines/foundationdb/flow/CMakeLists.txt

## Purpose
`flow/CMakeLists.txt` defines how the Flow library, tests, support tools, generated headers, optional compression, optional Swift support, and benchmarks are built.

## Important APIs, Types, and Functions
Important build constructs include `FLOW_USE_ZSTD`, `fdb_find_sources(FLOW_SRCS)`, `configure_file` for `ApiVersion.h`, `SourceVersion.h`, and `config.h`, protocol-version generation through `protocol_version.py`, `add_flow_target` for `flow`, `flow_sampling`, `flowlinktest`, and `flow_test`, and optional `flow_swift` targets.

## Control Flow
The script gathers sources, removes executable entry points from library sources, appends architecture-specific assembly, configures headers, ensures Python/Jinja2 availability for protocol generation, creates the Flow static libraries, links platform dependencies, and adds optional ZSTD and Swift wiring. It creates `flowlinktest` to force undefined symbol detection because static/shared library creation alone would not.

## State and Persistence Behavior
Build artifacts include generated headers under the binary include directory, generated Java/Python protocol files, optional virtualenv state for protocol generation, libraries, executables, and Swift interop headers. No runtime persistence is defined here.

## Dependencies and Integration Points
The file integrates with Threads, Python3, Jinja2, OpenSSL, Boost, fmt, crc32, libb64, stacktrace, coroutine detection, jemalloc, valgrind, platform libraries, zstd compilation, benchmarks, mkcert, acac, and Swift-to-C++ interop.

## Risks and Edge Cases
The fallback Jinja2 virtual environment modifies the build tree and depends on pip/ensurepip availability. Link libraries are accumulated in `FLOW_LIBS` inside a loop, so changes should avoid accidental duplication or leakage. Cross-compiling disables benchmarks and has Swift TODOs. Generated protocol and API files must be dependencies of all targets that include them.

## Test Signals
Build success of `flow`, `flow_sampling`, `flowlinktest`, and `flow_test` validates most wiring. `flowlinktest` is the explicit undefined-symbol gate, and optional feature paths are tested only when their CMake options are enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CodeProbe.cpp -->
# sources/storage-engines/foundationdb/flow/CodeProbe.cpp

## Purpose
`CodeProbe.cpp` implements registration, listing, filtering, and missed-probe tracing for FoundationDB code probes used by simulation and coverage tooling.

## Important APIs, Types, and Functions
The main internal type is `CodeProbes`, a singleton containing a multimap from normalized file/line `Location` to `ICodeProbe` pointers. Public APIs in namespace `probe` include `registerProbe`, `traceMissedProbes`, `functionNameFromInnerType`, `ICodeProbe::filename`, equality operators, `printProbesXML`, and `printProbesJSON`. Annotation predicates include `probe::assert::NoSim` and `SimOnly`.

## Control Flow
Static probes register themselves into `CodeProbes::instance()`. Printing first verifies duplicate comments per file, then emits either XML coverage cases or newline-delimited JSON-like probe records, optionally filtered by execution context strings. `traceMissedProbes` coalesces probes by location, checks whether any probe at each location was hit, and traces one missed probe per unhit location when tracing is enabled.

## State and Persistence Behavior
State is process-local singleton metadata. It is not durable, but printed XML/JSON output can be consumed by external coverage tools. Probe hit state is owned by individual `ICodeProbe` instances.

## Dependencies and Integration Points
The file depends on `CodeProbe.h`, `CodeProbeUtils.h`, `Arena`, `network`, fmt, Boost demangling, and Boost unordered maps. It uses `FDB_SOURCE_DIR` to normalize file paths and `g_network` to evaluate simulation-specific annotations.

## Risks and Edge Cases
`normalizePath` uses `FDB_SOURCE_DIR` for both source and binary base variables, which may not strip true binary paths if that was intended. `printJSON` emits two demangled local type names before probe records, which looks diagnostic and may surprise machine consumers. Context parsing throws `invalid_option_value` on unknown strings.

## Test Signals
There are no unit tests in this file. Signals are generated probe lists, uniqueness warnings printed by `verify`, and missed-probe traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CodeProbe.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressedInt.cpp -->
# sources/storage-engines/foundationdb/flow/CompressedInt.cpp

## Purpose
`CompressedInt.cpp` provides unit coverage and debug bit-printing utilities for the templated `CompressedInt` serialization type declared in `flow/CompressedInt.h`.

## Important APIs, Types, and Functions
`printBitsLittle` and `printBitsBig` print raw bit patterns for diagnostics. `testCompressedInt<IntType>` serializes a value through `BinaryWriter`, optionally verifies exact encoded bytes, deserializes through `BinaryReader`, and checks the decoded value. `forceLinkCompressedIntTests` forces test linkage.

## Control Flow
The single test case validates known encodings for small signed integers and one large `int64_t`, then generates ten million deterministic bit-pattern values and round-trips them as 64-bit, 32-bit, and 16-bit compressed integers.

## State and Persistence Behavior
There is no persistent state. Serialized byte strings are transient `BinaryWriter` values using the current network protocol version from `g_network`.

## Dependencies and Integration Points
The file depends on Flow unit tests, `CompressedInt.h`, `BinaryReader`, `BinaryWriter`, `AssumeVersion`, and deterministic randomness. It validates a serialization primitive used anywhere compact integer wire/disk encoding is needed.

## Risks and Edge Cases
The randomized loop is intentionally large and can be expensive. Because it casts a growing `int64_t` into smaller integer types, it exercises truncation behavior as seen by template instantiation. Exact expected byte strings lock compatibility for representative encodings.

## Test Signals
Failures print original, encoded, expected, and decoded bit patterns before assertions. The test case name is `/flow/compressed_ints`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressedInt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressionUtils.cpp -->
# sources/storage-engines/foundationdb/flow/CompressionUtils.cpp

## Purpose
`CompressionUtils.cpp` implements Flow compression helpers for `CompressionFilter::NONE` and optionally `CompressionFilter::ZSTD`, including support discovery, default compression levels, random filter selection, and unit tests.

## Important APIs, Types, and Functions
The implemented methods are `CompressionUtils::compress(filter, data, arena)`, `compress(filter, data, level, arena)`, `decompress`, `getDefaultCompressionLevel`, `getRandomFilter`, and the static `supportedFilters`. Test helpers `testCompression` and `testCompression2` validate round trips and compressibility.

## Control Flow
At static initialization, `getSupportedFilters` adds `NONE` and, when `ZSTD_LIB_SUPPORTED` is defined, `ZSTD`. All public operations call `checkFilterSupported`. `NONE` copies bytes into the provided arena. `ZSTD` uses `ZSTD_compressBound`, `ZSTD_compress`, `ZSTD_decompressBound`, and `ZSTD_decompress`, then copies the result into the arena. Errors become `internal_error`.

## State and Persistence Behavior
No durable state exists. The only global state is the supported filter set. Returned compressed or decompressed data is arena-owned, so caller arena lifetime controls validity.

## Dependencies and Integration Points
The file depends on `CompressionUtils.h`, `Arena`, Flow errors, deterministic randomness, unit tests, and optionally libzstd. `flow/CMakeLists.txt` enables `ZSTD_LIB_SUPPORTED` when `FLOW_USE_ZSTD` is on.

## Risks and Edge Cases
`ZSTD_decompressBound` can return an unknown or very large bound for malformed data, so callers should not feed untrusted arbitrary compressed payloads without considering allocation size. `testCompression` asserts compressed random data differs from input; with `NONE` that would be false, so that helper is only used for ZSTD.

## Test Signals
Tests cover no-compression round trip and, when compiled with zstd, random-data zstd round trip plus a highly compressible string size check. Trace events mark completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressionUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressionUtils.h -->
# sources/storage-engines/foundationdb/flow/CompressionUtils.h

## Purpose
`CompressionUtils.h` declares Flow's compression filter enum and utility API for compressing and decompressing `StringRef` data into an `Arena`.

## Important APIs, Types, and Functions
`CompressionFilter` contains `NONE`, `ZSTD`, and sentinel `LAST`. `CompressionUtils` declares overloads for compression with default or explicit level, decompression, default-level lookup, random filter selection, string conversion helpers, support checking, and the static `supportedFilters` set.

## Control Flow
Inline helpers convert exact strings `"NONE"` and `"ZSTD"` to enum values and back. Unsupported filters throw `not_implemented`. `checkFilterSupported` checks the runtime compiled support set before implementation functions perform work.

## State and Persistence Behavior
The header declares no mutable instance state. Compression outputs are specified as `StringRef` values backed by a caller-provided `Arena`, so persistence depends on the arena owner.

## Dependencies and Integration Points
It includes `flow/Arena.h` and `<unordered_set>`. The implementation is in `CompressionUtils.cpp`, and build support for ZSTD is controlled in the Flow CMake file.

## Risks and Edge Cases
The enum-to-string and string-to-enum helpers must be updated whenever new filters are added before `LAST`. The closing include guard comment has a spelling mismatch, but the macro itself is consistent.

## Test Signals
Tests live in `CompressionUtils.cpp`; compile-time use of this header catches missing enum support and signature drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CompressionUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CoroTests.cpp -->
# sources/storage-engines/foundationdb/flow/CoroTests.cpp

## Purpose
`CoroTests.cpp` is a broad unit and performance test suite for Flow's C++ coroutine integration: futures, streams, cancellation, choose/race combinators, async maps, async results, generators, mutexes, uncancellable actors, and no-throw-on-cancel semantics.

## Important APIs, Types, and Functions
The file defines many small coroutine helpers such as `oneWaitActor`, `chooseTwoActor`, `consumeOneActor`, `sumActor`, `coro::errorOr` use cases, `YieldMockNetwork`, `YAMRandom`, `Tracker`, `LifetimeTracked`, AsyncResult producers, generator helpers, file line readers, and no-throw-on-cancel recorders. Test cases cover `yieldedFuture`, `Choose`, `race`, `quorum`, `getAll`, `FlowMutex`, `PromiseStream`, `StrictFuture`, `AsyncGenerator`, and `Generator`.

## Control Flow
Tests create ready, delayed, failing, cancelled, and dropped futures and assert exact readiness, reference counts, error codes, move/copy counts, cancellation propagation, and result ordering. Some tests use `YieldMockNetwork` to force `yield` scheduling behavior one tick at a time. Generator tests write a randomized 1MB file, read it back line-by-line using block generators, and compare expected arena-backed lines.

## State and Persistence Behavior
Most state is transient in promises, futures, coroutine frames, streams, and local counters. `testReadLines` creates and deletes a temporary file through `IAsyncFileSystem` when available. `LifetimeTracked` static count detects leaked coroutine result state. Several tests inspect promise/future reference counts after cancellation or completion.

## Dependencies and Integration Points
The file depends on Flow unit tests, async file APIs, network/yield behavior, tracing, TLS config, fmt, standard coroutines-adjacent utilities, and deterministic randomness. It is linked into Flow tests through `forceLinkCoroTests`.

## Risks and Edge Cases
The suite intentionally codifies subtle semantics: first-ready tie-breaking for `race`, cancellation after `Choose` is already ready, `NoThrowOnCancel` bypassing catch blocks on cancellation but not on ordinary errors, queued versus callback-delivered stream moves, and cancellation of remaining producers on `quorum`/`getAll` completion or error. Performance tests with one million iterations can be expensive and are partly diagnostic.

## Test Signals
Every `TEST_CASE` is a signal. Notable names include `/flow/coro/cancel1`, `/flow/coro/trivial_actors`, `/flow/coro/YieldedAsyncMap/randomized`, `/flow/coro/AsyncResult/noThrowOnCancel`, `/flow/coro/FlowMutex`, `/flow/coro/generators`, `/flow/coro/actor`, `/flow/coro/noThrowOnCancel/*`, and `/flow/coro/race*`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/CoroTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Deque.cpp -->
# sources/storage-engines/foundationdb/flow/Deque.cpp

## Purpose
`Deque.cpp` contains unit tests for Flow's custom `Deque` container, including normal queue behavior, wraparound at maximum size, and exception safety during growth.

## Important APIs, Types, and Functions
The tests exercise `Deque<T>::push_back`, `pop_front`, `pop_back`, indexing, `front`, `back`, `size`, `empty`, and `max_size`. `RandomlyThrows` is a test helper whose copy and assignment operations randomly throw Flow `success()` errors to stress growth rollback.

## Control Flow
The basic test mutates a deque through pushes and pops and validates remaining values. The queue test uses `std::queue<int, Deque<int>>` with randomized push/pop choices while checking FIFO order. The max-size test fills to capacity after wraparound, validates physical adjacency of `back` and `front`, and expects `std::bad_alloc` on over-capacity push. The exception-safety test retries pushes until they succeed and verifies all stored values.

## State and Persistence Behavior
All state is in-memory container data. There is no persistence.

## Dependencies and Integration Points
The file depends on `flow/Deque.h`, `flow/UnitTest.h`, deterministic randomness, and standard queue adaptation. It validates behavior for Flow subsystems that rely on the custom deque.

## Risks and Edge Cases
The max-size test assumes specific wraparound storage behavior and pointer adjacency. Exception safety is especially important because Flow error throwing during element movement must not corrupt existing deque contents.

## Test Signals
Test case names are `/flow/Deque/12345`, `/flow/Deque/queue`, `/flow/Deque/max_size`, and `/flow/Deque/grow_exception_safety`. `forceLinkDequeTests` ensures linkage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/Deque.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/DeterministicRandom.cpp -->
# sources/storage-engines/foundationdb/flow/DeterministicRandom.cpp

## Purpose
`DeterministicRandom.cpp` implements the deterministic random generator used throughout Flow tests and simulation, with reproducible integer, floating, byte, id, string, and probability helpers.

## Important APIs, Types, and Functions
Core methods include `gen64`, constructor, `random01`, `randomInt`, `randomInt64`, `randomUInt32`, `randomUInt64`, `randomSkewedUInt32`, `randomUniqueID`, `randomAlphaNumeric`, `randomBytes`, `truePercent`, `peek`, `resetSeed`, `addref`, and `delref`.

## Control Flow
The generator keeps one prefetched `next` value. `gen64` returns it, advances the underlying RNG, and optionally emits a sampled trace. Range methods modulo the 64-bit output into requested ranges while handling negative minima. Byte generation writes chunks of generated 64-bit values. Optional `randLog` output records generated values when enabled.

## State and Persistence Behavior
State is in-memory RNG state: the underlying engine, prefetched `next`, and whether random logging is enabled. `resetSeed` restores reproducible sequence state for a seed. There is no durable persistence unless `randLog` points to an external log file.

## Dependencies and Integration Points
The file depends on fmt, `Arena`, `DeterministicRandom.h`, `UnitTest`, Flow tracing, `UID`, `StringRef`, and reference counting. It is used heavily across workloads and unit tests to keep randomized behavior deterministic under simulation seeds.

## Risks and Edge Cases
Modulo reduction is simple and can introduce bias, acceptable for simulation/test randomness but not cryptographic use. `truePercent` asserts the percent is strictly between 0 and 100, so callers needing 0 or 100 must special-case. Negative range arithmetic is carefully unsigned and worth preserving.

## Test Signals
The `/flow/DeterministicRandom/truePercent` test checks 1, 50, and 99 percent ranges under fixed seeds, same-seed determinism, and ordering across probabilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/DeterministicRandom.cpp -->
