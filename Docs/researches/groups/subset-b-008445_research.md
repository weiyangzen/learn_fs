# Research Report: subset-b-008445

This grouped report covers FoundationDB fdbclient storage-server interfaces, system-key declarations, transaction/read helpers, tuple and tracing utilities, versioned map primitives, and bundled json_spirit headers. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h

## Purpose
`StorageServerInterface.h` defines the durable RPC interface and request/reply payloads used by clients, proxies, ratekeeper, data distribution, audit, checkpoint, change feed, and bulk dump code to communicate with a storage server. It also defines storage metrics types and small helpers used by read routing and MVCC storage sizing.

## Important APIs, Types, and Functions
Important exports include `StorageServerInterface`, `StorageInfo`, `StorageServerMetaInfo`, `ServerCacheInfo`, `GetValueRequest/Reply`, `GetKeyRequest/Reply`, range read and mapped-range read request/reply types, streaming range replies, `WatchValueRequest/Reply`, `GetShardStateRequest/Reply`, `StorageMetrics`, `WaitMetricsRequest`, `SplitMetricsRequest/Reply`, `ReadHotRangeWithMetrics`, checkpoint fetch requests, obsolete change feed request types, queuing metrics, hot shard and checksum requests, `BulkDumpRequest`, and `mvccStorageBytes`.

## Control Flow
The interface object carries endpoint streams for every storage-server RPC. Callers serialize a request containing keys, version, tags, read options, span context, version-vector freshness information, and a reply promise. The storage server actor consumes the matching endpoint, validates shard ownership, reads local state, and replies with either load-balanced data, metrics, or streamed chunks. Metrics requests are used by data distribution to wait for thresholds, split ranges, and discover read-hot subranges. Checkpoint and bulk dump requests initiate server-side checkpoint lookup or data transfer.

## State and Persistence Behavior
`StorageServerInterface` is persisted in the database under server-list system keys, so its serialization is guarded by protocol-version assertions and reinitializes derived endpoints from `getValue` on deserialization. Several obsolete change-feed types remain because request-stream members of the persisted interface still depend on their type identifiers. Request objects hold transient arenas and reply promises; metric and checksum replies serialize operational state but do not persist it by themselves. `mvccStorageBytes` estimates in-memory mutation cost using `VersionedMap` overhead.

## Dependencies and Integration Points
This header depends on FoundationDB RPC primitives, load balancing, locality, tracing, queue metrics, `CommitTransaction`, `TagThrottle`, `VersionVector`, `StorageCheckpoint`, audit and bulk dump metadata, and storage-server shard state. It is integrated with client read paths, storage server actors, data distribution, ratekeeper commit-cost feedback, TSS comparison, backup/change-feed remnants, audit, and bulk loading or dumping flows.

## Risks and Edge Cases
Changing serialized fields or endpoint ordering can break downgrade compatibility because server-list values are durable. Read request freshness depends on correctly populated `VersionVector` data. Large selector offsets, wrong-shard ownership, and streamed reply backpressure are important behavior boundaries. Obsolete change-feed structures can look dead but are persistence-sensitive. Metric arithmetic can overflow or become misleading if callers mix logical and physical metrics without respecting field semantics.

## Test Signals
Useful signals include simulation read/write and range-read tests, storage relocation and shard-state tests, data distribution metric/split tests, checkpoint and bulk dump workloads, tag throttle/ratekeeper integration tests, serialization compatibility tests across protocol versions, and wrong-shard or TSS comparison simulation coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h

## Purpose
`StorageServerShard.h` defines `StorageServerShard`, the compact representation of a continuous key range hosted by one storage server and its local assignment state.

## Important APIs, Types, and Functions
The main type is `StorageServerShard` with `ShardState` values `NotAssigned`, `Adding`, `ReadWritePending`, `ReadWrite`, `MovingIn`, and `Error`. Constructors capture range, creation version, actual shard ID, desired shard ID, state, and optional physical move metadata. Helpers include `notAssigned`, `getShardState`, `setShardState`, `getShardStateString`, `toString`, and `serialize`.

## Control Flow
Storage actors and management code construct shard objects when reporting shard state or mutating assignment status. State is stored internally as `int8_t`, converted to the enum by accessors, and serialized with range and ID metadata. `toString` formats range, IDs, version, state, and optional move-in shard ID for tracing.

## State and Persistence Behavior
The object is a serializable state record. It persists range ownership and creation/move metadata in messages or server-local structures, but this header does not perform storage writes. `version` records shard creation version, `id` records current shard ID, `desiredId` records intended shard ID, and `moveInShardId` links physical move metadata when present.

## Dependencies and Integration Points
It depends on `FDBTypes.h` for `KeyRange`, `Version`, and `UID`, plus Flow serialization. `StorageServerInterface.h` returns vectors of `StorageServerShard` through `GetShardStateReply`, and data distribution or physical shard movement code interprets the states.

## Risks and Edge Cases
`getShardState` trusts the stored `int8_t`; corrupt or future values stringify as `InvalidState`. Physical move states require callers to preserve `moveInShardId` consistently. Tests should catch transitions where `desiredId` diverges from `id` longer than intended.

## Test Signals
Shard assignment, physical shard move, recovery, wrong-shard, and data distribution tests are the main signals. Serialization round trips should preserve optional `moveInShardId` and all state enum values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageServerShard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h

## Purpose
`StorageWiggleMetrics.h` models persistent metrics and control data for perpetual storage wiggle, the process that periodically moves storage servers to refresh placement. It also provides transaction helpers for delay accounting and metric updates in system keyspace.

## Important APIs, Types, and Functions
Important types include `StorageWiggleMetrics`, `StorageWiggleDelay`, `StorageWiggleData`, and nested `StorageWiggleData::DataForDc`. Helpers include `toJSON`, `reset`, `addPerpetualWiggleDelay_impl`, `resetStorageWiggleMetrics_impl`, `addPerpetualWiggleDelay`, `clearPerpetualWiggleDelay`, `resetStorageWiggleMetrics`, and `updateStorageWiggleMetrics`.

## Control Flow
Wiggle code updates start/finish timestamps and smoothed duration totals, serializes only the persisted scalar fields and smoother totals, and reconstructs smoothers when deserializing. Delay updates run inside transactions with system-key and lock-aware options, fetch the current delay object, add a delta, and write it back. Metric updates first read the perpetual wiggle speed key and only store metrics if wiggle remains enabled.

## State and Persistence Behavior
Metrics and delay state are persisted under `perpetualStorageWigglePrefix`, `perpetualStorageWiggleStatsPrefix`, and DC-specific primary or remote subspaces. `StorageWiggleMetrics::reset` clears counters and timestamps while carrying forward smoother accumulated totals. All database helpers explicitly access system keys and lock-aware transactions.

## Dependencies and Integration Points
The file depends on `Smoother`, Flow serialization, `SystemData`, `KeyBackedTypes`, and `RunTransaction`. It integrates with data distribution, status JSON generation, fdbcli/status consumers, and primary/remote region storage wiggle orchestration.

## Risks and Edge Cases
The anonymous helper namespace in a header creates per-translation-unit helper definitions, which is acceptable for templates but can surprise readers. Clock-derived epoch timestamps rely on caller-provided values. `updateStorageWiggleMetrics` silently probes rather than writing if wiggle is disabled, so callers must not assume a successful future implies persistence. System-key access options are mandatory and easy to omit in new helper paths.

## Test Signals
Signals include perpetual wiggle simulation tests, status JSON checks, system-key persistence round trips, primary and remote region coverage, and tests that disable wiggle while updates race with metric writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageWiggleMetrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h

## Purpose
`Subspace.h` declares a small tuple-prefixed keyspace abstraction used by task buckets and other layers to pack, unpack, and range-query namespaced keys.

## Important APIs, Types, and Functions
`Subspace` exposes constructors from a `Tuple` and raw prefix, `key`, `contains`, `pack`, templated `pack`, string-specific `pack`, `unpack`, `range`, `subspace`, `get`, templated `get`, and string-specific `get`. It stores its raw prefix as `Standalone<VectorRef<uint8_t>>`.

## Control Flow
Callers construct a raw prefix, pack tuple elements by appending FoundationDB tuple encoding to the prefix, and derive child subspaces by extending the tuple path. `contains` checks whether a key has the subspace prefix; `unpack` removes the prefix and decodes the remaining tuple bytes; `range` returns the key range for the prefix plus optional tuple.

## State and Persistence Behavior
The object is an in-memory namespace descriptor. It does not persist data itself, but keys produced by it become durable database keys in users such as `TaskBucket`. The standalone prefix keeps packed memory alive across returned keys and child subspaces.

## Dependencies and Integration Points
It depends on Flow key types and `Tuple.h`. It integrates with `TaskBucket`, key-backed data structures, directory-like code, and any component that wants tuple-encoded sub-keyspaces.

## Risks and Edge Cases
`unpack` is only valid for keys contained by the prefix; callers should use `contains` or enforce namespacing. Raw prefixes can be arbitrary bytes, so collisions are possible if multiple owners choose overlapping prefixes. String packing requires the caller to choose byte-string versus UTF-8 tuple element semantics.

## Test Signals
Tuple pack/unpack tests, subspace range tests, task-bucket key layout tests, and boundary-key tests for prefix ranges are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Subspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h

## Purpose
`SystemData.h` documents and declares the reserved `\xff` system keyspace layout for FoundationDB. It provides constants plus encode/decode helpers for shard placement, server metadata, configuration, backup, restore, bulk load, bulk dump, audit, range locks, tag throttling, global configuration, and many cluster-control records.

## Important APIs, Types, and Functions
Important declarations include key ranges such as `normalKeys`, `systemKeys`, `specialKeys`, `keyServersKeys`, `serverKeysRange`, `serverListKeys`, `serverTagKeys`, `configKeys`, backup ranges, bulk load/dump ranges, range lock ranges, tag throttle ranges, log/apply mutation ranges, and many singleton keys. Helper functions encode and decode key server values, server keys, server tags, process classes, worker lists, checkpoint state, audit state, data moves, bulk load/dump state, range lock state, backup metadata, healthy zones, and exclusion/failure entries.

## Control Flow
Cluster components use the declared constants to build transaction key ranges and use matching encode/decode helpers to convert typed metadata into `Value` records. Data distribution reads `keyServers` and `serverKeys` mappings, storage recruitment writes `serverList` and `serverTag` keys, configuration code mutates `conf` keys, backup and restore code manages its reserved prefixes, and management commands update exclusion, failure, and locking keys.

## State and Persistence Behavior
Nearly every declaration maps to durable system-key state. Some keys are watched or changed as version signals, such as metadata changes, process class changes, excluded server version keys, tag throttle signal keys, and backup partition request keys. The header itself only declares constants and helpers, but it is the contract for persistent cluster metadata and therefore has strict compatibility implications.

## Dependencies and Integration Points
It depends on checksums, bulk loading/dumping, `FDBTypes`, range locks, and `StorageServerInterface`. It is included by storage, data distribution, cluster controller, master/proxy, backup/restore, CLI, status, and administrative code that needs to read or mutate system keys.

## Risks and Edge Cases
Key-prefix changes are high risk because older binaries, recovery, and downgrade paths may depend on exact layouts. The header includes `StorageServerInterface.h`, while that header includes `SystemData.h` indirectly through other files in some paths, so include-order discipline matters. Encode/decode helpers must match the on-disk format exactly. Plain `extern` declarations hide implementation details in `.cpp` files, so tests need to cover runtime values, not just compilation.

## Test Signals
Signals include system-key encode/decode unit tests, simulation recovery tests, data distribution movement tests, configuration mutation tests, backup/restore integration tests, CLI exclusion/failure tests, bulk load/dump tests, and downgrade/upgrade serialization compatibility checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h

## Purpose
`TagThrottle.h` defines transaction tag storage, system-key encoding for manual and automatic tag throttles, client-visible throttle records, commit-cost estimation state, and templated APIs for listing, adding, removing, expiring, and enabling tag throttles.

## Important APIs, Types, and Functions
Important types include `TransactionTagRef`, `TransactionTag`, `TagSet`, dynamic serialization traits for `TagSet`, `TagThrottleType`, `TagThrottledReason`, `TagThrottleKey`, `TagThrottleValue`, `TagThrottleInfo`, `ClientTagThrottleLimits`, `ClientTrCommitCostEstimation`, and maps keyed by transaction tag. `ThrottleApi` exports `getValidAutoEnabled`, `getRecommendedTags`, `getThrottledTags`, `signalThrottleChange`, `updateThrottleCount`, `unthrottleMatchingThrottles`, `expire`, `unthrottleAll`, `unthrottleTags`, `throttleTags`, and `enableAuto`.

## Control Flow
`TagSet` serializes as length-prefixed tag bytes and deserializes into request arena-backed refs. Listing APIs create transactions, read system keys, retry on errors, and convert each key/value to `TagThrottleInfo`. Throttle changes set system-key access, optionally update the manual throttle count against the configured limit, write or clear throttle keys, signal changes with a versionstamped atomic op, and commit with retry loops.

## State and Persistence Behavior
Throttle records live under `tagThrottleKeys`, with manual and automatic prefixes separated by `tagThrottleAutoKeysPrefix`. `tagThrottleAutoEnabledKey` controls auto behavior, `tagThrottleLimitKey` and `tagThrottleCountKey` enforce manual throttle count, and `tagThrottleSignalKey` wakes watchers. `TagThrottleValue` serialization is protocol-versioned and includes rate, expiration, initial duration, and reason.

## Dependencies and Integration Points
The header depends on Flow arenas, errors, network time, thread-future bridging, FDB options, FDB types, and commit transaction types. It integrates with fdbcli tag throttle commands, ratekeeper, commit proxies, storage-server busy tag reporting, and client transaction commit-cost accounting.

## Risks and Edge Cases
`TagSet` refs can share the containing request arena, so persisting deserialized tag refs beyond arena lifetime is unsafe. Manual throttle count updates must stay atomic with throttle key changes to avoid count drift. `getRecommendedTags` returns an empty vector when auto throttling is enabled, which callers must interpret correctly. Expiration uses local `now()`, so clock differences are handled differently from serialized client throttle limits, which convert expiration to a duration.

## Test Signals
Relevant tests include tag throttle CLI/API tests, manual count limit tests, auto enable/disable and recommendation tests, expiration tests, commit proxy throttling behavior, serialization compatibility for `TagThrottleValue`, and arena lifetime stress around serialized `TagSet` requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TagThrottle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h

## Purpose
`TaskBucket.h` declares a database-backed asynchronous task framework. A `TaskBucket` stores tasks in subspaces, executors reserve and run them with at-least-once semantics, and `FutureBucket`/`TaskFuture` provide database-backed completion and callback chaining.

## Important APIs, Types, and Functions
Important types include `Task`, `TaskParam<T>`, `ReservedTaskParams`, `TaskBucket`, `FutureBucket`, `TaskFuture`, `TaskFuncBase`, registration macros, and `TaskCompletionKey`. Main methods cover adding tasks, reserving `getOne`, executing `doTask`/`doOne`/`run`, pausing, clearing, finishing, extending timeouts, keep-running validation, checking emptiness, task counts, futures, future joins, callbacks, and task-function dispatch.

## Control Flow
Tasks are created inside transactions with reserved parameters such as type, priority, version, done future, validation key, and block ID. Executors poll available task subspaces, move tasks to active/timeout state, execute non-transactional `TaskFuncBase::execute`, then call transactional `finish`, which is intended to run exactly once. Long-running tasks periodically call `keepRunning` or extend timeouts. Futures can schedule follow-up tasks when set, allowing task graphs to be built transactionally.

## State and Persistence Behavior
All task queue state is persisted below the configured `Subspace`, including available, prioritized, active, timeout, pause, future, block, and callback keys. Task execution side effects are at least once; finish database mutations are designed to be exactly once for a task. Access to system keys and lock-aware options is configurable per bucket and future bucket.

## Dependencies and Integration Points
It depends on Flow futures, dispatched factories, generic actors, `NativeAPI.actor.h`, RYW transactions, `Subspace`, and `KeyBackedTypes`. It integrates with background management workflows that need persistent task queues, including backup, restore, data movement, and other long-running database jobs.

## Risks and Edge Cases
Task execution can be duplicated if an executor loses contact or misses timeout extension, so `execute` implementations must be idempotent or check `keepRunning`. `finish` must avoid long external side effects because it is the exactly-once transactional boundary. Priority compatibility is delicate because priority 0 uses the legacy `available` subspace. Validation keys can interrupt tasks unexpectedly if changed by other actors.

## Test Signals
Signals include task lifecycle tests, timeout/retry tests, future join/callback tests, pause/resume behavior, prioritized task ordering, validation-key interruption, and simulated executor failures during execute and finish.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TaskBucket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h

## Purpose
`ThreadSafeTransaction.h` declares thread-safe implementations of the generic client API interfaces. These wrappers serialize operations onto the FoundationDB network thread while exposing `IDatabase`, `ITransaction`, and `IClientApi` to callers that may originate outside the network thread.

## Important APIs, Types, and Functions
Main types are `ThreadSafeDatabase`, `ThreadSafeTransaction`, and `ThreadSafeApi`. Database methods include transaction creation, database options, main-thread busyness, server protocol, connection status, worker reboot, forced recovery, snapshots, shared state, and client status. Transaction methods cover reads, ranges, mapped ranges, mutations, conflict ranges, watches, commit, version vector, span context, throttling duration, cost, approximate size, options, deferred errors, retry, reset, and debug tracing. API methods cover version selection, network options, setup/run/stop, database creation, and completion hooks.

## Control Flow
Public calls return `ThreadFuture` objects and dispatch work to the network thread. `ThreadSafeDatabase` owns or wraps a `DatabaseContext`; `ThreadSafeTransaction` owns a `ReadYourWritesTransaction` pointer and an initialization flag. Transaction methods forward to lower-level RYW/Native API operations after crossing the thread boundary. `ThreadSafeApi` manages process-global API version and network lifecycle with a mutex-protected completion-hook list.

## State and Persistence Behavior
The wrappers manage in-memory references to database contexts, transactions, network state, and shared state. They do not persist records directly, but all transaction mutation calls affect database state once committed. Thread safety is provided by serialization and thread-safe reference counting rather than by making the lower-level transaction object independently concurrent.

## Dependencies and Integration Points
The header depends on API/protocol version types, `ReadYourWrites`, thread helpers, cluster interfaces, and `IClientApi`. It is a bridge for C bindings, Java bindings, fdbcli refactoring, and any external-client path that needs a stable thread-safe interface.

## Risks and Edge Cases
Lifetime of raw `DatabaseContext*` and `ReadYourWritesTransaction*` must be controlled carefully. Move construction exists to support actors, which makes initialization-state correctness important. Network lifecycle methods are process-global and can race if callers misuse API setup/run/stop ordering. The fdbcli refactoring constructor from raw RYW transaction is explicitly transitional.

## Test Signals
Useful signals include C API and Java binding integration tests, external-client tests, multi-threaded transaction tests, network setup/stop lifecycle tests, client status tests, and tests that exercise futures completing from non-network threads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ThreadSafeTransaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h

## Purpose
`Tracing.h` declares the client/server span model used for FoundationDB tracing. It provides span contexts, span events, span attributes, trace sampling flags, span kind/status enums, and the tracer interface.

## Important APIs, Types, and Functions
Important exports include `Location`, the `_loc` literal, `TraceFlags`, `SpanContext`, `SpanKind`, `SpanStatus`, `SpanEventRef`, `Span`, `TracerType`, `ITracer`, and `openTracer`. `Span` supports construction from a context or parent, move-only ownership, links, events, attributes, parent replacement, and destructor-driven tracing behavior.

## Control Flow
Callers create spans at RPC or operation boundaries, passing parent context when available. Constructors copy trace IDs and sampling flags from parents, assign random span IDs, record begin time from `g_network`, and add local address attributes. Links can force sampling and initialize an otherwise invalid context. The destructor or assignment implementation emits the span to the active tracer when appropriate.

## State and Persistence Behavior
Trace data is in-memory until passed to an `ITracer`. `Span` owns strings, attributes, links, and events in an arena. Serialized `SpanContext` values propagate through RPC requests such as storage reads. The header itself has no durable persistence, but log-file tracers can persist emitted spans externally.

## Dependencies and Integration Points
It depends on Flow network, randomness, arenas, transport address reporting, and FDB key/value types. Storage read requests include `SpanContext`, and NativeAPI, proxies, commit paths, and server actors use spans for OpenTelemetry-like trace propagation.

## Risks and Edge Cases
`Span(Location)` intentionally creates mostly unsampled background spans, so instrumentation can appear absent unless parent sampling is present. Constructors warn that one overload does not enforce parent/context trace ID equality. Destruction-time emission requires move semantics to invalidate moved-from spans correctly. `TracerType` names are intentionally not stable client API.

## Test Signals
Signals include trace serialization tests, simulation tracer tests for `NETWORK_LOSSY` and `SIM_END`, log tracer output checks, parent/child propagation tests, sampling flag tests, and RPC request tests that preserve `SpanContext`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tracing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h

## Purpose
`TransactionLineage.h` declares actor-lineage metadata for transaction operations so sampled actor stacks can report transaction IDs and the current high-level operation.

## Important APIs, Types, and Functions
Important exports are `TransactionLineage`, its `Operation` enum, `TransactionLineageCollector`, and, when `ENABLE_SAMPLING` is defined, `ScopedLineage<T,V>` plus `make_scoped_lineage`. Operations include get value, get key, get range, watch, get read version, commit, and key-server location lookup.

## Control Flow
Transaction code writes lineage fields into the current actor lineage. The collector reads optional `txID` and `operation` values and converts them into a map of human-readable properties. `ScopedLineage` temporarily replaces one lineage member and restores the previous value when leaving scope unless moved or released.

## State and Persistence Behavior
Lineage state is in-memory diagnostic metadata associated with actor execution. It is not persisted to the database. The scoped helper mutates the current lineage and relies on RAII to restore values across normal control flow.

## Dependencies and Integration Points
The header depends on `ActorLineageProfiler.h` and integrates with NativeAPI transaction actors, sampling builds, profiling collectors, and diagnostics that inspect actor lineage trees.

## Risks and Edge Cases
The scoped helper only exists under `ENABLE_SAMPLING`, so instrumentation code must be compiled conditionally. Move assignment restores the old value before taking ownership, which is correct but easy to misuse if stored in containers. Collector output intentionally omits unset fields, so missing lineage may mean either no operation or disabled sampling.

## Test Signals
Sampling/profiler tests, actor-lineage collector tests, and transaction operation instrumentation tests are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TransactionLineage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h

## Purpose
`Tuple.h` declares FoundationDB tuple packing and unpacking support for C++ code, including primitive types, byte and UTF-8 strings, nested tuples, versionstamps, and user-defined tuple element codes.

## Important APIs, Types, and Functions
Important members include `Tuple::UnicodeStr`, `Tuple::UserTypeStr`, static `unpack`, `tupleToString`, `unpackUserType`, append overloads for strings, integers, bool, float, double, null, `TupleVersionstamp`, and user types, `pack`, `makeTuple`, `getType`, typed getters, `subTupleRawString`, `range`, `subTuple`, `getData`, and `getDataAsStandalone`.

## Control Flow
Callers build tuples by appending values, producing a packed byte string that preserves FoundationDB tuple ordering. Unpack parses a packed string into offsets and optional incomplete numeric filtering. Getters inspect the element type at a stored offset and decode the requested value. `range` computes the key range represented by a tuple prefix.

## State and Persistence Behavior
`Tuple` stores packed bytes in a standalone arena and element offsets in memory. It does not write to the database, but packed outputs are durable key material used by subspaces, directory-like layers, task buckets, and system-key encodings.

## Dependencies and Integration Points
It depends on Flow types, `FDBTypes`, and `TupleVersionstamp`. It integrates with C++ tuple users, Java binding tests conceptually, subspace APIs, task parameter codecs, and any code requiring lexicographically ordered composite keys.

## Risks and Edge Cases
Tuple encoding compatibility is critical because packed bytes become database keys. Incomplete numeric tuple parsing is optionally filtered, and callers must choose the right behavior for range scans. User type decoding can be excluded unless explicitly requested. `clear` replaces the standalone buffer so previously returned packed strings remain valid.

## Test Signals
Tuple round-trip tests, cross-binding tuple compatibility tests, key ordering tests, versionstamp tuple tests, incomplete tuple parsing tests, and subspace range tests are relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Tuple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h

## Purpose
`TupleVersionstamp.h` declares the 12-byte tuple versionstamp wrapper used by tuple encoding for incomplete and complete FoundationDB versionstamps.

## Important APIs, Types, and Functions
The file defines `VERSIONSTAMP_TUPLE_SIZE`, `TupleVersionstamp::DEFAULT_VERSIONSTAMP`, constructors from default, `StringRef`, and `(version, batchNumber, userVersion)`, plus `getVersion`, `getBatchNumber`, `getUserVersion`, `size`, `begin`, and equality.

## Control Flow
Callers construct a versionstamp either from raw bytes or from structured version, batch, and user version fields. Tuple code appends the bytes and later decodes fields through getters. The default value is the incomplete versionstamp marker with invalid version bytes and zero batch/user version.

## State and Persistence Behavior
The type stores a standalone 12-byte string. It does not persist independently, but packed tuple keys containing versionstamps are written by versionstamped operations and resolved at commit time.

## Dependencies and Integration Points
It depends on Flow arenas and is consumed by `Tuple.h`, transaction versionstamp APIs, tuple layer code, and binding compatibility tests.

## Risks and Edge Cases
Raw `StringRef` construction must enforce or assume 12-byte input in the implementation. Signed getter return types for batch and user version require care around values above signed range. Versionstamp encoding must stay cross-language compatible.

## Test Signals
Signals include tuple versionstamp pack/unpack tests, versionstamped key commit tests, and cross-binding tuple compatibility tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/TupleVersionstamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h

## Purpose
`VersionVector.h` defines per-storage-tag commit-version vectors used to communicate read freshness and causality information efficiently across sequencer, GRV proxy, client, and storage-server read paths.

## Important APIs, Types, and Functions
`VersionVector` stores a sorted `boost::container::flat_map<Tag, Version>`, `maxVersion`, and a cached encoded size. It exports setters, getters, `clear`, `getDelta`, `applyDelta`, string/compare helpers, encoded-size helpers, custom serialization and deserialization helpers for localities, tag IDs, and version deltas, dynamic serialization traits, and constants `minVersionVector`, `maxVersionVector`, and `invalidVersionVector`.

## Control Flow
Writers set tag versions only with monotonically increasing versions and update `maxVersion`. `getDelta` builds either the entire vector or only entries newer than a reference version based on `CLIENT_KNOBS->SEND_ENTIRE_VERSION_VECTOR`. `applyDelta` ignores invalid or stale deltas and otherwise merges newer entries. Serialization run-length encodes tag localities, compactly chooses tag ID width, delta-encodes commit versions from the minimum, and appends `maxVersion`.

## State and Persistence Behavior
The vector is normally serialized in RPC messages and read-version metadata rather than persisted as standalone database state. Cached encoded size is mutable performance state and invalidated on vector updates. The map must remain ordered because serialization groups consecutive tag localities.

## Dependencies and Integration Points
It depends on Boost flat maps, sets, FDB types, and client knobs. It integrates with `StorageServerInterface` read requests, commit/read-version propagation, storage freshness checks, and GRV proxy optimization.

## Risks and Edge Cases
`operator==` compares only `maxVersion`, while `compare` checks full map equality; callers must choose intentionally. Serialization assumes ordered tags and trusted buffer sizes. `applyDelta` only merges entries with version greater than current `maxVersion`, which matches delta semantics but would drop a tag-specific update lower than global max. Cached size assertions can expose stale invalidation bugs.

## Test Signals
Signals include version-vector unit tests for delta/apply behavior, serialization round trips with mixed localities and tag ID widths, read freshness tests, GRV proxy/client tests, and knob coverage for sending entire vectors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h

## Purpose
`VersionedMap.h` implements a partially persistent ordered map backed by a randomized treap-like persistent tree. It supports reading historical versions, creating new versions, mutating the latest version, and forgetting old roots.

## Important APIs, Types, and Functions
Important pieces include `DeferredCleanupWorklist`, `deferredCleanupActor`, namespace `PTreeImpl` with `PTree`, `PTreeFinger`, `insert`, `remove`, `removeFinger`, `split`, `append`, `compact`, `validate`, and traversal helpers, `ValueOrClearToRef`, and template `VersionedMap<K,T>` with version/root management, insert/erase, compaction, iterators, `ViewAtVersion`, historical lookup helpers, and `isClearContaining`.

## Control Flow
Each version points to a root in an ordered deque. `createNewVersion` appends a new root snapshot. Mutations update the latest root using persistent tree nodes that can hold an auxiliary pointer to avoid full path copying. Historical reads choose the newest root not greater than the requested version and traverse with version-aware child selection. Forgetting old versions erases old roots and can asynchronously drain uniquely owned tree nodes in bounded batches.

## State and Persistence Behavior
`VersionedMap` is in-memory MVCC state. Storage servers and read-your-writes logic use it to retain historical key-value views, clear ranges, and mutation snapshots. It does not directly persist to disk, but it models durable versioned database contents and contributes to memory accounting through `overheadPerItem`.

## Dependencies and Integration Points
It depends on Flow references, fast allocation, indexed-set-style map pairs, FDB types, randomness, and actor yielding. It integrates with storage-server MVCC maps, `WriteMap`, mutation logs, and `StorageServerInterface::mvccStorageBytes`.

## Risks and Edge Cases
Persistent tree correctness is subtle: version numbers must increase monotonically, fingers are invalidated by mutation, and auxiliary pointer compaction must not remove data still reachable by retained versions. Random priority balance is probabilistic. Recursive reference destruction is avoided by deferred cleanup, but cancellation and ownership checks are important. `getNextOldestVersion` assumes at least two roots.

## Test Signals
Signals include versioned map unit tests, historical read tests, random insert/erase validation, compaction and forget-version tests, storage-server MVCC simulation tests, memory accounting checks, and stress tests with long retained-version windows.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionedMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h

## Purpose
`WriteMap.h` declares the read-your-writes mutation overlay that tracks point mutations, clear ranges, conflict ranges, unreadable ranges, and dependency on snapshot values before a transaction commits.

## Important APIs, Types, and Functions
Important types include `RYWMutation`, `OperationStack`, boolean parameter wrappers, `WriteMapEntry`, comparison operators, and `WriteMap` with `mutate`, `clear`, `addUnmodifiedAndUnreadableRange`, `addConflictRange`, nested `iterator`, `coalesce`, `coalesceOver`, `coalesceUnder`, and private `clearNoConflict`.

## Control Flow
The map starts with sentinel entries for all keys and after-all keys. Mutations are inserted into a persistent tree at an internal version. Operation stacks coalesce or layer atomic operations, point writes, and clears. Iterators produce a complete segmentation of the keyspace into unmodified ranges, cleared ranges, independent writes, and dependent writes. Read-your-writes code combines these segments with snapshot reads to synthesize transaction-visible results.

## State and Persistence Behavior
`WriteMap` is transaction-local in-memory state backed by an arena and `PTreeImpl` persistent tree. It tracks conflict/unreadable flags and local mutation effects but persists only when the transaction commits through lower-level commit machinery. Its internal `ver` is not a database version; it separates iterator snapshots from later writes.

## Dependencies and Integration Points
It depends on FDB types, `VersionedMap`, `SnapshotCache`, and atomic mutation helpers. It integrates with `ReadYourWritesTransaction`, conflict range handling, snapshot cache reads, atomic operation coalescing, and approximate transaction size/cost calculations.

## Risks and Edge Cases
Atomic coalescing must preserve FoundationDB mutation semantics, especially dependent operations needing a snapshot value. Clear ranges and conflict ranges overlap but are tracked separately. Iterator snapshots can become stale after writes by design. Sentinel key handling must cover the entire keyspace without leaking after-all markers into user-visible results.

## Test Signals
Read-your-writes unit tests, atomic operation coalescing tests, conflict range tests, clear range/range read tests, unreadable range tests, and randomized transaction overlay tests are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h

## Purpose
`json_spirit_error_position.h` declares the small error-position object thrown by json_spirit parsing functions that report line and column information.

## Important APIs, Types, and Functions
The file defines `json_spirit::Error_position` with default and `(line, column, reason)` constructors, equality, and public fields `line_`, `column_`, and `reason_`.

## Control Flow
Position-aware parser paths construct `Error_position` when invalid input is found. Equality compares reason, line, and column, with a fast self-comparison path.

## State and Persistence Behavior
The type is transient exception/diagnostic state. It has no database persistence and no global state.

## Dependencies and Integration Points
It depends only on `<string>` and is included by `json_spirit_reader_template.h`. Callers catching parse errors can inspect line, column, and reason.

## Risks and Edge Cases
The fields are public and unsigned, so absent positions default to zero. Non-position parser paths may throw strings instead of this type, so callers need to know which API they used.

## Test Signals
Parser tests for invalid JSON through `read_*_or_throw` should assert line, column, and reason values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_error_position.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h

## Purpose
`json_spirit_reader_template.h` implements json_spirit's Boost.Spirit Classic based JSON parser templates for string, stream, iterator, ASCII, and wide-string value types.

## Important APIs, Types, and Functions
Important helpers include `is_eq`, `hex_to_num`, `hex_str_to_char`, `unicode_str_to_char`, `append_esc_char_and_incr_iter`, `substitute_esc_chars`, `get_str`, `Semantic_actions`, `throw_error`, `Json_grammar`, `add_posn_iter_and_read_range_or_throw`, `Multi_pass_iters`, `read_range_or_throw`, `read_range`, `read_string`, `read_string_or_throw`, `read_stream`, and `read_stream_or_throw`.

## Control Flow
Boost.Spirit parses JSON grammar rules for objects, arrays, strings, numbers, booleans, and null. Semantic actions maintain a pointer to the current compound value plus a stack of parent values, adding parsed members to arrays or objects through the value configuration. Non-throwing APIs catch all parse exceptions and return false. Throwing string/stream APIs wrap iterators in position iterators so errors include line and column.

## State and Persistence Behavior
Parsing state is local to `Semantic_actions` and the Boost.Spirit parse invocation. The input stream path disables `skipws` and uses multipass iterators. No database or global state is persisted.

## Dependencies and Integration Points
The header depends on json_spirit value and error headers, Boost.Bind, Boost.Function, Boost version-dependent Spirit Classic includes, multipass and position iterators. It integrates with FoundationDB code that still uses bundled json_spirit for JSON status/config parsing.

## Risks and Edge Cases
The grammar permits C/C++ style comments through the skipper, which is outside strict JSON. Escape handling maps `\uHHHH` directly into the target character type and does not perform surrogate-pair UTF-8 composition. Number parsing tries strict real, signed int64, then uint64. Non-throwing APIs catch all exceptions and lose reason details. Optional `BOOST_SPIRIT_THREADSAFE` is commented out.

## Test Signals
Signals include JSON round-trip tests, invalid JSON error-position tests, comment handling tests, escape and unicode tests, int64/uint64/real parsing tests, stream parsing tests, and wide-string parsing when enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_reader_template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h

## Purpose
`json_spirit_value.h` defines the json_spirit in-memory JSON value model, including vector-backed and map-backed object configurations for narrow and wide strings.

## Important APIs, Types, and Functions
Important exports include `Value_type`, `Null`, template `Value_impl<Config>`, `Pair_impl<Config>`, `Config_vector`, `Config_map`, typedefs `Value`, `Pair`, `Object`, `Array`, `wValue`, `mValue`, and `wmValue` when enabled, `to_str`, typed getters, constructors from JSON-compatible types and compatible Boost variants, and `value_type_to_string`.

## Control Flow
`Value_impl` stores data in a Boost variant containing object, array, string, bool, signed integer, real, null, or unsigned integer. Constructors normalize `int` to `int64_t` and keep `uint64_t` distinguishable while reporting it as `int_type`. Getters check the active JSON type and throw `std::runtime_error` with type names on mismatch. Config classes define whether objects append duplicate names in a vector or assign by key in a map.

## State and Persistence Behavior
Values are ordinary in-memory objects with recursive Boost variant storage. They do not persist directly. The typedef selection macros enable all narrow/wide and vector/map value models in this copy, affecting compile-time surface and object behavior.

## Dependencies and Integration Points
The file depends on STL containers and strings, assertions, streams, standard exceptions, Boost config, integer types, shared pointers, and variant. Reader and writer templates use these value models to parse and emit JSON for FoundationDB components that still rely on json_spirit.

## Risks and Edge Cases
`get_int` narrows `int64_t` to `int`, and signed/unsigned conversions in `get_int64` and `get_uint64` can wrap if callers ask for the wrong width. Vector-backed objects preserve duplicate keys, while map-backed objects overwrite by name. Enabling all value variants increases compile cost. Type checking happens at runtime rather than compile time.

## Test Signals
Signals include construction and typed getter tests, signed/unsigned boundary tests, vector versus map object duplicate-key behavior, parser/writer round trips, wide-string builds, and type mismatch exception tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_value.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h

## Purpose
`json_spirit_writer_options.h` declares the bit flags controlling json_spirit JSON output formatting and character escaping.

## Important APIs, Types, and Functions
The file defines `json_spirit::Output_options` values `none`, `pretty_print`, `raw_utf8`, `remove_trailing_zeros`, `single_line_arrays`, and `always_escape_nonascii`.

## Control Flow
Writer code treats these enum values as bit flags. Pretty and single-line array modes influence whitespace and newlines, UTF-8 and non-ASCII flags influence string escaping, and `remove_trailing_zeros` influences default double precision.

## State and Persistence Behavior
The file contains only constants and has no runtime state. Its effects are visible in serialized JSON output.

## Dependencies and Integration Points
It has no external include dependencies and is consumed by `json_spirit_writer_template.h`.

## Risks and Edge Cases
`single_line_arrays` is marked as no longer used but still affects writer behavior for compatibility. `raw_utf8` intentionally permits non-standard raw non-printable output. Since this is a plain enum, callers can combine invalid or unknown bits without type protection.

## Test Signals
Writer tests should cover each flag and combinations, especially pretty printing, single-line arrays, raw UTF-8, forced escaping, and double precision behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_template.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_template.h

## Purpose
`json_spirit_writer_template.h` implements json_spirit JSON generation for configured value types and output streams.

## Important APIs, Types, and Functions
Important helpers include `to_hex_char`, `non_printable_to_string`, `add_esc_char`, `add_esc_chars`, template `Generator<Value_type,Ostream_type>`, `write_stream`, and `write_string`.

## Control Flow
`write_stream` forces decimal output and constructs a `Generator`. The generator saves stream state, sets precision from explicit input or options, recursively emits objects, arrays, strings, booleans, integers, unsigned integers, doubles, and null. String output escapes JSON control characters, optionally writes raw UTF-8, or emits `\uNNNN` sequences for non-printable/non-ASCII characters. Pretty mode controls indentation, spaces, and newlines; single-line array mode keeps scalar arrays compact.

## State and Persistence Behavior
Generation state is local: output stream reference, indentation level, flags, precision, and an IOS state saver. No database state is persisted, but produced JSON can become logs, status payloads, or configuration text.

## Dependencies and Integration Points
It depends on json_spirit value and writer options, assertions, streams, iomanip, wide character print classification, and Boost IO state saving. It integrates with status and configuration writers using json_spirit values.

## Risks and Edge Cases
Escaping uses `iswprint` on widened character values and simple `\uNNNN` formatting, which may not fully model UTF-8 or surrogate pairs. `raw_utf8` can emit non-standard JSON for non-printable bytes. Double precision defaults differ when `remove_trailing_zeros` is set. Pretty printing arrays/objects with empty contents still emits newline/indent formatting.

## Test Signals
Signals include writer round trips through the reader, escaping tests for quotes/backslashes/control bytes/non-ASCII, pretty and single-line formatting snapshots, integer and uint64 output tests, and double precision tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/json_spirit/json_spirit_writer_template.h -->
