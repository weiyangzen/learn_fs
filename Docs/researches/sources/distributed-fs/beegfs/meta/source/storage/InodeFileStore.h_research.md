# sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.h

## Purpose

`InodeFileStore.h` declares the reference-counted in-memory store for file inodes. It is used for all non-directory file-like entries, both in the global `MetaStore` and inside each `DirInode` for inlined inode metadata.

## Important APIs and Types

`FileInodeReferencer` is an `ObjectReferencer<FileInode*>`. `InodeMap` maps entry ID strings to referencers. `FileInodeRes` returns a raw inode pointer plus `FhgfsOpsErr`. Public methods cover store lookup, reference, release, unlink, open/close, stat, setattr, remote move begin/complete, size, and unlinkability checks.

Private methods manage unlocked reference paths, refcount decrement, unreferenced inode lookup, unreferenced deletion, load/insert, referencer migration, map-iterator reference, and link count changes. Inline `incLinkCount` and `decLinkCount` wrap `incDecLinkCount`.

## Control Flow and State

The store owns an `InodeMap` and an `RWLock`. Public methods take appropriate locks and delegate to unlocked variants where `MetaStore` or `DirInode` already holds wider locks. `getReferencerAndDeleteFromMap` and `insertReferencer` are intentionally exposed only to friends so `MetaStore` can move loaded inodes from a per-directory store to the global store.

## Persistence and Dependencies

The header depends on `FileInode`, `GlobalInodeLockStore`, metadata toolkit types, and storage error definitions. Actual persistence is in `FileInode`; this class controls whether an inode is loaded and when the owned referencer is deleted.

## Integration Points

`DirInode` and `MetaStore` are friends and coordinate store migration, unlinking, open/close, and hardlink operations. Normal external users do not access the map directly.

## Risks and Test Signals

Because methods return raw `FileInode*` backed by a referencer, every successful reference must be paired with release/close. Store migration must preserve references and parent directory lifetimes. Tests should cover referencer migration, destructor cleanup with open sessions, unlinkability semantics, and locked inode access.
