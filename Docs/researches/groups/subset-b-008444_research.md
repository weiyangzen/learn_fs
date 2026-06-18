# subset-b-008444 research

Grouped research for FoundationDB fdbclient headers in `sources/storage-engines/foundationdb/fdbclient/include/fdbclient`. Each section preserves the source path and is bounded for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/NativeAPI.actor.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/NativeAPI.actor.h

## Purpose
`NativeAPI.actor.h` declares the native FoundationDB client entry points for network setup, database handles, non-RYW transactions, watch state, retry state, storage metric helpers, checkpoint helpers, and several administrative actors. It is the core public/internal header that ties Flow actors, RPC-facing client metadata, FDB option validation, tracing, transaction logging, and commit proxy requests into a single transaction API.

## Important APIs, Types, And Functions
- `NetworkOptions` stores global client/network configuration: cluster file, trace output settings, supported client versions, role flags, profiling, and client knob overrides.
- `Database` wraps `Reference<DatabaseContext>` and exposes factory methods for connection records, cluster files, simulated databases, direct context ownership, transaction defaults, and a coroutine-style `run()` retry loop.
- `TransactionOptions` captures per-transaction switches such as priority, retry backoff, GRV flags, raw/system access, lock awareness, cost accounting, conflict reporting, GRV cache behavior, storage quota bypass, and tag sets.
- `TransactionLogInfo` buffers structured client log events and can emit them to trace logs, database log mutation payloads, or both.
- `Watch` models key watches with old and set values, trigger promises, underlying watch future, and optional read options.
- `TransactionState` owns read version state, metadata version, auth token, transaction options, tracing span context, provisional proxy selection, commit version, conflicting-key map, cost counters, idempotency state, and start/read-version actors.
- `Transaction` is the native transaction facade: reads (`get`, `getKey`, range, mapped range, stream), conflict ranges, writes, atomic ops, watches, commit, retry (`onError`), option setting, versionstamp, protocol version, cost/throttle metrics, reset, logging, span and transaction IDs, and conflict range inspection.
- Free functions cover network lifecycle (`setNetworkOption`, `setupNetwork`, `runNetwork`, `stopNetwork`), integer option parsing, snapshots, checkpoints, safe exclusions, storage wiggle control, key size limits, storage metrics, split points, worker interface discovery, server class discovery, key location lookup, and transaction refresh.

## Control Flow And State
`Database::run()` constructs a `Transaction`, repeatedly awaits any prior `onError`, runs the caller function, and retries on `Error` by assigning `tr.onError(e)` to the next loop. `Transaction::getReadVersion()` lazily creates `TransactionState::readVersionFuture`; range/read APIs feed through private templated `getRangeInternal` implementations. Commit state is tracked with `CommitTransactionRequest tr`, `commitResult`, `committing`, watches, and `extraConflictRanges`. `reset()` and `fullReset()` rebuild transaction state, while `cloneAndReset()` lets `TransactionState` preserve selected options/logging and optionally generate a new tracing span.

## Persistence And External State
This header declares the structures that become persistent mutations: commit requests, read/write conflict ranges, watches, versionstamp promises, transaction logs, checkpoint metadata writes, storage wiggle configuration writes, and snapshot requests. `TransactionLogInfo` serializes log events with `BinaryWriter`. `createCheckpoint()` inserts mutations so each overlapping shard creates a checkpoint at commit version. `snapCreate()` requests a cluster-wide coordinator/TLog/storage snapshot. Persistent transaction defaults are inherited from `DatabaseContext`.

## Dependencies And Integration Points
It depends heavily on Flow (`Future`, `Promise`, actors, tracing, metrics), `FDBTypes`, option enums, commit proxy interfaces, cluster/coordination interfaces, key range maps, client log events, `ReadYourWritesTransaction` forward declarations, storage checkpoint types, and client knobs. It integrates with commit proxies, GRV proxies, storage servers, data distribution, transaction tracing, network setup, and the actor compiler (`actorcompiler.h`/`unactorcompiler.h`).

## Risks And Edge Cases
The API surface is central and option-heavy; adding an option requires updating reset/clear behavior and option propagation. Transaction retry lambdas must be idempotent. Watch cancellation and commit futures must be settled on all error paths. `TransactionState::readVersion()` asserts readiness, so callers must not bypass the future lifecycle. `TransactionLogInfo` can silently stop accumulating database logs after flush. Key size helpers distinguish system, raw, read, write, and clear semantics; using the wrong helper can admit invalid operations or reject valid system operations.

## Test Signals
Relevant tests should exercise network lifecycle errors, retry/onError semantics, transaction options, read version caching, conflict range accounting, commit success and unknown-result paths, versionstamp fulfillment, watch setup/cancel, transaction log flushing, storage metric split helpers, safe exclusion calls, checkpoint creation/lookup, and system/raw key size boundaries. Simulation tests should cover buggified client failures, provisional proxy use, idempotent retry behavior, and trace/log side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/NativeAPI.actor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Notified.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Notified.h

## Purpose
`Notified.h` provides a small monotonic value wrapper that lets actors wait until a numeric or metric-like value reaches a requested threshold. It is used for progress signals such as versions or time-like counters where waiters should complete as soon as the observed value advances far enough.

## Important APIs, Types, And Functions
- `IsMetricHandle<T>` detects `MetricHandle<T>` so metric-backed `Notified` instances can be initialized safely.
- `Notified<T, ValueType>` stores the current value and a priority queue of waiters keyed by threshold.
- `whenAtLeast(limit)` returns ready `Void()` if the value already meets the limit, otherwise enqueues a `Promise<Void>`.
- `set(v)` asserts monotonic increase, updates the value, pops all satisfied waiters, and sends them after removal.
- `initMetric(name, id)` initializes metric handles while preserving the current value.
- `NotifiedVersion` and `NotifiedDouble` are convenience aliases.

## Control Flow And State
The state is `val` plus a min-heap implemented by `std::priority_queue` with inverted comparison. `set()` moves promises out of the heap into a vector before sending them, which avoids callback reentrancy while the priority queue is being modified. Move construction and assignment transfer both value and waiter queue.

## Persistence And External State
The type is in-memory only. If `T` is a metric handle, `initMetric()` attaches it to TDMetric infrastructure; otherwise, invalid metric initialization emits a trace error. No data is serialized or persisted.

## Dependencies And Integration Points
It depends on `FDBTypes` for `Version`, Flow `Future`/`Promise`, TDMetric handles, Swift support annotations, and TraceEvent. It is a generic synchronization primitive for actor code and version notification patterns.

## Risks And Edge Cases
`set()` asserts `v >= val`; callers must never decrease values. `whenAtLeast()` can accumulate waiters indefinitely if the threshold is never reached. Metric initialization is compile-time gated but non-metric use logs an error instead of failing compilation. Moving an active `Notified` transfers pending waiters, so dangling references to the old object are unsafe.

## Test Signals
Tests should check immediate readiness, deferred readiness, multiple waiters released in threshold order, no release below limit, monotonic assertion behavior in debug builds, move semantics with pending waiters, and metric handle value preservation through `initMetric()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Notified.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/PImpl.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/PImpl.h

## Purpose
`PImpl.h` defines a minimal unique-ownership pimpl wrapper around `std::unique_ptr<T>`. It hides construction behind a static `create()` factory so callers can keep implementation storage opaque while still using pointer-like access.

## Important APIs, Types, And Functions
- `PImpl<T>` stores `std::unique_ptr<T> impl`.
- Private `ConstructorTag` disambiguates factory construction from the public default constructor.
- `create(args...)` forwards arguments to `std::make_unique<T>`.
- Dereference, arrow, and `get()` methods expose mutable and const `T` access.

## Control Flow And State
The default constructor leaves `impl` null. `create()` returns a fully constructed wrapper. Accessors do not guard against null, so callers must either use `create()` or explicitly handle default-initialized state before dereferencing.

## Persistence And External State
No persistence or serialization exists. Lifetime is RAII through `unique_ptr`; destruction of `PImpl` destroys the implementation.

## Dependencies And Integration Points
The only dependency is `<memory>`. It is suitable for headers that want to avoid including an implementation class definition while still keeping value-like ownership semantics.

## Risks And Edge Cases
The wrapper is move-only because `unique_ptr` is move-only. Null default state can cause crashes on `operator*` or `operator->`. There is no reset, release, swap, or explicit bool API, so consumers may need to use `get()` for presence checks.

## Test Signals
Compile tests should verify move-only behavior, factory forwarding, const and mutable accessors, destruction of owned objects, and expected failure or guarded behavior around default construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/PImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ProcessInterface.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ProcessInterface.h

## Purpose
`ProcessInterface.h` declares RPC message types for retrieving process-level interfaces and actor lineage profiling samples. It gives other components a typed way to ask a process for its actor lineage data over FoundationDB RPC streams.

## Important APIs, Types, And Functions
- `ProcessInterface` contains request streams for `GetProcessInterfaceRequest` and `ActorLineageRequest`. Its serializer currently serializes `actorLineage`.
- `GetProcessInterfaceRequest` carries a `ReplyPromise<ProcessInterface>`.
- `SerializedSample` transports a timestamp and a `std::unordered_map<WaitState, std::string>` of serialized profiling data.
- `ActorLineageReply` wraps a vector of samples.
- `ActorLineageRequest` carries a wait-state range, time range, and reply promise.

## Control Flow And State
Callers send `GetProcessInterfaceRequest` to discover a process interface, then send `ActorLineageRequest` through `actorLineage`. The request filters samples by wait-state start/end and time start/end; the reply returns a batch of serialized samples.

## Persistence And External State
All structures are transient RPC payloads. `constexpr FileIdentifier` values make them part of FDB's typed serialization protocol and must remain compatible across deployments.

## Dependencies And Integration Points
The header depends on actor annotation types, FDB types, fdbrpc streams/promises, and well-known endpoints. It integrates with actor lineage profiling, process discovery, and any special key or status surface that exposes process stack/lineage data.

## Risks And Edge Cases
Changing serialization fields or file identifiers can break wire compatibility. `ProcessInterface::serialize()` only serializes `actorLineage`, so adding streams requires a deliberate protocol update. Time fields use `time_t`, which can vary by platform width. Large sample vectors or maps may create heavy replies.

## Test Signals
Tests should cover serialization round trips across protocol versions, request/reply routing, lineage filtering by time and wait-state, behavior with no samples, and compatibility when process interfaces are fetched from mixed-version processes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ProcessInterface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RYWIterator.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RYWIterator.h

## Purpose
`RYWIterator.h` declares the iterator that merges `SnapshotCache` contents with `WriteMap` mutations for read-your-writes transactions. It also includes deterministic random helpers used by snapshot cache and RYW correctness tests.

## Important APIs, Types, And Functions
- `RYWIterator` tracks a snapshot-cache iterator, write-map iterator, comparison state for begin/end keys, and an unreadable bypass flag.
- Segment APIs report whether the current span is `UNKNOWN_RANGE`, `EMPTY_RANGE`, `KV`, unreadable, or dependent.
- `beginKey()`, `endKey()`, `kv(arena)`, increment/decrement, `skip`, `skipContiguous`, and `skipContiguousBack` provide range traversal and positioning.
- `extractWriteMapIterator()` exposes the underlying write iterator for performance-sensitive callers, with invalidation caveats.
- `RandomTestImpl` generates deterministic random keys, values, versionstamp keys/values, key ranges, and selectors.
- `testESR()` and `testSnapshotCache()` are declared correctness hooks.

## Control Flow And State
The iterator uses `begin_key_cmp` and `end_key_cmp` to decide how snapshot and write segments overlap. Traversal steps through merged segments and updates comparison state. The unreadable bypass switch lets special code continue through sections made unreadable by versionstamp operations.

## Persistence And External State
The iterator is in-memory and transaction-local. It observes `SnapshotCache` and `WriteMap`, both arena-backed. Random helpers use `deterministicRandom()` so simulation workloads can reproduce failures.

## Dependencies And Integration Points
It includes `SnapshotCache.h` and `WriteMap.h`, and is a private collaborator of `ReadYourWritesTransaction` implementation. The generated segments feed RYW range reads, conflict map updates, and read-ahead/caching behavior.

## Risks And Edge Cases
Iterator invalidation is explicit: modifying the extracted `WriteMap::iterator` invalidates the `RYWIterator` until the next `skip()`. Segment boundaries involving zero bytes and versionstamp unreadable regions are subtle. Random versionstamp helpers intentionally generate edge positions and should not be used as production data builders.

## Test Signals
Tests should cover merging cached reads with writes, forward/backward iteration, contiguous skip behavior, unknown/empty/KV segment classification, dependent/unreadable segments, versionstamp bypass, random key/range/selector generation, and deterministic reproduction in simulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RYWIterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RandomKeyValueUtils.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RandomKeyValueUtils.h

## Purpose
`RandomKeyValueUtils.h` defines reusable deterministic random generators for keys, values, key sets, tuple-like key composition, and mutation inputs. These helpers support simulation and workload tests that need compact string specifications for reproducible key/value distributions.

## Important APIs, Types, And Functions
- `IGenerator<T>` and `IKeyGenerator` define the common generator interface.
- `RandomIntGenerator` parses numeric or alphabetic ranges with optional skew marker `^`, and supports uniform, small-skewed, and large-skewed generation.
- `RandomStringGenerator` parses `sizeRange[/byteRange]` and generates arena-backed byte strings.
- `RandomValueGenerator` precomputes a large noise block and returns random substrings for faster value generation.
- `RandomStringSetGeneratorBase` builds a sorted unique key set from another key generator, supports random, sequential-distance, and range selection.
- `RandomStringSetGenerator<StringGenT>`, `RandomKeySetGenerator`, `RandomKeyTupleGenerator`, `RandomKeyTupleSetGenerator`, and `RandomKeyGenerator` compose keys from one or more generators.
- `RandomMutationGenerator` groups tuple keys and values for mutation workloads.

## Control Flow And State
String constructors parse generator specs using `StringRef::eat()`. Set generators repeatedly draw unique keys until the requested cardinality is met, then index into that stable vector. Tuple generators draw each part, allocate a combined key, and concatenate the latest output of each part. Value generation trades independence for speed by slicing a pregenerated noise buffer.

## Persistence And External State
No persistent state is written. Generated `Key`, `Value`, and `KeyRange` objects use arenas and `Standalone<StringRef>` lifetimes. Randomness comes from `deterministicRandom()`, making simulation results replayable.

## Dependencies And Integration Points
The header depends on Flow arenas/errors/randomness, FDB key/value types, STL containers, and formatting utilities. It is intended for correctness, performance, and workload code rather than production request handling.

## Risks And Edge Cases
`RandomStringGenerator` defaults to `"0:255"` for byte ranges even though `RandomIntGenerator` expects `..` ranges elsewhere; this relies on local parsing semantics and should be checked before changing specs. Unique set generation asserts if cardinality is too low after bounded retries. `getMaxKeyLen()` returns `size.max - 1`, so zero-length specs can produce surprising maximums. Arena ownership matters for returned keys and ranges.

## Test Signals
Tests should cover range parsing, alphabetic endpoints, skew direction, value/string length bounds, byte bounds, uniqueness failure cases, stable sorted key sets, sequential `next(distance, wrap)` behavior, range generation, tuple concatenation, deterministic replay, and maximum key/value length reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RandomKeyValueUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RangeLock.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RangeLock.h

## Purpose
`RangeLock.h` declares serializable metadata for range locks, currently focused on an exclusive read lock type that rejects commits to locked ranges. It models owners, individual locks, and persisted lock sets per range.

## Important APIs, Types, And Functions
- `RangeLockType` currently has `Invalid` and `ExclusiveReadLock`.
- `RangeLockOwner` stores owner unique ID, description, log ID, and creation time; construction validates non-empty owner and description.
- `RangeLockState` stores lock type, owner ID, range, and reserved physical lock ID; it validates, stringifies, serializes, and derives a unique string from owner/type/range.
- `RangeLockStateSet` stores a map of unique lock string to state, validates all locks, inserts/removes locks, tests lock type presence, and serializes the set.

## Control Flow And State
Owner construction assigns a random log ID and `now()` timestamp. `RangeLockStateSet::insertIfNotExist()` rejects adding a different exclusive read lock if any lock already exists, enforcing one exclusive lock owner/type/range combination at a time. Removal erases by derived unique string.

## Persistence And External State
The structs have `FileIdentifier` values and `serialize()` methods, making them suitable for network or system-key persistence. The comments call out `RangeLockStateSet` as persisted state on a range.

## Dependencies And Integration Points
The header depends on Flow errors/random IDs/time, FDB key ranges, and fdbrpc serialization. It integrates with range lock management code and transaction commit validation that checks locked ranges.

## Risks And Edge Cases
`RangeLockState::getLockUniqueString()` uses textual range formatting and has a TODO to use `lockId`; formatting changes could affect identity if persisted keys are derived from it elsewhere. `RangeLockStateSet::insertIfNotExist()` only special-cases exclusive read locks, so future lock types need explicit compatibility rules. Owner equality ignores description/log/time and compares only unique ID.

## Test Signals
Tests should cover invalid owner/state rejection, serialization round trips, exclusive lock insertion conflicts, idempotent insertion of the same lock, removal by state, `isLockedFor`, equality independent of map iteration, string output, and compatibility when new lock types are added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RangeLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ReadYourWrites.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ReadYourWrites.h

## Purpose
`ReadYourWrites.h` declares the RYW transaction wrapper that presents FoundationDB's normal transaction API while merging local writes with snapshot reads. It owns the snapshot cache, write map, conflict tracking, special key space writes, debug retry logging, timeout/retry state, and the underlying native `Transaction`.

## Important APIs, Types, And Functions
- `ReadYourWritesTransactionOptions` tracks RYW disablement, read-ahead, system key access, conflict disabling for the next write, retry logging, used-during-commit protection, special key space relaxation/configuration, timeouts, max retries, snapshot RYW, and unreadable bypass.
- `TransactionDebugInfo` stores transaction name and last retry log timestamp.
- `ReadYourWritesTransaction` exposes read APIs, mapped range reads, storage size/split helpers, conflict range APIs, writes/clears/atomic ops, watches, commit, versionstamp, options, retry handling, reset/cancel, debug traces/messages, and conflict range special-key readers.
- Private state includes `Arena`, native `Transaction`, `SnapshotCache`, `WriteMap`, read conflict map, watch map, reset promise, pending read aggregate, retries, approximate size, timeout actor, versionstamp state, native conflict range snapshots, special key write map, persistent option vectors, and sensitive option vectors.

## Control Flow And State
When RYW is enabled, reads use the native transaction with snapshot semantics and merge results through `SnapshotCache`, `WriteMap`, and `RYWIterator`. Writes update the write map and conflict maps before being pushed to the native transaction at commit. `pendingReads()` gates resets and commit-time used-during-commit protection. `onError()` resets state and reapplies persistent options. `getAndResetWriteConflictDisabled()` gives one-shot control for conflict range suppression.

## Persistence And External State
The wrapper itself is in-memory, but it accumulates mutations and conflict ranges that are eventually written by the native `Transaction`. Special key space writes are staged in `specialKeySpaceWriteMap` and committed via special key implementations. Persistent and sensitive transaction options survive retries. Debug messages/traces and JSON validation of special key errors are simulation-observable.

## Dependencies And Integration Points
It depends on `NativeAPI.actor.h`, status JSON parsing, key range maps, `RYWIterator`, `FastRef`, `WipedString`, `SnapshotCache`, and `WriteMap`. It is the transaction type used by bindings and internal helpers that need read-your-writes semantics. It also integrates with special key space, watches, versionstamps, conflict range introspection, tag throttling cost metrics, and status JSON fetch.

## Risks And Edge Cases
Returned values can hold the transaction arena alive, so long-lived values retain transaction memory. RYW-disabled mode delegates more behavior to `Transaction` and uses native conflict range snapshots after commit. Versionstamp operations can mark sections unreadable unless bypassed. Commit-time use protection, pending reads, and reset promises are concurrency-sensitive. Special key errors are expected to be valid JSON in simulation.

## Test Signals
Tests should cover read-after-set/clear/atomic behavior, range merge ordering, snapshot reads, conflict maps, watches, commit retry, persistent option replay, sensitive option handling, timeout/max retry behavior, special key writes and errors, versionstamp unreadable ranges, memory arena retention, debug trace logging, and RYW-disabled parity with native transaction behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ReadYourWrites.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunRYWTransaction.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunRYWTransaction.h

## Purpose
`RunRYWTransaction.h` defines coroutine helpers that run a caller-supplied function inside a `ReadYourWritesTransaction` retry loop. It is the convenience layer for idempotent transactional code that wants automatic commit and retry handling.

## Important APIs, Types, And Functions
- `RunRYWTransactionResult<Function>` infers the future value returned by a callback taking `Reference<ReadYourWritesTransaction>`.
- `runRYWTransaction()` retries forever on errors handled by `tr->onError()`.
- `runRYWTransactionDebug()` additionally logs the callback name and committed version on success.
- `runRYWTransactionVoid()` handles callbacks returning `Future<Void>`.
- `runRYWTransactionFailIfLocked()` propagates `database_locked` instead of retrying it.
- `runRYWTransactionNoRetry()` runs callback and commit exactly once.

## Control Flow And State
Each helper creates one `Reference<ReadYourWritesTransaction>` before the loop. The loop awaits callback result, commits, returns result, catches `Error`, and awaits `onError()` to reset/retry. The no-retry variant omits catch/onError. The fail-if-locked variant checks the error code before retry handling.

## Persistence And External State
Persistence occurs through the transaction commit itself. Debug mode emits `TraceEvent("DebugRunRYWTransaction")` with function name and commit version.

## Dependencies And Integration Points
It depends on Flow coroutines, generic `RunTransaction.h`, and `ReadYourWrites.h`. It integrates with all APIs expecting automatic RYW transaction retries and with callback code that must be idempotent under retry.

## Risks And Edge Cases
The callback must be idempotent because it can run multiple times. Reusing the same transaction reference across retries relies on `onError()` to reset all transaction-local state correctly. Functions returning references into transaction arenas should not outlive the transaction unexpectedly. `runRYWTransactionDebug()` requires a meaningful function name from the caller.

## Test Signals
Tests should cover successful return values, void callbacks, retry after retriable errors, propagation of non-retriable or locked errors where intended, no-retry behavior, callback idempotency assumptions, debug trace emission, and option/state reset across retries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunRYWTransaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunTransaction.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunTransaction.h

## Purpose
`RunTransaction.h` provides generic coroutine retry helpers for database-like objects that create transaction references. It also defines a wrapper for system-key transactions that automatically applies system, priority, and lock-aware options.

## Important APIs, Types, And Functions
- `transaction_option_setter` and `can_set_transaction_options` detect DB wrappers that should set options before each attempt.
- `RunTransactionResult<Function, DB>` infers callback result type.
- `runTransaction()` and `runTransactionVoid()` create a transaction, run callback, commit, return, and retry through `onError()`.
- `SystemTransactionGenerator<DB>` wraps another DB reference, creates its transactions, and sets read/write system key, immediate priority, and lock-aware options.
- `SystemDB()` and `SystemDBWriteLockedNow()` are convenience factories.

## Control Flow And State
On every retry loop, the helper calls `db->setOptions(tr)` if the DB type participates in `transaction_option_setter`. It awaits callback and commit through `safeThreadFutureToFuture`, catches Flow `Error`, and awaits `tr->onError(err)` before retrying.

## Persistence And External State
The helper itself is stateless beyond the transaction reference and wrapper booleans. Persistent effects are the user's mutations after a successful commit. The system wrapper can access and modify system keys depending on `write`.

## Dependencies And Integration Points
It depends on Flow futures/coroutines and generated transaction option enums. It integrates with thread-safe transaction implementations because commits and `onError()` are converted through `safeThreadFutureToFuture`.

## Risks And Edge Cases
Callbacks must be idempotent. Options are set before each attempt, so non-persistent options in the transaction implementation must tolerate repeated setting. The result type depends on `getValue()`, so callback return types must match FoundationDB future conventions. System transactions can bypass normal key protections if constructed with write access.

## Test Signals
Tests should cover generic DB wrappers, option setter detection for raw and `Reference<T>` types, retry semantics, void and non-void callbacks, thread-future conversion, system-key read/write options, immediate priority, lock-aware options, and `SystemDBWriteLockedNow()` all-true behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunTransaction.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3BlobStore.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3BlobStore.h

## Purpose
`S3BlobStore.h` declares the S3-compatible implementation of `IBlobStoreEndpoint`. It covers endpoint parsing, credential loading, request signing, retry hooks for token errors, object and bucket operations, listing, multipart upload, object tags, and URL construction.

## Important APIs, Types, And Functions
- `S3BlobStoreEndpoint` inherits `IBlobStoreEndpoint` and `ReferenceCounted`.
- `Credentials` stores key, secret, and security token.
- The constructor accepts host, service, region, proxy settings, optional credentials, blob knobs, and extra HTTP headers.
- `guessRegionFromDomain()` infers cloud region from known S3/COS style hostnames.
- `fromString()` downcasts the generic `IBlobStoreEndpoint::fromString()` result to S3.
- Credential APIs include `updateSecret()`, `extractCredentialFields()`, `credentialFileKey()`, and `lookupSecretOnEachRequest()`.
- Request APIs include `setRequestHeaders()`, `normalizeResourceForRequest()`, `setAuthHeaders()`, `setV4AuthHeaders()`, failure simulation/processing, and `preRetryCheck()`.
- Object APIs include list buckets/objects, existence/size/read/delete/create bucket, read/write entire files, multipart begin/upload/finish/abort, and tag put/get.

## Control Flow And State
Requests normalize resources, apply headers, sign with either legacy HMAC-SHA1 or AWS V4 style headers, then use inherited blob store request machinery. Token or credential failures can set `retryExtended` and run `preRetryCheck()` before retry. Multipart uploads begin with an upload ID, upload numbered parts with content hashes, then finish with a part set and optional total size.

## Persistence And External State
State includes optional credentials, lookup flags, simulated token error flag, endpoint/proxy/knob state inherited from `IBlobStoreEndpoint`, and extra headers. External persistence is remote S3-compatible bucket/object data and credential files or secret providers.

## Dependencies And Integration Points
It depends on Flow packet queues, `IBlobStore`, and HTTP RPC types. It is used by backup/restore, blob storage, bulk dump/load, and command-line S3 client helpers. The URL format is shared with `S3Client.h`.

## Risks And Edge Cases
Signature construction is security-critical and sensitive to resource normalization, date formats, headers, region, and temporary security tokens. Credential refresh on retry must avoid infinite retry loops and stale secrets. `fromString()` can return null if a non-S3 endpoint parses. Listing with recursive delimiters can fan out many requests. Multipart completion must preserve part order and eTags.

## Test Signals
Tests should cover URL parsing, region guessing, credential extraction/refresh, V2/V4 auth header golden cases, proxy handling, resource normalization, simulated token failures, retry extension, bucket/object existence, ranged reads, multipart upload lifecycle, tag operations, recursive listing, and S3-compatible provider variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3BlobStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3Client.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3Client.h

## Purpose
`S3Client.h` declares high-level file and directory copy utilities built on `S3BlobStoreEndpoint`. It is the user-facing helper layer for copying local files/directories to and from S3-compatible blobstore URLs, listing resources, deleting resources, and computing file checksums.

## Important APIs, Types, And Functions
- `s3VerboseEventSev()` and `s3PerfEventSev()` choose trace severities based on simulation status and `S3CLIENT_VERBOSE_LEVEL`.
- `BLOBSTORE_PREFIX` is the expected URL prefix.
- `copyUpDirectory()`, `copyUpFile()`, `copyDownFile()`, and `copyDownDirectory()` move data between local filesystem and S3 resources.
- `copyUpBulkDumpFileSet()` uploads bulk dump file sets after clearing destination content.
- `deleteResource()` recursively deletes a blobstore file or directory.
- `calculateFileChecksum()` returns an xxhash64 checksum string for an async file.
- `listFiles()` lists S3 resources to a bounded depth.
- `getEndpoint()` parses URL resource and parameters and returns an S3 endpoint.

## Control Flow And State
Operations parse the blobstore URL, construct or obtain an endpoint, then perform object operations, often using multipart transfer for large files. Directory operations recurse, preserving path/resource mapping. Upload/download workflows include checksum calculation and verification, cleanup on failure, and parallel part transfer per the implementation.

## Persistence And External State
The header does not define stateful classes. External effects are local filesystem reads/writes and remote S3 object mutations. Checksum calculation reads local async file content.

## Dependencies And Integration Points
It depends on `S3BlobStore.h`, `BulkDumping.h`, Flow errors/network globals, and client knobs. It integrates backup, restore, bulk load/dump, and operational tools with S3-compatible storage.

## Risks And Edge Cases
Trace severity helpers dereference `g_network`, so callers need network setup. URL parsing must retain bucket/resource semantics consistently with `S3BlobStoreEndpoint`. Recursive delete/list/copy can be expensive or dangerous if resource prefixes are wrong. Checksum mismatches, partial local files, and failed multipart cleanup need careful handling in implementation.

## Test Signals
Tests should cover endpoint parsing, single-file upload/download, large multipart transfers, checksum mismatch behavior, recursive directory upload/download/delete, max-depth listing, bulk dump file set upload, simulated network severity levels, and cleanup after failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3Client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Schemas.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Schemas.h

## Purpose
`Schemas.h` declares symbolic keys for JSON schema documents used by status and management API surfaces. It centralizes schema key references so producers and validators can agree on schema identities.

## Important APIs, Types, And Functions
- `JSONSchemas` contains static `KeyRef` declarations for status, cluster configuration, latency band configuration, data distribution stats, log health, storage health, aggregate health, management API error, and fault tolerance status schemas.

## Control Flow And State
There is no runtime control flow in the header. Definitions in the corresponding implementation provide the actual key values.

## Persistence And External State
The static `KeyRef` values likely identify schema text or schema records elsewhere in the client/status system. This header itself has no mutable state.

## Dependencies And Integration Points
It depends on Flow and FDB key types. It integrates with JSON status generation, management API errors, and schema validation or publication code.

## Risks And Edge Cases
Because only declarations are present, mismatches between declarations and implementation definitions will be link-time or runtime integration problems. Schema key changes can break clients expecting stable schema names.

## Test Signals
Tests should verify that all declared schema refs are defined, non-empty where expected, stable across releases unless intentionally changed, and used by status/management code consistently.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Schemas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SimpleIni.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SimpleIni.h

## Purpose
`SimpleIni.h` is a vendored single-header INI parser/writer, version 4.16, used for cross-platform configuration file loading and saving. It supports comments, sections, key/value pairs, optional duplicate keys, optional multiline values, load-order-preserving save, UTF-8/MBCS/wide-character conversion, file/string/stream I/O, and case-sensitive or case-insensitive lookup.

## Important APIs, Types, And Functions
- `SI_Error` reports success, update/insert outcomes, generic failure, allocation failure, and file errors.
- `CSimpleIniTempl<SI_CHAR, SI_STRLESS, SI_CONVERTER>` is the main template.
- Nested `Entry` stores item pointer, comment pointer, and load order, with `KeyOrder` and `LoadOrder` comparators.
- `TKeyVal`, `TSection`, and `TNamesDepend` represent section/key/value maps and pointer-returning name lists.
- `OutputWriter`, `FileWriter`, `StringWriter`, and optional `StreamWriter` abstract saving.
- `Converter` wraps the selected conversion backend and grows scratch space for output conversion.
- Public settings include `SetUnicode`, `SetMultiKey`, `SetMultiLine`, and `SetSpaces`.
- Loading APIs include `LoadFile()` for narrow/wide filenames, `FILE*`, optional `istream`, string, and raw memory.
- Saving APIs include `SaveFile()`, `Save(OutputWriter&)`, optional `ostream`, and string append.
- Query/mutation APIs include `GetAllSections`, `GetAllKeys`, `GetAllValues`, `GetSectionSize`, `GetSection`, `GetValue`, typed long/double/bool getters and setters, `SetValue`, and `Delete`.
- Conversion helpers include generic case comparators, `SI_ConvertA`, and wide conversion backends for generic ConvertUTF, ICU, and Win32.
- Typedefs provide `CSimpleIniA`, `CSimpleIniCaseA`, `CSimpleIniW`, `CSimpleIniCaseW`, and `CSimpleIni`.

## Control Flow And State
`LoadFile()` reads the whole file into a byte buffer and calls `LoadData()`. `LoadData()` strips UTF-8 BOM when needed, converts storage encoding to `SI_CHAR`, then mutates the converted buffer in place by inserting NUL terminators while `FindFileComment()` and `FindEntry()` parse comments, sections, keys, values, and multiline blocks. `AddEntry()` inserts or updates maps, copies strings when data is appended after an existing load, tracks load order, and handles multikey replacement. `Save()` sorts sections/keys by load order, writes comments, sections, key/value lines, and emits multiline data with `<<<END_OF_TEXT`. `Delete()` removes keys or sections and frees copied strings.

## Persistence And External State
The parser owns a mutable data block `m_pData`, copied strings in `m_strings`, file comment pointer, parsed map, encoding/multikey/multiline/spacing flags, and load-order counter. Saved output persists to files, streams, or strings. Returned pointers from query methods depend on `CSimpleIniTempl` lifetime and are invalidated by reset or deletion.

## Dependencies And Integration Points
The header depends on STL containers, C stdio/string functions, optional iostreams, platform conversion APIs, ICU if enabled, and FoundationDB's `ConvertUTF.h` for generic wide conversion. It is a third-party component embedded in fdbclient for INI-style configuration needs.

## Risks And Edge Cases
The parser mutates the load buffer in place and returns dependent pointers, so ownership/lifetime misuse is the largest risk. Duplicate-key behavior changes depending on `m_bAllowMultiKey`. Comments can only be changed by deleting and recreating entries. Multiline parsing requires exact tag placement and normalizes newlines. Case-insensitive comparison is ASCII-generic except for Win32 MBCS mode. Some code uses fixed-size buffers for numeric conversion and wide filename conversion. `DeleteString()` compares pointers against `m_pData`, which assumes all dependent strings belong either to the main block or `m_strings`.

## Test Signals
Tests should cover narrow and UTF-8 files with BOM, comments before file/section/key, key/value whitespace trimming, invalid lines, empty sections, duplicate keys in both modes, force replacement preserving order/comment, multiline load/save, save order, typed numeric/bool getters and setters, deletion and empty-section pruning, string/file/stream I/O, case-sensitive and insensitive typedefs, reset memory ownership, and conversion backends on supported platforms.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SimpleIni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SnapshotCache.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SnapshotCache.h

## Purpose
`SnapshotCache.h` declares the read snapshot cache used by RYW transactions. It records known key ranges and values from snapshot reads, exposes an iterator over known KVs, known-empty spans, and unknown spans, and supports promises for in-flight cache fills.

## Important APIs, Types, And Functions
- `ExtStringRef` represents a `StringRef` plus virtual trailing zero bytes, supports arena conversion, comparison, prefix checks, and `keyAfter()`.
- Comparison operators and `Traceable<ExtStringRef>` support ordering and trace output.
- `SnapshotCache::Entry` stores known `[beginKey, endKey)` plus sorted `KeyValueRef` values; absent keys inside the range are implicitly empty.
- `SnapshotCache::iterator` traverses `UNKNOWN_RANGE`, `EMPTY_RANGE`, and `KV` segments and supports skip/next/previous/contiguous skipping.
- `SnapshotCache` stores an arena pointer and an `IndexedSet<Entry>`, initialized with degenerate all-keys boundary entries.
- `insert(key, value)` records a known present or absent single key if still unknown.
- `insert(range, values)` records a known range, trimming around already-known subranges.
- `promise(segment, keys, onReady)` declares an in-flight read that should later populate the cache.

## Control Flow And State
The cache starts with sentinel entries at `allKeys.begin` and `allKeys.end`. Iterators compute segment type from an `Entry` plus offset. `skip()` finds the entry containing or just before a key, then classifies whether the key is known, empty, or unknown. Range insertion finds begin/end iterators, trims values against already-known boundaries, erases unknown entry spans, and inserts a new known entry.

## Persistence And External State
All state is transaction-local and arena-backed. The cache does not persist to disk. It depends on read results from native transactions and feeds RYW range merge logic.

## Dependencies And Integration Points
It depends on FDB types, native API constants such as `allKeys`/`afterAllKeys`, system data, and Flow `IndexedSet`. `ReadYourWritesTransaction` is a friend and combines it with `WriteMap` through `RYWIterator`.

## Risks And Edge Cases
`ExtStringRef` comparison with virtual trailing zeroes is subtle and critical for key-after semantics. Iterator offsets encode segment type; off-by-one errors can misclassify empty ranges as KVs or unknown ranges. Insert trimming must preserve cache invariants and sorted values. `promise()` must not invalidate the provided segment. Arena lifetimes govern returned refs.

## Test Signals
Tests should cover `ExtStringRef` comparison/prefix/keyAfter, empty cache behavior, single-key present/absent insertion, range insertion with existing known boundaries, iterator skip and forward/backward traversal, contiguous skip helpers, all-keys sentinels, promise readiness interactions, and cache dumping/tracing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SnapshotCache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SpecialKeySpace.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SpecialKeySpace.h

## Purpose
`SpecialKeySpace.h` declares the virtual keyspace used to expose management APIs, status-like reads, transaction diagnostics, tracing options, actor lineage, worker interfaces, data distribution metrics, and other operational controls through key reads and writes. It routes special key ranges to read-only, read-write, or async implementations and commits staged writes through the owning RYW transaction.

## Important APIs, Types, And Functions
- `SpecialKeyRangeReadImpl` is the base read interface for a registered key range.
- `SpecialKeyRangeRWImpl` adds `set`, `clear`, `commit`, and optional encode/decode from special keys to real keys.
- `SpecialKeyRangeAsyncImpl` adds cached async range reads through `getRangeAsyncActor()`.
- `ManagementAPIError::toJsonString()` builds standardized JSON error payloads.
- `SpecialKeySpace` owns maps from ranges to implementations and modules, exposes get/getRange/set/clear/commit/register/decode APIs, module and command range lookup helpers, option sets, and internal actors for aggregation and RYW validation.
- Implementation classes cover tests, conflicting keys, read/write conflict ranges, DD stats, management command options, locality/server exclusions and failures, exclusion progress, process class and source, database lock, consistency check, global config, tracing options, coordinators, advance version, version epoch, deprecated client profiling, actor lineage, actor profiler config, maintenance, data distribution, worker interfaces, and fault tolerance metrics.
- `validateSpecialSubrangeRead()` verifies subrange reads against stable special-key results.

## Control Flow And State
Reads locate the registered implementation for the requested key or range, call its `getRange()`, and aggregate across modules for multi-range reads. Async implementations cache a whole implementation range in a `KeyRangeMap<Optional<RangeResult>>` and slice it for subranges, preserving consistency during one getRange lifetime. Writes are staged into `ReadYourWritesTransaction::specialKeySpaceWriteMap` by default, then each RW implementation validates and commits its side effects.

## Persistence And External State
The `SpecialKeySpace` object stores implementation maps, module boundary maps, command range maps, option sets, and its configured key range. Persistent side effects are implementation-specific: changing system keys, coordinators, global configuration, tracing options, locks, exclusions, maintenance, data distribution, or management commands. Error messages are JSON strings.

## Dependencies And Integration Points
It depends on Flow, arenas, FDB types, key range maps, and `ReadYourWritesTransaction`. It integrates with status JSON, management API commands, transaction conflict diagnostics, actor lineage profiler, process interfaces, cluster configuration, data distribution, and system key mutation logic.

## Risks And Edge Cases
Special key semantics must preserve transactional consistency while some ranges call async RPCs. Range registration and module boundaries must not overlap incorrectly. Relaxed/change-configuration options on RYW transactions gate writes. Management error JSON must remain machine-readable. Async cache reads whole ranges for simplicity, which can be expensive. Encode/decode defaults assert, so RW implementations must override when translating to real keys.

## Test Signals
Tests should cover registration overlap, module boundary initialization, single-key and range reads, reverse/limit behavior, async range caching and slicing, write staging and commit per implementation, clear/set encode-decode, special-key error JSON validation, management command option ranges, transaction conflict key reads, and validation of stable subrange reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SpecialKeySpace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StackLineage.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StackLineage.h

## Purpose
`StackLineage.h` declares a collector for actor lineage stack traces. It bridges actor lineage profiler data into a vector of string views suitable for profiling consumers.

## Important APIs, Types, And Functions
- `getActorStackTrace()` is an external function returning Flow `StringRef` stack frames.
- `StackLineageCollector` inherits `IALPCollector<StackLineage>`.
- `collect(ActorLineage*)` asks the lineage for stack data keyed by `StackLineage::actorName`, converts each `StringRef` to `std::string_view`, and returns it in `std::any`.

## Control Flow And State
The collector is stateless. Each `collect()` call obtains a vector from the provided lineage and builds a vector of views over the returned string data.

## Persistence And External State
No persistent state exists. Returned string views depend on the lifetime of the underlying lineage/string storage.

## Dependencies And Integration Points
It depends on Flow and `ActorLineageProfiler.h`. It integrates with process/actor lineage reporting, including special key or RPC surfaces that expose profiling samples.

## Risks And Edge Cases
The conversion to `std::string_view` is non-owning; consumers must not retain views beyond the backing string lifetime. The collector assumes the provided `ActorLineage*` is valid. Empty or missing stack data returns an empty vector inside `std::any`.

## Test Signals
Tests should cover collecting from lineages with multiple frames, empty stacks, lifetime expectations for returned views, and integration with actor lineage serialization/reporting paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StackLineage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Status.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Status.h

## Purpose
`Status.h` defines JSON-backed status container types, serialization helpers, status message names, and convenience JSON lookup utilities used by FoundationDB status reporting and clients.

## Important APIs, Types, And Functions
- `readJSONStrictly()` parses exactly one JSON value from a string and rejects trailing non-whitespace.
- `StatusObject`, `StatusArray`, and `StatusValue` wrap `json_spirit` object/array/value types.
- `load()` and `save()` serialize `StatusObject` as a length-prefixed JSON string through FDB serializers.
- `MessageType` enumerates known status message categories.
- `messageTypeToName` maps message enum values to stable JSON names.
- `makeMessage()` builds a status message object with `name` and `description`.
- `StatusObjectReader` aliases `JSONDoc`.
- `JSONDoc::get<JSONDoc>()` specialization extracts a sub-object as a JSONDoc.
- `findMessagesByName()` scans `messages` array entries for selected names.

## Control Flow And State
Serialization writes JSON text length then bytes; deserialization reads length, bytes, parses JSON, and stores the object. `findMessagesByName()` first verifies `messages` exists and is an array, then iterates defensively, ignoring malformed entries that throw during object/name extraction.

## Persistence And External State
Status objects are transient but serialized over RPC or stored in client-facing responses as JSON. Message names are externally visible and should remain stable.

## Dependencies And Integration Points
It depends on `JSONDoc.h` and `json_spirit`. It integrates with `StatusClient`, management/status special keys, fault tolerance status, and any code generating health messages.

## Risks And Edge Cases
`load()` assumes parsed value is an object; malformed JSON or non-object JSON can throw/assert. Length-prefixed serialization uses `int32_t`, so huge status payloads are not supported. `messageTypeToName.at()` will throw for unmapped enum values. `findMessagesByName()` intentionally swallows malformed message entries, which can hide schema violations.

## Test Signals
Tests should cover strict JSON parsing, serialization round trips, malformed JSON, non-object inputs, every `MessageType` mapping, `makeMessage()` shape, JSONDoc sub-object extraction, message lookup success/failure, malformed message array entries, and compatibility of serialized status payloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StatusClient.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StatusClient.h

## Purpose
`StatusClient.h` declares the client entry point for fetching FoundationDB status JSON. It provides a small facade over the actor implementation that queries full or selected status fields from a database.

## Important APIs, Types, And Functions
- `StatusClient::StatusLevel` enumerates minimal, normal, detailed, and JSON status levels.
- `StatusClient::statusFetcher(Database db, std::string statusField = "")` returns `AsyncResult<StatusObject>`.
- The documented `statusField` currently supports empty/full status or `"fault_tolerance"` for a focused subset.

## Control Flow And State
The header only declares the static method. The implementation actor fetches status data from the database and returns a `StatusObject`.

## Persistence And External State
No local state is declared. The result is live cluster status JSON; requests may read from system/status APIs and depend on cluster availability.

## Dependencies And Integration Points
It depends on Flow, `Status.h`, and `DatabaseContext.h`. It integrates with CLI status commands, management APIs, monitoring tools, and any client code that needs cluster status.

## Risks And Edge Cases
Only selected field filtering is documented; arbitrary fields are not supported. Status fetches can be incomplete, timeout, or fail if the cluster/controller is unavailable. Callers need to handle `AsyncResult` errors and incomplete status messages.

## Test Signals
Tests should cover full status fetch, fault-tolerance subset fetch, unsupported field behavior, controller unavailable paths, timeout/incomplete messages, JSON shape validation, and status level use by callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StatusClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageCheckpoint.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageCheckpoint.h

## Purpose
`StorageCheckpoint.h` declares metadata structures for storage checkpoints and data moves. These structs describe checkpoint format, state, covered ranges, source servers, serialized engine-specific checkpoint data, application action IDs, and data movement phases.

## Important APIs, Types, And Functions
- Constants `checkpointBytesSampleFileName` and `emptySstFilePath` name metadata artifacts.
- `CheckpointFormat` covers invalid format, RocksDB column-family export checkpoints, RocksDB filesystem checkpoints, and key-value checkpoints.
- `CheckpointMetaData` stores version, ranges, format, source server IDs, checkpoint ID, state, optional bytes sample file, serialized checkpoint payload, optional action ID, and directory.
- `CheckpointMetaData` helpers get/set state and format, set/get serialized checkpoint data, test range/key coverage, compare by checkpoint ID, stringify, and serialize.
- `std::hash<CheckpointMetaData>` hashes by checkpoint ID.
- `DataMoveMetaData` stores data move ID, version, ranges, priority, source/destination server sets, checkpoint IDs, phase, mode, and optional bulk load task state.
- `DataMoveMetaData` helpers get/set phase, stringify, and serialize.

## Control Flow And State
Checkpoint metadata progresses through pending, complete, deleting, and fail states. Data moves progress through prepare, running, completing, and deleting phases. Coverage helpers iterate stored ranges to answer whether a range or key is represented. Serialization packs every field needed to reconstruct metadata over the wire or from system storage.

## Persistence And External State
These structs are explicitly metadata for persistent storage/data movement workflows. They are serializable and likely stored in system keys or sent to storage servers. `serializedCheckpoint` carries engine-specific metadata understood by the corresponding key-value store. `bulkLoadTaskState` links data moves to bulk load tasks.

## Dependencies And Integration Points
It depends on `BulkLoading.h` and `FDBTypes.h`. It integrates with `NativeAPI.actor.h` checkpoint creation/lookup helpers, storage servers, data distribution, data movement, RocksDB checkpoint export/create flows, and bulk loading.

## Risks And Edge Cases
The include guard has a spelling typo (`FDBCLIENT_STORAGCHECKPOINT_H`), which is harmless if consistent but easy to duplicate incorrectly. `format`, `state`, and `phase` are stored as integer fields, so invalid casts are possible if unvalidated data is deserialized. Equality and hash only consider checkpoint ID, not covered ranges/version. Coverage helpers require full containment, not overlap. Serialized checkpoint payload lifetime and arena ownership must be preserved.

## Test Signals
Tests should cover serialization round trips, state/format/phase casts, range and key coverage, equality/hash behavior, string output with optional fields, checkpoint lifecycle transitions, data move lifecycle transitions, bulk load task linkage, invalid enum values from deserialization, and interactions with checkpoint creation/metadata lookup actors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StorageCheckpoint.h -->
