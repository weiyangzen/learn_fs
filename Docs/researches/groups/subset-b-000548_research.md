# Research: subset-b-000548

Grouped research for BeeGFS common storage, system, threading, and toolkit files. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h

Purpose: Defines serializable resync progress/status records for buddy mirror jobs. `BuddyResyncJobState` captures lifecycle states from not started through success, interruption, failure, and completed-with-errors.

Important APIs/types: `BuddyResyncJobStatistics` stores state/start/end timestamps. `StorageBuddyResyncJobStatistics` adds discovered, matched, synced, and error counters for files and directories. `MetaBuddyResyncJobStatistics` adds metadata-specific counters for directory gather/sync, file sync, sessions, modification objects, and errors. Each class exposes a static `serialize` function for BeeGFS serdes integration and simple getters.

Control flow/state/persistence: This header has no active control flow beyond construction and serialization. State is value-owned and persisted only when callers serialize these records into messages, stores, or status files.

Dependencies/integration: Depends on `common/Common.h` and BeeGFS serialization helpers. Integrated with storage and metadata buddy resync reporting paths and any management/ctl message that transports job statistics.

Risks/test signals: Wire compatibility depends on field order and enum integer values. Tests should round-trip default and populated storage/meta statistics, verify old/new readers agree on ordering, and cover all terminal states plus error counter combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h

Purpose: Provides a templated producer/consumer queue for metadata or storage resync candidates, split into separate directory and file queues.

Important APIs/types: `SyncCandidateStore<SyncCandidateDir, SyncCandidateFile>` exposes overloaded `add` and `fetch` for file and directory candidates, `waitForFiles`, `waitForFilesWithResult`, `waitForDirs`, emptiness/size accessors, `clear`, and `notifyFilesAdded`. Internally it uses `Mutex` and `Condition` wrappers and tracks `numQueuedFiles`/`numQueuedDirs` with a `MAX_QUEUE_SIZE` of 50000.

Control flow/state/persistence: Producers block on queue-size limits until consumers signal fetched items, unless the caller `PThread` has a self-terminate request. Consumers wait with timed condition waits and return default-constructed candidates on shutdown. No data is persisted; all state is in memory.

Dependencies/integration: Used by buddy resync workers to coordinate gather/sync stages. Integrates with BeeGFS thread termination conventions through `PThread::getSelfTerminate`.

Risks/test signals: `waitForDirs(0)` uses a single wait rather than a spurious-wakeup loop, unlike file waits. Tests should stress multiple producers/consumers, shutdown while queues are full/empty, clear during idle periods, and timeout result correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/SyncCandidateStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp

Purpose: Implements thread-safe lookup, insertion, and removal of per-target exceeded-quota stores.

Important APIs/functions: `get(targetId)` returns a shared `ExceededQuotaStorePtr` or null. `add(targetId, ignoreExisting)` creates or returns a store depending on existing state and policy. `remove(targetId)` erases a target entry.

Control flow/state/persistence: A `RWLockGuard` protects the backing `std::map<uint16_t, ExceededQuotaStorePtr>`. Reads acquire a read lock; add/remove acquire a write lock. The class is an in-memory registry only and does not write target quota state to disk.

Dependencies/integration: Depends on `ExceededQuotaPerTarget.h`, `ExceededQuotaStore`, and BeeGFS `RWLockGuard`. Used by quota enforcement code that needs target-scoped exceeded ID sets.

Risks/test signals: The `ignoreExisting` flag controls whether duplicate add returns the existing store or null, so caller expectations should be tested. Concurrency tests should cover parallel add/get/remove and shared pointer lifetime after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h

Purpose: Declares a target-id indexed container for exceeded quota state.

Important APIs/types: `ExceededQuotaPerTarget` exposes `get`, `add`, and `remove`. Private state is an `RWLock` plus `std::map<uint16_t, ExceededQuotaStorePtr> exceededQuotaStores`.

Control flow/state/persistence: The header defines the ownership model: stores are shared pointers, allowing returned stores to outlive map membership. Persistence is delegated elsewhere; this object is a synchronization and registry layer.

Dependencies/integration: Includes `ExceededQuotaStore.h` and BeeGFS threading primitives. It is an integration point between target selection and quota enforcement checks.

Risks/test signals: The map key is a 16-bit target ID; invalid target handling is caller-owned. Tests should validate null returns, duplicate handling, removal semantics, and ABI expectations around `const ExceededQuotaStorePtr` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp

Purpose: Maintains in-memory sets of user/group IDs that exceed size or inode quotas.

Important APIs/functions: `updateExceededQuota` replaces one of four sets based on `QuotaDataType` and `QuotaLimitType`. `isQuotaExceeded(uid,gid)` checks size and inode sets together. The overload with `QuotaLimitType` checks only one limit family. `getExceededQuota` copies sets to a list, and `someQuotaExceeded` reports whether any set is non-empty.

Control flow/state/persistence: Public methods take `SafeRWLock` read/write guards around `rwLockExceededLists`. Updating clears and repopulates a `UIntSet` from a caller-provided `UIntList`. Checking prioritizes user matches before group matches and returns specific `QuotaExceededErrorType` values.

Dependencies/integration: Depends on quota enums from `QuotaData.h`, BeeGFS list/set aliases, and `SafeRWLock`. It feeds quota enforcement decisions in storage/session paths.

Risks/test signals: Return precedence matters when both user and group exceed limits. Tests should cover all four sets, empty inputs, duplicated IDs, concurrent readers during updates, and `someQuotaExceeded` after clear/update cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h

Purpose: Declares the exceeded-quota ID set container used by quota enforcement.

Important APIs/types: `ExceededQuotaStore` exposes update, query, copy-out, and non-empty checks. Private state has four `UIntSet` members: user/group size exceeded and user/group inode exceeded. `ExceededQuotaStorePtr` is a shared pointer alias.

Control flow/state/persistence: Thread-safety is implemented in the `.cpp` with an `RWLock`. State is memory-only and expected to be refreshed from quota scans or management updates.

Dependencies/integration: Includes `QuotaData.h`, `RWLock`, and common BeeGFS collection aliases. It is often nested under `ExceededQuotaPerTarget`.

Risks/test signals: The header exposes pointer-based inputs (`UIntList*`), so null-pointer behavior is not guarded by the API. Tests should exercise all enum branches and ensure invalid enum values do not silently corrupt unrelated sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h

Purpose: Defines the request configuration structure for quota information retrieval.

Important APIs/types: `GetQuotaInfoConfig` extends `QuotaConfig` with `cfgTargetSelection`, `cfgTargetNumID`, and `cfgIDRangeStart`, selecting whether data is requested for all targets in one request, per target, or for a single target/range.

Control flow/state/persistence: This is a plain configuration value passed to worker/message code. It has no persistence or locking behavior.

Dependencies/integration: Includes `QuotaConfig.h` and `TargetSelection.h`. It is consumed by `GetQuotaInfo`, `GetQuotaInfoWork`, and quota request messages.

Risks/test signals: Defaults select all targets in one request, target ID 0, and ID range 0. Tests should verify callers override defaults for single-target and per-target modes and that storage pool filtering is only used with compatible target-selection modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp

Purpose: Orchestrates parallel quota limit and quota usage requests, collecting responses into target-indexed maps.

Important APIs/functions: `requestQuotaLimitsAndCollectResponses` sends work to the management node. `requestQuotaDataAndCollectResponses` dispatches storage-node work according to target selection mode. `getMaxMessageCount` computes the number of ID-range messages. `calculateQuotaSums` merges per-node quota maps for all-targets mode.

Control flow/state/persistence: The code creates `GetQuotaInfoWork` items, pushes them to `MultiWorkQueue`, waits on `SynchronizedCounter`, and validates per-work result target IDs. Per-target maps are protected by per-map `Mutex` instances. In all-targets-one-request mode it merges node maps into an aggregate all-target entry. It persists nothing directly.

Dependencies/integration: Integrates `NodeStoreServers`, `TargetMapper`, `StoragePoolStore`, `QuotaInodeSupport`, and quota response messages. It is a central quota collection coordinator for ctl/management/storage workflows.

Risks/test signals: `nodeResults` sizing and `numWorks` indexing must match the number of enqueued works, especially with storage pool filters. Tests should cover all target-selection modes, offline targets, missing mapper entries, empty pools, multi-message ID ranges, and merge correctness for duplicate IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h

Purpose: Declares the quota collection coordinator class.

Important APIs/types: `GetQuotaInfo` owns a `GetQuotaInfoConfig` and exposes `requestQuotaLimitsAndCollectResponses` and `requestQuotaDataAndCollectResponses`. Protected helpers are `getMaxMessageCount` and `calculateQuotaSums`.

Control flow/state/persistence: Instances are lightweight and store only request configuration. Actual asynchronous flow is in the implementation and delegated work items.

Dependencies/integration: Pulls in node stores, work queues, target mappers, quota data maps, and quota config. It provides a shared API for components that need current quota limits or usage.

Risks/test signals: Because the class stores config by value, tests should verify later caller-side mutations do not affect an existing object. Public methods accept many raw pointers; nullability expectations should be covered in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp

Purpose: Implements stream rendering for quota block-device filesystem types.

Important APIs/functions: `operator<<(std::ostream&, QuotaBlockDeviceFsType)` emits strings for `QuotaBlockDeviceFsType_EXTX`, `QuotaBlockDeviceFsType_XFS`, `QuotaBlockDeviceFsType_ZFS`, and a fallback for unknown values.

Control flow/state/persistence: The function is a switch-style formatter with no state or persistence.

Dependencies/integration: Includes `Quota.h`; output is used in logs, diagnostics, and command-line reporting.

Risks/test signals: String names are user-visible and may be parsed by scripts. Tests should verify all known enum values and unknown-value fallback formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h

Purpose: Defines filesystem and inode-support enums for quota features.

Important APIs/types: `QuotaBlockDeviceFsType` enumerates unknown, ext-family, XFS, and ZFS filesystem types. `QuotaInodeSupport` records whether inode quota accounting is unknown, supported, or unsupported. The stream operator is declared here.

Control flow/state/persistence: Header-only enum definitions with no active state. Values may cross module and message boundaries.

Dependencies/integration: Includes `<ostream>`. Used by quota detection, logging, and configuration/reporting paths.

Risks/test signals: Enum numeric stability matters if serialized or stored. Tests should cover formatting and behavior when callers receive unknown filesystem or inode support status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/Quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h

Purpose: Defines common quota request configuration shared by derived quota retrieval configs.

Important APIs/types: `QuotaConfig` stores quota data type (`cfgType`), limit type (`cfgLimitType`), list-selection mode (`cfgUseAll`), and an ID list pointer (`cfgIDList`). Defaults select user data, size+inode limits, all IDs, and no explicit list.

Control flow/state/persistence: Plain data structure. It does not own the `UIntList*`, so list lifetime is managed by callers.

Dependencies/integration: Includes `QuotaData.h`. Extended by `GetQuotaInfoConfig` and used by quota messages/workers.

Risks/test signals: Pointer ownership and null handling are the main hazards. Tests should cover explicit ID list mode, all-ID mode, user/group modes, and derived config copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp

Purpose: Implements serialization-file persistence and human-readable formatting for quota maps/lists.

Important APIs/functions: `loadQuotaDataMapForTargetFromFile` reads a serialized `QuotaDataMapForTarget`. `saveQuotaDataMapForTargetToFile` creates parent directories and writes serialized map data. `quotaDataMapToString`, `quotaDataMapForTargetToString`, and `quotaDataListToString` format usage values.

Control flow/state/persistence: Loading opens, stats, allocates a full-file buffer, reads once, and deserializes. Saving serializes into a new buffer then creates/truncates/writes the target file. There is no temporary-file atomic rename, so partial writes or crashes can leave corrupt state.

Dependencies/integration: Uses BeeGFS `Serialization`, `StorageTk`, `Path`, logging, POSIX `open/read/write/stat`, and quota collection aliases.

Risks/test signals: Tests should cover missing/empty/corrupt files, partial read/write behavior, large maps, directory creation failures, serialization round trips, and debug counter paths. Persistence tests should note truncate-write crash risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h

Purpose: Defines quota usage data, quota maps, quota enums, and serialization traits.

Important APIs/types: Aliases include `QuotaDataMap`, `QuotaDataMapForTarget`, and `QuotaDataList`. Enums cover data type, limit type, and exceeded-error type. `SessionQuotaInfo` stores per-session quota counters. `QuotaData` stores ID, size, inode count, type, and validity with merge helpers, list insertion helper, string conversion helpers, and static persistence/formatting methods.

Control flow/state/persistence: `QuotaData::serialize` writes ID, size, inodes, type, and validity. `mergeQuotaDataCounter` only merges compatible valid records; `forceMergeQuotaDataCounter` unconditionally increments counters. Map/list serialization length traits tune wire/file encoding.

Dependencies/integration: Used by quota messages, storage scans, management limits, exceeded-quota stores, and persistence helpers.

Risks/test signals: Type/validity gates must be tested because invalid quota data can poison aggregate results. Verify enum string helpers, unique list insertion, overflow behavior for counter accumulation, and map serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp

Purpose: Persists default quota limit values for users and groups.

Important APIs/functions: `loadFromFile` reads and deserializes four default limit counters. `saveToFile` creates parent paths and writes serialized limits. `clearLimits` zeros all defaults and unlinks the store file.

Control flow/state/persistence: Loading uses `open`, `fstat`, `malloc`, single `read`, and `deserialize`. Saving uses `open(O_CREAT|O_TRUNC|O_WRONLY)`, `malloc(serialLen())`, `serialize`, and single `write`. Like `QuotaData`, persistence is truncate-write rather than atomic rename.

Dependencies/integration: Depends on `StorageTk`, `Path`, BeeGFS logger macros, and POSIX file APIs. Integrated with quota configuration state on management/storage services.

Risks/test signals: Tests should cover absent file, corrupt serialized contents, parent path creation, write failure, unlink failure, and clear/reload behavior. Crash during save can leave an empty or partial default-limits file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h

Purpose: Declares default quota limit storage for user/group inode and size limits.

Important APIs/types: `QuotaDefaultLimits` has getters, `updateUserLimits`, `updateGroupLimits`, `updateLimits`, `clearLimits`, file load/save methods, and serialization helpers. Private state includes `storePath` plus four `uint64_t` limit values.

Control flow/state/persistence: The header defines a value object with an associated persistence path. `serialize` writes user inode/size then group inode/size; `deserialize` requires the same order.

Dependencies/integration: Includes BeeGFS serialization helpers and quota logging dependencies in the implementation. Used wherever default quota policies are managed.

Risks/test signals: Field order is the persistent file format. Tests should verify updates preserve unrelated limits, serialization round trips, empty path failure behavior, and limits of zero as "unset/no default" semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp

Purpose: Implements mutable target update and equality comparison for buddy-mirror stripe patterns.

Important APIs/functions: `updateStripeTargetIDs` validates that the incoming pattern is also buddy mirror, then copies its stripe target vector. `patternEquals` compares target IDs and default target count after casting to `BuddyMirrorPattern`.

Control flow/state/persistence: No persistence here; it mutates in-memory pattern target IDs for special repair/fsck-style flows.

Dependencies/integration: Depends on `BuddyMirrorPattern.h` and the virtual `StripePattern` API. Used by metadata and fsck code that manipulates stripe layouts.

Risks/test signals: Update rejects mismatched pattern types but does not validate minimum target count. Tests should cover mismatched type, equal/different target vectors, default target count differences, and repair paths that rely on mutable target IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h

Purpose: Defines the stripe pattern for buddy mirrored file placement.

Important APIs/types: `BuddyMirrorPattern` derives from `StripePattern`, stores `stripeTargetIDs` and `defaultNumTargets`, serializes default count plus target IDs, and implements target access, mutable update, clone, min/default target counts, and assigned target count.

Control flow/state/persistence: The pattern is serialized as a `StripePattern` header plus buddy content. It has no separate disk behavior, but serialized patterns are part of inode/message metadata.

Dependencies/integration: Integrates with `StripePattern`, `StoragePoolStore`, serialization, and fsck/metadata layout code. Buddy mirror target IDs represent mirror group IDs rather than direct storage targets.

Risks/test signals: Clone must preserve storage pool ID and default count expectations. Tests should cover serialization with and without storage pool IDs, target indexing through the base class, and update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/BuddyMirrorPattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp

Purpose: Implements equality for chunk file dynamic metadata wrappers.

Important APIs/functions: `ChunkFileInfo::operator==` compares storage version and dynamic attributes.

Control flow/state/persistence: No control flow beyond value comparison. Persistence is handled by serialization in the header.

Dependencies/integration: Depends on `ChunkFileInfo.h` and `DynamicFileAttribs` equality. Used by metadata/storage update logic to detect changed chunk state.

Risks/test signals: Equality must stay aligned with serialization fields. Tests should compare all fields, especially storage version changes with identical dynamic attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h

Purpose: Represents one chunk file's storage version and dynamic attributes.

Important APIs/types: `ChunkFileInfo` stores `storageVersion` and `DynamicFileAttribs`. It serializes both, exposes file size, mtime, atime, complete chunk counts, block count, raw attribute access, and `updateDynAttribs`.

Control flow/state/persistence: `updateDynAttribs` selectively applies newer/larger dynamic attributes and reports whether state changed. Serialization makes this object suitable for metadata and network transport.

Dependencies/integration: Depends on `DynamicFileAttribs`, BeeGFS serialization, and chunk metadata consumers that aggregate file attributes across targets.

Risks/test signals: Attribute update semantics affect file-size and timestamp reconciliation. Tests should cover older/equal/newer storage versions, zero/negative file sizes, chunk-count math for incomplete chunks, and equality round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/ChunkFileInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h

Purpose: Defines dynamic file attributes reported by storage targets for chunked files.

Important APIs/types: `DynamicFileAttribs` stores file size, allocated blocks, modification time, last access time, storage version, and complete chunk count. It has a static serdes method and vector typedefs.

Control flow/state/persistence: This is a serialized value object. It is persisted or sent as part of higher-level metadata structures such as `ChunkFileInfo`.

Dependencies/integration: Used by stripe/chunk metadata aggregation, stat refresh, and fsck/repair code.

Risks/test signals: Field order and signedness are important, particularly `int64_t` file size/times and `uint64_t` blocks/version. Tests should round-trip edge values and verify consumers handle unset or stale versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/DynamicFileAttribs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp

Purpose: Implements mutable target update and equality comparison for RAID0 stripe patterns.

Important APIs/functions: `updateStripeTargetIDs` accepts only another RAID0 pattern and copies its stripe target vector. `patternEquals` compares target IDs and default target count.

Control flow/state/persistence: The implementation only mutates/comparisons in memory. Serialized representation is defined in the header and base pattern logic.

Dependencies/integration: Depends on `Raid0Pattern.h` and base `StripePattern`. Used for normal non-mirrored BeeGFS file striping.

Risks/test signals: Updates are intended for special cases because stripe targets are normally immutable. Tests should cover pattern type mismatch, vector differences, default target count differences, and cloned/serialized equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h

Purpose: Defines the basic BeeGFS RAID0 stripe layout.

Important APIs/types: `Raid0Pattern` derives from `StripePattern`, stores `stripeTargetIDs` and `defaultNumTargets`, serializes default count plus target list, exposes target accessors, update, clone, min target count, and assigned target count.

Control flow/state/persistence: Base-class serialization writes the common header, then RAID0-specific target content. Persistent/wire compatibility depends on this content order.

Dependencies/integration: Integrates with metadata inode patterns, file creation target selection, fsck conversion helpers, and storage pool assignment.

Risks/test signals: Minimum target count is one, but empty target vectors can still be constructed by bad callers. Tests should cover chunk-size defaulting, storage pool ID preservation, target indexing, and empty-vector handling in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid0Pattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp

Purpose: Implements mutable stripe target update and equality comparison for legacy RAID10 patterns.

Important APIs/functions: `updateStripeTargetIDs` requires another RAID10 pattern and copies only stripe target IDs. `patternEquals` compares stripe IDs, mirror IDs, and default target count.

Control flow/state/persistence: Runtime state mutation is limited to target-vector updates. Mirror target IDs remain separately tracked and are compared for equality.

Dependencies/integration: Depends on `Raid10Pattern.h` and `StripePattern`. RAID10 appears in fsck conversion and old pattern compatibility paths.

Risks/test signals: Updating only stripe IDs but not mirror IDs can produce inconsistent layouts if misused. Tests should cover equal-length stripe/mirror vectors, mismatches, update semantics, and clone/equality behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h

Purpose: Defines a stripe pattern with separate primary stripe and mirror target vectors.

Important APIs/types: `Raid10Pattern` derives from `StripePattern`, stores `stripeTargetIDs`, `mirrorTargetIDs`, and `defaultNumTargets`. It serializes default count, stripe IDs, and mirror IDs. It exposes mirror target accessors in addition to stripe accessors.

Control flow/state/persistence: Constructors perform debug-only vector length sanity checks. Serialized content order and target-vector length pairing define the persisted layout.

Dependencies/integration: Used for older RAID10-style mirror layouts and fsck conversions. Depends on serialization, storage pools, and base striping helpers.

Risks/test signals: The public `clone(const UInt16Vector&)` currently returns a copy and ignores its argument, which is suspicious. Tests should assert clone semantics, vector length mismatch handling, serialization, and mirror target lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/Raid10Pattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp

Purpose: Implements polymorphic stripe-pattern deserialization, type naming, and common equality checks.

Important APIs/functions: `StripePattern::deserialize` reads `StripePatternHeader`, creates `Raid0Pattern`, `Raid10Pattern`, or `BuddyMirrorPattern`, deserializes content, and marks the deserializer bad on invalid type/chunk size/content. `getPatternTypeStr` formats pattern types. `stripePatternEquals` compares type, chunk size, storage pool ID, then delegates derived content equality.

Control flow/state/persistence: Deserialization is a factory with strict validation and cleanup on failure. It supports old/no-pool-id payloads through header flags.

Dependencies/integration: Includes all derived pattern classes, serialization, logging, and `StringTk`. Used whenever patterns are loaded from metadata or messages.

Risks/test signals: Compatibility with pre-pool-id formats is central. Tests should cover invalid type, zero chunk size, malformed content, no-pool flag, storage pool ID comparison, and all derived type round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h

Purpose: Defines the abstract base class and serialized header for BeeGFS stripe patterns.

Important APIs/types: `StripePatternType`, `StripePatternHeader`, and `StripePattern` provide chunk size, storage pool ID, polymorphic serialization, target indexing by file offset, clone/equality hooks, and target-vector access/update APIs. `HasNoPoolFlag` encodes no-pool compatibility in high bits of the serialized type.

Control flow/state/persistence: Serialization writes a placeholder length, header, derived content, then backfills length. Deserialization is implemented in the `.cpp`. `getChunkStart` uses bit arithmetic and assumes chunk size is a power of two.

Dependencies/integration: Central to inode metadata, file layout, fsck, storage pool assignment, and network messages that move file layout.

Risks/test signals: Chunk size validity and non-empty target vectors are caller-critical. Tests should verify length backfill, v6/v7 storage pool compatibility, power-of-two chunk sizes, target index math, and equality across derived types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/striping/StripePattern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.cpp -->
## sources/distributed-fs/beegfs/common/source/common/system/System.cpp

Purpose: Implements Linux/system utility functions used across BeeGFS common code.

Important APIs/functions: Provides errno string formatting, hostname, CPU/NUMA discovery and binding, thread ID, FD limit raising, memory info, mountpoint device lookup, user/group name-ID mapping, user/group enumeration, and filesystem UID/GID changes.

Control flow/state/persistence: Most functions query `/proc`, `/sys`, libc, or kernel syscalls. Static `strerrorMutex` serializes `strerror`. Static saved effective UID/GID are captured at process startup for later FS-ID elevation. NUMA error logging suppresses repeated warnings.

Dependencies/integration: Uses `StorageTk`, `StringTk`, `LogContext`, POSIX APIs, `/proc/self/mountinfo`, `/proc/meminfo`, passwd/group databases, and Linux `setfsuid`/`setfsgid`.

Risks/test signals: Several passwd/group functions are explicitly non-reentrant. `getDevicePathFromMountpoint` depends on mountinfo parsing. Tests should cover NUMA absence, mountpoint lookup failures, FD limits, memory parsing, privilege drop/elevation, and concurrent error-string use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.h -->
## sources/distributed-fs/beegfs/common/source/common/system/System.h

Purpose: Declares the common system utility interface.

Important APIs/types: `System` exposes static helpers for errors, host/system topology, memory, device/machine UUIDs, user/group lookup, process/thread IDs, FD limits, and filesystem identity changes. Private static state stores a mutex for error formatting and saved effective IDs.

Control flow/state/persistence: This is a stateless static utility facade except for saved process credentials and the errno mutex.

Dependencies/integration: Includes common type aliases, invalid-config exceptions, CPU sets, pthread, and time/syscall headers. `UUID.h` provides definitions for UUID-specific methods.

Risks/test signals: The header exposes broad platform-specific behavior, so portability is Linux-bound. Tests should mock or isolate `/proc`, `/sys`, passwd/group DB, and privilege-sensitive helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/System.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/UUID.h -->
## sources/distributed-fs/beegfs/common/source/common/system/UUID.h

Purpose: Provides header-only UUID helpers without forcing all common-library users to link libblkid.

Important APIs/functions: `UUID::getFsUUID` resolves the device for a mountpoint and probes its filesystem UUID. `UUID::getPartUUID` scans blkid cache entries for a preferred mountpoint UUID/PARTUUID with fallback rules. `UUID::getMachineUUID` reads `/sys/class/dmi/id/product_uuid` and falls back to partition UUID.

Control flow/state/persistence: Functions query system files/devices and blkid cache; they do not persist state. `getFsUUID` throws `InvalidConfigException`; `getPartUUID` returns `FhgfsOpsErr` plus text; `getMachineUUID` logs warnings and returns empty string on failure.

Dependencies/integration: Uses `System::getDevicePathFromMountpoint`, libblkid, `StorageErrors`, and logging. Used by service startup/storage identity checks.

Risks/test signals: Requires device permissions for full probing, and cache order influences fallback identity. Tests should cover inaccessible devices, missing DMI UUID, non-36-character UUIDs, preferred mountpoint selection, and blkid cache failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/system/UUID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h

Purpose: Wraps GCC legacy atomic builtins for simple atomic scalar values.

Important APIs/types: `Atomic<T>` and aliases for size, ssize, uint32, uint64, int16, and int64 expose `set`, `setZero`, `increase`, `decrease`, `compareAndSet`, and `read`.

Control flow/state/persistence: State is a single volatile-ish scalar updated with `__sync_*` full-barrier builtins. `read` uses fetch-add-zero for atomic read behavior.

Dependencies/integration: Used by threading and counters, notably `PThread` self-termination fast path. It avoids `<atomic>` and reflects older BeeGFS portability choices.

Risks/test signals: `increase`/`decrease` return the old value because `__sync_fetch_and_add/sub` is used. Tests should document return semantics, compare-and-set ordering, concurrent increments, and type width assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Atomics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h

Purpose: RAII wrapper around `pthread_barrier_t`.

Important APIs/types: `Barrier` initializes a pthread barrier for a fixed count, destroys it in the destructor, and exposes `wait()`.

Control flow/state/persistence: Constructor throws `PThreadException` on initialization failure. `wait` delegates to `pthread_barrier_wait`; no state is persisted.

Dependencies/integration: Depends on `PThreadException` and `System::getErrString`. Used by thread coordination tests or components needing phase synchronization.

Risks/test signals: Destructor does not report destroy errors. Tests should cover successful multi-thread waits, invalid count behavior, and exception propagation on init failure where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp

Purpose: Implements static condition-variable attributes and safe clock validation.

Important APIs/functions: `initStaticCondAttr` initializes a global `pthread_condattr_t` and sets `SAFE_CLOCK_ID`. `destroyStaticCondAttr` destroys it. `testClockID` validates that the selected monotonic/realtime clock works and advances.

Control flow/state/persistence: Static initialization configures all `Condition` instances to use the safe clock. Errors throw `ConditionException`, `MutexException`, or `TimeException`. No persistence exists.

Dependencies/integration: Uses `System::getErrString`, `Time`, BeeGFS exceptions, and pthread condition attributes. `Condition.h` depends on this static attr for constructor behavior.

Risks/test signals: Process initialization order matters. Tests should cover attr initialization/destroy, clock failures through mocks, and timed wait consistency with the configured clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Condition.h

Purpose: Wraps `pthread_cond_t` with BeeGFS mutex and timeout conventions.

Important APIs/types: `Condition` constructs with static `condAttr`, exposes `timedwait`, `signal`, `broadcast`, and indefinite `wait`. Static helpers initialize/destroy/test the condition clock.

Control flow/state/persistence: `timedwait` builds an absolute timeout using `Time::getClockVal` and treats `ETIMEDOUT` as non-exceptional. Other pthread errors throw `MutexException`. State is only the pthread condition variable.

Dependencies/integration: Used by `PThread`, `SyncCandidateStore`, `AcknowledgmentStore`, and many wait/notify paths with the custom `Mutex` wrapper.

Risks/test signals: Callers must hold the matching mutex. Tests should check timed timeout, signal/broadcast wakeups, spurious-wakeup caller loops, and behavior before static attr initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h

Purpose: Defines the named exception type for condition-variable failures.

Important APIs/types: Uses the `DECLARE_NAMEDEXCEPTION` macro to derive `ConditionException` from `SynchronizationException`.

Control flow/state/persistence: No runtime logic or state beyond exception construction and `what()` inherited from `NamedException`.

Dependencies/integration: Includes `SynchronizationException.h`. Thrown by `Condition.cpp` initialization paths.

Risks/test signals: Tests should ensure the exception name/message are preserved through catch by base type and that condition initialization failures map to this type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h

Purpose: Provides a small RAII wrapper for accessing a value protected by `std::mutex`.

Important APIs/types: `LockedView<T>` owns a `std::unique_lock<std::mutex>` and a raw pointer to `T`, exposing pointer-like operators and access to the unique lock. `MutexProtected<T>` stores a value and mutex and returns `lockedView()`.

Control flow/state/persistence: Lock acquisition happens in the `LockedView` constructor and is released by `unique_lock` destruction. No persistence.

Dependencies/integration: Uses standard C++ mutex types, distinct from BeeGFS pthread `Mutex`. Useful for new C++ code needing scoped access to state.

Risks/test signals: `LockedView` stores a raw pointer to state owned by `MutexProtected`; views must not outlive the owner. Tests should cover move behavior, const/non-const access expectations, and mutation under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h

Purpose: Wraps `pthread_mutex_t` for BeeGFS synchronization.

Important APIs/types: `Mutex` initializes/destroys a pthread mutex and exposes `lock`, `tryLock`, `unlock`, and raw `getMutex` for condition waits.

Control flow/state/persistence: `lock` throws `MutexException` on pthread errors; `tryLock` returns false on busy/error; `unlock` delegates directly. The object is non-persistent and owns its pthread mutex.

Dependencies/integration: Used by `Condition`, quota stores, candidate queues, ack stores, and many older BeeGFS components.

Risks/test signals: Copying is not explicitly deleted here, so accidental copies would duplicate pthread state incorrectly if allowed by compiler rules. Tests should cover lock/unlock, try-lock contention, and error handling in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h

Purpose: Defines the named exception type for mutex failures.

Important APIs/types: `MutexException` is declared with `DECLARE_NAMEDEXCEPTION` and derives from `SynchronizationException`.

Control flow/state/persistence: No logic beyond exception construction inherited from the macro-generated type.

Dependencies/integration: Included by mutex/condition/RW-lock wrappers when pthread errors need to become BeeGFS exceptions.

Risks/test signals: Test catch behavior through `SynchronizationException` and message preservation for representative pthread error strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp

Purpose: Implements BeeGFS thread lifecycle helpers, signal handling, priority shifting, and NUMA-aware start.

Important APIs/functions: Static TLS keys/destructors store thread name and app. `blockInterruptSignals`/`unblockInterruptSignals` manage signal masks. `registerSignalHandler` installs crash/termination handlers. `signalHandler` turns fatal signals into `SignalException` or exits. `setPriorityShift`, `applyPriorityShift`, `resetSelfTerminate`, and `startOnNumaNode` implement runtime controls.

Control flow/state/persistence: `startOnNumaNode` configures pthread affinity attributes before `pthread_create`. Priority shift maps to `nice`. Signal handling is process-global; app/name state is thread-local.

Dependencies/integration: Integrates with `AbstractApp`, `System`, logging/string helpers, Linux signals, sched affinity, and pthread APIs. Many BeeGFS worker classes derive from `PThread`.

Risks/test signals: Signal handlers throwing exceptions is delicate and context-sensitive. Tests should cover start/join, TLS app/name propagation, self-terminate reset, NUMA fallback, priority errors, and fake-thread initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThread.h

Purpose: Declares the BeeGFS base class for pthread-backed worker threads.

Important APIs/types: `PThread` exposes `start`, `startOnNumaNode`, `startInCurrentThread`, `join`, `timedjoin`, `terminate`, `kill`, `selfTerminate`, self-terminate waits, sleep/yield helpers, TLS accessors for current thread/app/name, and a pure virtual `run`.

Control flow/state/persistence: `runStatic` installs TLS name/app, kernel thread name, applies priority shift, then calls `run`. Self-termination uses both an atomic fast flag and a mutex/condition pair for waiters. No persistent state.

Dependencies/integration: Foundation for long-running BeeGFS components and worker queues. Uses `Condition`, `Mutex`, `Atomics`, `System`, signal APIs, and pthread attributes.

Risks/test signals: `join` does not reset `threadID`; repeated joins are unsafe. Tests should cover timeout math, self-terminate wakeups, `startInCurrentThread`, name truncation/prefixing, and exception behavior on invalid operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h

Purpose: Defines the named exception for pthread creation failures.

Important APIs/types: `PThreadCreateException` derives from `PThreadException` via `DECLARE_NAMEDEXCEPTION`.

Control flow/state/persistence: No logic beyond exception construction and inherited `what()`.

Dependencies/integration: Thrown by `PThread::start` and `PThread::startOnNumaNode` when pthread creation or attribute setup fails.

Risks/test signals: Tests should catch it as both `PThreadCreateException` and `PThreadException`, and validate messages include underlying system errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h

Purpose: Defines the base named exception for BeeGFS pthread wrapper failures.

Important APIs/types: `PThreadException` derives from `SynchronizationException`.

Control flow/state/persistence: Pure exception type with inherited message/name behavior.

Dependencies/integration: Used by `PThread`, `Barrier`, and derived create exceptions.

Risks/test signals: Verify exception names and `what()` content remain stable for log/error-reporting code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h

Purpose: Wraps `pthread_rwlock_t` with optional deadlock-debug tracking.

Important APIs/types: `RWLock` initializes pthread RW attributes, exposes `writeLock`, `readLock`, timed/try variants, `unlock`, raw access, and debug-state queries. `RWLockLockType` records none/read/write state for debug builds.

Control flow/state/persistence: In normal builds it delegates to pthread RW locks. With `DEBUG_MUTEX_LOCKING`, it tracks lock state and owner thread to detect recursive or invalid usage and can log/throw on suspicious behavior.

Dependencies/integration: Used by quota stores, target maps, and shared state requiring read-heavy synchronization. Depends on `System`, `PThread`, and `RWLockException`.

Risks/test signals: Debug tracking is not a substitute for ownership in release builds. Tests should cover read/write mutual exclusion, try locks, timed reads, recursive locking behavior in debug mode, and unlock error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h

Purpose: Defines the named exception for reader/writer lock failures.

Important APIs/types: `RWLockException` derives from `SynchronizationException`.

Control flow/state/persistence: Exception-only header with inherited message behavior.

Dependencies/integration: Thrown by `RWLock` initialization and lock operations.

Risks/test signals: Tests should verify catch-by-base compatibility and stable error messages for lock initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h

Purpose: Provides a small RAII guard for `RWLock`.

Important APIs/types: `RWLockGuard` takes an `RWLock&` and `SafeRWLockType`, locks read or write in the constructor, and unlocks in the destructor.

Control flow/state/persistence: Scope lifetime controls lock ownership. No move/copy controls are visible, so intended usage is stack-only.

Dependencies/integration: Used by newer code such as `ExceededQuotaPerTarget` for concise read/write locking.

Risks/test signals: Copying a guard would double-unlock if not prevented by compiler behavior; usage should be audited. Tests should cover read/write acquisition and exception safety on early returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp

Purpose: Implements debug logging helpers for `SafeRWLock` misuse.

Important APIs/functions: `errRWLockStillLocked`, `errRWLockAlreadyUnlocked`, and `errRWLockAlreadyLocked` log error messages through `LogContext("SafeRWLock")`.

Control flow/state/persistence: No locking occurs here; these helpers are invoked from `SafeRWLock` when `DEBUG_MUTEX_LOCKING` detects misuse.

Dependencies/integration: Depends on `SafeRWLock.h` and BeeGFS logging. Supports lock debugging in quota and other shared-state code.

Risks/test signals: In release builds most `SafeRWLock` misuse tracking is disabled. Tests with debug locking enabled should assert warnings fire for double unlock, double lock, and destructor-with-lock cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h

Purpose: Stack-oriented wrapper around `RWLock` intended to catch forgotten unlocks in debug builds.

Important APIs/types: `SafeRWLock` can lock on construction or later via `lock`, and exposes `unlock`, `tryLock`, `timedReadLock`, and debug logging. `SafeRWLockType` selects read or write mode.

Control flow/state/persistence: In debug builds it tracks a `locked` flag and logs misuse, unlocking in the destructor if still locked. In release builds the destructor does not unlock, so callers must still call `unlock` explicitly.

Dependencies/integration: Used in older BeeGFS code where explicit unlocks are common, including quota stores.

Risks/test signals: Unlike typical RAII locks, release builds do not auto-unlock. Tests and code review should verify every path calls `unlock`, and debug builds should cover misuse logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h

Purpose: Defines the common base exception for synchronization primitives.

Important APIs/types: `SynchronizationException` derives from `NamedException` and supplies the synchronization exception name.

Control flow/state/persistence: Exception construction delegates to `NamedException`; no other behavior.

Dependencies/integration: Base class for mutex, condition, pthread, and RW-lock exceptions.

Risks/test signals: Catch hierarchy stability matters for callers that handle all synchronization errors together. Tests should validate message/name behavior through base catches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h

Purpose: Modern RAII/move-only wrapper for `RWLock`.

Important APIs/types: `UniqueRWLock` can be empty or constructed with a lock and mode, unlocks in its destructor when owned, supports move construction/assignment, `unlock`, `lock`, and `swap`.

Control flow/state/persistence: Unlike `SafeRWLock`, it always auto-unlocks when `locked` is true. The default constructor leaves `rwlock` null; callers must associate a lock before calling `lock`.

Dependencies/integration: Depends on `RWLock` and `SafeRWLockType`. Useful for exception-safe lock ownership in newer code.

Risks/test signals: Calling `lock` or `unlock` on a default/null instance will dereference null. Tests should cover move transfer, destructor unlock, manual unlock, and null-state misuse prevention in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp

Purpose: Implements wait/notify tracking for string-identified acknowledgments.

Important APIs/functions: `registerWaitAcks` registers pending ack IDs and immediately separates already received acks. `unregisterWaitAcks` removes waiter entries. `receivedAck` marks or stores an ack and signals waiters. `waitForAckCompletion` waits until a pending map becomes empty or times out.

Control flow/state/persistence: The global `ackStore` map is protected by `mutex`; each waiter has its own `waitAcksMutex` and `Condition`. Acks can arrive before or after registration. State is memory-only.

Dependencies/integration: Uses BeeGFS `Mutex`, `Condition`, and `WaitAckMap` structures. Used by messaging or management workflows that need asynchronous acknowledgment completion.

Risks/test signals: Lock ordering between store mutex and waiter mutex must remain stable. Tests should cover pre-received acks, partial completion, timeout, unregister during wait, duplicate ack IDs, and concurrent receivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h

Purpose: Declares the acknowledgment wait-store data model.

Important APIs/types: `WaitAckNotification` owns a mutex and condition. `WaitAck` stores an ack ID. `AckStoreEntry` links an ID to a waiter map and notifier. `AcknowledgmentStore` exposes register, unregister, receive, and wait methods over `WaitAckMap`.

Control flow/state/persistence: Data structures are pointer-linked rather than owning waiter maps, so caller lifetime is important. Persistence is not involved.

Dependencies/integration: Includes BeeGFS mutex/condition wrappers and common map aliases. Used around RPC/control workflows that wait for distributed acknowledgments.

Risks/test signals: Raw pointers to waiter-owned maps/notifiers can dangle if unregister is missed. Tests should verify lifecycle and concurrent receipt before/after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h

Purpose: Provides iterator adapters for raw arrays/slices.

Important APIs/types: `ValueIter`, `PointerIter`, `IterateAsValues`, `IterateAsPointers`, and `IterateAsRefs` allow range-style iteration over contiguous arrays as values, pointers, or references.

Control flow/state/persistence: Iterators advance raw pointers and dereference according to adapter type. No state beyond pointer positions.

Dependencies/integration: Used by `ArraySlice` to expose typed iteration over raw buffers.

Risks/test signals: Pointer lifetime and bounds are caller-owned. Tests should cover empty slices, const/non-const refs, pointer iteration, value copies, and compatibility with range-for loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayIteration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h

Purpose: Represents a non-owning typed view over contiguous array data.

Important APIs/types: `ArraySlice<T>` stores a pointer and element count, exposes `data`, `count`, and iteration helpers as values, pointers, const pointers, refs, and const refs.

Control flow/state/persistence: No ownership or persistence; it is a lightweight view.

Dependencies/integration: Depends on `ArrayIteration.h`. Used by serialization/buffer helpers that need typed views without copies.

Risks/test signals: The class does not validate null pointer with nonzero count. Tests should cover view creation from arrays, empty views, constness, and mutation through refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArraySlice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h

Purpose: Converts C arrays and `ArraySlice` values into byte-slice views.

Important APIs/types: `ArrayTypeTraits::Util<T,N>` exposes `As_ArraySlice`, `As_RO_Slice`, `As_WO_Slice`, and `As_Slice` overloads for fixed arrays and `ArraySlice<T>`.

Control flow/state/persistence: Pure compile-time/static conversion helpers. They compute byte lengths as element count times `sizeof(T)`.

Dependencies/integration: Depends on `ArraySlice` and `Slice` abstractions. Used by serialization and IO helpers that operate on raw byte spans.

Risks/test signals: Endianness and object representation are caller concerns when converting typed data to bytes. Tests should validate byte lengths, const correctness, and zero-length array/slice handling where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ArrayTypeTraits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h

Purpose: Provides intrusive atomic reference counting for a raw object pointer.

Important APIs/types: `AtomicObjectReferencer<T>` stores `referencedObject`, `ownReferencedObject`, and atomic `refCount`. It exposes `reference`, `release`, `getRefCount`, and ownership flag accessors.

Control flow/state/persistence: `reference` increments and returns the raw pointer. `release` decrements; when the old count indicates the last reference and ownership is enabled, it deletes the object. Logging reports misuse when release is called with count 0.

Dependencies/integration: Uses `Atomics` and `LogContext`. It predates widespread `shared_ptr` usage.

Risks/test signals: Raw pointer lifetime and old-value semantics of `Atomic::decrease` are critical. Tests should cover last release deletion, non-owning mode, over-release logging, concurrent references, and object destruction ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AtomicObjectReferencer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp

Purpose: Implements a compact fixed-size bit store with optimized inline storage for low bits.

Important APIs/functions: `setBit`, `setSize`, `clearBits`, `freeHigherBits`, serializer/deserializer overloads, equality, and assignment manage the internal bit representation.

Control flow/state/persistence: The store keeps initial bits in a direct integer and allocates `higherBits` blocks for larger sizes. Serialization writes size and enough bit blocks. Deserialization resizes then fills the block data.

Dependencies/integration: Uses BeeGFS serialization and standard memory helpers. Used wherever compact target/flag sets are transported or stored.

Risks/test signals: Boundary calculations between direct and higher bits are sensitive. Tests should cover sizes 0, 1, direct-block boundary, multi-block, resize smaller/larger, equality, assignment deep copy, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h

Purpose: Declares a serializable bit vector optimized for small stores.

Important APIs/types: `BitStore` exposes constructors, `init`, `setBit`, `getBitNonAtomic`, `setSize`, `clearBits`, serialization, equality, assignment, and `calculateBitBlockCount`.

Control flow/state/persistence: State consists of bit count, low block, and optional heap-allocated higher blocks. It is not thread-safe; callers synchronize externally.

Dependencies/integration: Used by message/config structures needing dense boolean sets.

Risks/test signals: Bounds checking is caller-limited. Tests should verify out-of-range behavior expected by callers, allocation transitions, and copy/assignment independence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BitStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp

Purpose: Returns the debug/release build type for the common library.

Important APIs/functions: `BuildTypeTk::getCommonLibDebugBuildType` returns debug or release based on compile-time macros.

Control flow/state/persistence: Compile-time conditional logic only, no runtime state.

Dependencies/integration: Used with `BuildTypeTk.h` to check build-type consistency across components.

Risks/test signals: Tests/build checks should confirm debug builds report debug and release builds report release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h

Purpose: Provides build-type detection and consistency checks.

Important APIs/types: `FhgfsBuildTypeDebug` enumerates debug, release, and unknown. `BuildTypeTk` exposes `getCommonLibDebugBuildType`, `getCurrentDebugBuildType`, and `checkDebugBuildTypes`.

Control flow/state/persistence: Header inline methods compare compile-time build type against the linked common library result. No persistence.

Dependencies/integration: Used to detect mixed debug/release component builds.

Risks/test signals: Check behavior depends on macros and link unit boundaries. Build tests should validate mixed-build detection where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/BuildTypeTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h

Purpose: Defines helper macros for environment-variable controlled debug tunables.

Important APIs/types: The file provides macro support used by code such as `MessagingTk` to override values from environment variables during debugging.

Control flow/state/persistence: Values are read from process environment at runtime where the macro is invoked. No persistent state is stored by the header itself.

Dependencies/integration: Integrated into diagnostics and test knobs for timing, networking, and other runtime behavior.

Risks/test signals: Environment overrides can change behavior unexpectedly in production-like tests. Tests should validate default use, override parsing, invalid values, and scope of the generated variable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DebugVariable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp

Purpose: Walks disposal directories on metadata nodes and optionally unlinks disposal entries.

Important APIs/functions: `run` iterates nodes and invokes `walkNode`. `walkNode` pages through disposal entries with `ListDirFromOffsetMsg`, calls an `onItem` callback, and can remove entries depending on callback result. `unlinkFile` sends `UnlinkFileMsg` for a disposal entry.

Control flow/state/persistence: The cleaner communicates with metadata nodes, tracks server offsets, and uses metadata entry IDs for disposal directories. Persistent effects occur only through remote unlink requests.

Dependencies/integration: Uses `Node`, `MessagingTk`, list-dir/unlink messages, `EntryInfo`, and metadata constants. It integrates cleanup tooling with metadata disposal state.

Risks/test signals: Remote list/unlink errors and pagination loops are key. Tests should cover empty directories, multiple pages, callback stop/delete decisions, mirrored disposal entries, communication failures, and unlink result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h

Purpose: Declares the disposal cleanup helper.

Important APIs/types: `DisposalCleaner::OnItemFn` callback receives node, entry name, and mirrored flag and returns a bool decision. Public `run` walks nodes with the callback, and static `unlinkFile` removes an item. Private `walkNode` implements per-node traversal.

Control flow/state/persistence: The class has no member state. It performs remote metadata operations during `run`.

Dependencies/integration: Depends on node handles and BeeGFS operation errors. Used by maintenance tools or services cleaning disposal directories.

Risks/test signals: Callback behavior defines deletion policy. Tests should validate callback invocation order, mirrored flag propagation, and error propagation from node walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp

Purpose: Implements validation helpers for BeeGFS entry IDs and hexadecimal tokens.

Important APIs/functions: `EntryIdTk::isValidEntryIdFormat` checks the expected tokenized entry-id shape. `EntryIdTk::isValidHexToken` verifies uppercase hex-token characters.

Control flow/state/persistence: Pure string validation; no state.

Dependencies/integration: Used by metadata/fsck/tools before accepting entry IDs.

Risks/test signals: Format strictness can reject older or externally generated IDs. Tests should cover valid IDs, lowercase hex, missing tokens, extra separators, empty tokens, and non-hex characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h

Purpose: Declares entry ID validation helpers.

Important APIs/types: Namespace `EntryIdTk` exposes `isValidEntryIdFormat` and `isValidHexToken`.

Control flow/state/persistence: Stateless declarations for pure validation functions.

Dependencies/integration: Includes `<string>`. Used in metadata-facing tooling and consistency checks.

Risks/test signals: Tests should pin accepted format examples to prevent accidental loosening/tightening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h

Purpose: RAII wrapper for POSIX file descriptors.

Important APIs/types: `FDHandle` owns an `int fd`, closes it in the destructor, supports move construction/assignment, `close`, `get`, `reset`, `valid`, and `swap`.

Control flow/state/persistence: Ownership transfer is move-only. `reset` closes the existing descriptor before replacing it. No file content persistence logic beyond descriptor lifetime.

Dependencies/integration: Used by `LockFD` and other low-level POSIX helpers.

Risks/test signals: `close` returns the system close result but destructor cannot report errors. Tests should cover move transfer, reset from valid/invalid descriptors, double close prevention, and valid state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h

Purpose: Adapts a raw file descriptor to the BeeGFS `Pollable` interface with read/write helpers.

Important APIs/types: `FileDescriptor` wraps an fd, exposes `readExact`, `read`, `write`, and `getFD`.

Control flow/state/persistence: `readExact` loops until the requested byte count is read or an error/EOF occurs. `read` and `write` delegate to POSIX calls. Descriptor ownership is not clearly RAII here; caller semantics matter.

Dependencies/integration: Depends on `Pollable` and POSIX IO. Used where fd-backed objects participate in polling/event loops.

Risks/test signals: Partial reads/writes and EINTR/EAGAIN handling should be verified. Tests should cover EOF before exact length, write errors, invalid fd, and poll integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp

Purpose: Converts between runtime metadata/stripe types and fsck-specific representations.

Important APIs/functions: `DirEntryTypeToFsckDirEntryType` maps directory entry types. `stripePatternToFsckStripePattern` maps `StripePattern` instances to fsck enum plus target vectors. `FsckStripePatternToStripePattern` creates runtime patterns from fsck type, chunk size, and targets.

Control flow/state/persistence: Conversion switches on enum values and allocates new `StripePattern` objects for reverse conversion. Caller owns returned pattern pointers.

Dependencies/integration: Uses `Raid0Pattern`, `BuddyMirrorPattern`, `StripePattern`, and fsck enums. Bridges online metadata with checker/repair tools.

Risks/test signals: Unsupported RAID10 conversion behavior and ownership of allocated patterns should be tested. Cover all dir entry types, null/unknown patterns, target vector preservation, and buddy mirror conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h

Purpose: Declares fsck conversion enums and helpers.

Important APIs/types: `FsckStripePatternType`, `FetchFsckChunkListStatus`, and class `FsckTk` with stripe-pattern and dir-entry conversion functions.

Control flow/state/persistence: Stateless conversion interface. Pattern creation in the implementation returns heap ownership to callers.

Dependencies/integration: Includes metadata and striping types. Used by BeeGFS fsck and repair tooling.

Risks/test signals: Tests should pin enum mapping and ownership expectations, especially as new stripe or dir entry types are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FsckTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp

Purpose: Implements hashing utilities used for placement or authentication-style checks.

Important APIs/functions: `HashTk::hsieh32` implements a 32-bit Hsieh/SuperFastHash-style function over byte data. `HashTk::authHash` produces a 64-bit hash over unsigned bytes.

Control flow/state/persistence: Pure deterministic hash computation, no state. Both process input buffers sequentially.

Dependencies/integration: Used wherever stable BeeGFS hashes are required for metadata placement, routing, or lightweight authentication/checking.

Risks/test signals: Hash output stability is compatibility-sensitive. Tests should use golden vectors for empty input, short tails, aligned/unaligned buffers, long buffers, and byte values over 127.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h

Purpose: Declares common hash functions.

Important APIs/types: Namespace `HashTk` exposes `hsieh32(const char*, int)` and `authHash(const unsigned char*, std::size_t)`.

Control flow/state/persistence: Stateless deterministic functions.

Dependencies/integration: Included by placement/authentication helpers requiring stable hash APIs.

Risks/test signals: Tests should ensure null/zero-length caller expectations are documented and hash outputs remain stable across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HashTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h

Purpose: Defines high-resolution raw and incremental statistics containers.

Important APIs/types: `HighResolutionStats` contains `RawVals` and `IncrementalVals` with serialization. `HighResolutionStatsTk` provides helpers to add raw/inc stats and reset stats.

Control flow/state/persistence: Stats are value-owned and serializable, typically transported in lists/vectors. Add helpers accumulate counters into existing structures.

Dependencies/integration: Used by performance monitoring and management reporting. Serialization traits declare list length behavior.

Risks/test signals: Counter accumulation can overflow if unbounded. Tests should cover serialization, reset behavior, incremental addition, raw addition, and list/vector transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/HighResolutionStats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h

Purpose: Provides generic and string-specific list utility functions.

Important APIs/types: `ListTk` exposes `listContains` overloads, `listsEqual`, `removeFromList`, `advance`, and `erase`.

Control flow/state/persistence: Functions iterate and mutate `std::list` values. `advance` moves an iterator up to a count and returns steps advanced; `erase` removes by position.

Dependencies/integration: Used throughout older BeeGFS code built on list aliases.

Risks/test signals: Position and iterator edge cases are main risks. Tests should cover empty lists, duplicate elements, removal with duplicates, erase out of range, and equality order sensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp

Purpose: Implements file-based process locking and lock-file content updates.

Important APIs/functions: `LockFD::lock(path, forUpdate)` opens/truncates/creates a path and takes a non-blocking flock-style lock through `flock`. `update` rewrites lock-file contents. `updateWithPID` writes the current PID.

Control flow/state/persistence: Successful lock returns an owning `LockFD` with an `FDHandle`. `update` writes new content to the lock file and truncates/resets as needed. Persistent effect is lock-file contents; lock lifetime is fd lifetime.

Dependencies/integration: Uses POSIX `open`, `flock`, `write`, `ftruncate`, `lseek`, `FDHandle`, and `nu::error_or`.

Risks/test signals: `O_TRUNC` before lock acquisition can erase another process's lock-file content. Tests should cover contention, update errors, read-only mode, PID writes, and fd close unlock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h

Purpose: Declares an RAII lock-file handle.

Important APIs/types: `LockFD` is final and move-only, stores `path` and `FDHandle`, and exposes `lock`, `update`, `updateWithPID`, `valid`, and `swap`.

Control flow/state/persistence: Lock ownership follows fd ownership. File contents can be updated after acquisition when opened for update.

Dependencies/integration: Depends on `FDHandle` and `nu::error_or`. Used by daemon/process coordination code.

Risks/test signals: Move semantics should preserve single ownership. Tests should cover invalid handles, swap, update without write permission, and destructor unlock through fd close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp

Purpose: Implements string-map file parsing/writing and selected map copy helpers.

Important APIs/functions: `addLineToStringMap` parses key/value lines into `StringMap`. `loadStringMapFromFile` reads a config-like file. `saveStringMapToFile` writes map entries. `copyUInt64VectorMap` deep-copies maps of vector pointers.

Control flow/state/persistence: File load skips comments/blank lines through parser behavior. Save opens an output file and throws `InvalidConfigException` on failures. Copy helper allocates new vectors for each entry.

Dependencies/integration: Uses C++ streams, BeeGFS string/map aliases, and invalid-config exceptions. Used for config-style persistence.

Risks/test signals: Tests should cover duplicate keys, malformed lines, comments, write errors, deep-copy ownership, and exception messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h

Purpose: Declares map utility helpers for string configs and vector maps.

Important APIs/types: `MapTk` exposes parser/load/save/copy functions and inline `stringMapRedefine` to erase and reinsert a key/value.

Control flow/state/persistence: Most logic is in the implementation. `stringMapRedefine` mutates the caller-provided map in place.

Dependencies/integration: Includes common map/list aliases. Used by configuration and utility code.

Risks/test signals: Tests should cover redefinition preserving only one key, missing file exceptions, and pointer-map copy ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MapTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h

Purpose: Provides small math helper functions.

Important APIs/types: `MathTk` exposes integer log2 helpers for 64-bit and 32-bit values, `isPowerOfTwo`, and `medianOfSorted` returning `boost::optional<T>`.

Control flow/state/persistence: Pure computations, no state. `medianOfSorted` assumes the input vector is already sorted and returns empty for no values.

Dependencies/integration: Used by striping and configuration validation logic where power-of-two chunk sizes and medians are needed.

Risks/test signals: Tests should cover zero, one, powers/non-powers of two, max values, even/odd median lengths, empty vectors, and unsorted caller behavior documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MathTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp

Purpose: Implements common request/response RPC helpers for BeeGFS nodes and targets.

Important APIs/functions: `requestResponse` wraps `requestResponseComm` with one retry on communication failure. `requestResponseNode` resolves nodes, mirror groups, and target states before sending. `requestResponseTarget` maps target IDs to owner nodes and sets message header target ID. `recvMsgBuf` receives bounded messages. `createMsgVec` serializes messages. `handleGenericResponse` maps generic control responses to operation errors.

Control flow/state/persistence: RPC flow acquires a stream socket from a node pool, serializes/sends, optionally sends extra data, receives/deserializes a response, releases reusable sockets on success, and invalidates sockets on failure. It does not persist state.

Dependencies/integration: Central integration point for `Node`, `NodeConnPool`, target mappers/states, mirror buddy mappers, net message factory, sockets, `PThread` app config, and logging.

Risks/test signals: Message size cap is 4 MiB; timeout can be environment-overridden. Tests should cover retries, wrong response type, generic TRYAGAIN/INDIRECTCOMMERR, offline target skipping, mirror mapping, socket invalidation, extra-data failures, and oversized messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h

Purpose: Declares the common BeeGFS RPC helper facade.

Important APIs/types: `MessagingTk` exposes request/response helpers for direct nodes, node wrappers, target wrappers, message receive buffers, and message serialization vectors. Private helpers handle lower-level communication and generic responses.

Control flow/state/persistence: Interface is stateless and static. Callers supply `RequestResponseArgs`, `RequestResponseNode`, or `RequestResponseTarget` structures to control routing and behavior.

Dependencies/integration: Includes node, socket, message, target state, and messaging argument types. Used across storage, metadata, management, fsck, and ctl paths.

Risks/test signals: Callers must initialize argument structs correctly, especially `rrArgs->node` ownership/nullness. Integration tests should exercise node and target paths with mocked stores and sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h

Purpose: Defines argument structures for `MessagingTk` request/response helpers.

Important APIs/types: `RequestResponseTarget` stores target ID, mapper/store pointers, optional target states and mirror buddy mapping. `RequestResponseNode` stores node ID/store and optional state/mirror mapping. `RequestResponseArgs` stores resolved node, request/expected response, output response, timeout, logging flags, and optional extra-data callback/context.

Control flow/state/persistence: These are mutable call-context structures; `MessagingTk` fills output state and response fields. No persistence.

Dependencies/integration: Shared by RPC callers and `MessagingTk.cpp`, connecting routing metadata, target state stores, and messages.

Risks/test signals: Raw pointer initialization is critical. Tests should construct minimal and fully populated args, verify output state updates, log-flag suppression, and extra-data callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTkArgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h

Purpose: Provides metadata storage path helper functions.

Important APIs/types: `MetaStorageTk` exposes helpers to build inode paths, hash values, dentry paths, and dentry-ID paths using `StorageTk` hashing rules and metadata directory depth constants.

Control flow/state/persistence: Pure path computation; no disk IO in this header.

Dependencies/integration: Depends on `StorageTk` and metadata path constants. Used by metadata server storage layout code and tools.

Risks/test signals: Path hashing must match on-disk layout. Tests should use golden paths for representative inode and dentry IDs, including edge-length names and nested hash directory expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp

Purpose: Implements metadata owner lookup across metadata nodes.

Important APIs/functions: `referenceOwner` resolves and references the metadata node owning a path and fills `EntryInfo`. `findOwnerStep` sends one `FindOwnerMsg` to a node. `findOwner` iteratively follows owner handoffs until the requested depth is reached.

Control flow/state/persistence: The search starts at the root node or mirrored root primary, sends find-owner requests, and advances by returned `EntryInfoWithDepth`. It aborts on errors, unknown nodes, non-progressing depth, or exceeding `METADATATK_OWNERSEARCH_MAX_STEPS`. No local persistence.

Dependencies/integration: Uses `NodeStoreServers`, `RootInfo`, `MirrorBuddyGroupMapper`, `MessagingTk`, `FindOwnerMsg/Resp`, and metadata constants. Central for ctl/client-side metadata routing.

Risks/test signals: Concurrent namespace changes can cause non-progressing depth or owner changes. Tests should cover root lookup, mirrored root, multi-hop lookup, unknown next node, communication failure, max-step guard, and entry info flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h

Purpose: Declares metadata lookup and file-type conversion helpers.

Important APIs/types: `ModificationEventType` enumerates metadata modification event kinds. `MetadataTk::referenceOwner` is the public owner-resolution API. Private helpers perform find-owner steps. Inline `posixFileTypeToDirEntryType` maps POSIX mode bits to BeeGFS entry types.

Control flow/state/persistence: Stateless API; owner lookup performs network communication in the implementation.

Dependencies/integration: Includes node stores, entry info, root info, path, storage errors, and messaging. Used by tools and services that need to locate metadata owners.

Risks/test signals: Tests should cover POSIX type mapping for regular, directory, symlink, and unknown modes, plus owner lookup integration with mirrored metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetadataTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h

Purpose: Tracks minimum, maximum, sum, and count for entered values.

Important APIs/types: `MinMaxStore<T>` exposes constructors for default, single-value, and explicit min/max initialization, plus `getMin`, `getMax`, and `enter`.

Control flow/state/persistence: `enter` updates min/max in memory using BeeGFS min/max macros. The default constructor initializes min to `numeric_limits<T>::max()` and max to `numeric_limits<T>::min()`. No persistence.

Dependencies/integration: Template utility for statistics gathering.

Risks/test signals: Empty/default-state getter behavior is the main concern. Tests should cover no values, one value, increasing/decreasing sequences, negative values for signed types, and explicit min/max constructor invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MinMaxStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h

Purpose: Defines BeeGFS named exception infrastructure and a macro for derived exception classes.

Important APIs/types: `DECLARE_NAMEDEXCEPTION` and `DECLARE_NAMEDSUBEXCEPTION` generate exception classes with constructors that pass an exception name and message to the base. `NamedException` derives from `std::exception`, stores the name/message internally, and exposes `what()` for the message text.

Control flow/state/persistence: Exception messages are stored in `std::string`; `what()` returns a stable C string from a member buffer/string. No persistence.

Dependencies/integration: Base for synchronization, config, signal, and other BeeGFS exception families.

Risks/test signals: `what()` lifetime and message preservation are critical for logging. Tests should cover message constructors, catch by `std::exception`, copy behavior, and macro-generated inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/NamedException.h -->
