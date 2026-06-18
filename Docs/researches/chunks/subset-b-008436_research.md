# sources/storage-engines/foundationdb/fdbclient/NativeAPI.actor.cpp lines 1-6674

## Scope

This chunk covers nearly all of FoundationDB's native client implementation in `fdbclient/NativeAPI.actor.cpp`, from global client/network state through transaction read/write paths, read-version batching, storage metrics, checkpoints, exclusion checks, and the beginning of worker reboot support. The requested range ends at line 6674 inside `rebootWorkerActor()` after it has fetched worker interfaces and split the requested address list; the rest of that administrative helper and later tail functions are outside this chunk.

## Purpose

The code implements the asynchronous client-side API used by FoundationDB transactions. It translates `Database`, `DatabaseContext`, `TransactionState`, and `Transaction` operations into requests against coordinators, GRV proxies, commit proxies, storage servers, and management endpoints. The major responsibilities are:

- Initialize and run the Flow network, TLS, tracing, client knobs, metrics, and system monitoring.
- Create database contexts from cluster connection records and monitor proxy/coordinator state.
- Maintain location caches for key-to-storage-server routing, plus TSS and tag mappings.
- Execute transactional reads (`get`, `getKey`, `getRange`, mapped ranges, streams, split points, address lookup) with snapshot/conflict-range semantics.
- Batch and throttle read-version requests through GRV proxies, including optional cached GRV background refresh.
- Build, validate, submit, retry, and diagnose commits through commit proxies, including idempotency, unknown-result handling, versionstamps, watch setup, and conflict reporting.
- Support watches, transaction options, client transaction logging, tracing spans, and per-operation metrics.
- Provide storage-metrics/data-distribution helpers, checkpoint metadata creation/lookup, storage wiggle metadata, snapshot requests, safe exclusion checks, and early administrative worker-connectivity/reboot plumbing.

## Important APIs, Types, and Functions

- Global/client setup:
  - `NetworkOptions`, `networkOptions`, and `tlsConfig` hold process-wide client configuration for tracing, TLS, supported client versions, run-loop profiling, logging, and external-client identity.
  - `setNetworkOption()` decodes `FDBNetworkOptions` into tracing/TLS/knob/client-buggify/distributed-tracing state.
  - `setupNetwork()`, `runNetwork()`, and `stopNetwork()` manage `g_network`, `FlowTransport`, `Net2FileSystem`, tracing initialization, and network busyness monitoring.
  - `initializeClientTracing()` opens or completes trace setup, annotates `ClientStart`, initializes metrics, and starts system monitoring once a local address is available.

- Database context and connection state:
  - `Database::createDatabase()` creates a `DatabaseContext`, starts `monitorProxies()`, initializes `globalConfig`, and records connection trace metadata.
  - `DatabaseContext::switchConnectionRecord()` and `switchConnectionRecordImpl()` reset proxy/location/version-vector state and wait for a successful GRV on the new cluster before firing `connectionFileChangedTrigger`.
  - `DatabaseContext::updateProxies()`, `getCommitProxies()`, `getGrvProxies()`, `getCommitProxiesFuture()`, and `isCurrentGrvProxy()` materialize proxy interfaces from `ClientDBInfo` and reject stale GRV deltas.
  - `DatabaseContext::setOption()` handles database-level options such as location cache size, locality IDs, max watches, snapshot RYW toggles, and causal-read testing.

- Location cache and routing:
  - `getCachedLocation()`, `getCachedLocations()`, `setCachedLocation()`, and `invalidateCache()` manage the `KeyRangeMap<Reference<LocationInfo>>` cache with random eviction.
  - `getKeyLocation_internal()` and `getKeyRangeLocations_internal()` ask commit proxies for key-server locations, update the cache, and refresh TSS/tag mappings.
  - `checkOnlyEndpointFailed()` throttles cache refresh for endpoint-only failures on otherwise healthy servers to avoid overloading proxies during bounces or data movement.
  - `updateBackoff()` applies client backoff when commit proxies reject location requests for memory pressure.

- Transaction state and read APIs:
  - `TransactionState::TransactionState()`, `cloneAndReset()`, `startTransaction()`, and `getReadVersion()` coordinate span context, options, read versions, metadata version promises, and retry-preserved state.
  - `Transaction::get()`, `getKey()`, `getRange()`, `getMappedRange()`, `getRangeStream()`, `getAddressesForKey()`, and `getRangeSplitPoints()` are the public native transaction read surfaces.
  - `getValue()`, `getKey()`, templated `getRange()`, `getExactRange()`, `getRangeFallback()`, and `getRangeStreamImpl()` implement storage-server request loops, load balancing, conflict-range promises, byte/row limits, reverse scans, cache invalidation, and physical read metrics.
  - `GetRangeLimits` tracks row/byte/min-row limits across partial replies for normal and mapped range results.
  - `TSSDuplicateStreamData`, `tssStreamComparison()`, and `maybeDuplicateTSSStreamFragment()` duplicate streaming reads to a test storage server and trace mismatches.

- Watches:
  - `watchValue()`, `watchStorageServerResp()`, `sameVersionDiffValue()`, `getWatchFuture()`, `watchValueMap()`, `restartWatch()`, and actor `watch()` implement watch de-duplication by key, ABA handling, storage-server polling fallbacks, reference counting, watch recreation after connection-file changes, and max-watch enforcement.
  - `WatchRefCountUpdater` is an RAII helper that updates `DatabaseContext` watch reference counts even when actor control flow throws.

- Commit and retry:
  - `Transaction::set()`, `atomicOp()`, `clear()`, `addReadConflictRange()`, `addWriteConflictRange()`, `makeSelfConflicting()`, and `getSize()` build the `CommitTransactionRequest`.
  - `commitMutations()` performs read-only short-circuiting, size checks, self-conflicting conflict-range enforcement, idempotency conflict ranges, debug dumps, lock/quota flags, optional sampled write checking, and `tryCommit()` dispatch.
  - `tryCommit()` gets/uses a read version, optionally estimates commit costs, submits to commit proxies, updates cached versions, versionstamp promise, metadata-version cache, latency/transaction counters, conflicting-key state, and handles `request_maybe_delivered`/`commit_unknown_result`.
  - `commitDummyTransaction()` and `determineCommitStatus()` are used to make commit-unknown outcomes safe and to query idempotency records.
  - `commitAndWatch()`, `Transaction::commit()`, `Transaction::onError()`, `resetImpl()`, `reset()`, and `fullReset()` define retry lifecycle, watch cleanup/setup, backoff, and API-version-specific automatic reset behavior.

- Options, tracing, and logging:
  - `Transaction::setOption()` implements transaction options for priorities, causal read/write risk, lock awareness, tags, logging, server request tracing, size limits, provisional proxies, GRV cache use/skip, system/raw access, auth tokens, idempotency, read server-side cache hints, read priorities, and replica consistency checks.
  - `debugAddTags()`, `createTrLogInfoProbabilistically()`, `flushTrLogsIfEnabled()`, `setTransactionID()`, and `setToken()` integrate tracing, transaction lineage/logging, and sampled client status reporting.

- Read-version path:
  - `getConsistentReadVersion()` sends `GetReadVersionRequest` to GRV proxies, updates tag throttle data, min acceptable read version, metadata version, and storage-server version-vector deltas.
  - `readVersionBatcher()` groups `VersionRequest`s by flags and max GRV queue delay, records histograms, adapts batch timeout from reply latency, and broadcasts one GRV reply to many callers.
  - `extractReadVersion()` maps a GRV reply into a transaction read version and metadata-version promise, applies lock checks, tag throttling, cached-version updates, and completion counters.
  - `backgroundGrvUpdater()` and `rkThrottlingCooledDown()` maintain optional cached GRVs when allowed by knobs/options and recent RK throttling.

- Storage metrics and data-distribution helpers:
  - `getStorageMetricsLargeKeyRange()`, `doGetStorageMetrics()`, `waitStorageMetrics()`, `waitStorageMetricsMultipleLocations()`, `trackBoundedStorageMetrics()`, `waitStorageMetricsWithLocation()`, `DatabaseContext::getStorageMetrics()`, and `waitDataDistributionMetricsList()` query and wait for `StorageMetrics` across one or more shard locations.
  - `getReadHotRanges()` and `DatabaseContext::getReadHotRanges()` fetch read-hot subrange metrics.
  - `splitStorageMetricsStream()`, `splitStorageMetricsWithLocations()`, `splitStorageMetrics()`, and `DatabaseContext::splitStorageMetrics()` compute split points by byte/metric limits while preserving shard boundaries and retrying on movement.
  - `setPerpetualStorageWiggle()` and `readStorageWiggleValues()` write/read system-key-backed wiggle metadata through RYW transactions.

- Checkpoints and administration:
  - `snapCreate()` sends snapshot commands to commit proxies.
  - `createCheckpointImpl()` maps requested ranges to storage-server source IDs, writes pending `CheckpointMetaData` records, and currently supports `DataMoveRocksCF`.
  - `getCheckpointMetaDataInternal()`, `getCheckpointMetaDataForRange()`, and `getCheckpointMetaData()` query storage servers for checkpoint metadata per shard with timeout/error aggregation.
  - `checkSafeExclusions()` asks data distribution for exclusion safety and separately verifies coordinator quorum/fault-tolerance impact.
  - `verifyInterfaceActor()` tests whether a worker interface can answer a leader request under a `FlowLock`.
  - `rebootWorkerActor()` begins by normalizing duration, fetching worker interfaces from the connection record, indexing primary and secondary addresses, and splitting the user-provided address list; its request-sending body is outside this chunk.

## Control Flow

Network setup is process-wide and must happen before opening databases. `setupNetwork()` applies saved knob overrides, creates the network and transport, optionally initializes tracing, and starts background busyness monitoring. `Database::createDatabase()` then opens a cluster connection record, starts proxy monitoring, initializes config sampling triggers, and returns a ref-counted `DatabaseContext`.

Read operations follow a common pattern: ensure a transaction read version exists, validate the version, resolve storage-server locations from cache or commit proxies, load-balance the storage-server request, account for physical reads/bytes/latency, and invalidate the location cache on shard-location errors. Range reads add selector resolution, shard iteration, limit decrementing, continuation keys, fallback exact-range logic, and conflict-range computation for non-snapshot reads. Streaming range reads use a storage-server reply stream, backpressure through `results.onEmpty()`, explicit end-of-stream signaling, and optional TSS duplicate comparison.

Read-version control flow is batched. `TransactionState::getReadVersion()` may return a fresh cached GRV when enabled and not stale; otherwise it chooses a `VersionBatcherKey`, starts a `readVersionBatcher()` actor if needed, sends a `VersionRequest`, records `startTime`, and returns `extractReadVersion()` over the reply promise. The batcher aggregates until max batch size or timeout, calls `getConsistentReadVersion()`, then broadcasts the result or error.

Commit control flow starts in `Transaction::commit()`, which wraps `commitMutations()` in `commitAndWatch()`. `commitMutations()` validates that the transaction is writable and within size limits, merges asynchronously computed conflict ranges, inserts idempotency/self-conflict ranges when needed, sets request flags, and calls `tryCommit()`. `tryCommit()` waits for/readies a read version, optionally estimates costs, submits to the selected commit proxy path, and distinguishes committed, conflict, retryable, and unknown-result outcomes. Unknown-result handling may force a dummy conflicting transaction and query idempotency records before returning success, `transaction_too_old`, or `commit_unknown_result`.

Watch flow is split between transaction commit and background storage-server watch actors. A watch registered on a transaction is stored until commit; after a successful commit, `setupWatches()` starts `watchValueMap()` at the committed/read version. `getWatchFuture()` coalesces duplicate key/value watches, replaces stale lower-version metadata, handles same-version/different-value validation with a read, and uses `watchStorageServerResp()` to wait for storage-server notification while surviving selected transient watch errors.

Storage metrics and checkpoint helpers repeatedly resolve shard locations, fan out to storage servers or commit proxies, aggregate replies, and retry after cache invalidation on `wrong_shard_server`/`all_alternatives_failed`. The split-metrics functions either stream split keys through a `PromiseStream` or return a vector after walking all locations, trimming final split points when the used metrics are within the unfair-split bound.

## State and Persistence Behavior

- `DatabaseContext` owns long-lived client state: connection record, proxy/coordinator async vars, client locality, global config, location cache, TSS/tag mappings, failed endpoint refresh state, throttled tag maps, version-vector cache, metadata-version cache ring, GRV batchers, watch metadata, latency histograms/counters, client status queue, and optional shared state.
- The location cache persists only in memory and is aggressively invalidated on connection-file switches, locality changes, shard errors, endpoint-only failures that need refresh, and storage-metrics retries. It stores `LocationInfo` references built from `StorageServerInterface`s adapted to client locality.
- Transactions persist mutable request state in `TransactionState` and `CommitTransactionRequest`: options, read-version future, metadata-version promise, transaction mutations/conflict ranges, tags, auth token, span context, versionstamp promise, retry count, committed version, idempotency state, and optional conflicting-key map.
- Successful commits persist user mutations through commit proxies and update client-side caches: cached read version, committed version, versionstamp, metadata-version cache, counters, and sampled transaction logs. Failed commits may persist no data but can update throttling/backoff/counters and conflict diagnostics.
- Idempotency records are persistent system-key state managed by the commit path; `determineCommitStatus()` reads `idempotencyIdsExpiredVersion` and scans `idempotencyIdKeys` to decide whether a maybe-delivered commit actually committed.
- Watches are client-side coalesced state plus storage-server watch requests. `watchMetadata` maps keys to `WatchMetadata`, reference counts protect shared promises, and connection-record changes cause restart at `minAcceptableReadVersion`.
- Storage metrics/read-hot/split helpers do not directly mutate user data, but they depend on current key-server metadata and storage-server long-poll state. `setPerpetualStorageWiggle()`, checkpoint creation, snapshot creation, and storage wiggle reads/writes operate on system keys or management proxy APIs.
- Checkpoint creation persists `CheckpointMetaData` entries keyed by generated checkpoint IDs, with state set to `Pending`; retrieval queries storage servers for checkpoint availability rather than just reading metadata keys.
- `checkSafeExclusions()` does not persist changes; it combines transient data-distribution safety replies with live coordinator reachability/quorum observations.

## Dependencies and Integration Points

- Flow actor runtime: all `ACTOR` functions, `Future`, `Promise`, `PromiseStream`, `choose`, `wait`, `waitNext`, `delay`, `actorCollection`, `uncancellable`, `TaskPriority`, and arena-backed `Standalone`/`VectorRef` types depend on Flow's actor compiler and runtime.
- RPC/load balancing: `basicLoadBalance()`, `loadBalance()`, `commitProxyLoadBalance()`, `RequestStream`, `PublicRequestStream`, `FailureMonitor`, and `QueueModel` connect client requests to GRV proxies, commit proxies, storage servers, coordinators, and worker interfaces.
- Cluster metadata: `monitorProxies()`, `ClientDBInfo`, `ClientLeaderRegInterface`, `ClientCoordinators`, `ClusterConnectionFile`, `ClusterConnectionMemoryRecord`, and connection-record async vars drive topology/proxy/coordinator changes.
- System key encodings and management APIs: key-server/server-list keys, server tag maps, idempotency keys, storage wiggle metadata, checkpoint keys, exclusion safety requests, snapshot requests, and DD metrics all depend on `SystemData.h`, `ManagementAPI.h`, and key-backed type helpers.
- Read-your-writes integration: several administrative helpers use `ReadYourWritesTransaction`; the native transaction layer also exposes raw/system access while leaving higher-level RYW semantics to `ReadYourWrites`.
- Observability: `TraceEvent`, `Span`, `TraceInterval`, `g_traceBatch`, histograms, client status transaction logs, system monitor, distributed tracing, and code probes are deeply interleaved with normal paths.
- Configuration and knobs: behavior depends heavily on `CLIENT_KNOBS`, `FLOW_KNOBS`, global config keys such as transaction tag sampling and CSI sampling, transaction/database/network options, buggify, simulation flags, and API version gates.
- Security/auth: transaction authorization token state is carried on `TransactionState` and copied into internal dummy/status transactions where needed.

## Risks and Edge Cases

- Location-cache correctness is critical. Stale cache entries can cause `wrong_shard_server`; over-eager refresh after endpoint-only failure can overload commit proxies while data movement is trying to resolve the failed endpoint.
- Connection-record switching resets proxies, min acceptable read version, location cache, version-vector cache, and client ID. In-flight reads/watches must observe `connectionFileChanged()` and return `transaction_too_old` or restart watches, or they could mix cluster state.
- Read-version batching shares one GRV reply across many transactions. Incorrect flag/max-queue-delay grouping, stale GRV proxy deltas, or tag-throttle updates can cause wrong priority behavior, missed throttling, or version-vector cache corruption.
- GRV cache use is intentionally gated by knobs, explicit options, staleness, and RK throttling cooldown. Returning an overly stale cached version would affect read freshness and `future_version` behavior.
- Range-read selector/conflict-range logic is subtle, especially with reverse reads, byte limits, `readThrough`, boundary selectors, `allKeys.begin/end`, mapped ranges lacking native non-snapshot serialization, and fallback from wrong-shard errors.
- Streaming range reads have explicit caveats: row/byte limits and reverse streaming are asserted unsupported in the public wrapper. TSS stream comparison adds asynchronous duplicate streams whose error propagation must not corrupt the main stream.
- Watch de-duplication has ABA and same-version/different-value cases. Incorrect metadata replacement, reference counting, or restart logic can leak watch counters, drop notifications, or complete watches too early.
- Commit unknown-result handling is high risk. The code relies on self-conflicting ranges, dummy transactions, idempotency IDs, and idempotency expiration version bounds to distinguish committed from not committed. Bad conflict-range intersection or idempotency scan bounds could turn uncertainty into duplicate effects or false failures.
- Automatic idempotency uses deterministic randomness in simulation and OS entropy in production; it must not reuse IDs across transactions, and cleanup is best-effort through the chosen commit proxy.
- Transaction option validation is API-sensitive. Misordered or missing validation can allow illegal option values, unsafe raw/system-key access, unsupported mapped-range conflict behavior, or inconsistent read-only/lock-aware semantics.
- Metadata-version cache and versionstamp promises are updated on both GRV and commit paths. Errors after partial promise/cache updates must avoid double-send or stale values after reset.
- Storage metrics and split logic assume split keys returned by storage servers are ordered and that shard limits are not exceeded indefinitely. The code asserts on out-of-order splits and delays/retries on too many shards, so data movement races are expected but bounded.
- Checkpoint metadata requests query all replicas for each shard with timeouts. Error prioritization between timeout, `checkpoint_not_found`, and other storage-server failures affects user-visible checkpoint availability.
- `checkSafeExclusions()` combines data-distributor safety with a coordinator quorum snapshot. Hostname resolution, delayed coordinator replies, and partial coordinator unavailability can make the conservative result false even when data distribution says safe.
- The chunk boundary cuts off the worker reboot request loop. Any full analysis of reboot semantics must include the following lines after address parsing.

## Test Signals

- Network/client setup tests should cover option validation, trace initialization before and after database open, TLS paths, supported client version parsing, external-client mode, knob parsing, network double setup/restart errors, and stop behavior with tracing/profiling enabled.
- Database/proxy tests should exercise database creation from files and memory records, proxy-change triggers, provisional proxy handling, connection-record switch, localities changing cache/proxy load-balance state, and cluster protocol lookup through endpoints and connect packets.
- Location-cache tests should cover single-key and range cache hits/misses, reverse lookup, cache eviction, shard movement, `wrong_shard_server`, `all_alternatives_failed`, endpoint-only failure refresh throttling, TSS mapping updates, and tag mapping updates.
- Read tests should cover `get`, `getKey`, forward/reverse `getRange`, byte and row limits, min rows, mapped ranges, selector boundary cases, snapshot versus conflict-generating reads, metadata-version key cache hits, address lookup from system key metadata, storage-server version-vector deltas, and read-server cache/priority options.
- Streaming tests should validate ordered fragments, end-of-stream signaling, shard boundary `readThrough`, backpressure via `onEmpty`, broken promise to connection failure mapping, retry after shard errors, and TSS mismatch/timeout metrics.
- Watch tests should cover max outstanding watches, duplicate key/value coalescing, higher/lower/same-version replacement cases, same-version different value validation, storage-server watch cancellation/timeouts/process-behind fallback, connection-record switch restart, future reference count cleanup, and transaction commit/error interaction.
- Commit tests should cover read-only commits, size limits, conflict-range inclusion from reads/getKey/ranges, self-conflicting automatic range insertion, all mutation types, versionstamp availability/errors, commit-on-first-proxy, lock-aware and quota flags, sampled check-writes, transaction logging, conflicting-key reports, and metadata-version cache update.
- Retry/error tests should cover `onError()` behavior for `not_committed`, `commit_unknown_result`, proxy memory limits, database locked, process behind, batch/tag/hot-shard/range-lock throttling, transaction too old, future version, non-retryable range lock rejection, retry backoff limits, and API-version-specific reset behavior.
- Idempotency tests should cover explicit and automatic IDs, invalid ID sizes, maybe-delivered requests, dummy transaction safety, idempotency record lookup success/failure, expired idempotency versions, and versionstamp reconstruction from committed idempotent results.
- GRV tests should cover batch sizing/timeouts, per-priority counters, tag throttle insertion/removal/recheck, `maxGrvQueueDelayMS`, stale proxy ID handling, version-vector cache clear/apply, cached GRV use/skip options, forced cache off, RK cooldown, and background updater failures.
- Storage metric tests should cover large key ranges, expected shard count mismatch, shard-limit penalties, permitted error aggregation, long-poll delta tracking, wrong-shard retry, future-version retry, read-hot range aggregation, range split points, split metrics streaming/vector variants, unfair final split trimming, and out-of-order split detection.
- Management tests should cover perpetual storage wiggle set/read, snapshot request tracing/errors, checkpoint creation for multi-shard ranges, checkpoint retrieval from one replica among many, checkpoint timeout/error aggregation, safe exclusions involving data-distributor denial, coordinator quorum loss, coordinator address exclusion, worker interface verification timeout/success, and the continuation of reboot behavior in the next chunk.
