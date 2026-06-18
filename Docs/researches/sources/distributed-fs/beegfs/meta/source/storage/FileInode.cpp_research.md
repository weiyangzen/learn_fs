# sources/distributed-fs/beegfs/meta/source/storage/FileInode.cpp

## Purpose

`FileInode.cpp` implements BeeGFS file inode behavior. It covers file metadata serialization/deserialization, dynamic per-target attributes, persistent updates for inlined and standalone inode storage, remote storage target xattrs, open-session counters and access-state checks, POSIX-like attribute changes, hardlink count updates, user xattrs for non-inlined inodes, and append, whole-file, and byte-range lock management.

The file bridges the namespace layer's `EntryInfo` view with two possible persistence layouts: an inode embedded in a dentry, or a separate inode file under the inode hash tree.

## Important APIs and Functions

- Constructors initialize session counters, lock state, dentry compatibility data, and, for loaded inodes, `FileInodeStoreData`.
- `initFileInfoVec` derives per-target `ChunkFileInfo` from file size, stripe pattern, chunk size, sparse-file block data, and stat timestamps.
- `setRemoteStorageTarget`, `clearRemoteStorageTarget`, `storeRemoteStorageTargetUnlocked`, `storeRemoteStorageTargetBufAsXAttr`, `loadRstFromInodeFile`, and `loadRstFromFileXAttr` manage remote storage target metadata and the `FILEINODE_FEATURE_HAS_RST` flag.
- `checkAccessAndOpen` validates file state restrictions and increments read/write session counters atomically under the inode write lock.
- `decNumSessionsAndStore` decrements read/write sessions and persists updated dynamic attributes on close.
- `updateDynamicAttribs`, `serializeMetaData`, and `deserializeMetaData` coordinate dynamic stat data with `DiskMetaData`.
- `storeUpdatedMetaDataBuf*`, `storeUpdatedInodeUnlocked`, and `storeUpdatedInlinedInodeUnlocked` persist inode updates to xattrs, file contents, or the owning dentry.
- `getMetaFilePath` resolves the metadata file path for inlined and standalone layouts.
- `removeStoredMetaData`, `loadFromInodeFile`, `loadFromFileXAttr`, `loadFromFileContents`, `createFromEntryInfo`, `createFromInodeFile`, and `createFromInlinedInode` implement lifecycle and load fallback behavior.
- `setAttrData`, `incDecNumHardLinks`, `listXAttr`, `getXAttr`, `removeXAttr`, and `setXAttr` mutate POSIX metadata and user xattrs.
- `flockAppend`, `flockEntry`, and shared helpers manage exclusive append locks and whole-file shared/exclusive locks.
- `flockRange` and its helpers manage byte-range shared/exclusive locks with wait queues, writer preference, merging, splitting, conflict detection, cancellation, and status dumps.
- `initLocksRandomForSerializationTests` populates lock structures for serialization/equality testing.

## Control Flow

Loading starts from `createFromEntryInfo`. If `EntryInfo` says the inode is inlined, it tries the dentry first and falls back to the inode file; if not inlined, it tries the inode file first and falls back to the dentry. This tolerates stale client-side `EntryInfo`. After load, RST xattrs are loaded when the feature flag is present.

Metadata persistence starts with `storeUpdatedInodeUnlocked`. If the inode is believed to be inlined, it tries to load the parent dentry by ID, copy current inode data into the dentry's inlined store data, and write the dentry. If that reports `INODENOTINLINED`, the object switches to standalone mode and retries as a separate inode file. Standalone writes serialize through `DiskMetaData` and use xattrs or content files depending on configuration.

Content-file updates use temp-file write plus rename for atomic replacement, with in-place fallback on `ENOSPC`. Xattr updates open/create the metadata file and write `META_XATTR_NAME`.

Locking APIs all run under `rwlock` write mode for mutations. New lock requests are deduplicated by `lockAckID`, checked against granted locks and waiters, optionally queued if waiting is allowed, and followed by attempts to grant queued waiters after unlocks or cancellations. Whole-file locks prefer waiting writers before new readers. Range locks also check overlapping waiting writers to avoid writer starvation.

## State and Persistence Behavior

In-memory state includes `inodeDiskData`, per-target `fileInfoVec`, session counters, exclusive TID, dentry compatibility data, inlined-state flag, parent-reference tracking, remote storage target info, and several granted/waiting lock containers for append, whole-file, and range locks.

Persistent state includes:

- The serialized file inode, either in the owning dentry or in a separate inode metadata file.
- Dynamic file attributes folded into `StatData` before serialization.
- Optional remote storage target data in `RST_XATTR_NAME`.
- User xattrs for non-inlined inode files only.

Buddy-mirrored standalone inode updates and deletes enqueue inode modifications/deletions in the buddy resync changeset. Xattr mutations also enqueue inode modifications, with FIXME comments noting the resync granularity is broader than just the xattr.

## Dependencies and Integration Points

The implementation depends on `DiskMetaData`, `DirEntry`, `EntryInfo`, `FileInodeStoreData`, `Locking.h`, `XAttrTk`, BeeGFS serialization, `MetaStorageTk`, `Program` paths/configuration, `RemoteStorageTarget`, POSIX file and xattr APIs, and lock-detail types. It is used by metadata open/close, setattr, unlink-busy-file, hardlink, lock, RST, and xattr workflows.

## Risks and Edge Cases

- `getMetaFilePath` constructs the inlined dentry-by-ID path by concatenating `MetaStorageTk::getMetaDirEntryIDPath(dirEntryPath)` and `entryID`; this relies on the helper returning a path with the correct separator.
- Inlined-to-standalone fallback in `storeUpdatedInodeUnlocked` handles unexpected layout changes, but it logs a locking warning because the write lock should normally prevent this state drift.
- In-place update fallback on low disk space has weaker crash behavior than temp-file rename.
- `clearRemoteStorageTarget` clears the feature flag and persists before removing the xattr; xattr removal failure is logged but not returned as failure.
- User xattr methods assert that inlined inodes cannot access their own xattrs; callers must route inlined file xattr operations through `DirInode`/dentry paths.
- Lock queues can grow with waiters; cancellation by client or handle is critical for cleanup on disconnect/close.
- Writer preference avoids starvation for writers but can delay readers behind queued exclusive requests.
- Range-lock merging/splitting mutates ordered sets; comparator consistency with modified ranges is essential because entries are erased and reinserted around changes.
- `initFileInfoVec` assumes valid stripe patterns and chunk sizes. Corrupt metadata can lead to bad per-target calculations if deserialization validation misses it.

## Test Signals

Important tests include load fallback between inlined and standalone layouts, serialize/deserialize round trips for sparse and non-sparse files, dynamic attribute recalculation across stripe target counts, xattr and content metadata modes, low-space in-place fallback, RST set/clear/load behavior, open access checks for read/write/full lock states, session counter decrement persistence, setattr rollback on store failure, hardlink count rollback, buddy-resync records, non-inlined user xattrs, append and whole-file lock wait queues, range-lock overlap/merge/split/unlock behavior, cancellation by handle/client, duplicate lock request handling, writer-preference behavior, and randomized lock serialization equality.
