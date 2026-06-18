# sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp lines 12190-12732

## Scope

This chunk covers the tail of `storageserver.actor.cpp`, from the retry loop used by memory-engine recovery to decide whether an old storage server can be removed, through storage-server interface re-registration, RocksDB log cleanup, the two `storageServer()` actor entry points for new recruitment and reboot recovery, and the local `versionedMapTest()` diagnostic. It is the final chunk for this oversized source file and depends on earlier chunks for the definitions of `StorageServer`, `storageServerCore()`, `StorageServerDisk`, shard state, durable-state serialization, byte-sample recovery, and many request handlers.

## Purpose

The code in this range wires a `StorageServer` object into cluster metadata and its local storage engine lifecycle. It decides how a process should rejoin after reboot, how a newly recruited storage server becomes durable and visible, how a TSS is reattached to its paired storage server, and how teardown should distinguish permanent removal from retryable reboot-style exits. It also adds a small background cleaner for RocksDB log files and a standalone versioned-map memory experiment.

The highest-level responsibilities are:

- Repeatedly check whether an in-memory storage server can be safely removed when recovery races with cluster metadata cleanup.
- Replace or refresh the `serverList`, `serverTag`, tag history, tag locality, and TSS mapping records used by commit proxies, data distribution, and clients.
- Gate when a `StorageServerInterface` advertises request acceptance during startup and recovery.
- Initialize local folders for checkpoints, fetched checkpoints, bulk dump, and bulk load state.
- Initialize, commit, mark durable, restore, or dispose the storage engine depending on whether this is a new recruitment or a rebooted server.
- Start `storageServerCore()` only after durable state and system-key registration are coherent.
- Ensure shutdown drains server-owned actors and local locks before `StorageServer self` leaves the stack.

## Important APIs, Types, and Functions

- `memoryStoreRecover(IKeyValueStore* store, Reference<IClusterConnectionRecord> connRecord, UID id)`: visible here from inside its retry loop. It creates a temporary client database and a `ReadYourWritesTransaction`, sets `PRIORITY_SYSTEM_IMMEDIATE` and `ACCESS_SYSTEM_KEYS`, calls `canRemoveStorageServer(tr, id)`, and waits/retries until cluster metadata confirms that the memory-backed server can be removed. It never completes for non-memory stores or missing connection records.
- `replaceInterface(StorageServer* self, StorageServerInterface ssi)`: actor used by normal storage servers during interface registration. It asks commit proxies for `GetStorageServerRejoinInfoReply`, writes the current `serverList` entry, updates locality/tag metadata if needed, prunes old tag history, then updates `self->tag`, `self->history`, and `self->allHistory`.
- `replaceTSSInterface(StorageServer* self, StorageServerInterface ssi)`: TSS-specific registration path. It reads the paired storage server's `serverTagKey`, fails with `worker_removed()` if the pair no longer exists, writes this TSS interface to `serverList`, and updates `tssMappingKeys` unless the TSS is quarantined.
- `storageInterfaceRegistration(StorageServer* self, StorageServerInterface ssi, Optional<Future<Void>> readyToAcceptRequests)`: common wrapper that either waits for an accept-ready future and calls `ssi.startAcceptingRequests()` or immediately calls `ssi.stopAcceptingRequests()`, then dispatches to the normal or TSS replacement path.
- `rocksdbLogCleaner(std::string folder)`: periodic actor that sanitizes the storage folder into a log prefix, scans `SERVER_KNOBS->LOG_DIRECTORY`, and deletes matching files older than `STORAGE_ROCKSDB_LOG_TTL`.
- `storageServer(...)` new-recruit overload: creates a new `StorageServer`, initializes storage, creates local directories, optionally calls `addStorageServer()`, sets the initial version/tag, calls `makeNewStorageServerDurable()`, replies to the recruiter, and runs `storageServerCore()`.
- `storageServer(...)` recovery overload: creates a `StorageServer` around an existing store, initializes/commits or races that commit with `memoryStoreRecover()`, restores durable state, validates TSS identity, re-registers the interface, and runs `storageServerCore()`.
- `versionedMapTest()`: local diagnostic that mutates a `VersionedMap<int,int>` at many versions and prints node size, allocation size, distinct key count, and memory usage.

Important data and integration types in the chunk include `IKeyValueStore`, `StorageServerInterface`, `Tag`, `Version`, `ReplyPromise<InitializeStorageReply>`, `AsyncVar<ServerDBInfo>`, `ReadYourWritesTransaction`, `Transaction`, `CommitProxyInfo`, `GetStorageServerRejoinInfoRequest/Reply`, `KeyBackedMap<UID, UID>`, `ActorCollection`, and `VersionedMap`.

## Control Flow

`memoryStoreRecover()` repeatedly starts or reuses a RYW transaction against the cluster connection record. On each pass it sets system/immediate options and calls `canRemoveStorageServer()`. If removal is not yet safe, it waits for `REMOVE_RETRY_DELAY`, resets the transaction, traces `RemoveStorageServerRetrying`, and tries again. Retryable transaction errors flow through `tr->onError()`. Completion of this actor indicates the memory store can be disposed; otherwise the storage-engine commit can win the race in the recovery overload.

`replaceInterface()` loops until it can obtain rejoin information from a live commit proxy and commit the replacement metadata. Each iteration captures `self->db->onChange()` and the current commit proxy list. If no commit proxies are known it waits only for database-info changes. When a proxy replies, the function pins the transaction to `rep.version`, sets immediate and lock-aware options, adds read conflict ranges over the server-list/tag/tag-history/locality keys, and writes the current `serverList` value. If the server moved localities, it updates the tag-locality map. If a new tag is assigned, it uses `FIRST_IN_BATCH`, adds a tag-conflict read/write range, writes `serverTagKeyFor(ssi.id())`, and appends old tag history via `SetVersionstampedKey`. It also clears stale tag-history entries older than the storage server's durable version. After commit, in-memory tag/history fields are updated and traced; a buggify path can force `please_reboot()` when history is present.

`replaceTSSInterface()` is simpler but stricter. It loops on transaction errors, reads the pair's `serverTagKey`, and treats a missing pair as permanent worker removal. It then writes the TSS interface to `serverList` and conditionally writes the pair-to-TSS map. On commit it copies the pair's decoded tag into `self->tag`, because a TSS shadows its pair's tag rather than owning an independent server tag.

`storageInterfaceRegistration()` first controls whether the interface is accepting requests. New servers pass a future that is only set when the outer startup path allows serving. Recovery first invokes this helper without a future, intentionally registering a non-accepting interface to refresh metadata before core startup; later it starts the long-lived accepting registration actor using `self.registerInterfaceAcceptingRequests.getFuture()`.

The new-recruit `storageServer()` overload follows a staged startup:

1. Construct `StorageServer self`, preserve shard-awareness, set initial cluster version, and set TSS pair state if applicable.
2. Initialize server key prefix and storage-related folder paths, then add `rocksdbLogCleaner()`.
3. Call `self.storage.init()` and `self.storage.commit()` to establish an initialized local store.
4. Create checkpoint/fetched-checkpoint folders and clear bulk dump/load folders.
5. If `seedTag == invalidTag`, open the interface for accepting requests, send the internal readiness promise, call `addStorageServer()`, assign the returned tag, and set the initial version to `addedVersion - 1` for normal servers or `tssSeedVersion` for TSS.
6. If a seed tag was provided, use it directly.
7. Persist the fact that this is a new durable storage server with `makeNewStorageServerDurable(self.shardAware)` and commit again.
8. Start the long-lived interface-registration actor, send `InitializeStorageReply`, clear byte-sample recovery to ready state, and run `storageServerCore()`.

Any error before the recruitment reply sends `recruitment_failed()` to the recruiter. All errors halt `ssLock`, clear `moveInShards`, call `storageServerTerminated()`, cancel `ssCore`, drop background actors, yield once, and either return for terminal removal-style errors or rethrow for higher-level process handling.

The recovery `storageServer()` overload follows a different sequence:

1. Construct `StorageServer self`, derive folder paths, create missing checkpoint folders with warning traces, clear bulk dump/load folders, and add the RocksDB log cleaner.
2. Initialize storage, then race `self.storage.commit()` with `memoryStoreRecover()`. A memory-recovery win means the server was removed from cluster metadata before recovery could finish; the code traces `DisposeStorageServer` and throws `worker_removed()`.
3. Restore durable server state with `restoreDurableState()`. If the store is not a durable storage server, signal `recovered` and return.
4. Validate TSS identity: for TSS recovery, the durable `tssPairID` from the store becomes source of truth for `ssi.tssPairID`; for non-TSS, the store must not report TSS state.
5. Rebuild `self.sk`, trace the restored version, and send `recovered`.
6. Synchronously perform a non-accepting `storageInterfaceRegistration()` and surface any registration error.
7. Start the long-lived accepting registration actor, then run `storageServerCore()`.

Recovery shutdown mirrors new-server shutdown, with additional cancellation of `byteSampleRecovery` if it is still valid and a final attempt to set the `recovered` promise.

## State and Persistence Behavior

- Cluster metadata writes are concentrated in system keys: `serverListKeyFor(ssi.id())`, `serverTagKeyFor(ssi.id())`, `serverTagHistoryKeyFor(ssi.id())`, `tagLocalityListKeyFor(dcId)`, and `tssMappingKeys`.
- `replaceInterface()` uses read conflicts over metadata that must be stable across rejoin, and a write conflict on `serverTagConflictKeyFor(newTag)` when assigning a new tag. This protects against duplicate tag ownership and locality-list races.
- Tag history persists old tags using a versionstamped key mutation, and stale history before `self->version.get()` is cleared so future recovery/rejoin logic only sees relevant tag epochs.
- `self->tag`, `self->history`, and `self->allHistory` are volatile mirrors of committed metadata. They are assigned only after the metadata transaction commits.
- `replaceTSSInterface()` persists a TSS's current network interface but derives `self->tag` from the paired storage server. The `tssMappingKeys` entry is suppressed while the TSS is quarantined, which keeps quarantined TSS instances from being selected as live shadows.
- New-server startup persists local storage state in two phases: an initial storage commit after `init()`, then `makeNewStorageServerDurable()` followed by another commit after tag/version decisions are made.
- Recovery uses `restoreDurableState()` as the local source of truth for server identity, version, TSS state, and other durable fields written by earlier chunks. If no durable storage-server marker exists, recovery reports success to the caller but does not run core.
- The local filesystem state under `folder` contains checkpoint, fetched-checkpoint, bulk-dump, and bulk-load subfolders. Startup creates checkpoint directories and clears bulk transfer folders so stale bulk artifacts do not survive process restart.
- RocksDB log cleanup is external to the key-value store state. It matches files in the global log directory by a sanitized folder-derived prefix and deletes them after a knob-defined TTL.
- Shutdown calls `storageServerTerminated()` outside this chunk to decide between `persistentData->dispose()` and `persistentData->close()` for removal/recruitment failure versus reboot-style exits.

## Dependencies and Integration Points

- Commit proxies provide `getStorageServerRejoinInfo`, including the rejoin version, tag, tag history, possible new locality, and possible new tag. Normal server re-registration cannot complete without a live commit proxy set in `ServerDBInfo`.
- System-key encoders from the management/metadata layer define server-list, server-tag, server-tag-history, locality-list, and TSS mapping keys. Correct encoding compatibility is required for commit proxies, data distribution, clients, and TSS routing.
- `ReadYourWritesTransaction` is used for TSS map writes and memory-store removal checks because those paths use higher-level key-backed structures and normal transaction retry handling.
- `Transaction` is used directly in `replaceInterface()` to pin the metadata transaction to the commit proxy's supplied version and to set low-level options such as `FIRST_IN_BATCH`.
- `StorageServerInterface` owns the RPC endpoints registered in `serverList`. `startAcceptingRequests()` and `stopAcceptingRequests()` change advertised readiness before serializing the interface value.
- `StorageServerDisk` or the storage wrapper behind `self.storage` supplies `init()`, `commit()`, `makeNewStorageServerDurable()`, `restoreDurableState()`, `getKeyValueStoreType()`, and shard-awareness state.
- `storageServerCore()` is the main serving actor from earlier chunks; this range ensures it starts only after cluster metadata and local durable state are prepared.
- `ActorCollection` owns background actors such as `rocksdbLogCleaner()` and actors started by the core. Assigning `ActorCollection(false)` cancels them during teardown.
- `SERVER_KNOBS` controls retry delay, RocksDB log cleanup delay, log TTL, and log directory; simulation `buggify()` can force history-related reboot behavior.

## Risks and Edge Cases

- `replaceInterface()` deliberately races `self->db->onChange()` against commit-proxy work. If proxy info changes while a transaction is in flight, the actor may abandon that attempt and loop. Bugs here can leave a storage server with stale interface data or an incorrect tag history.
- The metadata transaction is set to `rep.version`. If `GetStorageServerRejoinInfoReply` is stale or inconsistent with system keys, conflict ranges and transaction retry behavior must catch the mismatch.
- New tag assignment is high risk: duplicate or lost tags can corrupt log routing. The explicit `serverTagConflictKeyFor(newTag)` read/write conflict and `FIRST_IN_BATCH` option are important safety signals.
- The `rep.history.back().first < self->version.get()` cleanup assumes history is ordered in a way where `back()` is the oldest or cleanup boundary is otherwise meaningful. A change to history ordering would make this pruning dangerous.
- TSS recovery depends on the durable store's TSS marker rather than the incoming interface alone. If the durable marker and process recruitment state diverge, the assertions deliberately crash rather than silently register the wrong type of server.
- A TSS whose pair was removed while it was down throws `worker_removed()`. This is correct for cleanup, but the path must ensure the local store is disposed/closed consistently by `storageServerTerminated()`.
- The memory-store recovery race is subtle: if `memoryStoreRecover()` returns before `self.storage.commit()`, recovery treats the server as removed. If it never returns for a valid server, the storage commit should win. Changes to this race can affect in-memory engine restart semantics.
- Startup clears bulk dump/load directories unconditionally with `ignoreError=false`; filesystem permission or stale-file problems become startup failures.
- `rocksdbLogCleaner()` matches log files by substring of a sanitized folder prefix. A too-broad prefix could delete unrelated RocksDB logs; a too-narrow prefix could leak logs. It also assumes file modification time is available and meaningful.
- Both `storageServer()` overloads keep `StorageServer self` on the actor stack. Teardown must halt locks and cancel child actors before returning or rethrowing to avoid child actors using invalid stack memory.
- The new-server path starts accepting requests before `addStorageServer()`, but only after the interface is created for recruitment. This ordering relies on the broader recruitment protocol preventing client traffic before server-list metadata is committed.
- `recruitReply` must be completed exactly once. The catch block sends `recruitment_failed()` only if it has not already sent a success reply.

## Test Signals

- New storage server recruitment should be tested for invalid versus seeded tags, normal versus TSS servers, correct initial version selection, durable marker persistence, and `InitializeStorageReply` contents.
- Reboot recovery tests should cover existing durable servers, stores without durable storage-server state, TSS durable-state recovery, non-TSS assertions, and `recovered` promise completion on success and failure.
- Interface registration tests should cover commit-proxy unavailability, `ServerDBInfo` changes while waiting, conflict retries, new locality creation, new tag assignment, tag-history insertion, tag-history pruning, and buggified reboot from non-empty history.
- TSS registration tests should cover pair tag lookup, missing pair removal, quarantine suppressing `tssMappingKeys`, non-quarantined mapping creation, and assigning the pair tag to `self->tag`.
- Memory-engine recovery tests should cover `canRemoveStorageServer()` returning false several times, transaction retry errors through `onError()`, the race where memory recovery wins and triggers `worker_removed()`, and non-memory stores never taking the removal path.
- Filesystem tests should cover missing checkpoint directories on reboot, clear failures for bulk folders, checkpoint/fetched-checkpoint creation for new stores, and safe handling of folder names used by the RocksDB log cleaner.
- Shutdown tests should inject `worker_removed`, `recruitment_failed`, `please_reboot`, actor cancellation, and generic internal errors to verify close/dispose behavior, core cancellation, actor collection cancellation, lock halt, move-in shard clearing, and error propagation.
- Observability expectations include `StorageServerInitProgress`, `StorageServerInit`, `StorageServerRebootStart`, `SSTimeRestoreDurableState`, `StorageServerReboot`, `StorageServerStartingCore`, `SSTag`, `SSHistory`, `RemoveStorageServerRetrying`, `CleanUpRocksDBLogs`, and `DeleteRocksDBLog` traces.

## Unresolved Cross-Chunk References

- `StorageServer` fields and `self.storage` durable-state semantics are defined earlier in the file and are needed to fully audit `makeNewStorageServerDurable()` and `restoreDurableState()`.
- `storageServerTerminated()` begins immediately before this chunk and controls final `close()` versus `dispose()` behavior.
- `storageServerCore()` and request-serving actors are in earlier chunks; this chunk only shows when core starts and how it is cancelled.
- `addStorageServer()`, `canRemoveStorageServer()`, `serverListValue()`, `decodeServerTagValue()`, and system-key helpers are external integration points whose exact invariants are not shown here.
