## sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.cpp

Purpose: Implements the storage daemon's periodic synchronization with mgmtd and peers: registration, node/mapping/pool/state downloads, target-state publication, capacity publication, quota-list sync, network change detection, and client-session cleanup.

Important APIs/types/functions: `syncLoop()` schedules repeated work. `updateTargetStatesAndBuddyGroups()` downloads states/groups, marks resync jobs when a target was offline, syncs state store, asks `StorageTargets::decideResync()`, publishes local changes, and checks buddy resync needs. `publishTargetCapacities()`, `publishTargetState()`, `publishLocalTargetStateChanges()`, and `publishTargetStateChanges()` send state/capacity messages. Static helpers register nodes/targets, request buddy target states, download nodes/mappings/groups/pools/states, sync client sessions, and download exceeded quota lists.

Control flow: The thread wakes every three seconds and evaluates elapsed timers/force flags. State update publication retries up to ten times because mgmtd state may change between download and compare-and-set. `requestBuddyTargetStates()` is timer-requeued every 30 seconds and updates last-buddy-communication timestamps only when the buddy target reports `GOOD` and local state does not already need resync.

State and persistence: Maintains force flags under mutexes. Updates in-memory node stores, target mapper, mirror buddy mappers, target state store, storage pool store, exceeded quota stores, and session store. Indirectly updates storage target last-buddy-comm state and resync-needed state through `StorageTargets`.

Dependencies and integration: Central bridge to mgmtd via `MessagingTk`, `NodesTk`, heartbeat/map/target-state/capacity/quota messages, `Program::getApp()`, `StorageTargets`, `BuddyResyncer`, `DatagramListener`, and all node stores.

Risks and test signals: In `downloadAllExceededQuotaLists(uint16_t)`, the group inode quota request passes `QuotaDataType_USER` but updates `QuotaDataType_GROUP`, which looks like a copy/paste bug. `downloadAndSyncStoragePools()` returns true even when download fails. Network comparison uses `std::equal` without first checking lengths, which risks incorrect behavior if NIC list sizes differ. Tests should cover mgmtd conflict retries, offline target marking during resync, quota type correctness, storage-pool download failure, NIC add/remove, and state-publication skipping during offline timeout.
