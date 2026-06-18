# Research: subset-b-000477

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockManager.java

## Purpose
`InodeLockManager` centralizes all inode-tree locking for the Alluxio file master. It supplies read/write locks for inode ids and parent-child edges without embedding locks in every inode, so large namespaces do not carry permanent lock objects for millions of files. It also provides auxiliary locks for parent metadata updates and synchronous UFS persistence exclusion.

## Important APIs, Types, and Functions
The main APIs are `lockInode(InodeView, LockMode, boolean)`, `lockInode(Long, LockMode)`, `tryLockInode(Long, LockMode)`, `lockEdge(Edge, LockMode, boolean)`, `tryLockEdge(Edge, LockMode)`, `tryAcquirePersistingLock(long)`, and `lockUpdate(long)`. The constructor registers gauges for inode and edge lock pool sizes. Testing helpers report whether the current thread holds inode or edge read/write locks and `assertAllLocksReleased()` scans both pools for leaked locks.

## Control Flow, State, and Persistence
There is no journaled state here. Runtime state is a pair of `LockPool` instances keyed by inode id and `Edge`, a striped lock array for parent timestamp/child-count updates, and a weak-valued Guava `LoadingCache<Long, AtomicBoolean>` for per-inode persistence locks. `tryAcquirePersistingLock()` uses `compareAndSet(false, true)` and returns a `Scoped` releaser that resets the boolean; callers that fail to acquire know another thread is already persisting the inode.

## Dependencies and Integration Points
`LockedInodePath`, `SimpleInodeLockList`, and `InodeTreePersistentState` are the main consumers. `InodeTree.syncPersistExistingDirectory()` uses the persisting lock to serialize UFS directory creation. `InodeTreePersistentState.updateTimestampsAndChildCount()` and `InodeTree.createPath()` use `lockUpdate()` while modifying parent metadata under only read-level inode-tree locks. Metrics are exported through `MetricsSystem` and lock-pool behavior is driven by master lock pool configuration keys.

## Risks
The parent update lock has a strict ordering rule documented in the class: callers should not hold more than one such lock and should not acquire other locks while holding it. Violating that rule can deadlock. The persisting-lock cache uses weak values, which is memory-friendly but means correctness depends on the returned `Scoped` retaining the `AtomicBoolean` while held. `lockInode(..., useTryLock=true)` still blocks through the `LockPool` retry behavior, so it should not be confused with the non-blocking `tryLockInode`.

## Test Signals
Useful tests assert current-thread read/write lock visibility, no leaked locks after path operations, correct edge/inode lock release on exceptions, parent update serialization under concurrent create/delete/rename, and single-writer behavior for concurrent `syncPersistExistingDirectory()` calls. Metrics assertions can check lock pool gauges after acquiring and releasing locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodePathPair.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodePathPair.java

## Purpose
`InodePathPair` is an immutable, closeable pair of `LockedInodePath` objects. It is used when the inode tree needs to hold two path locks at once, for example rename-like operations, while guaranteeing both paths are released together.

## Important APIs, Types, and Functions
The class extends `Pair<LockedInodePath, LockedInodePath>` and implements `AutoCloseable`. Its package-private constructor accepts two locked paths. `setFirst()` and `setSecond()` are overridden to throw `UnsupportedOperationException`, making the pair immutable after construction. `close()` synchronously closes both paths.

## Control Flow, State, and Persistence
There is no persistence. Runtime state is inherited from `Pair`. `InodeTree.lockInodePathPair()` constructs the pair after locking paths in deterministic lexicographic path order; if locking either path fails, that method closes any partial locks before the pair is returned.

## Dependencies and Integration Points
The class depends on the generic Alluxio `Pair` utility and `LockedInodePath`. It integrates with try-with-resources usage around operations that need two locked namespace locations and relies on `LockedInodePath.close()` to flush merged inode journals before releasing locks when configured.

## Risks
`close()` always closes `getFirst()` before `getSecond()`. That is simple and normally correct, but callers must not pass null paths or independently close one side before the pair unless double-close behavior remains safe. The class comment says elements cannot be set once constructed; the constructor is package-private, so immutability depends on only trusted package code creating it.

## Test Signals
Tests should verify mutation methods throw, try-with-resources closes both paths, and exception paths in `InodeTree.lockInodePathPair()` release partially acquired locks. Lock-order tests around rename workloads are the important integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodePathPair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTree.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTree.java

## Purpose
`InodeTree` is the file master's high-level namespace tree API. It coordinates path locking, inode id allocation, creation, deletion, pinning, replication policy updates, path-to-id/id-to-path lookup, descendant locking, root initialization, and synchronous UFS directory persistence. It delegates all durable metadata mutations to `InodeTreePersistentState`.

## Important APIs, Types, and Functions
The `LockPattern` enum defines `READ`, `WRITE_INODE`, and `WRITE_EDGE`, which control whether traversal locks existing inodes/edges for reads, metadata mutation, or structural mutation. Public mutation/read APIs include `initializeRoot()`, `lockInodePath()`, `tryLockInodePath()`, `lockFullInodePath()`, `lockInodePathPair()`, `createPath()`, `getDescendants()`, `deleteInode()`, `setPinned()`, `setReplication()`, `syncPersistExistingDirectory()`, and `syncPersistNewDirectory()`. Delegating wrappers expose `newBlock()`, inode update journal methods, `getTtlBuckets()`, pinned and replication-limited id sets, and retry-cache methods.

## Control Flow, State, and Persistence
`InodeTree` itself is marked not thread-safe; correctness comes from path locks and the persistent-state delegate. Root initialization creates a persisted `MutableInodeDirectory` with id from `InodeDirectoryIdGenerator` and journals it. Path locking constructs a `LockedInodePath` and traverses from root; id-based locking repeatedly computes a path from parent pointers, locks it, and retries up to `PATH_TRAVERSAL_RETRIES` if concurrent rename/delete changed the path. Two-path locking orders paths by string comparison to reduce deadlock risk.

`createPath()` requires `WRITE_EDGE`. It rejects root creation, handles existing-directory `allowExists`, validates file block size, optionally sync-persists existing missing parent directories, updates ancestor timestamps, creates missing intermediate directories when recursive, inherits pin state, ACLs, owner/group, TTL, xattrs, and persistence state, and journals every new inode via `mState.applyAndJournal()`. File creation allocates a block container id or uses complete-file metadata, sets async-through files to `TO_BE_PERSISTED`, and adds the final inode to the locked path.

Delete journals a `DeleteFileEntry` and registers file blocks for deletion. Pin and replication changes recurse through directories by locking children and journaling inode/file updates. Synchronous directory persistence resolves the Alluxio path through `MountTable`, calls UFS `mkdirs`, reconciles existing UFS status into owner/group/mode/xattrs/times, and uses a per-inode persisting lock with exponential backoff so only one thread creates a given UFS directory.

## Dependencies and Integration Points
The class integrates `InodeStore`, `InodeLockManager`, `InodeTreePersistentState`, `MountTable`, `TtlBucketList`, block container/directory id generators, `RpcContext`, file creation contexts, journal entries, ACL utilities, UFS resources, and retry policies. It is the metadata core used by higher-level file-system-master operations and by metadata sync paths that need locking decisions and UFS persistence.

## Risks
The class relies on callers holding the correct `LockedInodePath` pattern; many methods enforce this with `Preconditions`, but misuse can still surface as runtime failure. `lockFullInodePath(AlluxioURI, LockingScheme, JournalContext)` ignores the passed journal context and locks with `NoopJournalContext.INSTANCE`, which is notable because journal flushing on close will not occur through that argument. Recursive descendant/pin/replication traversal can hold many locks and consume memory on large subtrees. UFS persistence has a bounded retry loop; persistent contention or slow UFS can convert a namespace create into an `IOException`. The code contains non-atomic id-to-path computation warnings because parent pointers can change while computing paths.

## Test Signals
Strong signals are path-lock pattern tests, create-file/create-directory tests for recursive parents, ACL/default ACL inheritance, owner/group inheritance config, pin and replication recursion, delete block-registration, mount-table UFS resolution during sync persistence, and journal replay round trips through `InodeTreePersistentState`. Concurrency tests should cover id-based path lookup under rename, two-path lock ordering, and concurrent persisted directory creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTree.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreeBufferedIterator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreeBufferedIterator.java

## Purpose
`InodeTreeBufferedIterator` enumerates inode-tree journal entries with concurrent read-ahead buffering for checkpoints and journal snapshots. It keeps parent directory entries before their children within each crawled branch, improving replay efficiency and preserving the requirement that parent inodes exist before child entries are replayed.

## Important APIs, Types, and Functions
The public factory `create(InodeStore, InodeDirectory)` returns a `CloseableIterator<JournalEntry>`. Internally, `DirectoryCrawler` buffers the current directory, iterates direct children, queues child directories for further traversal, and buffers file entries immediately. `hasNext()`, `next()`, `remove()`, and `close()` implement iterator and resource lifecycle behavior.

## Control Flow, State, and Persistence
The constructor reads crawler count and buffer size configuration, creates a single coordinator executor and fixed crawler pool, seeds the directory queue with root if present, and calls `startBuffering()`. The coordinator submits crawlers while directories remain, tracks active futures, polls for completion, and enqueues a sentinel journal entry with sequence `-1` on normal termination or `-2` after crawler failure. `hasNext()` drains or polls the blocking buffer into `mNextElements`; `next()` throws a runtime exception if it sees the failure sentinel.

## Dependencies and Integration Points
`InodeTreePersistentState.getJournalEntryIterator()` uses this iterator. It depends on `InodeStore.getChildren()`, inode `toJournalEntry()` conversion, Alluxio checkpoint/journal types, and thread names created through `ThreadFactoryUtils`. Its output feeds journal checkpoint writing and later replay by `InodeTreePersistentState`.

## Risks
The coordinator loop only removes active crawler futures in the branch where there are no pending directories, so if crawlers continue producing directories quickly, completed futures can remain tracked longer than necessary. Failure is propagated through a synthetic journal entry rather than directly through executor futures, so consumers must call `next()` to observe it. `close()` uses `shutdownNow()` and does not wait for worker termination. Snapshot consistency depends on the underlying inode store and surrounding checkpoint protocol; this iterator does not lock the whole tree.

## Test Signals
Tests should verify parent-before-child ordering, complete enumeration for mixed file/directory trees, empty/null root behavior, bounded-buffer behavior, failure propagation when `getChildren()` or `toJournalEntry()` fails, and that `close()` stops background executors. Checkpoint/replay integration should compare restored inode state to the source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreeBufferedIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreePersistentState.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreePersistentState.java

## Purpose
`InodeTreePersistentState` owns all durable inode-tree state and the journal replay contract. All metadata modifications are expected to flow through this class as journal entries so in-memory state, checkpoints, and standby replay stay aligned.

## Important APIs, Types, and Functions
Public APIs expose retry-cache state, root lookup, inode count and file-size histogram, pinned/replication-limited/to-be-persisted id sets, TTL buckets, `applyAndJournal()` overloads for create/delete/rename/new-block/update/set-acl entries, non-journaled access-time application, `processJournalEntry()`, checkpoint write/restore, and `getJournalEntryIterator()`. Derived checkpointed sets are `PinnedInodeFileIds`, `ReplicationLimitedFileIds`, `ToBePersistedFileIds`, `InodeCounter`, and `TtlBucketList`.

## Control Flow, State, and Persistence
`applyAndJournal()` methods apply mutations and append corresponding `JournalEntry` objects, with fatal master termination on unexpected failure. Delete is special: the delete journal entry is appended before in-memory removal to avoid replay ordering races with a concurrent create of the same name. Create writes the inode, adds the parent edge, increments counters, updates parent child count, pin/replication derived sets, TTL buckets, to-be-persisted ids, and file-size buckets for completed files. Rename removes the old child edge, changes name and parent, adds the new edge, writes the inode, and updates old/new parent timestamps and child counts.

Replay is implemented by `processJournalEntry()`, which dispatches current entries plus deprecated entries (`AsyncPersistRequest`, `CompleteFile`, `InodeLastModificationTime`, `PersistDirectory`, `SetAttribute`) into current update routines. Operation ids from `RpcContext` are attached to selected journal entries and cached after replay for retry de-duplication. Checkpoints persist and restore the inode store plus derived checkpointed structures; TTL buckets are ordered after the inode store because they resolve ids to inodes.

## Dependencies and Integration Points
This class depends on `InodeStore`, `InodeLockManager` parent update locks, journal/checkpoint utilities, proto journal entries, ACL/proto conversion, `BucketCounter`, and configuration for retry cache and file size histogram buckets. `InodeTree` delegates all durable namespace mutation to it, and the journal subsystem delegates replay/checkpointing through the `Journaled` interface.

## Risks
Many apply paths call `.get()` on optional inode lookups and assume replay/input validity; corrupt or out-of-order journals can crash the master. `applyDelete()`'s recursive deprecated branch appears to call `removeInodeAndParentEdge(inode)` for queued children using the original inode variable, which is a risk for old recursive delete replay. `resetState()` clears the inode store and some derived sets but not all visible derived structures such as TTL buckets, inode counter, to-be-persisted ids, or bucket counter in the shown code, so reset semantics need careful integration testing. Asynchronous access-time updates are deliberately ignored if the target inode is missing, but other missing inode updates are fatal.

## Test Signals
Round-trip tests should apply journal entries, checkpoint/restore, and compare inode store plus derived sets. Specific signals include delete-before-create replay ordering, rename parent child-count/timestamp updates, pin updates affecting replication min and pinned ids, replication max affecting replication-limited ids, TTL update bucket removal/reinsert, async access-time missing-inode tolerance, deprecated journal entry replay, and retry-cache operation id behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeTreePersistentState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeView.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeView.java

## Purpose
`InodeView` defines the read-only inode contract shared by mutable inodes and immutable/wrapped inode views. It gives callers a stable interface for common metadata, permissions, client `FileInfo` generation, proto conversion, and journal representation without requiring mutation access.

## Important APIs, Types, and Functions
The interface exposes timestamps, owner/group/mode, id/name/parent id, TTL and TTL action, persistence state, deleted/file/directory/pinned/persisted flags, pinned medium types, UFS fingerprint, xattrs, access/default ACLs, permission checks, `generateClientFileInfo(String)`, and `toProto()`. It extends `JournalEntryRepresentable` and `Comparable<InodeView>`, comparing by inode name.

## Control Flow, State, and Persistence
There is no implementation state. Persistence behavior is indirect: implementers must serialize themselves to journal entries through `JournalEntryRepresentable` and to metastore proto through `toProto()`. Permission checks are delegated by implementations to their `AccessControlList`.

## Dependencies and Integration Points
The interface is consumed by lock managers, path logic, metadata listing, permission checks, metastore serialization, and client response construction. `MutableInode`, `MutableInodeDirectory`, and `MutableInodeFile` implement this contract, while `InodeTree`, `InodeLockManager`, and `LockedInodePath` accept `InodeView` where mutation is not required.

## Risks
The default `compareTo()` sorts only by name, so two inodes with the same name under different parents compare equal. Callers should not use it as a global identity ordering. Returning mutable structures such as xattr maps or ACL objects depends on implementation discipline; the interface itself does not enforce deep immutability.

## Test Signals
Contract tests should verify file and directory implementations provide consistent `FileInfo`, proto, and journal fields; permission checks match ACL behavior; and compare-by-name ordering is acceptable for local child-list use but not used as a global unique key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LazyUfsBlockLocationCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LazyUfsBlockLocationCache.java

## Purpose
`LazyUfsBlockLocationCache` lazily caches UFS block location host lists for Alluxio file blocks. It avoids paying UFS location lookup cost until callers need locations and bounds memory by configured cache capacity.

## Important APIs, Types, and Functions
The class implements `UfsBlockLocationCache`. `invalidate(long)` removes a block id, `get(long)` returns a cached value only, and `get(long, AlluxioURI, long)` resolves the file through the mount table, asks the underlying UFS for file locations at an offset, caches non-null results, and returns them.

## Control Flow, State, and Persistence
State is an in-memory Guava cache keyed by block id and a reference to `MountTable`. There is no checkpoint or journal state. A cache miss with file URI and offset resolves the Alluxio path to UFS, acquires a closeable UFS resource, calls `getFileLocations()` with `FileLocationOptions.defaults().setOffset(offset)`, and stores the list if UFS returns one. Invalid path and I/O errors are logged as warnings and return null.

## Dependencies and Integration Points
The class integrates with `MountTable.Resolution`, `UnderFileSystem`, UFS file-location APIs, and master configuration `MASTER_UFS_BLOCK_LOCATION_CACHE_CAPACITY`. It is used by file master/block location code that needs UFS locality for blocks not yet materialized in Alluxio workers.

## Risks
The cache key is only block id, not `(block id, file uri, offset)`, so correctness assumes block ids are globally unique and stable for their file/offset. Null results are not cached, so repeated UFS failures or unsupported location lookups can be retried frequently. Returning the cached `List<String>` directly allows caller-side mutation unless all callers treat it as read-only.

## Test Signals
Tests should cover cache hit/miss behavior, invalidation, mount resolution and UFS resource closing, null UFS results, exception logging/return-null behavior, and capacity eviction. Integration tests can mock UFS `getFileLocations()` and verify one UFS call for repeated block id lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LazyUfsBlockLocationCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePath.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePath.java

## Purpose
`LockedInodePath` represents a path from the inode-tree root with the corresponding inode and edge locks held according to a chosen `LockPattern`. It is the main scoped object that higher-level file master operations use to safely inspect or mutate namespace paths.

## Important APIs, Types, and Functions
Key APIs include `traverse()`, `getInode()`, `getInodeOrNull()`, `getParentInodeDirectory()`, `getLastExistingInode()`, `getInodeList()`, `fullPathExists()`, `removeLastInode()`, `addNextInode()`, `downgradeToRead()`, `lockDescendant()`, `lockChild()`, `lockChildByName()`, `lockFinalEdgeWrite()`, and `close()`. Constructors create either a root-based lock path or a composite child path built from an existing locked prefix.

## Control Flow, State, and Persistence
The immutable target state is the URI and path components. The mutable lock state lives in an `InodeLockList`, typically `SimpleInodeLockList` or `CompositeInodeLockList` for derived paths. `traverse()` bootstraps the root edge and root inode, alternates edge and inode locks, reads children from `ReadOnlyInodeStore`, and stops when the full path exists or the next component is missing. `WRITE_EDGE` upgrades the first missing non-final edge to a write lock so structural creation can proceed. `WRITE_INODE` write-locks the final inode if it exists.

The object owns a `JournalContext` only for flushing before reducing/releasing lock scope when `MASTER_FILE_SYSTEM_MERGE_INODE_JOURNALS` is enabled and the context is a `FileSystemMergeJournalContext`. `addNextInode()`, `removeLastInode()`, `downgradeToRead()`, and `close()` call `maybeFlushJournals()` before releasing or downgrading locks.

## Dependencies and Integration Points
`InodeTree.lockInodePath()` creates these objects for almost every namespace operation. It depends on `PathUtils`, `ReadOnlyInodeStore`, `InodeLockManager`, lock-list implementations, Netty resource leak tracking, and journal contexts. Descendant and child lock methods are used by recursive delete, pinning, replication, and metadata sync.

## Risks
The class is explicitly not thread-safe and derived child paths can be invalidated by mutating the original path. Methods such as `fullPathExists()` and `getExistingInodeCount()` can become stale after local mutation unless traversal is repeated or the path object is updated. Journal flushing during lock release can throw and is wrapped as runtime failure. Composite paths require careful ownership: closing a child path must not close the prefix locks owned by the parent.

## Test Signals
Tests should exercise all three lock patterns on existing, partially existing, and missing paths; traversal through a file-as-parent failure; lock upgrade/downgrade paths; `addNextInode()` pushing the write edge forward during create; journal flush before close/downgrade when merge journals are enabled; leak detection or close discipline; and composite child path close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePathList.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePathList.java

## Purpose
`LockedInodePathList` is a closeable iterable wrapper for a collection of descendant `LockedInodePath` objects. It lets callers process a batch of held path locks and then release them uniformly.

## Important APIs, Types, and Functions
The constructor stores a list of locked paths. `getInodePathList()` returns the stored list, `iterator()` delegates to that list, and `close()` closes every `LockedInodePath` in iteration order.

## Control Flow, State, and Persistence
There is no persistent state. `InodeTree.getDescendants()` builds the list by recursively locking child paths; if gathering fails, it closes already gathered paths before rethrowing. Once returned, this wrapper becomes the caller's close discipline for all descendant locks.

## Dependencies and Integration Points
The class depends only on `LockedInodePath` and standard `Iterable`/`AutoCloseable` contracts. It is used by namespace operations that need all descendant paths locked before applying recursive changes.

## Risks
`getInodePathList()` exposes the mutable underlying list, so callers can reorder, remove, or add paths and affect close behavior. `close()` does not catch exceptions per path; an exception from an early close could prevent later paths from closing if `LockedInodePath.close()` ever throws.

## Test Signals
Tests should verify iteration order, all paths are closed in normal use, and `InodeTree.getDescendants()` closes partial results on traversal errors. A defensive test around list mutation can document that returned-list mutation is unsupported by convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockedInodePathList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockingScheme.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockingScheme.java

## Purpose
`LockingScheme` bundles a target path, the caller's desired inode-tree lock pattern, and the metadata-sync decision for that path. It lets file master RPC code compute whether a read or metadata update must be upgraded to structural locking because UFS sync may delete or create namespace entries.

## Important APIs, Types, and Functions
Constructors accept either an explicit boolean sync decision or RPC common options plus `UfsSyncPathCache` and `DescendantType`. `getDesiredPattern()` returns the caller-requested pattern, `getPattern()` returns `WRITE_EDGE` when sync is required or the desired pattern otherwise, `getPath()` returns the target URI, and `shouldSync()` exposes the `SyncCheck`.

## Control Flow, State, and Persistence
The class is immutable and has no persistence. The option-based constructor chooses a sync interval from client options if present or server configuration `USER_FILE_METADATA_SYNC_INTERVAL` otherwise, then asks `pathCache.shouldSyncPath()`. `getPattern()` is the key control-flow decision: sync requires write-edge locking because syncing can remove an inode deleted in UFS.

## Dependencies and Integration Points
`InodeTree.lockInodePath(LockingScheme, ...)` consumes the scheme. The class integrates with RPC common options, `UfsSyncPathCache`, `DescendantType`, and `SyncCheck`, and is typically created by `DefaultFileSystemMaster` before path locking and metadata sync.

## Risks
Using the boolean constructor with `shouldSync=true` bypasses path-cache deduplication and loses last-sync-time information; the source comment explicitly discourages it when the option-based constructor is available. A sync decision upgrades locking to `WRITE_EDGE`, which can reduce concurrency for otherwise read-only operations.

## Test Signals
Tests should verify default sync interval fallback, client sync interval override, descendant type forwarding to `UfsSyncPathCache`, `getPattern()` upgrade on sync, and no upgrade when `SyncCheck` says sync is unnecessary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockingScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MountTable.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MountTable.java

## Purpose
`MountTable` tracks Alluxio mount points and resolves between Alluxio namespace paths and underlying file-system URIs. It owns journaled mount-table state, UFS client registration, mount validation, read-only checks, mount id generation, and path sync cache access.

## Important APIs, Types, and Functions
Core APIs include `add()`, `addValidated()`, `validateMountPoint()`, `delete()`, `update()`, `getMountPoint()`, `getMountTable()`, `containsMountPoint()`, `findChildrenMountPoints()`, `isMountPoint()`, `reverseResolve()`, `resolve()`, `checkUnderWritableMountPoint()`, `getMountInfo()`, `getUfsClient()`, `getUfsSyncPathCache()`, and `createUnusedMountId()`. Nested `Resolution` exposes resolved UFS URI, UFS client/resource acquisition, shared flag, and mount id. Nested `ReverseResolution` exposes the resolved Alluxio URI and mount info. Nested `State` implements the journaled mount table.

## Control Flow, State, and Persistence
`MountTable` uses a `ReentrantReadWriteLock`. Add validates under the write lock, rejects duplicate Alluxio mount paths, rejects UFS mount paths that are prefix/suffix-related to existing mounts with the same scheme/authority, and checks that the new Alluxio mount path does not shadow an existing path in the parent UFS. Successful adds journal an `AddMountPointEntry`, and `State.applyAddMountPoint()` inserts `MountInfo` and registers the UFS mount with `UfsManager`.

Delete rejects root unmount, optionally blocks unmount if nested mount points exist, removes the UFS mount, and journals `DeleteMountPointEntry`; replay also removes through `State.applyDeleteMountPoint()`. `update()` deletes then re-adds a mount with new options/mount id, attempting to restore the old mount if re-add fails. `resolve()` finds the longest matching mount point, obtains a UFS client by mount id, lets UFS resolve the relative path, and returns a `Resolution`. Journal iteration emits add entries for non-root mounts only; root is considered initial state.

## Dependencies and Integration Points
The class integrates with `UfsManager`, `UnderFileSystem`, `UnderFileSystemConfiguration`, `MountInfo`, mount proto options, metrics counters for sync, `PathUtils`, `Journaled`, and `UfsSyncPathCache`. `InodeTree.syncPersistDirectory()` and `LazyUfsBlockLocationCache` use mount resolution to reach UFS paths.

## Risks
Validation performs live UFS `exists()` checks, so mount operations depend on UFS availability and permissions. `delete()` removes the UFS manager mount before applying/journaling the delete entry; if journaling fails, runtime state and durable state can diverge. `update()` nests delete/add calls under the write lock; this works with the reentrant write lock but broadens the critical section and performs UFS work while locked. `reverseResolve()` is linear over all mounts and can be expensive for many mount points.

## Test Signals
Tests should cover duplicate mount rejection, UFS prefix/suffix conflict detection, shadowing detection, root unmount rejection, nested mount checks, update rollback, longest-prefix resolution, reverse resolution, read-only write checks, mount id uniqueness, journal replay of add/delete, and checkpoint/journal iterator exclusion of root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MountTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInode.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInode.java

## Purpose
`MutableInode` is the abstract base for mutable file and directory inodes in the file master. It stores shared metadata and implements the `InodeView` read contract plus mutation helpers for ACLs, timestamps, TTL, persistence, pinning, xattrs, ownership, and proto conversion.

## Important APIs, Types, and Functions
Important methods include shared getters, ACL mutation (`setAcl`, `replaceAcl`, `removeAcl`, `removeExtendedAcl`, `updateMask`, `setInternalAcl`), timestamp setters with optional override, owner/group/mode setters, `setPersistenceState()`, `setPinned()`, `setXAttr()` with strategies `TRUNCATE`, `UNION_REPLACE`, `UNION_PRESERVE`, and `DELETE_KEYS`, `updateFromEntry(UpdateInodeEntry)`, type casts `asDirectory()`/`asFile()`, permission checks, and `toProtoBuilder()`. Subclasses implement `setDefaultACL()`, `generateClientFileInfo()`, `getThis()`, and `toJournalEntry(String)`.

## Control Flow, State, and Persistence
Each inode carries id, name, parent id, creation/modification/access times, deletion flag, directory flag, TTL and action, persistence state, pinned flag, pinned media set, ACL, UFS fingerprint, and xattrs. `updateFromEntry()` is the central replay/update method for common fields; it interns owner/group strings, respects timestamp overwrite flags, applies xattr update strategies, and filters pinned medium types against configured global media. `toProtoBuilder()` serializes common inode fields to metastore proto; journal serialization is completed by subclasses.

## Dependencies and Integration Points
`MutableInodeDirectory` and `MutableInodeFile` extend this base. `InodeTreePersistentState` obtains mutable inodes from `InodeStore`, applies journal entries through `updateFromEntry()`, and writes them back. ACL behavior depends on Alluxio security authorization classes and proto conversion utilities. Configuration provides allowed tiered-store medium types.

## Risks
The class is not thread-safe; only timestamp setters synchronize locally, and higher-level inode locks are required. `setXAttr()` can retain and mutate caller-provided maps instead of copying them. File subclasses throw for default ACL operations, so common ACL code must not pass default entries to files unless expected. Equality and hash code use only inode id, which is correct for identity but can hide stale object comparisons.

## Test Signals
Tests should cover ACL replace/modify/remove/default behavior, mask recomputation, timestamp monotonic and override semantics, xattr update strategies, pin medium filtering, `UpdateInodeEntry` field application, proto round trips through subclasses, and file/directory cast failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeDirectory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeDirectory.java

## Purpose
`MutableInodeDirectory` is the mutable metadata representation for directories in the file master. It adds directory-specific state to `MutableInode`: mount-point status, direct-children-loaded flag, child count, and default ACL.

## Important APIs, Types, and Functions
Directory-specific APIs include `isMountPoint()`, `isDirectChildrenLoaded()`, `getChildCount()`, `getDefaultACL()`, setters for mount point/direct-children-loaded/child count/default ACL, `generateClientFileInfo()`, `updateFromEntry(UpdateInodeDirectoryEntry)`, static `fromJournalEntry()`, static `create()`, `toJournalEntry()`, `toJournalEntry(String)`, `toProto()`, and `fromProto()`.

## Control Flow, State, and Persistence
The private constructor initializes a directory inode with no mount point, no loaded direct children, zero child count, and a default ACL derived from the access ACL. `create()` builds a new directory from `CreateDirectoryContext`, including owner/group/mode, ACLs, mount flag, TTL, xattrs, and optional UFS fingerprint. `fromJournalEntry()` supports backward compatibility by building ACLs from owner/group/mode when no ACL proto is present and by using modification time as access time if the journal lacks access time. Journal and proto serialization include access/default ACLs, medium types, xattrs, direct-children-loaded, mount-point status, and child count in proto.

## Dependencies and Integration Points
`InodeTree.createPath()` creates these for root, missing parents, and target directories. `InodeTreePersistentState` applies directory creation and directory update entries, increments parent child counts, and stores directories in `InodeStore`. Mount operations and metadata loading rely on `isMountPoint()` and `isDirectChildrenLoaded()`.

## Risks
`isDirectChildrenLoaded()` and its setter are synchronized, but most other fields are not; caller locking is required. `fromJournalEntry()` initializes a missing default ACL to a new empty default ACL rather than one derived from access ACL, which preserves older journal semantics but differs from fresh construction. `generateClientFileInfo()` sets UFS fingerprint to `INVALID_UFS_FINGERPRINT` for directories even though the inode may carry a fingerprint.

## Test Signals
Tests should cover create context mapping, ACL/default ACL inheritance and serialization, journal/proto round trips, backward-compatible journal entries without ACL/access time, direct-children-loaded updates, child count in proto, and client `FileInfo` fields for directories and mount points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeFile.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeFile.java

## Purpose
`MutableInodeFile` is the mutable metadata representation for files in the file master. It tracks block ids, block container id, block size, length, completion/cacheability, persistence job metadata, replication settings, and temporary UFS persistence path.

## Important APIs, Types, and Functions
Important APIs include file-specific getters, `getBlockIdByIndex()`, `getNewBlockId()`, setters for block size/ids/cacheable/completed/length/persist job/replication/temp UFS path, `reset()`, `updateFromEntry(UpdateInodeFileEntry)`, static `fromJournalEntry()`, static `create()`, `toJournalEntry()`, `toJournalEntry(String)`, `toProto()`, and `fromProto()`. File inodes reject default ACL get/set with `UnsupportedOperationException`.

## Control Flow, State, and Persistence
The constructor derives the inode id from `BlockId.createBlockId(blockContainerId, maxSequenceNumber)`, while actual data block ids are generated from the same container id and the current block count. `create()` validates max replication is infinity or at least min, copies file options and common options, initializes owner/group/mode/ACL, persistence state, persistence wait time, xattrs, optional fingerprint, and optional complete-file block ids/length/completed status. `updateFromEntry()` applies file-specific journal updates, including replacing block lists when `setBlocks` is present. Journal/proto serialization includes block ids, block size, completion, length, replication, persistence job, temp UFS path, ACL, medium types, xattrs, and common fields.

## Dependencies and Integration Points
`InodeTree.createPath()` creates file inodes and allocates block containers. `InodeTreePersistentState.applyNewBlock()` calls `getNewBlockId()` and writes the inode back. File metadata feeds block deletion registration on delete, client `FileInfo`, file size histogram buckets, pinned and replication-limited id sets, and persistence queues.

## Risks
`getNewBlockId()` mutates `mBlocks` as a side effect, so callers must journal/write the inode through `InodeTreePersistentState` immediately. `setLength()` does not validate non-negative length. `generateClientFileInfo()` intentionally does not compute in-Alluxio percentage, so callers need block-master data for locality/completion. Default ACL methods throw, which can surprise generic ACL code if default entries are applied to files.

## Test Signals
Tests should cover block id sequence generation, invalid block index errors, replication max/min validation, create context mapping for persisted/not-persisted and complete-file cases, update entry application, journal/proto round trips, default ACL exceptions, file size histogram updates when completed length changes, and block deletion registration after file delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/NoopUfsAbsentPathCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/NoopUfsAbsentPathCache.java

## Purpose
`NoopUfsAbsentPathCache` is a disabled implementation of `UfsAbsentPathCache`. It satisfies the cache interface while intentionally recording no absent-path information.

## Important APIs, Types, and Functions
The implementation provides no-op `processAsync(AlluxioURI, List<Inode>)`, `addSinglePath(AlluxioURI)`, and `processExisting(AlluxioURI)`. `isAbsentSince(AlluxioURI, long)` always returns `false`.

## Control Flow, State, and Persistence
There is no runtime or persistent state. Every mutating call returns immediately and every query says the path is not known absent, forcing callers to consult UFS or other metadata rather than trusting an absent-path cache.

## Dependencies and Integration Points
The class implements `UfsAbsentPathCache` and is used when absent-path caching is disabled or intentionally bypassed. It accepts the same path and inode-prefix arguments as the asynchronous cache implementation but ignores them.

## Risks
Using this implementation removes an optimization and may increase UFS metadata calls. Behavior is safe but conservative: it cannot return stale absent positives because it never returns positives.

## Test Signals
Tests should verify all operations are no-ops and `isAbsentSince()` always returns false. Integration tests can assert that disabling absent-path caching selects this implementation and still produces correct namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/NoopUfsAbsentPathCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/PinnedInodeFileIds.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/PinnedInodeFileIds.java

## Purpose
`PinnedInodeFileIds` is a checkpointed set of file inode ids whose files are pinned. It is a small type marker over `CheckpointedIdHashSet` so this derived index has a distinct checkpoint name.

## Important APIs, Types, and Functions
The only override is `getCheckpointName()`, returning `CheckpointName.PINNED_INODE_FILE_IDS`. Set operations, checkpoint serialization, and restoration are inherited from `CheckpointedIdHashSet`.

## Control Flow, State, and Persistence
The set is maintained by `InodeTreePersistentState`, especially through `setReplicationForPin()` and delete/create replay. It is checkpointed with the inode tree's auxiliary state but is not directly journaled as standalone operations.

## Dependencies and Integration Points
`InodeTreePersistentState.getPinnedInodeFileIds()` exposes an unmodifiable view, and `InodeTree.getPinIdSet()` forwards it. Pinning operations, replication minimum updates, and checkpoint restore depend on this set for efficient scans of pinned files.

## Risks
Because this is a derived index, bugs in inode update replay can desynchronize it from actual inode fields. Tests should validate index consistency after replay and checkpoint restore, not just direct set behavior.

## Test Signals
Signals include pin/unpin file operations, directory recursive pinning, deleting pinned files, checkpoint restore, and journal replay where pinned state and replication min interact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/PinnedInodeFileIds.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ReplicationLimitedFileIds.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ReplicationLimitedFileIds.java

## Purpose
`ReplicationLimitedFileIds` is a checkpointed set of file inode ids whose maximum replication is not the default infinity value. It gives the master an efficient derived index for files with replication ceilings.

## Important APIs, Types, and Functions
The class extends `CheckpointedIdHashSet` and overrides `getCheckpointName()` to return `CheckpointName.REPLICATION_LIMITED_FILE_IDS`. All set and checkpoint mechanics are inherited.

## Control Flow, State, and Persistence
`InodeTreePersistentState.applyUpdateInodeFile()` adds or removes file ids when `replicationMax` changes. `setReplicationForPin()` can also add ids when pinning adjusts replication constraints. The set is written and restored as part of inode-tree checkpointing.

## Dependencies and Integration Points
`InodeTree.getReplicationLimitedFileIds()` exposes the set through persistent state. Replication management and block placement logic can use this index to find files requiring special replication enforcement.

## Risks
The set is only updated when specific journal/update paths run; any future mutation path that changes `replicationMax` must update this derived index or it will drift. The pinning helper adds ids when max is finite but does not explicitly remove ids in all unpin scenarios, so replay/update coverage is important.

## Test Signals
Tests should cover file creation with finite and infinite max replication, `UpdateInodeFileEntry` changes in both directions, pin/unpin interactions, delete cleanup, and checkpoint restore consistency against inode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ReplicationLimitedFileIds.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SimpleInodeLockList.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SimpleInodeLockList.java

## Purpose
`SimpleInodeLockList` is the concrete lock-list implementation for a root-based `LockedInodePath`. It records the alternating edge and inode locks held during path traversal, enforces ordering invariants, supports write-lock downgrades, and releases all locks on close.

## Important APIs, Types, and Functions
It implements `InodeLockList` methods: `lockInode()`, `lockEdge()`, `lockRootEdge()`, `pushWriteLockedEdge()`, `unlockLastInode()`, `unlockLastEdge()`, `downgradeToReadLocks()`, `downgradeLastEdge()`, `getLockMode()`, `getLockedInodes()`, `get(int)`, `numInodes()`, `isEmpty()`, `endsInInode()`, `getInodeLockManager()`, and `close()`. Helpers track the last edge, first write-lock index, and edge/inode consistency.

## Control Flow, State, and Persistence
Runtime state is a linked list of locked inodes, a linked list of `RWLockResource`s, optional `mLastEdge`, and `mFirstWriteLockIndex`. Locks must alternate edge/inode; after a write lock appears, `nextLockMode()` upgrades later requested read locks to write to preserve the invariant that no read lock follows a write lock. `pushWriteLockedEdge()` moves a structural write lock forward during create by acquiring read locks on the previous edge and new inode plus a write lock on the next edge, then releasing the old write edge.

## Dependencies and Integration Points
The class delegates actual lock acquisition to `InodeLockManager` and is used by `LockedInodePath` traversal. It depends on `Edge`, `Inode`, `LockMode`, and `RWLockResource`. Composite path locking builds on a separate `CompositeInodeLockList` but relies on the same interface semantics.

## Risks
`pushWriteLockedEdge()` temporarily holds both old and new locks and must preserve ordering to avoid deadlocks. `close()` clears inode state before closing lock resources; if close ever failed midstream, diagnostic state would be reduced. `checkInodeNameAndEdgeNameMatch()` guards against stale traversal but throws an unchecked exception with proto output that may be large for deep paths.

## Test Signals
Tests should cover lock alternation preconditions, root edge behavior, read-to-write upgrade invariants, write-edge push/downgrade sequences, unlocking last inode/edge, name mismatch detection, try-lock behavior propagation, close releasing all locks, and no leaked locks through `InodeLockManager.assertAllLocksReleased()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SimpleInodeLockList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncCheck.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncCheck.java

## Purpose
`SyncCheck` is the value returned by `UfsSyncPathCache` to say whether a metadata sync should run and, when skipped, what previous sync time justified the skip. It also creates `SyncResult` objects used to feed sync outcomes back into the cache.

## Important APIs, Types, and Functions
Static values `SHOULD_NOT_SYNC` and `SHOULD_SYNC` represent decisions without a last-sync time. `shouldSyncWithTime(long)` and `shouldNotSyncWithTime(long)` create decisions carrying a timestamp. `isShouldSync()`, `getLastSyncTime()`, `syncSuccess()`, and `skippedSync()` expose decision and result state. Nested `SyncResult` has `INVALID_RESULT`, success/skipped constructors, `isResultValid()`, `wasSyncPerformed()`, and `getLastSyncTime()`.

## Control Flow, State, and Persistence
The class is immutable and not directly persisted. `getLastSyncTime()` is valid only when a real timestamp was supplied. `syncSuccess()` returns a valid performed-sync result with no last-sync timestamp. `skippedSync()` returns a valid non-performed result carrying the decision's last-sync time. `INVALID_RESULT` represents external sync failure and should not update cache validation time.

## Dependencies and Integration Points
`LockingScheme` stores a `SyncCheck` and upgrades locking if `isShouldSync()` is true. `UfsSyncPathCache` computes these objects and consumes `SyncResult` values after metadata sync attempts.

## Risks
Calling `getLastSyncTime()` on `SHOULD_SYNC`, `SHOULD_NOT_SYNC`, or performed-success results throws due to preconditions. Callers must distinguish skipped-sync results from performed-sync results. The typo in the comment does not affect behavior but indicates this class is lightweight rather than a rich state machine.

## Test Signals
Tests should verify valid/invalid timestamp access, result validity flags, performed-versus-skipped flags, skipped result timestamp propagation, and `LockingScheme` behavior when given each decision type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncCheck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncState.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncState.java

## Purpose
`SyncState` is the per-path mutable timestamp record used by `UfsSyncPathCache`. It tracks invalidation and validation times for the exact path, direct children, and recursive descendants, plus whether the path is known to be a file.

## Important APIs, Types, and Functions
Fields are package-private volatile timestamps: `mDirectChildrenInvalidation`, `mRecursiveChildrenInvalidation`, `mInvalidationTime`, `mSyncTime`, `mDirectChildrenSyncTime`, `mRecursiveSyncTime`, and volatile `mIsFile`. Methods update these monotonically: `setInvalidationTime()`, `setDirectChildInvalidation()`, `setRecursiveChildInvalidation()`, `setIsFile()`, and `setValidationTime(long, DescendantType)`.

## Control Flow, State, and Persistence
State is in-memory cache state only. The class assumes at most one writer per sync state and multiple volatile readers. Invalidation setters keep the maximum timestamp. `setValidationTime()` always updates exact sync time if newer, updates direct-child sync time for `DescendantType.ONE` or `ALL`, and updates recursive sync time for `ALL`. `setIsFile()` only transitions from file to directory/unknown by setting false when the new value is false and current value is true; it intentionally does not transition false to true.

## Dependencies and Integration Points
`UfsSyncPathCache` owns instances and interprets timestamps to decide whether future RPCs need UFS sync. `DescendantType` controls whether validation covers the path only, direct children, or all descendants. `LockingScheme` indirectly depends on this state through `UfsSyncPathCache.shouldSyncPath()`.

## Risks
The one-writer assumption is not enforced by the class. Because fields are volatile but updates are compound comparisons, concurrent writers can lose updates. The file-to-directory-only transition for `mIsFile` is subtle: callers needing to mark an unknown path as a file cannot do it through `setIsFile(true)` once false.

## Test Signals
Tests should cover monotonic timestamp updates, descendant-type validation effects, invalidation versus validation comparisons in `UfsSyncPathCache`, volatile-reader expectations under controlled concurrency, and `mIsFile` transition semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/SyncState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ToBePersistedFileIds.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ToBePersistedFileIds.java

## Purpose
`ToBePersistedFileIds` is a checkpointed set of inode ids whose persistence state is `TO_BE_PERSISTED`. It gives persistence workers an efficient derived view of files awaiting asynchronous persistence.

## Important APIs, Types, and Functions
The class extends `CheckpointedIdHashSet` and overrides `getCheckpointName()` to return `CheckpointName.TO_BE_PERSISTED_FILE_IDS`. Set mutation and checkpoint read/write behavior are inherited.

## Control Flow, State, and Persistence
`InodeTreePersistentState.updateToBePersistedIds()` adds an inode id when its persistence state is `TO_BE_PERSISTED` and removes it for all other states. The set is checkpointed with the inode tree auxiliary state and restored alongside the inode store.

## Dependencies and Integration Points
`InodeTree.getToBePersistedIds()` exposes an unmodifiable view for persistence scheduling. File creation with async-through writes, async persist journal replay, and persistence-completion updates all depend on this derived set being maintained accurately.

## Risks
The class itself is thin; the risk is drift if any code changes persistence state without going through `InodeTreePersistentState.applyUpdateInode()` or equivalent derived-index maintenance. Checkpoint restore must keep the set consistent with inode persistence states.

## Test Signals
Tests should cover async-through file creation, async persist request replay, transition to persisted/not-persisted, delete cleanup, checkpoint restore, and consistency scans comparing the set to inode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/ToBePersistedFileIds.java -->
