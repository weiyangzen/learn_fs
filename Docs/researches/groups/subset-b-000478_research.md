# subset-b-000478 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucket.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucket.java

## Purpose
`TtlBucket` is the in-memory container used by the file master TTL checker to group inode ids whose expiration timestamps fall in the same checker interval. The interval length is `MASTER_TTL_CHECKER_INTERVAL_MS`, captured in the static `sTtlIntervalMs`, and each bucket is ordered by its interval start time.

## Important APIs, types, and functions
The class exposes interval metadata through `getTtlIntervalStartTimeMs()`, `getTtlIntervalEndTimeMs()`, and static `getTtlIntervalMs()`. `getInodeIds()` returns an unmodifiable key-set view, while `getInodeExpiries()` exposes inode ids with remaining TTL-processing retry counts. `addInode(Inode)` uses `DEFAULT_RETRY_ATTEMPTS`; `addInode(Inode, int)` records the smaller remaining retry count if the inode already exists. `removeInode(InodeView)` and `size()` provide mutation and accounting. `compareTo`, `equals`, and `hashCode` define bucket identity solely by interval start time.

## Control flow
There is no background processing in this class. Callers compute the correct interval, construct or find a bucket, then call `addInode`. The `ConcurrentHashMap.compute` call makes duplicate insertion deterministic under concurrency by keeping the lower retry count. Ordering is delegated to `Long.compare` on interval start times for use in sorted sets.

## State and persistence behavior
State is volatile in memory: `mTtlIntervalStartTimeMs` and `mInodeToRetryMap`. This class does not write journal entries or checkpoints itself; `TtlBucketList` checkpoints inode ids and reconstructs buckets from the inode store. The static interval is intentionally non-final so tests can alter it.

## Dependencies and integration points
It depends on Alluxio configuration/property keys for the TTL interval, `Inode`/`InodeView` for id extraction, Guava `Objects`, and JDK concurrent collections. It integrates with `TtlBucketList` and ultimately with the inode TTL checker.

## Risks
Bucket equality ignores retry map contents, so callers must not use equal buckets as distinct state containers. The unmodifiable views are live views over a concurrent map, so iteration can observe concurrent changes. Changing `sTtlIntervalMs` after buckets are created can make existing interval boundaries inconsistent with lookup logic.

## Test signals
Useful tests should cover interval boundary inclusion, zero interval handling, duplicate insertion retry-min behavior, remove semantics, compare/equality/hash consistency, and concurrent add/remove visibility through `TtlBucketList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucketList.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucketList.java

## Purpose
`TtlBucketList` manages the sorted set of non-empty `TtlBucket` instances for inode TTL processing. It maps inode expiration times into checker intervals, supports polling expired intervals, and persists enough checkpoint state to rebuild the list after restart.

## Important APIs, types, and functions
The constructor takes a `ReadOnlyInodeStore`. `insert(Inode)` and `insert(Inode, int)` place valid-TTL inodes into interval buckets. `remove(InodeView)` removes an inode from its current bucket. `pollExpiredBuckets(long)` atomically removes and returns all buckets whose start time is no later than `time - interval`. `getNumBuckets()` and `getNumInodes()` expose accounting. As a `Checkpointed` implementation, it returns `CheckpointName.TTL_BUCKET_LIST`, writes inode ids as a `CheckpointType.LONGS` checkpoint, and restores by reloading inodes from the inode store.

## Control flow
Insertion skips `Constants.NO_TTL`, looks for an existing containing bucket using `floor`, and creates a new bucket at `(ttlEnd / interval) * interval` or exactly `ttlEndTimeMs` when interval is zero. If another thread concurrently adds the same bucket, insertion retries. After adding the inode, insertion verifies the bucket still exists in the skip-list; if the TTL checker polled it concurrently, insertion repeats so the inode is not missed. Polling repeatedly removes the first bucket while it is expired.

## State and persistence behavior
The durable checkpoint contains only inode ids, not bucket start times or retry counts. Restore clears the set, reads ids until EOF, reloads each inode from `mInodeStore`, and calls `insert`, which recomputes buckets from current inode metadata. Retry counts are therefore reset to defaults across checkpoint restore. Missing inode ids are logged as errors and skipped.

## Dependencies and integration points
This class depends on `TtlBucket`, `ReadOnlyInodeStore`, checkpoint streams, checkpoint names/types, and inode metadata. It is consumed by TTL checker code that polls expired buckets and processes `TtlBucket.getInodeExpiries()`.

## Risks
The `loadInode` helper uses `orElseGet(null)`, which is suspicious because `Optional.orElseGet` expects a supplier; if compiled in this source state it should be reviewed. Checkpoint restore drops remaining retry counts. `getBucketContaining` has subtle boundary logic around exact interval-end timestamps and zero interval. Empty buckets are not removed by `remove`, so callers may leave zero-size buckets unless the checker polls them.

## Test signals
Tests should exercise insert/remove across boundaries, exact end-time behavior, zero interval behavior, concurrent insert-versus-poll races, checkpoint write/restore with deleted inodes, retry-count restore expectations, and accounting for empty buckets after removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucketList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsAbsentPathCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsAbsentPathCache.java

## Purpose
`UfsAbsentPathCache` is the file-master abstraction for remembering paths or ancestors known to be absent in the under file system. It lets metadata operations avoid repeated UFS existence checks when a path has recently been proven absent.

## Important APIs, types, and functions
The interface defines `processAsync(AlluxioURI, List<Inode>)`, `addSinglePath(AlluxioURI)`, `processExisting(AlluxioURI)`, and `isAbsentSince(AlluxioURI, long)`. Constants `ALWAYS = -1` and `NEVER = Long.MAX_VALUE` express validity thresholds. The nested `Factory.create(MountTable, Clock)` returns `NoopUfsAbsentPathCache` when `MASTER_UFS_PATH_CACHE_THREADS <= 0`, otherwise `AsyncUfsAbsentPathCache`.

## Control flow
Implementations decide the actual traversal and mutation behavior. The contract states that async processing sequentially walks path components against UFS, existing-path processing removes or adjusts absence state, and `isAbsentSince` checks the path and its ancestors against the supplied timestamp.

## State and persistence behavior
The interface itself has no persisted state. Implementations maintain cache entries in memory, and factory selection is entirely configuration driven. State is safe to lose on master restart because UFS absence can be rediscovered.

## Dependencies and integration points
It integrates with `MountTable`, `Inode` prefix information, `AlluxioURI`, and the UFS path cache thread configuration. `DefaultFileSystemMaster` and inode sync paths use it when resolving paths against UFS.

## Risks
Behavior depends heavily on implementation details outside this file. Disabling via thread count silently switches to a no-op cache, so tests and production diagnostics must account for that. Stale absent entries can hide newly-created UFS paths until invalidated or considered too old by the `absentSince` threshold.

## Test signals
Factory tests should validate disabled and enabled selection. Implementation tests should cover ancestor absence, existing-path invalidation, mount boundary behavior, async ordering, and `ALWAYS`/`NEVER` threshold semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsAbsentPathCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsBlockLocationCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsBlockLocationCache.java

## Purpose
`UfsBlockLocationCache` abstracts caching for under-file-system block locations. It lets file block metadata lookups reuse UFS locality information keyed by Alluxio block id.

## Important APIs, types, and functions
`get(long)` returns cached locations or null. `get(long, AlluxioURI, long)` returns cached locations or loads them from UFS for a file URI and block offset, caching only successful results. `invalidate(long)` removes a cached mapping. `Factory.create(MountTable)` instantiates `LazyUfsBlockLocationCache`.

## Control flow
The interface defines read-through cache behavior: a plain `get` is non-loading, while the overloaded `get` can consult the UFS through the mount table. Failed UFS lookup returns null and should not populate cache state.

## State and persistence behavior
No state is persisted through this interface. Implementations cache location lists in memory and can discard them on invalidation or restart.

## Dependencies and integration points
The abstraction depends on `AlluxioURI`, `MountTable`, and the `LazyUfsBlockLocationCache` implementation. It integrates with file block info generation where UFS locations are merged with Alluxio worker locations for clients and web UI display.

## Risks
The null-on-miss contract is easy to misuse; callers must distinguish no cached entry, UFS lookup failure, and valid empty location lists. Cached UFS locality can become stale after external UFS changes unless invalidation is wired correctly.

## Test signals
Tests should cover non-loading misses, load success and load failure, invalidation, repeated lookup caching, mount table resolution errors, and empty-location results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsBlockLocationCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncPathCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncPathCache.java

## Purpose
`UfsSyncPathCache` tracks when Alluxio paths were synchronized with UFS and whether later invalidations require another sync. It is a core decision helper for metadata sync, mapping path strings to `SyncState` objects with exact, direct-child, recursive-child sync and invalidation timestamps.

## Important APIs, types, and functions
The constructor builds a Guava cache sized by `MASTER_UFS_PATH_CACHE_CAPACITY` and concurrency-level configured by `MASTER_UFS_PATH_CACHE_THREADS`. `recordStartSync()` returns the current clock time. `getSyncTimesForPath(AlluxioURI)` returns direct and recursive sync times if cached. `shouldSyncPath(AlluxioURI, long, DescendantType)` computes a `SyncCheck`. `notifyInvalidation(AlluxioURI)` and `notifySyncedPath(AlluxioURI, DescendantType, long, Long, boolean)` update invalidation and validation state. Root state is held separately in `mRoot` behind `mRootLock`.

## Control flow
`shouldSyncPath` walks from the target path to root, selecting the strongest usable sync timestamp based on whether the request covers no children, one level, or all descendants. At the base path it considers file syncs, direct-child syncs, recursive syncs, and invalidation fields; at parent and ancestor levels it uses direct or recursive sync times depending on child/file semantics. `computeSyncResult` then compares interval policy, validation time, invalidation time, and current clock time: interval `0` always syncs, negative intervals suppress sync unless invalidated, and non-negative intervals sync when stale. `notifyInvalidationInternal` updates the path and all ancestors. `notifySyncedPath` writes validation time and clears invalidation fields only when no newer invalidation arrived after sync start.

## State and persistence behavior
The cache is in-memory only. Root is never evicted; non-root paths can be evicted by Guava. The removal listener currently does not call `onCacheEviction` because invalidation propagation on eviction was disabled due to issue commentary in the source. Sync times are based on the injected `Clock`, making test-time control possible.

## Dependencies and integration points
It depends on `AlluxioURI`, `PathUtils`, `DescendantType`, `SyncState`, `SyncCheck`, Guava cache, Alluxio configuration, and `LockResource`. It is called from inode sync paths and file-master sync decisions, including external invalidation notifications.

## Risks
The state machine is subtle: wrong descendant type, file flag, or timestamp ordering can either skip needed UFS syncs or trigger excessive syncs. Eviction invalidation propagation is disabled, so eviction can lose invalidation history. Root locking differs from non-root `Cache.asMap().compute` updates, so code changing root handling needs concurrency scrutiny.

## Test signals
Tests should cover all `DescendantType` combinations, file versus directory base paths, direct and recursive ancestor validation, negative/zero/positive intervals, invalidation after sync start, root path updates, eviction behavior, path cleanup, and injected-clock boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncPathCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncUtils.java

## Purpose
`UfsSyncUtils` provides pure decision helpers for reconciling an Alluxio inode with a UFS fingerprint. Its main output is a `SyncPlan` saying whether to update metadata, delete the inode, load metadata, and/or sync directory children.

## Important APIs, types, and functions
`computeSyncPlan(Inode, Fingerprint, boolean)` is the main API. `inodeUfsIsContentSynced` checks persisted/unpersisted content presence and fingerprint content matching. `inodeUfsIsMetadataSynced` checks metadata fingerprint matching. Nested `SyncPlan` exposes read methods `toDelete()`, `toUpdateMetaData()`, `toLoadMetadata()`, and `toSyncChildren()`.

## Control flow
The method parses the inode's stored UFS fingerprint and validates it. If content and metadata match, persisted directories sync children and everything else is a no-op. If a directory is out of sync but the UFS side is also a directory or the subtree contains a mount point, the plan updates directory metadata unless the inode is root and then syncs children. For file mismatches, or directory-vs-nondirectory mismatches, unsynced content causes delete and optional metadata load if UFS exists; metadata-only differences cause update-metadata.

## State and persistence behavior
This class has no state or persistence. It interprets persisted inode fields such as `isPersisted`, `getUfsFingerprint`, parent id, and directory/file type.

## Dependencies and integration points
It depends on `Inode`, `InodeTree.NO_PARENT`, and `alluxio.underfs.Fingerprint`. `InodeSyncStream` and file-master sync code consume `SyncPlan` to perform actual deletes, metadata loads, and child sync traversal.

## Risks
An invalid stored inode fingerprint triggers a precondition failure. Root directory metadata is intentionally not updated from UFS, which is a special-case behavior tests should preserve. Mount-point containment prevents delete/reload of directories, so incorrect `containsMountPoint` input has high behavioral impact.

## Test signals
Tests should cover persisted file matches/mismatches, unpersisted absent UFS, UFS missing for persisted inodes, directory metadata-only changes, directory-vs-file conflicts, root directory handling, mount-point containment, invalid fingerprints, and each `SyncPlan` flag combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/options/MountInfo.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/options/MountInfo.java

## Purpose
`MountInfo` is the immutable holder for one Alluxio mount point: the Alluxio URI, UFS URI, mount id, and `MountPOptions`. It converts internal mount metadata into gRPC and wire objects used by clients and web UI.

## Important APIs, types, and functions
The constructor validates non-null Alluxio and UFS URIs. Accessors expose `getAlluxioUri()`, `getUfsUri()`, `getOptions()`, and `getMountId()`. `toUfsInfo()` builds a gRPC `UfsInfo`. `toMountPointInfo()` builds a wire `MountPointInfo` with URI, read-only/shared flags, properties, and mount id. `toDisplayMountPointInfo()` converts properties through `UnderFileSystemConfiguration` with display-value masking. Equality compares mount id, URIs, read-only flag, and shared flag; `hashCode` includes full options.

## Control flow
The methods are direct transformations. Display conversion creates a mount-specific UFS configuration and asks it for a user property map using display-value options so sensitive or formatted values are suitable for display.

## State and persistence behavior
The object holds constructor-provided mount state in final fields and does not journal itself. Mount-table code persists and reconstructs mount metadata elsewhere. The `MountPOptions` object is retained by reference.

## Dependencies and integration points
It integrates with `MountTable`, gRPC mount APIs, `UfsInfo`, wire `MountPointInfo`, and UFS configuration display masking. REST and web UI mount-table endpoints consume the converted wire form.

## Risks
`equals` ignores mount properties except read-only/shared, while `hashCode` includes `mOptions`, which can violate the Java equality/hashCode contract if options differ only in properties. Retaining `MountPOptions` by reference assumes protobuf immutability. Display masking depends on UFS configuration property metadata.

## Test signals
Tests should check conversion fields, display masking for sensitive properties, equality/hash behavior with differing property maps, read-only/shared comparisons, and mount id propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/options/MountInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/replication/ReplicationChecker.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/replication/ReplicationChecker.java

## Purpose
`ReplicationChecker` is a heartbeat executor that keeps file block replication levels aligned with file policy. It schedules job-service actions for under-replicated pinned blocks, over-replicated blocks, and blocks stored on the wrong medium for pinned files.

## Important APIs, types, and functions
Constructors wire `InodeTree`, `BlockMaster`, `SafeModeManager`, and a `ReplicationHandler`, defaulting to `DefaultReplicationHandler` backed by a job-master client pool. `heartbeat(long)` performs the periodic scan. `findMisplacedBlock(InodeFile, BlockInfo)` computes worker-host to desired-medium moves. Internal `check` handles `Mode.REPLICATE` and `Mode.EVICT`; `checkMisreplicated` handles medium migration. `mActiveJobToInodeID` tracks outstanding job ids and registers the `MASTER_REPLICA_MGMT_ACTIVE_JOB_SIZE` gauge.

## Control flow
Heartbeat skips safe mode and no-worker clusters unless test mode is enabled. It refreshes active job ids by querying job types `Evict`, `Move`, and `Replicate`, pruning completed jobs from the bimap. It scans pinned ids for under-replication, replication-limited ids for over-replication, and pinned ids again for medium mismatch. Each file is locked read-only through `InodeTree.lockFullInodePath`; block locations come from `BlockMaster.getBlockInfo`. Requests are accumulated per file, then submitted through `handler.setReplica` or `handler.migrate` until the active-job cap is reached.

## State and persistence behavior
State is in-memory only: active job id to inode id, plus registered metrics. The checker does not journal its progress. If the master restarts, job-service state and inode/block metadata are re-scanned on future heartbeats.

## Dependencies and integration points
It depends on inode metadata, block metadata, safe mode, job service replication handlers, Alluxio metrics, and job statuses. It integrates with pinned file tracking (`getPinIdSet`), replication-limited ids, block lost detection, and persistence state/durable replication constraints.

## Risks
The active job map prevents duplicate work per inode but is local to the checker and refreshed best-effort; job master RPC failures can leave stale entries until later refresh. Full path locking may add inode-tree contention. The medium-migration logic only targets the first pinned medium type. Unavailable block master or job service aborts the current scan early, delaying other files.

## Test signals
Tests should cover safe-mode/no-worker skipping, active job pruning, job cap enforcement, min/max/durable replication calculations, lost non-persisted block skip, job service busy/unavailable handling, medium mismatch movement, duplicate suppression by inode, and interruption behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/replication/ReplicationChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/state/DirectoryId.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/state/DirectoryId.java

## Purpose
`DirectoryId` is a small mutable value object representing a directory id split into a container id and sequence number. It also exposes a live read-only view for callers that should not mutate the id.

## Important APIs, types, and functions
The constructor initializes both fields to zero and creates an anonymous `UnmodifiableDirectoryId` view. Getters and setters cover `containerId` and `sequenceNumber`. The nested `UnmodifiableDirectoryId` interface exposes only getters, and `getUnmodifiableView()` returns the stable view instance.

## Control flow
There is no control flow beyond direct field access. The immutable view reads the outer object's current fields, so it reflects later mutations.

## State and persistence behavior
State is in-memory in two longs. Persistence, if any, is handled by callers that serialize directory id allocation state elsewhere.

## Dependencies and integration points
It is used by file-master directory id generation/allocation code. It has no external library dependencies.

## Risks
The class is not synchronized or annotated thread-safe; concurrent readers of the view and writers through setters can race. The view is immutable only in API surface, not in snapshot semantics.

## Test signals
Tests should verify default zero state, setter/getter behavior, live view updates after mutation, and caller-level synchronization where shared across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/state/DirectoryId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/AbstractJob.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/AbstractJob.java

## Purpose
`AbstractJob` supplies common job identity, user, lifecycle state, start/end timing, and running/done predicates for master-side scheduler jobs.

## Important APIs, types, and functions
It implements `Job<T extends Task<?>>`. The constructor requires a user optional and job id, starts in `JobState.RUNNING`, and records `mStartTime`. APIs include `getJobId()`, `getEndTime()`, `setEndTime(long)`, `getJobState()`, `setJobState(JobState)`, `isRunning()`, and `isDone()`.

## Control flow
`setJobState` logs the transition and automatically sets `mEndTime` when the new state is not running or verifying. `isRunning` treats `RUNNING` and `VERIFYING` as active. `isDone` returns true only for `SUCCEEDED` and `FAILED`.

## State and persistence behavior
This base class stores runtime state in fields; subclasses decide what to journal. `LoadJob` journals job id, state, options, and optional end time but not all runtime counters inherited or created.

## Dependencies and integration points
It depends on the scheduler `Job`, `Task`, and `JobState` contracts. `LoadJob` extends it in this subset.

## Risks
The logger is initialized with `LoadJob.class`, which is odd for an abstract base and may mislabel logs for other future subclasses. State is mutable and not synchronized; subclasses are expected to be manipulated by the scheduler thread.

## Test signals
Tests should cover initial state, end-time setting on terminal state, verifying treated as running, done predicates, and subclass journal restore behavior for end time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/AbstractJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/FileIterable.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/FileIterable.java

## Purpose
`FileIterable` provides scheduler jobs with an iterable stream of `FileInfo` objects produced by `FileSystemMaster`. It supports full recursive listing or bounded partial listing and applies a caller-supplied filter, primarily for load jobs.

## Important APIs, types, and functions
The constructor captures `FileSystemMaster`, path, optional user, partial-listing flag, and filter. `iterator()` returns a new `FileIterator`. The inner iterator checks access, lists status through `listStatus`, supports `PARTIAL_LISTING_BATCH_SIZE = 100`, maintains `mStartAfter`, and tracks current-batch file and byte counts.

## Control flow
On construction the iterator sets `AuthenticatedClientUser`, checks access, then either fully lists recursively or begins partial listing. `hasNext()` and `next()` trigger another partial listing when the current iterator is exhausted. `partialListFileInfos` loops through list-status batches until it finds filtered results or reaches an empty batch, updating `startAfter` and disabling descendant-loaded checks after the first batch.

## State and persistence behavior
Iteration state is runtime-only: current batch list, current iterator, `startAfter`, and counters. No journal entries are produced. Full listing materializes the filtered list at once; partial listing bounds memory per batch.

## Dependencies and integration points
It depends on `FileSystemMaster`, list/check-access contexts, `AuthenticatedClientUser`, Alluxio exceptions converted to runtime exceptions, and wire `FileInfo`/block info. `LoadJobFactory` and `JournalLoadJobFactory` build it with `LoadJob.QUALIFIED_FILE_FILTER`.

## Risks
`checkAccess` sets the authenticated user but does not remove it in a finally block, unlike `listStatus`; this can leak thread-local user context. Partial listing updates `mStartAfter` to the last filtered file rather than always the last raw file when filtered results exist, which should be examined for skipped or repeated entries depending on list API semantics. Counters are reset to each batch, not cumulative.

## Test signals
Tests should cover access denied/not found conversion, full and partial listing, filters that skip many batches, empty results, user context cleanup, batch boundary `startAfter`, and file byte-count calculations for blocks without locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/FileIterable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JobFactoryProducer.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JobFactoryProducer.java

## Purpose
`JobFactoryProducer` centralizes creation of scheduler `JobFactory` instances from either client job requests or journal entries. In this source slice, it supports only load jobs.

## Important APIs, types, and functions
`create(JobRequest, FileSystemMaster)` returns a `LoadJobFactory` for `LoadJobRequest` or throws `IllegalArgumentException`. `create(Journal.JournalEntry, FileSystemMaster)` returns `JournalLoadJobFactory` when `entry.hasLoadJob()` or throws.

## Control flow
Both factory methods perform type/field discrimination and delegate all actual job construction to concrete factories.

## State and persistence behavior
The class is stateless and non-instantiable. It is part of persistence recovery because journal entries are converted back into job factories.

## Dependencies and integration points
It depends on `JobRequest`, `LoadJobRequest`, `FileSystemMaster`, journal proto entries, and scheduler `JobFactory`. Scheduler/job manager code uses it at submission and recovery boundaries.

## Risks
Adding new job types requires updating both overloads. Unknown journal entries include the entire entry in the exception, which may be verbose. There is no null validation here beyond downstream constructors.

## Test signals
Tests should cover load request creation, load journal creation, unknown request and unknown journal errors, and future job-type registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JobFactoryProducer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JournalLoadJobFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JournalLoadJobFactory.java

## Purpose
`JournalLoadJobFactory` reconstructs a `LoadJob` from a persisted `LoadJobEntry` journal record during scheduler recovery.

## Important APIs, types, and functions
The constructor captures the journal entry and `FileSystemMaster`. `create()` extracts optional user, bandwidth, partial listing, verify flag, job id, load path, state, and optional end time; builds a `FileIterable` with `LoadJob.QUALIFIED_FILE_FILTER`; creates `LoadJob`; restores state and end time.

## Control flow
Creation is linear. The factory reconstructs listing behavior from persisted options and then applies persisted scheduler state after object construction.

## State and persistence behavior
It is a recovery adapter: only fields present in `LoadJob.toJournalEntry()` can be restored. Runtime counters, retry queues, failed-file maps, and iterators are not recovered; a running job resumes from a fresh iterator.

## Dependencies and integration points
It depends on journal proto `Job.LoadJobEntry`, `FileSystemMaster`, `FileIterable`, `LoadJob`, and `JobState.fromProto`. Scheduler journal replay uses this factory through `JobFactoryProducer`.

## Risks
Restored running jobs may repeat work because runtime progress is not journaled. If file-system state changes between original submission and replay, the new iterator sees current metadata. Invalid or obsolete job state proto values depend on `JobState.fromProto` behavior.

## Test signals
Tests should verify all optional fields, state restoration, end-time restoration, filter use, partial listing propagation, and replay behavior for completed versus running jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/JournalLoadJobFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJob.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJob.java

## Purpose
`LoadJob` is a master scheduler job that loads persisted, completed files from UFS into Alluxio workers. It batches missing blocks, sends `LoadRequest`s to workers, tracks progress/failures, supports optional bandwidth limits and verification pass, and journals enough job metadata for recovery.

## Important APIs, types, and functions
The public job type is `TYPE = "load"`. `QUALIFIED_FILE_FILTER` selects non-folder, completed, persisted files not already 100 percent in Alluxio. Main APIs include `getDescription()`, `getBandwidth()`, `updateBandwidth()`, `isVerificationEnabled()`, `setVerificationEnabled()`, `failJob()`, `setJobSuccess()`, `getProgress()`, `getNextTask(WorkerInfo)`, `getNextBatchBlocks(int)`, `processResponse(LoadTask)`, `updateJob(Job<?>)`, `needVerification()`, `initiateVerification()`, and `toJournalEntry()`. Nested `LoadTask` runs a block-worker `load` RPC. Nested `LoadProgressReport` formats text or JSON progress.

## Control flow
The scheduler asks for tasks. `getNextBatchBlocks` lazily creates a file iterator, advances files and block ids, and emits blocks whose block info has no locations. Retry blocks are drained early only when the retry queue is near capacity or no new work remains. Worker responses subtract failed block lengths, retry retryable failures while the job remains healthy and retry capacity permits, and record per-file failure messages for non-retryable or unhealthy failures. Execution/cancellation/interruption exceptions route blocks back to retry or failure and preserve interrupt status. Verification resets current counters and iterator state for another pass when the previous pass is complete.

## State and persistence behavior
The job stores configuration (`path`, `user`, `jobId`, bandwidth, partial listing, verification flag), runtime queues/counters, failed file summaries, current iterators, state, and failure reason. `toJournalEntry()` persists path, state, partial listing, verify, job id, optional user, optional bandwidth, and optional end time. Runtime progress, retry blocks, loaded bytes, and failures are not journaled, so recovery reconstructs a fresh job over current file metadata.

## Dependencies and integration points
It depends on scheduler `Job`/`Task`, worker `BlockWorkerClient.load`, gRPC load messages, `FileIterable`, metrics, Jackson for JSON reports, Alluxio wire file/block/worker info, and configuration `JOB_BATCH_SIZE`. It integrates with the master scheduler and worker block loading RPC path.

## Risks
The class is explicitly not thread-safe and assumes scheduler-thread mutation, though it uses atomics for report counters. `isHealthy` relies on operator precedence; as written, the failure ratio can make a failed-state job appear healthy if the ratio is low, so callers should verify intended grouping. `mTotalByteCount` can be inaccurate for retries and verification as the comment notes. Recovery repeats work because runtime progress is not persisted. Failed-file map keys use UFS path and retain only the first failure message per file.

## Test signals
Tests should cover filtering, batching across files, retry threshold/capacity, response statuses, exception paths, health threshold edge cases, verification reset, progress text/JSON, metrics increments, journal serialization, update-job semantics, and recovery through `JournalLoadJobFactory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJobFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJobFactory.java

## Purpose
`LoadJobFactory` creates new `LoadJob` instances from client `LoadJobRequest`s. It translates gRPC load options and authenticated user context into the scheduler job model.

## Important APIs, types, and functions
The constructor stores `LoadJobRequest` and `FileSystemMaster`. `create()` extracts path, optional bandwidth, partial-listing flag, verify flag, authenticated user name, creates a filtered `FileIterable`, generates a UUID job id, and returns a `LoadJob`.

## Control flow
The factory reads request options, interprets `has*` flags, captures user via `AuthenticatedClientUser.getOrNull()`, and delegates iteration to `FileIterable`.

## State and persistence behavior
The factory is short-lived and stateless after creation. The generated job id and options become the job state that `LoadJob` journals later.

## Dependencies and integration points
It depends on `LoadJobRequest`, `LoadJobPOptions`, `FileSystemMaster`, `AuthenticatedClientUser`, `User`, UUID generation, and the scheduler factory contract. It is selected by `JobFactoryProducer`.

## Risks
If no authenticated user is set, the job runs with an empty user optional; downstream access/listing behavior must handle that. The user is fetched twice, which is usually harmless but assumes the thread-local does not change. Invalid bandwidth values are rejected by the `LoadJob` constructor rather than here.

## Test signals
Tests should cover optional bandwidth, partial listing, verify flag, user present/absent, UUID uniqueness expectation, filter wiring, and invalid request option propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/job/LoadJobFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/DefaultJournalMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/DefaultJournalMaster.java

## Purpose
`DefaultJournalMaster` implements journal management RPCs for master and job-master processes. It exposes embedded-journal quorum operations and node-state reporting through a master service.

## Important APIs, types, and functions
The constructor captures `JournalDomain`, `JournalSystem`, and `PrimarySelector` from `MasterContext`. `getQuorumInfo()`, `removeQuorumServer(NetAddress)`, `transferLeadership(NetAddress)`, `resetPriorities()`, and `getTransferLeaderMessage(String)` delegate to `RaftJournalSystem` after `checkQuorumOpSupported()`. `getNodeState()` returns primary selector state. `getName()` and `getServices()` integrate with the master service registry.

## Control flow
Quorum operations first verify the journal system is `RaftJournalSystem` and that the local process is the Raft leader. Unsupported journal type or non-leader calls throw `UnsupportedOperationException`. Service registration wraps `JournalMasterClientServiceHandler` with `ClientContextServerInjector`.

## State and persistence behavior
This master is `NoopJournaled`; it does not persist independent state. It manipulates the embedded journal subsystem, whose Raft state is persisted elsewhere.

## Dependencies and integration points
It depends on `AbstractMaster`, `MasterContext`, `RaftJournalSystem`, `PrimarySelector`, gRPC service definitions, and client-context injection. CLI/admin clients reach it through `JournalMasterClientServiceHandler`.

## Risks
Quorum operations must be routed to the current Raft leader or they fail. The exception message says quorum operations are supported for journal type `EMBEDDED` when rejecting non-Raft systems, which can be confusing wording. Casting after support checks must remain aligned with journal-system implementations.

## Test signals
Tests should cover UFS journal rejection, non-leader rejection, successful Raft delegation, node-state response, service map contents, and handler exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/DefaultJournalMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMaster.java

## Purpose
`JournalMaster` defines the master-facing contract for journal administration. It covers quorum inspection/mutation, leadership transfer, priority reset, transfer status messages, and node-state inspection.

## Important APIs, types, and functions
Methods are `getQuorumInfo()`, `removeQuorumServer(NetAddress)`, `transferLeadership(NetAddress)`, `resetPriorities()`, `getTransferLeaderMessage(String)`, and `getNodeState()`. It extends the generic `Master` interface.

## Control flow
The interface has no implementation flow, but method documentation states quorum operations are supported only for embedded journals, while `getNodeState` works for both UFS and embedded journals.

## State and persistence behavior
No state is defined here. Implementations decide whether state is journaled; `DefaultJournalMaster` is no-op journaled and delegates to the journal system.

## Dependencies and integration points
It depends on gRPC response/address types and the `Master` lifecycle/service contract. Client service handlers and factories target this interface.

## Risks
The interface mixes universally available node-state calls with embedded-only quorum calls, so clients must handle unsupported-operation errors. Transfer leadership returns a string transfer id rather than a structured status.

## Test signals
Contract tests should validate client behavior for supported and unsupported journal types, IOException propagation, and transfer-message lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterClientServiceHandler.java

## Purpose
`JournalMasterClientServiceHandler` is the gRPC server adapter for `JournalMaster` client RPCs. It translates protobuf requests into interface calls and sends protobuf responses through `RpcUtils`.

## Important APIs, types, and functions
It extends `JournalMasterClientServiceGrpc.JournalMasterClientServiceImplBase`. RPC methods include `getQuorumInfo`, `removeQuorumServer`, `transferLeadership`, `resetPriorities`, `getTransferLeaderMessage`, and `getNodeState`.

## Control flow
Each override wraps a lambda in `RpcUtils.call`, supplying logging metadata and the response observer. Mutating RPCs build default response instances after successful delegation. `transferLeadership` wraps the returned transfer id in `TransferLeadershipPResponse`.

## State and persistence behavior
The handler stores only a `JournalMaster` reference. Persistence is entirely in the delegated journal system.

## Dependencies and integration points
It integrates with generated gRPC stubs, `RpcUtils`, and `JournalMaster`. The handler is installed by `DefaultJournalMaster.getServices()`.

## Risks
All authorization/authentication behavior comes from service registration interceptors and `RpcUtils`, not this handler. Unsupported operations and IO failures are surfaced through RPC error conversion; clients need to handle them.

## Test signals
Tests should verify request field mapping, response construction, exception-to-RPC behavior, logging method names, and every RPC delegating exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterClientServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterFactory.java

## Purpose
`JournalMasterFactory` creates and registers the master-domain `JournalMaster` during master startup.

## Important APIs, types, and functions
It implements `MasterFactory`. `isEnabled()` always returns true. `getName()` returns `Constants.JOURNAL_MASTER_NAME`. `create(MasterRegistry, MasterContext)` constructs `DefaultJournalMaster` with `JournalDomain.MASTER`, registers it under `JournalMaster.class`, and returns it.

## Control flow
Creation is unconditional and logs the class name before registration.

## State and persistence behavior
The factory is stateless. The created journal master is no-op journaled and delegates to the journal system.

## Dependencies and integration points
It depends on master registry/context/factory APIs, constants, `JournalDomain`, and `DefaultJournalMaster`. Master bootstrap uses it in the factory list.

## Risks
This factory only creates the master-domain journal master; job-master domain creation must be handled elsewhere. Since `isEnabled` is unconditional, failures in journal master creation affect all master startups.

## Test signals
Tests should cover enabled/name values, registry insertion, returned instance type, journal domain passed to `DefaultJournalMaster`, and logging is not functionally required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/JournalMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/AbstractJournalDumper.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/AbstractJournalDumper.java

## Purpose
`AbstractJournalDumper` is the base for offline journal dump tools. It owns common input/output paths and converts checkpoint streams into human-readable files, including compound and RocksDB-backed inode checkpoints.

## Important APIs, types, and functions
The constructor captures master name, sequence range, input/output dirs, checkpoint output prefix, and edits file path, and creates the output directory. Subclasses implement `dumpJournal()`. `readCheckpoint(CheckpointInputStream, Path)` dispatches to compound, Rocks single, or regular checkpoint readers. `readCompoundCheckpoint`, `readRocksCheckpoint`, and `readRegularCheckpoint` perform the concrete conversions.

## Control flow
Compound checkpoints are recursively expanded by reading named entries and resolving child paths. Rocks checkpoints restore into a temporary `RocksInodeStore`, iterate inode views, and print proto forms separated by a dashed line. Regular checkpoints delegate to the checkpoint type's human-readable parser. Temporary Rocks DB directories are removed in `finally`.

## State and persistence behavior
This tool reads persisted journal/checkpoint state and writes text output under the requested output directory. It does not mutate the source journal, except for creating and deleting a temporary local Rocks database during conversion.

## Dependencies and integration points
It depends on checkpoint formats, `RocksInodeStore`, `CloseableIterator`, path/file utilities, and Java I/O. `UfsJournalDumper` and `RaftJournalDumper` subclass it.

## Risks
Large Rocks checkpoints can be expensive to restore and dump. Output files are overwritten if paths collide. Cleanup failure could leave temporary `*-rocks-db` directories. Recursive compound checkpoint handling must preserve names to avoid overwriting nested outputs.

## Test signals
Tests should cover regular checkpoint parsing, compound recursion, Rocks checkpoint restore/dump/cleanup, output directory creation, malformed checkpoint errors, and path collision scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/AbstractJournalDumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/JournalTool.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/JournalTool.java

## Purpose
`JournalTool` is the command-line entry point for converting Alluxio journals into human-readable files. It selects the UFS or embedded journal dumper from configuration and parses common dump options.

## Important APIs, types, and functions
`main(String[])` parses arguments, handles help, and calls `dumpJournal()`. CLI options are `help`, `master`, `start`, `end`, `inputDir`, and `outputDir`. `dumpJournal()` selects `UfsJournalDumper` for `JournalType.UFS` and `RaftJournalDumper` for `JournalType.EMBEDDED`. `parseInputArgs` fills static option fields. `usage()` prints Apache CLI help.

## Control flow
Argument parsing uses `DefaultParser`; parse failure prints usage and exits failed. Help exits successfully. The input directory defaults to `MASTER_JOURNAL_FOLDER`; output defaults to `journal_dump-${timestamp}`. Unsupported journal types print an error and return.

## State and persistence behavior
The tool stores parsed options in static fields for the process lifetime and writes dump output under `sOutputDir`. It reads but should not mutate journal state.

## Dependencies and integration points
It depends on Alluxio configuration, `JournalType`, Apache Commons CLI, runtime constants, and the two dumper implementations. Operators use it offline for debugging/recovery inspection.

## Risks
`main` catches `Exception` around dump but not all `Throwable` even though `dumpJournal` declares `Throwable`; serious errors may escape. Static parsed state makes repeated invocation in the same JVM awkward for tests. The tool relies on process configuration to decide journal type, so an incorrect config can select the wrong reader for an input dir.

## Test signals
Tests should cover option parsing defaults, help and parse failures, UFS/embedded dumper selection, unsupported type behavior, absolute path normalization, start/end parsing including `Long.MAX_VALUE`, and repeated parse invocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/JournalTool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/RaftJournalDumper.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/RaftJournalDumper.java

## Purpose
`RaftJournalDumper` implements offline dumping for embedded/Raft journals. It reads the local Ratis snapshot and log files directly without contacting a running quorum.

## Important APIs, types, and functions
`dumpJournal()` validates the input directory and calls `readFromDir()`. `readRatisSnapshotFromDir()` finds the latest snapshot and converts snapshot files through `readCheckpoint`. `readRatisLogFromDir()` opens Ratis storage, scans log segment paths, parses state-machine log data into `JournalEntry`, and writes selected entries. `writeSelected(PrintStream, JournalEntry)` handles aggregate and empty entries. `isSelected` filters by sequence number and master association.

## Control flow
The dumper recovers Raft storage from the journal dir, reads snapshot first, then log segments. For log entries, it ignores non-state-machine entries, parses journal entries, recursively expands aggregated journal entries, drops empty snapshotting entries, checks single-operation invariants, and writes entries whose sequence number is within `[mStart, mEnd)` and whose associated master matches `mMaster`.

## State and persistence behavior
It reads persisted Ratis snapshots and logs and writes `edits.txt` plus checkpoint directories under the output path. Snapshot MD5 is verified after reading. It does not append to or mutate Raft logs.

## Dependencies and integration points
It depends on Apache Ratis storage/log APIs, Alluxio Raft journal utilities, `SnapshotDirStateMachineStorage`, `OptimizedCheckpointInputStream`, journal proto parsing, `JournalEntryAssociation`, and `AbstractJournalDumper`.

## Risks
Direct offline reading may produce stale or partial state if used while a cluster is active. `readRatisLogFromDir` logs and swallows exceptions, so dump output can be incomplete without failing the command. Master association failures are silently filtered. Snapshot directory naming includes last-modified time, so repeated dumps can create different output paths.

## Test signals
Tests should cover missing input dir, snapshot-only and log-only journals, aggregate entries, empty entries, sequence filtering, master filtering, MD5 verification failures, corrupt log segment handling, and exception visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/RaftJournalDumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/UfsJournalDumper.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/UfsJournalDumper.java

## Purpose
`UfsJournalDumper` implements journal dumping for legacy UFS-backed journals. It reads checkpoints and edit logs with `UfsJournalReader` and writes human-readable checkpoint files plus `edits.txt`.

## Important APIs, types, and functions
The constructor delegates common setup to `AbstractJournalDumper`. `dumpJournal()` creates a `UfsJournalSystem` at the input URI, creates a journal for a `NoopMaster` named by `mMaster`, opens `UfsJournalReader` at `mStart`, and loops until done or `mEnd`. `getJournalLocation(String)` ensures a trailing slash and parses a URI.

## Control flow
The reader state machine emits `CHECKPOINT`, `LOG`, or `DONE`. Checkpoints are read through `readCheckpoint` into `checkpoints-${nextSequenceNumber}`. Log entries are printed to `edits.txt` preceded by an 80-character separator. Unknown reader states throw.

## State and persistence behavior
The dumper is read-only against the journal and writes output files under the dump directory. It uses try-with-resources for journal, output stream, and reader cleanup.

## Dependencies and integration points
It depends on `UfsJournalSystem`, `UfsJournal`, `UfsJournalReader`, `NoopMaster`, checkpoint streams, journal protos, and URI/path handling. It is selected by `JournalTool` when `MASTER_JOURNAL_TYPE` is `UFS`.

## Risks
Input URI parsing wraps syntax errors in `RuntimeException`. The dumper prints all log entries from the selected master journal reader rather than doing additional master association filtering. Very large journals produce large single `edits.txt` files.

## Test signals
Tests should cover URI normalization, checkpoint and log state handling, end-sequence stopping, unknown state failure, missing/corrupt UFS journal behavior, and output separator formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/UfsJournalDumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/AlluxioMasterRestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/AlluxioMasterRestServiceHandler.java

## Purpose
`AlluxioMasterRestServiceHandler` is the JAX-RS REST and web-UI data handler for the master process. It serves general master info, overview, browse, logs, configuration, workers, masters, mount table, metrics, and log-level updates.

## Important APIs, types, and functions
Endpoints include `GET /master/info`, `webui_init`, `webui_overview`, `webui_browse`, `webui_data`, `webui_logs`, `webui_config`, `webui_workers`, `webui_masters`, `webui_mounttable`, `webui_metrics`, and `POST /master/logLevel`. Internal helpers compute capacity, configuration, metrics, mount points, tier capacity, and UFS capacity. `isMounted(String)` filters per-UFS metrics to currently mounted UFS URIs.

## Control flow
The constructor retrieves `AlluxioMasterProcess`, `BlockMaster`, `FileSystemMaster`, `MetaMaster`, and a filesystem client from servlet context. Endpoints wrap work in `RestUtils.call`. Overview composes cluster capacity, config check status, storage tiers, root UFS capacity, journal warnings, checkpoint warnings, Raft role, leader id, and system status gauges. Browse resolves paths, handles file preview and directory listing with pagination. Logs list allowed log filenames or read a 5 KB window from a selected log file. Metrics combines gauges/counters, cache-hit estimates, per-UFS metrics filtered by mounts, time-series metrics, and journal disk metrics.

## State and persistence behavior
The handler does not persist state. It reads live master state, metrics, configuration, filesystem metadata, and log files. `logLevel` mutates runtime logging level. Browse and data endpoints may set `AuthenticatedClientUser` to the server user when security is enabled and no user is present.

## Dependencies and integration points
It depends on master process services, block/file/meta masters, file-system client APIs, metrics registry, web UI wire objects, configuration, security utilities, path utilities, and JAX-RS/Swagger annotations. It is mounted by `MasterWebServer`.

## Risks
Many metrics are assumed present and cast to specific types; missing gauges/counters can cause runtime failures. Browse/data pagination validates parse and arithmetic but still uses list materialization, which can be expensive. Log reading protects against arbitrary paths by taking only `new File(requestFile).getName()`, but log-level changes are powerful runtime operations. Some security code sets authenticated user without obvious cleanup in these endpoint lambdas.

## Test signals
Tests should cover each endpoint response shape, disabled `WEB_FILE_INFO_ENABLED`, browse file and directory modes, pagination errors, log filename sanitization, missing metrics behavior, mounted-UFS metric filtering, journal warning population, security user context handling, and log-level mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/AlluxioMasterRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DailyMetadataBackup.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DailyMetadataBackup.java

## Purpose
`DailyMetadataBackup` schedules automatic daily backups of primary master metadata at a configured UTC time and prunes old backup files according to retention settings.

## Important APIs, types, and functions
The constructor captures `MetaMaster`, scheduler, `UfsManager`, backup directory, retained-file count, and whether root UFS is local. `start()` schedules `dailyBackup()` at fixed daily rate. `dailyBackup()` invokes `MetaMaster.backup` with `StateLockOptions.defaultsForDailyBackup()` and then `deleteStaleBackups()`. `stop()` cancels the scheduled future and shuts down the executor.

## Control flow
`getTimeToNextBackup()` parses `MASTER_DAILY_BACKUP_TIME` as UTC `H:mm`, schedules today if still future, otherwise tomorrow. Backup request sets target directory and local-filesystem option based on root UFS type. Retention lists backup dir, filters files matching `BackupManager.BACKUP_FILE_PATTERN`, sorts by timestamp from filename, and deletes oldest beyond the configured retention count.

## State and persistence behavior
The class owns scheduling state (`ScheduledFuture`) and writes backup files through meta master backup machinery. It deletes stale persisted backup files from the configured backup directory.

## Dependencies and integration points
It depends on `MetaMaster.backup`, `UfsManager`, `UnderFileSystem`, backup manager filename pattern, Alluxio configuration, path utilities, and scheduled executor services. `DefaultMetaMaster` starts it only on primary when daily backup is enabled.

## Risks
Retention cleanup assumes backup filenames contain sortable timestamps and uses a `TreeMap<Instant, String>` comparator that treats equal instants as equal keys, potentially dropping duplicates. `ufs.listStatus(mBackupDir)` may return null or throw depending on UFS behavior. Backup and cleanup catch `Throwable`, log, and continue, so failures rely on log monitoring.

## Test signals
Tests should cover UTC schedule calculation, local versus non-local backup option, successful backup logging, backup failure isolation, retention deletion count/order, nonmatching files preserved, duplicate timestamp behavior, and stop cancellation/shutdown timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DailyMetadataBackup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DefaultMetaMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DefaultMetaMaster.java

## Purpose
`DefaultMetaMaster` is the core implementation of Alluxio's meta master. It manages cluster identity, master/proxy liveness, configuration reporting and dynamic updates, path-level configuration, backup roles, journal checkpointing, daily backup, update checks, and journal-space monitoring.

## Important APIs, types, and functions
It implements `MetaMaster` and extends `CoreMaster`. The nested `State` journals the cluster id under `CheckpointName.CLUSTER_INFO`. Service APIs include `getServices()`, `getStandbyServices()`, lifecycle `start(Boolean)`/`stop()`, backup methods, `checkpoint()`, configuration getters/hash/update, path configuration mutation, master id/register/heartbeat, proxy heartbeat/status, journal entry iteration/processing/reset, and liveness executors for lost masters/proxies and config report logging.

## Control flow
Construction registers worker configuration listeners with `BlockMaster`, initializes path properties and cluster state, and conditionally creates `JournalSpaceMonitor` for embedded journals on Linux. On primary start it registers the leader master's config, starts heartbeat threads for lost standby detection, config report logging, lost proxy detection, optional daily backups, optional journal-space monitor, initializes and journals a new cluster id if missing, optionally starts update checking, and uses `BackupLeaderRole`. On standby start it may run `MetaMasterSync` to heartbeat to the leader and may use `BackupWorkerRole`. Master ids are reused for known/lost addresses or randomly generated until unique. Heartbeats update mutable `MasterInfo`; timeouts move entries to lost sets.

## State and persistence behavior
Persisted state is cluster id plus path properties via journal entries. Live master/proxy sets, lost sets, config stores, backup role, newer-version flag, and monitor data are in-memory and rebuilt from runtime registration/heartbeat. `checkpoint()` delegates to `mJournalSystem.checkpoint` with the state lock manager. Dynamic configuration updates mutate runtime `Configuration` and notify `ReconfigurableRegistry`.

## Dependencies and integration points
It depends on `CoreMasterContext`, `BlockMaster`, journal system/context, backup roles, configuration stores/checker, path properties, heartbeat framework, UFS manager, Raft/UFS journal type config, OS detection, network utilities, generated meta-master service handlers, and Alluxio wire/gRPC config/status types.

## Risks
The class is `@NotThreadSafe` but heartbeat executors, RPC handlers, and maps/sets interact concurrently; mutable `IndexedSet` access needs careful synchronization. `mBackupRole` is added to services in `getServices`, so lifecycle ordering must ensure it is initialized before service discovery. Dynamic config updates only allow dynamic keys when enabled but parsing and reconfiguration failures are per-key. Master/proxy lost detection relies on local clock and heartbeat intervals.

## Test signals
Tests should cover primary and standby startup branches, cluster id journaling/replay, service registration, backup role selection, daily backup enablement, journal monitor condition, master id reuse/lost recovery, heartbeat timeout movement, proxy active/lost/delete transitions, config report/hash, path config journaling, dynamic config update success/failure, and checkpoint delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DefaultMetaMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/JournalSpaceMonitor.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/JournalSpaceMonitor.java

## Purpose
`JournalSpaceMonitor` is a heartbeat executor that monitors free disk space for the embedded journal path on Linux and emits warnings/metrics when capacity is low.

## Important APIs, types, and functions
The configuration constructor reads `MASTER_JOURNAL_FOLDER` and `MASTER_JOURNAL_SPACE_MONITOR_PERCENT_FREE_THRESHOLD`. `getRawDiskInfo()` executes `df -k -P -T`. `getDiskInfo()` parses `df` output into `JournalDiskInfo`, updates an atomic metric-info map, and registers free-bytes and free-percent gauges per disk. `getJournalDiskWarnings()` returns warning strings below threshold. `heartbeat(long)` logs warnings.

## Control flow
Construction validates that the journal path exists. Each disk-info read shells out, skips the header, tokenizes lines, parses size fields, records metric source data, and registers gauges that read the latest `AtomicReference` map. Warning generation filters current disk info by percent available.

## State and persistence behavior
State is in-memory only: journal path, threshold, and latest disk info for metrics. It does not persist state or modify disk contents.

## Dependencies and integration points
It depends on POSIX `df`, `ShellUtils`, `MetricsSystem`, `JournalDiskInfo`, Alluxio URI escaping, and heartbeat framework. `DefaultMetaMaster` starts it only for embedded journals on Linux; REST metrics/overview endpoints read it.

## Risks
The parser assumes `df -P -T` column layout and indexes `data.get(6)` while filtering only `data.size() >= 6`, which looks like an off-by-one guard and should require at least 7 tokens. Shelling out can be slow or unavailable. Gauge names include escaped device URIs and remain registered even if devices change.

## Test signals
Tests should cover constructor path validation, df parse success/failure, multiple filesystems, short/malformed lines, threshold warnings, metric gauge values after refresh, and heartbeat logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/JournalSpaceMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MasterInfo.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MasterInfo.java

## Purpose
`MasterInfo` is the mutable in-memory record for a standby or lost master known to the primary meta master. It tracks identity, address, heartbeat time, lifecycle times, version/revision, and journal checkpoint progress.

## Important APIs, types, and functions
The constructor requires id and address and initializes last-updated time. Getters expose all fields. Setters update start time, lose-primacy time, version, revision, last checkpoint time, and journal entries since checkpoint. `updateLastUpdatedTimeMs()` records current system time. `toString()` prints diagnostic fields.

## Control flow
There is no complex flow; `DefaultMetaMaster` mutates records on register, heartbeat, lost detection, and lost-master recovery.

## State and persistence behavior
This class is `@NotThreadSafe` and in-memory only. Standby master info is not journaled; it is rebuilt by standby registration/heartbeat.

## Dependencies and integration points
It depends on wire `Address` and Guava preconditions/toString helper. It integrates with `DefaultMetaMaster` indexed sets and conversion to wire master info for RPC/REST/UI responses.

## Risks
No synchronization inside the class means callers must guard concurrent reads/writes. Using `System.currentTimeMillis()` directly makes tests time-sensitive unless wrapped at caller level. Version/revision default to empty strings.

## Test signals
Tests should cover constructor validation, timestamp update, setter/getter values, wire conversion in `DefaultMetaMaster`, and concurrent access assumptions in liveness detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MasterInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMaster.java

## Purpose
`MetaMaster` defines the central metadata/control-plane interface for Alluxio masters. It combines backup operations with master lifecycle/service behavior and exposes cluster configuration, identity, liveness, checkpoint, dynamic configuration, and proxy status operations.

## Important APIs, types, and functions
The interface includes cluster/config APIs (`getClusterID`, `getConfigCheckReport`, `getConfiguration`, `getConfigHash`, `getJournalSpaceMonitor`), path configuration mutations, version availability flag, master/worker address accessors, master id/register/heartbeat, safe mode, checkpoint, dynamic `updateConfiguration`, proxy heartbeat, and `listProxyStatus`. It extends `BackupOps` and `Master`.

## Control flow
The interface documents expected RPC flows: standby masters obtain/register ids and heartbeat to the leader; proxies heartbeat to the primary; clients request config/report/master info; admins trigger checkpoints and backups.

## State and persistence behavior
No state is stored in the interface. `DefaultMetaMaster` persists cluster id and path configuration while keeping liveness/config stores in memory.

## Dependencies and integration points
It depends on gRPC options/commands, Alluxio wire config/status types, backup ops, master lifecycle, and address types. Client, master, proxy, REST, and configuration service handlers all depend on this contract.

## Risks
The interface is broad, mixing admin, liveness, backup, configuration, and proxy APIs. Implementations must be careful about which methods are valid only on primary, which mutate journaled state, and which are safe on standby.

## Test signals
Contract tests should cover primary/standby behavior, RPC handler mappings, checkpoint/backup error propagation, path config journaling, dynamic config updates, proxy status lifecycle, and configuration hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterClientServiceHandler.java

## Purpose
`MetaMasterClientServiceHandler` is the gRPC adapter for client-facing meta-master operations: backups, backup status, config reports, filtered master info, checkpoint, and proxy status listing.

## Important APIs, types, and functions
It extends `MetaMasterClientServiceGrpc.MetaMasterClientServiceImplBase`. RPC methods are `backup`, `getBackupStatus`, `getConfigReport`, `getMasterInfo`, `checkpoint`, and `listProxyStatus`. `getMasterInfo` fills fields selected by `MasterInfoField` filters, defaulting to all enum values.

## Control flow
Each RPC uses `RpcUtils.call`. `backup` uses `StateLockOptions.defaultsForShellBackup()`. `getMasterInfo` switches over requested fields and pulls cluster id, leader address, master addresses, RPC/web ports, safe mode, uptime, worker addresses, ZooKeeper addresses, Raft addresses, Raft-journal boolean, and primary/standby/lost master versions. Unknown fields are logged.

## State and persistence behavior
The handler stores only the `MetaMaster` reference. Backup and checkpoint RPCs can trigger persisted backup files or journal checkpoints through the delegated meta master; info/report RPCs are read-only.

## Dependencies and integration points
It depends on generated gRPC/protobuf types, `RpcUtils`, `RuntimeConstants`, `Configuration`, `RaftJournalSystem`, `StateLockOptions`, and `MetaMaster`. `DefaultMetaMaster.getServices()` registers it with client-context injection.

## Risks
The default "all enum values" loop may include future enum constants that need explicit support. Raft address extraction depends on the journal system being a `RaftJournalSystem`. Primary master version state is hardcoded as `"PRIMARY"` and standby/lost states are derived from meta-master arrays.

## Test signals
Tests should verify every `MasterInfoField`, filtered versus unfiltered behavior, ZooKeeper config parsing, Raft and non-Raft cases, backup/checkpoint delegation, proxy status response, unknown enum logging, and RPC error conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMasterClientServiceHandler.java -->
