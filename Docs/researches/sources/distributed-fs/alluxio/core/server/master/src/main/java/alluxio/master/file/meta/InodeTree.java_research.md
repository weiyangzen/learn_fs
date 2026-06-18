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
