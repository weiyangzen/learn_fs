# sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.h

Purpose: This header declares the metadata service's internode synchronization thread and static synchronization helpers.

Important APIs/types: `InternodeSyncer` derives from `PThread`. Public static APIs include `registerNode()`, `updateMetaStatesAndBuddyGroups()`, `syncClients()`, `downloadAndSyncNodes()`, `downloadAndSyncTargetMappings()`, `downloadAndSyncStoragePools()`, `downloadAndSyncTargetStatesAndBuddyGroups()`, `downloadAndSyncClients()`, capacity-pool updates, exceeded-quota downloads, and sync-result logging. Instance methods expose force flags for pools, target states, capacity publishing, storage pools, and network checks; local consistency state accessors; and resync-in-progress flags.

Control flow contract: `run()` delegates to `syncLoop()`. Atomic force flags allow other components and message handlers to request refresh work without blocking. `nodeConsistencyStateMutex` protects consistency state transitions, while `buddyResyncInProgress` uses an atomic wrapper.

State and persistence behavior: The class owns no persistent files directly but orchestrates updates to persistent-adjacent runtime state: quota stores, state stores, node stores, session cleanup, cache sweeping, and capacity publication based on storage stats.

Dependencies/integration: It includes node stores, capacity pool messages, quota data, `NodeOfflineWait`, and threading primitives. `App` owns one syncer and exposes it for force-update calls.

Risks and test signals: The broad static API makes it callable during both startup and steady state, including before an instance exists. Callers must account for that split. Tests should focus on state transition decisions, forced refresh handling, and session cleanup behavior.
