# Research: subset-b-000484

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeTest.java

## Purpose
`InodeTreeTest` is the main unit-level contract for Alluxio master inode-tree behavior. It validates root initialization, recursive path creation, file/directory metadata, path and id lookup, child iteration ordering, pin propagation, deletion, and journal checkpoint/replay semantics.

## Important APIs, Types, and Functions
The parameterized test runs against `CachingInodeStore` over Rocks and heap stores, plus raw `HeapInodeStore` and `RocksInodeStore`. It exercises `InodeTree.initializeRoot`, `createPath`, `inodeIdExists`, `inodePathExists`, `lockFullInodePath`, `getPath`, `getPathInodeNames`, `getDescendants`, `deleteInode`, `setPinned`, `getJournalEntryIterator`, and `processJournalEntry`. Helpers create paths under `WRITE_EDGE` locks and fetch mutable inodes from `InodeStore`.

## Control Flow, State, and Persistence
Each test starts a `MasterRegistry`, metrics master, block master, directory id generator, mount table, lock manager, and fresh inode tree. Creation flows lock the target path, call `createPath`, then verify created inode lists, parent ids, modes, owner/group inheritance, modification time updates, and exception messages. Journal tests stream current tree entries in breadth-first order and replay inode journal entries into a reset tree.

## Dependencies and Integration Points
The test integrates the inode tree with block id allocation, metastore implementations, mount table construction, authorization configuration, journal contexts, and `RpcContext.NOOP`. It is also a cross-store compatibility test because the same assertions must pass for heap, Rocks, and caching inode stores.

## Risks
The test relies on deterministic inode ids and child ordering across stores. Timing assertions use sleeps to distinguish modification times. The journal replay test expects descendants to become visible as entries are processed, so changes to parent-child linking or journal entry ordering can break recovery behavior.

## Test Signals
Strong signals include recursive create failures, block-size validation, file-under-file traversal errors, deleted inode lookup, prefix/from child iterators, nested child iteration after deletion, pin set size, checkpoint contents, and replay of empty owner/group metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InodeTreeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InvalidationSyncCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InvalidationSyncCacheTest.java

## Purpose
This test focuses on `UfsSyncPathCache` invalidation semantics after interval-based invalidation callers were removed. It establishes how explicit sync notifications and invalidations interact for root, child, and multi-level paths.

## Important APIs, Types, and Functions
The test uses `UfsSyncPathCache.recordStartSync`, `notifySyncedPath`, `notifyInvalidation`, and `shouldSyncPath`, with `DescendantType.NONE`, `ONE`, and `ALL`. It also configures `MASTER_UFS_PATH_CACHE_CAPACITY` and observes cache eviction through the constructor callback and direct `mItems.cleanUp()`.

## Control Flow, State, and Persistence
A mocked `Clock` advances an `AtomicLong` on `millis()` calls, making sync timestamps deterministic. Tests first assert unsynced paths require sync, then notify syncs at different descendant depths and invalidate paths to verify upward and downward freshness propagation. Eviction fills a cache under `/one`, then checks evicted paths require sync while retained entries stay valid.

## Dependencies and Integration Points
The cache depends on Alluxio URI ancestry, global configuration, Caffeine-like cache cleanup behavior, and `DescendantType` semantics shared by metadata sync/listing APIs.

## Risks
The tests encode intentionally conservative invalidation behavior: after invalidating and resyncing a child, the root can still require descendant sync. This is called out as an improvement opportunity and is a compatibility risk for future cache optimizations.

## Test Signals
Coverage includes direct validation, one-level propagation, multi-level propagation, parent invalidation invalidating descendants, sync interval coexistence, and invalidations racing with in-progress syncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/InvalidationSyncCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LazyUfsBlockLocationCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LazyUfsBlockLocationCacheTest.java

## Purpose
`LazyUfsBlockLocationCacheTest` validates lazy loading and invalidation of UFS block locations through the mount table.

## Important APIs, Types, and Functions
The test constructs `MasterUfsManager`, `MountTable`, `MountInfo`, and `LazyUfsBlockLocationCache`, then calls `get(blockId)`, `get(blockId, fileUri, offset)`, and `invalidate(blockId)`.

## Control Flow, State, and Persistence
A temporary local UFS is mounted at `/mnt`; the test creates a UFS file, fetches its native locations from the local `UnderFileSystem`, confirms a cold cache miss, lazily resolves locations through the Alluxio path, confirms the warm cache hit, and finally invalidates the entry.

## Dependencies and Integration Points
This links block-location caching to `UnderFileSystem.Factory`, mount-specific UFS configuration, mount resolution, and local UFS file-location APIs.

## Risks
The test assumes the local UFS returns stable file locations. It validates only one block id and one offset, so multi-block, remote UFS, and mount-resolution failure behavior are outside this file.

## Test Signals
The key signal is that cache misses do not precompute, lazy lookup matches UFS locations, cached lookup returns the same list, and invalidation clears the block id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LazyUfsBlockLocationCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LockedInodePathTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LockedInodePathTest.java

## Purpose
`LockedInodePathTest` is the detailed lock-state contract for path traversal and extension. It validates which inode locks and edge locks are held for existing, partially missing, root, child, and descendant paths.

## Important APIs, Types, and Functions
The test constructs `LockedInodePath` with `LockPattern.READ`, `WRITE_INODE`, and `WRITE_EDGE`, then exercises `traverse`, `fullPathExists`, inode accessors, `removeLastInode`, `addNextInode`, `downgradeToRead`, `lockChild`, `lockDescendant`, and `lockFinalEdgeWrite`. It also uses `FileSystemMergeJournalContext` to test flush behavior.

## Control Flow, State, and Persistence
Tests create canonical `/a/b/c` fixtures from `BaseInodeLockingTest`, traverse paths, then assert both semantic path state and exact held locks through helper checks. Adding or removing path components moves write-edge ownership forward or releases final inode state. Merge-journal mode verifies flushes when adding intermediate inodes, downgrading, and closing.

## Dependencies and Integration Points
The file integrates `LockedInodePath` with `InodeStore`, `InodeLockManager`, `JournalContext`, global merge-inode-journals configuration, and Alluxio path parsing.

## Risks
This suite is sensitive to lock ordering and lock ownership details, which is intentional because these are deadlock and race-prevention contracts. Journal flush counts depend on exact implementation timing.

## Test Signals
Signals include existing vs missing path accessors, root lock special cases, implicit locks on descendants, child lock release after close, write-edge downgrades, final-edge locking for missing paths, and merge journal flush counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/LockedInodePathTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MountTableTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MountTableTest.java

## Purpose
`MountTableTest` validates path-to-UFS mount resolution, reverse resolution, nested mount behavior, deletion constraints, read-only mount enforcement, and mount-info lookup.

## Important APIs, Types, and Functions
The tests exercise `MountTable.add`, `delete`, `resolve`, `reverseResolve`, `getMountPoint`, `isMountPoint`, `containsMountPoint`, `checkUnderWritableMountPoint`, `getMountTable`, and `getMountInfo`.

## Control Flow, State, and Persistence
Each test starts with a root mount to `s3a://bucket/`. It adds mounts under `/mnt`, verifies longest-prefix resolution and reverse resolution, rejects duplicate Alluxio mount points and conflicting UFS prefixes, checks nested mount deletion ordering, and validates read-only access exceptions for mount roots and descendants.

## Dependencies and Integration Points
The test uses mocked `UfsManager`, local UFS clients, `MountContext`, `MountInfo`, `AlluxioURI`, and `ExceptionMessage` text. It covers both path-only and fully qualified Alluxio URIs.

## Risks
Mount conflict rules are path-prefix sensitive and scheme-aware. Nested mount deletion must avoid removing a parent while child mounts remain. Reverse resolution returning `null` for unmounted UFS paths is an important boundary.

## Test Signals
Signals include duplicate mount rejection, UFS prefix conflict rejection, root fallback resolution, nested longest-prefix matching, `containsMountPoint` with include-self toggles, read-only denial, writable success, copy equality from `getMountTable`, and lookup by mount id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MountTableTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeDirectoryTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeDirectoryTest.java

## Purpose
This file tests the mutable directory inode data model: identity, type flags, deleted state, timestamps, naming, parent linkage, permissions, and client-facing `FileInfo` generation.

## Important APIs, Types, and Functions
It exercises `MutableInodeDirectory.create`, `equals`, `getId`, `isDirectory`, `isFile`, `setDeleted`, timestamp getters/setters, `setName`, `setParentId`, `getMode`, and `generateClientFileInfo`.

## Control Flow, State, and Persistence
Tests create isolated directory inodes from `AbstractInodeTest`, mutate one field at a time, and assert the in-memory object state. Timestamp setters reject backwards updates by leaving the previous time intact.

## Dependencies and Integration Points
The test depends on `CreateDirectoryContext`, security umask configuration, `ModeUtils.applyDirectoryUMask`, and `alluxio.wire.FileInfo` fields consumed by clients.

## Risks
Equality is id-based rather than name-based, which is intentional but easy to misuse. The generated client info is a serialization boundary; incorrect defaults such as cacheable, folder, completed, length, or UFS path would leak to clients.

## Test Signals
Signals cover id-based equality, directory/file flags, deletion toggling, monotonic timestamp behavior, default owner/group/mode, and directory `FileInfo` shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeDirectoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeFileTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeFileTest.java

## Purpose
`MutableInodeFileTest` validates core mutable file inode behavior for identity, length, block sizing, block id allocation/indexing, completion state, and permission defaults.

## Important APIs, Types, and Functions
It exercises `MutableInodeFile.equals`, `getId`, `setLength`, `getBlockSizeBytes`, `getNewBlockId`, `getBlockIdByIndex`, `setCompleted`, `isCompleted`, and `getMode`.

## Control Flow, State, and Persistence
The test creates file inodes with deterministic ids, generates several block ids, verifies index lookup order, and checks negative/out-of-range block index exceptions. All state is local to mutable inode objects.

## Dependencies and Integration Points
It depends on `AbstractInodeTest`, block id creation conventions, `BlockInfoException`, security umask configuration, and `ModeUtils.applyFileUMask`.

## Risks
Block id order and index validation are critical because file metadata and block master state must agree. Permission defaults inherit global configuration and can shift if defaults change.

## Test Signals
Signals include id-based equality, block size defaults, length mutation, precise block index exception messages, completion transition, and owner/group/mode default assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeFileTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/SimpleInodeLockListTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/SimpleInodeLockListTest.java

## Purpose
This test validates `SimpleInodeLockList`, the low-level ordered container for inode and edge locks used by path locking.

## Important APIs, Types, and Functions
The suite exercises `lockRootEdge`, `lockInode`, `lockEdge`, `pushWriteLockedEdge`, `unlockLastInode`, `unlockLastEdge`, `downgradeToReadLocks`, `downgradeLastEdge`, `getLockMode`, `endsInInode`, `getLockedInodes`, and `numInodes`.

## Control Flow, State, and Persistence
Tests build lock sequences over `/a/b/c`, verify the aggregate lock mode, then release or downgrade from the tail. Invalid sequencing tests expect `IllegalStateException` when callers try to lock root after other locks, lock inode after inode, edge after edge, wrong edge/inode pairings, or unlock the wrong terminal type.

## Dependencies and Integration Points
The test uses `BaseInodeLockingTest`, `InodeLockManager`, and `LockMode`. It is the unit foundation for `LockedInodePath` correctness.

## Risks
The lock list enforces strict alternation and parent-child consistency. Any relaxation could introduce deadlocks or allow callers to believe a path is protected when the wrong edge is locked.

## Test Signals
Signals include read-to-write escalation tracking, write-edge push-forward behavior, full unlock to empty, root downgrade, read-after-write aggregate mode, non-root starts, invalid operation exceptions, and inode count accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/SimpleInodeLockListTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketListTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketListTest.java

## Purpose
`TtlBucketListTest` verifies grouping of TTL-bearing inodes into interval buckets and polling/removing expired buckets.

## Important APIs, Types, and Functions
The test exercises `TtlBucketList.insert`, `remove`, and `pollExpiredBuckets`. It uses `TtlIntervalRule` to set a 10 ms bucket interval and `TtlTestUtils` to construct inode views with specific TTL values.

## Control Flow, State, and Persistence
The test inserts files whose TTLs fall into bucket `[0,10)` and `[10,20)`, polls at boundary and interior times, reinserts after polling to continue assertions, and removes individual inodes before polling again.

## Dependencies and Integration Points
`TtlBucketList` depends on an `InodeStore` for production behavior, but this test uses a mock because it is focused on bucket membership and expiration order.

## Risks
Boundary handling is the main risk: TTL equal to the bucket end belongs to the next bucket, and polling at end time expires the previous interval. Reinsert-after-poll patterns can hide single-shot lifecycle mistakes if changed.

## Test Signals
Signals include no early expiry, correct grouping within bucket 1, bucket 2 separation, all-bucket expiry at the second boundary, removal of one or all entries, and empty final state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketListTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketTest.java

## Purpose
`TtlBucketTest` validates individual TTL bucket interval math, membership uniqueness, retry-attempt metadata, ordering, equality, and hash behavior.

## Important APIs, Types, and Functions
It exercises `TtlBucket` construction, `getTtlIntervalStartTimeMs`, `getTtlIntervalEndTimeMs`, static `getTtlIntervalMs`, `addInode`, `removeInode`, `getInodeIds`, `getInodeExpiries`, `size`, `compareTo`, `equals`, and `hashCode`.

## Control Flow, State, and Persistence
Tests add duplicate and distinct inode ids to one bucket, remove them, re-add with default and explicit retry attempts, then compare buckets with equal and different start times.

## Dependencies and Integration Points
The test uses `TtlTestUtils` inode factories and validates the in-memory data structure that `TtlBucketList` orders and expires.

## Risks
Bucket equality and ordering are based only on interval start time, not contents. Retry attempt storage must stay attached to inode expiry entries, or TTL retry scheduling can drift.

## Test Signals
Signals cover interval end calculation, start-time comparison, duplicate suppression, file and directory-like membership, retry-attempt updates, compare/equality symmetry, and hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlIntervalRule.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlIntervalRule.java

## Purpose
`TtlIntervalRule` is a JUnit rule that temporarily overrides the static TTL bucket interval for deterministic TTL tests.

## Important APIs, Types, and Functions
The class implements `TestRule`, stores `mIntervalMs`, and returns a `Statement` from `apply`. During `evaluate`, it reads `TtlBucket.getTtlIntervalMs`, uses PowerMock `Whitebox.setInternalState` to set `TtlBucket.sTtlIntervalMs`, runs the wrapped statement, and restores the previous value in `finally`.

## Control Flow, State, and Persistence
The rule mutates static process state only for the duration of a test or class rule. The `finally` block is the persistence boundary preventing interval leakage into later tests.

## Dependencies and Integration Points
It depends on JUnit rules/statements, PowerMock reflection, and the private static field name in `TtlBucket`.

## Risks
The rule is brittle to renaming `sTtlIntervalMs` or removing mutable static state. Parallel TTL tests would share the global interval and could interfere.

## Test Signals
Its primary signal is indirect: TTL bucket tests can assert exact bucket boundaries without depending on production configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlIntervalRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlTestUtils.java

## Purpose
`TtlTestUtils` provides small inode factories for TTL bucket tests.

## Important APIs, Types, and Functions
`createFileWithIdAndTtl` creates an `Inode` wrapping a `MutableInodeFile` with `FileSystemMasterCommonPOptions.ttl` set. `createDirectoryWithIdAndTtl` has the same signature for directory tests.

## Control Flow, State, and Persistence
Both helpers construct `CreateFileContext` from `CreateFilePOptions`, set the TTL in common options, and return wrapped mutable inodes. No persistent state is touched.

## Dependencies and Integration Points
The helpers depend on gRPC file-create options, `CreateFileContext`, `MutableInodeFile`, and `Inode.wrap`.

## Risks
`createDirectoryWithIdAndTtl` currently also creates a `MutableInodeFile`, not a directory inode. Existing tests only require id and TTL behavior, but the helper name can mislead future tests that depend on inode type.

## Test Signals
The file itself has no tests; its signal is fixture reuse in `TtlBucketTest` and `TtlBucketListTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsAbsentPathCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsAbsentPathCacheTest.java

## Purpose
This file tests factory selection for absent UFS path caching based on the configured async thread count.

## Important APIs, Types, and Functions
It exercises `UfsAbsentPathCache.Factory.create` and checks returned implementations `AsyncUfsAbsentPathCache` and `NoopUfsAbsentPathCache`.

## Control Flow, State, and Persistence
Tests set or leave `MASTER_UFS_PATH_CACHE_THREADS`, create a cache with a system clock, assert implementation type, and reload configuration after each test.

## Dependencies and Integration Points
The test depends on Alluxio global configuration and clock injection. The mount table argument is `null`, showing that factory selection is independent from mount behavior.

## Risks
Factory behavior changes can silently disable async absent-path caching. Configuration cleanup is important because this test mutates global properties.

## Test Signals
Signals include default async cache creation, zero-thread fallback to noop, and negative-thread fallback to noop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsAbsentPathCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsSyncCachePathTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsSyncCachePathTest.java

## Purpose
`UfsSyncCachePathTest` validates `UfsSyncPathCache` freshness rules for file-info and list-status style sync checks across exact paths, direct parents, grandparents, and file vs directory paths.

## Important APIs, Types, and Functions
The test exercises `notifySyncedPath`, `recordStartSync`, and `shouldSyncPath`, plus helper predicates `syncNeeded` and `syncNeededParentSync`. It covers `DescendantType.NONE`, `ONE`, and `ALL`.

## Control Flow, State, and Persistence
Tests sync `/dir1`, `/dir1/dir2`, or `/one`, sleep long enough to exceed short intervals, and assert sync decisions for child directories and files under short and long intervals. A negative interval means "do not sync"; zero means immediate sync is needed.

## Dependencies and Integration Points
The cache integrates Alluxio URI ancestry with metadata sync callers such as get-file-info and list-status. The `isFile` flag in `notifySyncedPath` changes descendant-type validation.

## Risks
Freshness inheritance is subtle: a direct parent synced with `ONE` validates child `NONE` but not deeper listing, while `ALL` validates descendants. File syncs are special because any descendant sync check on the file itself is considered valid.

## Test Signals
Signals cover interval bypass/expiry, exact-path descendant coverage, direct-parent and grandparent inheritance, list-status behavior, and special file validation compared with directory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/UfsSyncCachePathTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/options/MountInfoTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/options/MountInfoTest.java

## Purpose
`MountInfoTest` validates the simple mount metadata value object.

## Important APIs, Types, and Functions
It constructs `MountInfo` with Alluxio URI, UFS URI, mount id, and `MountPOptions`, then exercises `getAlluxioUri`, `getUfsUri`, `getOptions`, `getMountId`, and `toUfsInfo`.

## Control Flow, State, and Persistence
The test performs direct field round-trip assertions and converts to gRPC `UfsInfo`. No mutable or persistent state is used.

## Dependencies and Integration Points
It depends on `AlluxioURI`, `MountContext.defaults`, `MountPOptions`, and the `UfsInfo` wire type consumed by mount-related APIs.

## Risks
The main risk is serialization drift: `toUfsInfo` currently exposes the UFS URI string but not every `MountInfo` field.

## Test Signals
The signal is basic constructor/getter/wire conversion integrity for mount table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/options/MountInfoTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/replication/ReplicationCheckerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/replication/ReplicationCheckerTest.java

## Purpose
`ReplicationCheckerTest` validates the master heartbeat logic that detects under-replicated, over-replicated, lost, and misplaced file blocks and submits replication or migration jobs.

## Important APIs, Types, and Functions
The test exercises `ReplicationChecker.heartbeat`, a mock `ReplicationHandler` implementing `setReplica`, `migrate`, `getJobStatus`, and `findJobs`, and helpers that create file inodes, register block workers, commit blocks, and heartbeat block locations.

## Control Flow, State, and Persistence
Setup starts a UFS journal system, block master, inode tree, and safe-mode aware context. File helpers create completed one-block files with replication min/max and optional pin location. Heartbeats compare actual block locations against replication policy, call the mock handler, and track in-flight job ids to avoid duplicate scheduling.

## Dependencies and Integration Points
The suite integrates `InodeTree`, `BlockMaster`, worker registration/heartbeats, journal system startup, file-create contexts, replication job APIs, and Alluxio configuration such as `JOB_MASTER_JOB_CAPACITY`.

## Risks
The checker must avoid scheduling for lost blocks, avoid duplicates while jobs are running, reschedule failed jobs, and use migration for wrong storage medium rather than replica-count changes. The test mutates one `CreateFileContext` across cases, so isolation depends on per-test setup.

## Test Signals
Signals include empty-tree no-op, within-range no-op, under-replication by 1 or 10, pinned-medium migration, over-replication, mixed under/over files, lost-block suppression, multiple files, partial scheduling under capacity, running-job suppression, failed-job retry, and completed-job cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/replication/ReplicationCheckerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/FileIterableTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/FileIterableTest.java

## Purpose
This test validates how `FileIterable` maps checked file-system access/listing errors into runtime exceptions for scheduler callers.

## Important APIs, Types, and Functions
It constructs `FileIterable` with a mocked `FileSystemMaster`, optional user, partial-listing flag, and `LoadJob.QUALIFIED_FILE_FILTER`, then calls `iterator`.

## Control Flow, State, and Persistence
The mock `checkAccess` first throws `FileDoesNotExistException`, then `InvalidPathException`, then `AccessControlException`. The test asserts not-found cases become `NotFoundRuntimeException` and access denial becomes `UnauthenticatedRuntimeException`.

## Dependencies and Integration Points
This bridges checked master exceptions to runtime scheduler/job APIs, preserving caller-facing semantics for load-job file iteration.

## Risks
Exception translation is small but user-visible. Incorrect mapping can make missing paths look like auth failures or vice versa.

## Test Signals
The signal is focused translation coverage for missing file, invalid path, and access denial before iteration begins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/FileIterableTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadJobTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadJobTest.java

## Purpose
`LoadJobTest` validates batching, retry health, partial listing, and progress reporting for master load jobs.

## Important APIs, Types, and Functions
The test exercises `LoadJob.getNextBatchBlocks`, `addBlockToRetry`, `isHealthy`, `setJobState`, `addLoadedBytes`, `getProgress`, `addBlockFailure`, and `failJob`, with `FileIterable` backed by mocked `FileSystemMaster.listStatus`.

## Control Flow, State, and Persistence
Batch tests generate synthetic files and blocks, request fixed block counts, requeue failures, and verify distinct UFS paths in each batch. Partial-listing tests emulate `ListStatusContext` start-after and batch size handling. Progress tests compare exact text and JSON report strings before and after block failures and job failure.

## Dependencies and Integration Points
The tests depend on generated `FileInfo` fixtures from `LoadTestUtils`, scheduler job state, gRPC `Block`, `JobProgressReportFormat`, and runtime exception types.

## Risks
Progress report formatting is asserted as exact strings, so intended formatting changes require test updates. Randomized fixture generation can make debugging harder, though counts are deterministic enough for these assertions.

## Test Signals
Signals include retry queue ordering, end-of-iteration empty batches, partial listing skip of already-loaded files, unhealthy state after repeated retries, byte and file progress accounting, failure percentage, failed-file counting, and verbose/non-verbose error inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadJobTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadTestUtils.java

## Purpose
`LoadTestUtils` provides synthetic block-status and file-info fixtures for load scheduler tests.

## Important APIs, Types, and Functions
It exposes `generateRandomBlockStatus`, `fileWithBlockLocations`, and `generateRandomFileInfo`. Private helpers create `FileInfo` and `FileBlockInfo` values with random ids, paths, UFS paths, block sizes, offsets, and lengths.

## Control Flow, State, and Persistence
`generateRandomBlockStatus` probabilistically emits OK or failed gRPC block statuses with retryable flags. `fileWithBlockLocations` clones file metadata while adding block locations for a selected ratio. `generateRandomFileInfo` creates completed, persisted files with block metadata.

## Dependencies and Integration Points
The helpers use Alluxio wire `FileInfo`, `FileBlockInfo`, `BlockInfo`, `BlockLocation`, gRPC `Block` and `BlockStatus`, Guava immutable collections, Java randomness, and gRPC status codes.

## Risks
Use of `Math.random` and new `Random` instances makes fixtures nondeterministic. Tests relying on exact failure rates can become flaky if assumptions are too tight; current tests mostly use aggregate eventual behavior.

## Test Signals
This file has no tests of its own, but it supports scheduler coverage for success, partial failure, full failure, existing block locations, and multi-file multi-block loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/LoadTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/SchedulerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/SchedulerTest.java

## Purpose
`SchedulerTest` validates master-side load-job scheduling: worker discovery, job submission/stop, journaling, capacity limits, asynchronous block load dispatch, exception handling, and stale job retention.

## Important APIs, Types, and Functions
The test exercises `Scheduler.updateWorkers`, `getActiveWorkers`, `submitJob`, `stopJob`, `start`, `stop`, `getJobProgress`, `getJobs`, and `cleanupStaleJob`. It uses `DefaultWorkerProvider`, `JournaledJobMetaStore`, `LoadJob`, `FileIterable`, mocked `BlockWorkerClient.load`, and helper `buildResponseFuture`.

## Control Flow, State, and Persistence
Worker tests simulate changing `FileSystemMaster.getWorkerInfoList` results and unavailable exceptions. Submit/stop tests verify journal entries for created, stopped, succeeded, and resubmitted jobs. Scheduling tests start the scheduler thread, feed mocked workers async futures with success, partial failure, full failure, and exceptions, then wait for terminal states. Retention mutates job states and cleans terminal jobs when retention is zero.

## Dependencies and Integration Points
The test integrates scheduler logic with authenticated user context, file-system master listing, file-system context worker clients, journal context append calls, load-job progress reporting, gRPC load requests/responses, and global job capacity/retention configuration.

## Risks
Several tests use sleeps and polling loops around asynchronous scheduling. Randomized block statuses and large full-capacity runs can make timing sensitive. Exact journal predicates encode persistence contract for job metadata.

## Test Signals
Signals include worker set stability across transient errors, duplicate job update behavior, capacity rejection, stop idempotence, successful async load completion with verification, handling worker exceptions and retryable listing failures, resource exhaustion, and cleanup of failed/succeeded/stopped while retaining created/verifying jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/scheduler/SchedulerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/CountingNoopFileSystemMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/CountingNoopFileSystemMaster.java

## Purpose
`CountingNoopFileSystemMaster` is a test double for a file-system master that counts applied journal entries and can simulate slow or failing journal application.

## Important APIs, Types, and Functions
It extends `NoopMaster`, overrides `processJournalEntry`, `resetState`, and `getName`, exposes `setApplyDelay`, `getApplyCount`, and static factory `withApplyDelay`, and defines `ENTRY_DOES_NOT_EXIST`.

## Control Flow, State, and Persistence
On each journal entry, it optionally sleeps, increments `mApplyCount`, throws `NoSuchElementException` for delete-file entries, and otherwise returns true. `resetState` clears the count.

## Dependencies and Integration Points
It depends on `Journal.JournalEntry` and the `NoopMaster` lifecycle. Returning `"FileSystemMaster"` as the name ensures journal routing accepts test entries for file-system master journals.

## Risks
The class intentionally throws on a specific journal entry type, so tests using arbitrary delete-file entries can fail unexpectedly. The artificial delay preserves thread interrupt status but otherwise ignores exceptions.

## Test Signals
The double supports journal replay, apply-count, delay, and failure-path tests elsewhere in the journal suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/CountingNoopFileSystemMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalContextTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalContextTest.java

## Purpose
`JournalContextTest` validates journal context interactions with master state locking, standby journals, fairness during state changes, and journal-entry merge contexts for both UFS and embedded journal types.

## Important APIs, Types, and Functions
The parameterized test covers `JournalSystem`, `BlockMaster.createJournalContext`, `StateLockManager.lockExclusive`, `MergeJournalContext`, `FileSystemMergeJournalContext`, `MetadataSyncMergeJournalContext`, and `FileSystemJournalEntryMerger`.

## Control Flow, State, and Persistence
Setup configures the journal type, embedded journal port, registry, journal system, metrics master, and block master, then starts and gains primacy. Lock tests open journal contexts or exclusive state locks in one thread and assert the other operation blocks until release. Merge tests append journal entries, flush or close merge contexts, and inspect emitted merged entries.

## Dependencies and Integration Points
The test integrates journal systems with master state-lock coordination, block master journal contexts, embedded journal configuration, file-system inode journal entries, metadata sync merge contexts, and Alluxio wait utilities.

## Risks
Concurrency tests rely on sleeps and timeouts. Fairness matters: continuous shared journal-context creation must not starve exclusive state changes. Merge behavior is subtle because only matching entries should merge while unrelated entries pass through.

## Test Signals
Signals include journal contexts blocking pause, pause blocking new journal contexts, no state-lock leak when standby journal rejects context creation, exclusive lock fairness under heavy context churn, create/complete merge output, flush-on-flush, close-on-close, and ignoring default journal entries until flushed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalContextTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalTestUtils.java

## Purpose
`JournalTestUtils` centralizes test setup for journal systems and embedded journal port allocation.

## Important APIs, Types, and Functions
It exposes `createEmbeddedJournalTestPorts`, `createJournalSystem(TemporaryFolder)`, and `createJournalSystem(String)`.

## Control Flow, State, and Persistence
Port creation obtains free ports, writes comma-separated embedded journal addresses plus hostname and port into global configuration, and returns the allocated port list. Journal-system creation builds a `JournalSystem` at a temporary URI with zero quiet time for master process tests.

## Dependencies and Integration Points
It depends on `PortRegistry`, global `Configuration`, `PropertyKey` journal settings, `TemporaryFolder`, `URI`, and `JournalSystem.Builder`.

## Risks
Free-port allocation can race with other processes before use. The helper mutates global configuration, so callers must reload properties after tests.

## Test Signals
This file has no direct tests; its value is consistent journal setup for replication and journal context tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/JournalTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/NoopRaftJournalSystem.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/NoopRaftJournalSystem.java

## Purpose
`NoopRaftJournalSystem` is a lightweight raft journal test double with controllable leadership and no external raft side effects.

## Important APIs, Types, and Functions
It extends `RaftJournalSystem`, exposes `setIsLeader`, overrides `start`, `stop`, `isLeader`, `startInternal`, `stopInternal`, `gainPrimacy`, `losePrimacy`, and `createJournal`.

## Control Flow, State, and Persistence
Lifecycle methods are no-ops. `isLeader` returns the synchronized `mIsLeader` flag. `createJournal` returns a `NoopJournal`.

## Dependencies and Integration Points
The class depends on `RaftJournalSystem`, `NoopJournal`, `Master`, and master raft service addressing. It lets tests satisfy raft journal type dependencies without starting a real raft cluster.

## Risks
Because primacy methods do nothing, tests using this double must explicitly set leadership if behavior depends on it. It cannot validate persistence, quorum, or log replication.

## Test Signals
The double supports tests that only need journal-system shape, leadership state, and no-op journals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/NoopRaftJournalSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalReaderOptionsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalReaderOptionsTest.java

## Purpose
`JournalReaderOptionsTest` validates defaults and mutable fields for journal reader options.

## Important APIs, Types, and Functions
It exercises `JournalReaderOptions.defaults`, `getNextSequenceNumber`, `setNextSequenceNumber`, `isPrimary`, and `setPrimary`.

## Control Flow, State, and Persistence
The test checks defaults of sequence number `0` and non-primary, then sets random boolean and long values and verifies round-trip getters.

## Dependencies and Integration Points
It depends only on the options object and Java `Random`. Reader options are consumed by journal readers to choose sequence start and primary behavior.

## Risks
Random values are not seeded, but the test only checks exact round trip. There is no validation for negative sequence numbers or fluent API behavior.

## Test Signals
Signals are default option contract and setter/getter integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalReaderOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalWriterOptionsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalWriterOptionsTest.java

## Purpose
`JournalWriterOptionsTest` validates defaults and mutable fields for journal writer options.

## Important APIs, Types, and Functions
It exercises `JournalWriterOptions.defaults`, `getNextSequenceNumber`, `setNextSequenceNumber`, `isPrimary`, and `setPrimary`.

## Control Flow, State, and Persistence
The test asserts the default writer starts at sequence number `0` and non-primary, then verifies randomly chosen sequence and primary values round-trip through setters/getters.

## Dependencies and Integration Points
It depends only on the writer options object and Java `Random`. Writer options feed journal writer startup and primary-mode behavior.

## Risks
The test does not enforce range validation or immutability. Randomized values are safe here because assertions are direct round trips.

## Test Signals
Signals are default writer option contract and setter/getter integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/options/JournalWriterOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemConfigTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemConfigTest.java

## Purpose
`RaftJournalSystemConfigTest` validates how `RaftJournalSystem` derives local and cluster raft addresses from master and job-master configuration.

## Important APIs, Types, and Functions
It constructs `RaftJournalSystem` for `ServiceType.MASTER_RAFT` and `JOB_MASTER_RAFT`, uses reflection helpers `getLocalAddress` and `getClusterAddresses`, and checks `NetworkAddressUtils.containsLocalIp`.

## Control Flow, State, and Persistence
Each test sets relevant `PropertyKey` values, creates a journal system with a temporary URI, reflects its private address fields, and asserts host/port derivation. Cleanup reloads configuration after each test.

## Dependencies and Integration Points
The test depends on Alluxio configuration keys for master hostname, embedded journal addresses and ports, job-master hostname and journal addresses, temporary folders, service-type defaults, Guava sets, and network address utilities.

## Risks
The test reaches private fields reflectively, so internal field renames break it even if behavior is preserved. Address derivation is sensitive to hostname defaults and local-IP matching.

## Test Signals
Signals include default master port `19200`, explicit master raft port propagation, master hostname derivation, job-master hostname fallback from master hostname, job-master port override from master addresses, direct job-master address parsing, and local IP containment when hostnames differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalSystemConfigTest.java -->
