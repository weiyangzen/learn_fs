# sources/distributed-fs/beegfs/meta/source/storage/MetaStore.h

## Purpose

`MetaStore.h` declares the main metadata-server object used by client-side POSIX metadata message handlers. It exposes directory and file lifecycle operations, namespace mutation, stat/setattr, fsck scanning, raw metadata access, hardlink and inode movement helpers, and the global inode lock store.

## Important APIs and Types

`MetaFileHandleRes` returns a `MetaFileHandle` and `FhgfsOpsErr`. Public methods include reference/release for dirs and files, open/close, stat, setattr, link count updates, directory parent updates, file creation, directory inode creation/removal, unlink, same-dir and remote rename helpers, fsck enumeration, reference/cache stats, disposable file insertion, entry-data extraction, hardlink creation, inode deinline/reinline verification, duplicate inode repair, raw metadata get/begin/unlink for resync, `setFileState`, and mirrored-dir invalidation.

Private state consists of `InodeDirStore dirStore`, global `InodeFileStore fileStore`, `GlobalInodeLockStore inodeLockStore`, and `RWLock rwlock`. Private helpers implement unlink variants, reference variants, global-store migration, rename overwrite checks, attr/link-count internals, deinline/reinline internals, and inode movement.

## Control Flow and State

The class intentionally centralizes lock ordering across metadata operations. Public methods acquire `rwlock` and delegate to unlocked variants when caller already holds the correct locks. File inodes may come from the global store or a parent directory store, which is why references are returned as `MetaFileHandle`.

## Persistence and Dependencies

The header depends on fsck structures, stripe patterns, remote targets, metadata errors, `EntryInfo`, locks, atomics, `FsckTk`, `GlobalInodeLockStore`, `IncompleteInode`, `MkFileDetails`, `EntryLock`, `DirEntry`, `InodeDirStore`, `InodeFileStore`, `MetadataEx`, and `MetaFileHandle`. It is not a storage format itself, but declares all operations that mutate the metadata tree.

## Integration Points

Message handlers and background jobs call `MetaStore` rather than manipulating stores directly. The global lock store is exposed through `getInodeLockStore` for internal operations such as chunk balancing and file-state updates.

## Risks and Test Signals

Any new method must preserve lock ordering between `MetaStore`, `InodeDirStore`, `DirInode`, and file stores. APIs returning `MetaFileHandle` require explicit release. Tests should focus on public operation contracts, error propagation, lock-store interaction, buddy mirroring behavior, and source-tree transitions between inlined and non-inlined file metadata.
