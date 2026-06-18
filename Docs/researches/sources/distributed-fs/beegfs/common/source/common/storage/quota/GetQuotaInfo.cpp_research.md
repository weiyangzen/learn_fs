<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp

Purpose: Orchestrates parallel quota limit and quota usage requests, collecting responses into target-indexed maps.

Important APIs/functions: `requestQuotaLimitsAndCollectResponses` sends work to the management node. `requestQuotaDataAndCollectResponses` dispatches storage-node work according to target selection mode. `getMaxMessageCount` computes the number of ID-range messages. `calculateQuotaSums` merges per-node quota maps for all-targets mode.

Control flow/state/persistence: The code creates `GetQuotaInfoWork` items, pushes them to `MultiWorkQueue`, waits on `SynchronizedCounter`, and validates per-work result target IDs. Per-target maps are protected by per-map `Mutex` instances. In all-targets-one-request mode it merges node maps into an aggregate all-target entry. It persists nothing directly.

Dependencies/integration: Integrates `NodeStoreServers`, `TargetMapper`, `StoragePoolStore`, `QuotaInodeSupport`, and quota response messages. It is a central quota collection coordinator for ctl/management/storage workflows.

Risks/test signals: `nodeResults` sizing and `numWorks` indexing must match the number of enqueued works, especially with storage pool filters. Tests should cover all target-selection modes, offline targets, missing mapper entries, empty pools, multi-message ID ranges, and merge correctness for duplicate IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp -->
