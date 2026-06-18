# sources/storage-engines/foundationdb/fdbclient/NativeAPI.actor.cpp lines 6675-6810

## Scope And Purpose

This chunk completes several client-side management and helper APIs on `DatabaseContext`, then opens the `NativeAPI` namespace for a storage-server/process-class lookup helper. It is not one continuous subsystem; it is a compact group of public API bridge points for:

- sending reboot, kill, suspend, or expensive-data-check requests to worker processes;
- forcing recovery with possible data loss;
- validating and issuing management snapshot requests;
- initializing shared client state used by multi-version clients and GRV caching;
- constructing read-your-writes transactions;
- querying per-storage-server read-hot metrics;
- computing legal key-size limits;
- correlating registered storage servers with their worker `ProcessClass`.

The code is actor-based and uses Flow `Future`, `co_await`, `Reference`, `Standalone`, and `VectorRef` lifetimes. Most functions are thin adapters from public interfaces declared in `fdbclient/include/fdbclient/DatabaseContext.h` and `fdbclient/include/fdbclient/NativeAPI.actor.h` to lower-level management, cluster metadata, or storage-server request streams.

## Important APIs, Types, And Functions

- `rebootWorkerActor(...)` continuation, lines 6675-6697: receives a comma-separated address list from `DatabaseContext::rebootWorker`, validates worker addresses against cluster-controller worker interfaces, asynchronously verifies connectivity, then sends `RebootRequest(false, check, duration)` to every requested worker. The visible section covers the validation, connection checks, and request fan-out; the preceding lines build `workerInterfaces` from `getWorkerInterfaces()`.
- `DatabaseContext::rebootWorker(StringRef addr, bool check, int duration)`, lines 6699-6701: public management API wrapper returning `Future<int64_t>`. Callers treat `1` as requests sent and `0` as failure. fdbcli kill, suspend, and expensive data check commands call through this path.
- `DatabaseContext::forceRecoveryWithDataLoss(StringRef dcId)`, lines 6703-6705: forwards to `forceRecovery(getConnectionRecord(), dcId)`. It depends on the current connection record and delegates the actual recovery protocol elsewhere.
- `createSnapshotActor(DatabaseContext* cx, UID snapUID, StringRef snapCmd)`, lines 6707-6709: calls `mgmtSnapCreate(cx->clone(), snapCmd, snapUID)` on a cloned database reference.
- `DatabaseContext::createSnapshot(StringRef uid, StringRef snapshot_command)`, lines 6711-6719: validates that the supplied snapshot UID is exactly 32 hexadecimal characters before converting with `UID::fromString` and starting `createSnapshotActor`; invalid input throws `snap_invalid_uid_string`.
- `sharedStateDelRef(DatabaseSharedState* ssPtr)`, lines 6721-6725: shared-state deletion callback that decrements the atomic refcount and deletes the object at zero.
- `DatabaseContext::initSharedState()`, lines 6727-6736: allocates a fresh `DatabaseSharedState`, initializes refcount ownership for both the MultiVersion API map and this `DatabaseContext`, installs `delRef`, calls `setSharedState`, and returns the raw pointer in a future.
- `DatabaseContext::setSharedState(DatabaseSharedState* p)`, lines 6738-6742: installs externally supplied shared state after checking `p->protocolVersion == currentProtocolVersion()`, then increments its refcount.
- `DatabaseContext::createTransaction()`, lines 6744-6746: constructs a `ReadYourWritesTransaction` around `Database(Reference<DatabaseContext>::addRef(this))`.
- `getHotRangeMetricsActor(...)`, lines 6748-6761: sends a `ReadHotSubRangeRequest` to one `StorageServerInterface::getReadHotRanges` request stream and returns a `Standalone<VectorRef<ReadHotRangeWithMetrics>>`; errors are printed and converted to an empty result.
- `DatabaseContext::getHotRangeMetrics(...)`, lines 6763-6771: packages `KeyRange`, `ReadHotSubRangeRequest::SplitType`, and split count into a request and retains the database reference while the actor is outstanding.
- `getMaxKeySize`, `getMaxReadKeySize`, `getMaxWriteKeySize`, `getMaxClearKeySize`, lines 6773-6787: shared key-limit helpers. System keys use `CLIENT_KNOBS->SYSTEM_KEY_SIZE_LIMIT`; all other keys use `CLIENT_KNOBS->KEY_SIZE_LIMIT`. The `hasRawAccess` parameter is currently unused by this implementation despite the header comment noting raw-access behavior.
- `NativeAPI::getServerListAndProcessClasses(Transaction* tr)`, lines 6791-6808: concurrently loads worker process metadata via `getWorkers(tr)` and storage server registrations via `tr->getRange(serverListKeys, CLIENT_KNOBS->TOO_MANY)`, then returns `(StorageServerInterface, ProcessClass)` pairs keyed by `LocalityData::processId`.

Related declarations are in `fdbclient/include/fdbclient/DatabaseContext.h` around the `getHotRangeMetrics`, management API, and `sharedStatePtr` members, plus `fdbclient/include/fdbclient/NativeAPI.actor.h` for key-size helpers and `getServerListAndProcessClasses`. `DatabaseSharedState` is declared in `fdbclient/include/fdbclient/FDBTypes.h` with a fixed leading layout of `protocolVersion` and `delRef`, mutex-protected `GRVCacheSpace`, and atomic `refCount`.

## Control Flow

`rebootWorkerActor` first limits concurrent connection verification with `FlowLock(CLIENT_KNOBS->CLI_CONNECT_PARALLELISM)`. For each requested address, the actor returns `0` immediately if the address is absent from the map built from cluster-controller worker interfaces. Otherwise it starts `verifyInterfaceActor(...)` futures, waits for all of them, and aborts with `0` if any connection check failed. Only after all requested workers are verified does it loop again and call `reboot.send(...)` on every worker. The comments explicitly preserve parallel request behavior: verification futures are started before waiting, and reboot messages are sent without awaiting individual replies.

`createSnapshot` performs synchronous input validation before any management actor starts. It copies `StringRef uid` into `std::string`, applies `std::all_of(..., std::isxdigit)` and a fixed length check of 32 bytes, throws on invalid UID, and otherwise passes a parsed `UID` to `createSnapshotActor`.

`initSharedState` is a one-time initializer. It asserts that `sharedStatePtr` is null, allocates heap state, increments `refCount` once for the MultiVersion API map ownership, assigns the deletion callback, and calls `setSharedState`, which increments the count again for this database context. `setSharedState` itself is also used by multi-version and thread-safe API layers when they propagate already-created shared state into another context.

`getHotRangeMetrics` builds a `ReadHotSubRangeRequest` and delegates to an actor that performs a single request/reply operation against a specific storage server endpoint. `tryGetReply` returns `ErrorOr`; on error this code logs a printable message with `fmt::print` and returns an empty `Standalone<VectorRef<...>>`, so downstream callers see "no metrics" rather than an exception.

`getServerListAndProcessClasses` runs two transaction reads in parallel by creating both futures before `co_await (success(workers) && success(serverList))`. It asserts that the server-list range was not truncated, builds a process-id-to-`ProcessData` map from workers, decodes each server-list value into `StorageServerInterface`, and appends the server interface with the process class looked up by `ssi.locality.processId()`.

## State And Persistence Behavior

The persistent cluster state read in this chunk is limited to system-key metadata:

- `serverListKeys` is read transactionally to discover registered storage servers.
- `getWorkers(tr)` reads management metadata for live worker processes.
- `forceRecovery(...)` and `mgmtSnapCreate(...)` are management APIs that mutate cluster control state outside this chunk; this code only invokes them.

The main in-memory state mutation is `DatabaseContext::sharedStatePtr`. `DatabaseSharedState` is shared across multi-version API database instances and currently holds GRV cache state guarded by `mutexLock`. The refcount protocol is manual:

- constructor initializes `refCount` to zero;
- `initSharedState` increments once for the MultiVersion API map;
- `setSharedState` increments once for the `DatabaseContext`;
- `sharedStateDelRef` deletes when decremented to zero;
- `DatabaseContext` destruction elsewhere calls `sharedStatePtr->delRef(sharedStatePtr)` when present.

The hot-range helper does not persist anything. It sends a request to a storage server, receives metrics derived from storage-server memory and metrics state, and returns an owned `Standalone<VectorRef<ReadHotRangeWithMetrics>>`.

The key-size helpers are pure reads of `CLIENT_KNOBS` and the key prefix. They encode the distinction that system keys can be larger than normal application keys.

## Dependencies And Integration Points

- Flow actor runtime: `Future`, `co_await`, `waitForAll`, `success`, `ErrorOr`, and `Reference` shape every asynchronous path here.
- Client knobs: `CLIENT_KNOBS->CLI_CONNECT_PARALLELISM`, `CLIENT_KNOBS->TOO_MANY`, `CLIENT_KNOBS->SYSTEM_KEY_SIZE_LIMIT`, and `CLIENT_KNOBS->KEY_SIZE_LIMIT` control fan-out and limits.
- Management API: `getWorkerInterfaces`, `getWorkers`, `forceRecovery`, and `mgmtSnapCreate` provide the cluster-management backing for worker reboot, forced recovery, snapshots, and process metadata.
- Network interfaces: `ClientWorkerInterface::reboot` receives `RebootRequest`; `StorageServerInterface::getReadHotRanges` serves `ReadHotSubRangeRequest`.
- System metadata: `serverListKeys` and `decodeServerListValue` turn transaction reads into `StorageServerInterface` objects.
- API wrappers: C bindings, Flow bindings, thread-safe database wrappers, and multi-version database wrappers forward reboot and snapshot requests into these `DatabaseContext` methods. fdbcli commands such as kill, suspend, snapshot, and expensive data check use those wrappers.
- Data distribution and ratekeeper components call `NativeAPI::getServerListAndProcessClasses` to reason about storage servers alongside process classes.
- Transaction stack: `createTransaction` ties `DatabaseContext` to `ReadYourWritesTransaction`, which is the standard client transaction implementation.

## Risks And Edge Cases

- `rebootWorkerActor` treats any unknown requested address or failed connectivity verification as complete failure for the whole comma-separated request. No partial reboot sends occur unless all targets pass validation.
- Address matching is exact against the map built earlier, including normalization performed before this visible range. Callers must supply the same primary or secondary address form expected by that map.
- `duration < 0` is sanitized before this chunk to zero; in this visible range the value is trusted and passed into `RebootRequest`.
- `reboot.send(...)` is fire-and-forget. Returning `1` means the requests were sent to known interfaces, not that the workers rebooted, killed themselves, suspended, or completed an expensive data check.
- Snapshot UID validation uses `std::isxdigit` on `unsigned char`, which avoids the common signed-char undefined behavior risk. The only accepted shape is 32 hex characters; no dashed UUID form is accepted.
- `createSnapshotActor` clones the database context for `mgmtSnapCreate`, so snapshot management is decoupled from the caller's raw pointer lifetime, but failures in `mgmtSnapCreate` still surface through the returned future.
- `setSharedState` relies on `ASSERT` for protocol compatibility. In release configurations where assertions may be disabled, a mismatched `DatabaseSharedState` would not be actively rejected here.
- Manual shared-state refcounting is sensitive to every owner calling the deletion callback exactly once. The struct's leading-member layout is called out as compatibility-sensitive for MultiVersion Client access.
- `getHotRangeMetricsActor` logs and returns an empty vector on storage-server request failure. This can make endpoint failures indistinguishable from a server reporting no hot ranges unless callers separately inspect logs or surrounding health.
- `getServerListAndProcessClasses` uses `id_data[ssi.locality.processId()]`, which default-inserts `ProcessData` if a storage server's process id is missing from the worker map. That may yield a default `ProcessClass` rather than an explicit error. It also asserts, rather than handles, a truncated server list.
- The key-size helper signature includes `hasRawAccess`, but this implementation ignores it. Tests or callers expecting a special raw-access allowance need to match the current behavior, not just the header comment.

## Test Signals

Useful tests and workload signals around this chunk include:

- fdbcli kill/suspend/expensive-data-check paths should verify that unknown addresses return zero, verified addresses send reboot requests, and multi-address requests do not partially send when one target is invalid.
- Snapshot command tests should cover invalid UID length, non-hex characters, and accepted 32-character hex UIDs.
- Multi-version API or sideband tests should exercise `initSharedState`/`setSharedState` lifecycle, protocol-version assertions, and cleanup paths that call `DatabaseSharedState::delRef`.
- Read-hot detection or `HotRangeCommand` style tests should cover successful `ReadHotSubRangeRequest` replies and failed storage-server endpoints producing empty results.
- API correctness and workload fuzz tests already reference `getMaxKeySize`, `getMaxReadKeySize`, `getMaxWriteKeySize`, and `getMaxClearKeySize`; boundary cases should include normal keys at `KEY_SIZE_LIMIT`, system keys at `SYSTEM_KEY_SIZE_LIMIT`, and oversized read/clear keys that are treated as non-existent.
- Data-distribution, ratekeeper, and worker workloads that call `NativeAPI::getServerListAndProcessClasses` should validate behavior when server-list entries and worker process metadata are consistent, plus failure/truncation scenarios if a test harness can force `CLIENT_KNOBS->TOO_MANY` limits or missing process IDs.
