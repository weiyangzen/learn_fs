# sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.h

## Purpose

`DirEntryStore.h` declares `DirEntryStore`, the per-directory dentry store abstraction used by metadata directory inodes, and `ListIncExOutArgs`, the output bundle used for incremental directory listings. The header defines the public API for creating, linking, removing, renaming, listing, querying, and updating dentries while hiding unlocked helpers and filesystem path state.

## Important APIs and Types

- `ListIncExOutArgs` groups output lists for names, entry types, entry IDs, server offsets, and the newest server offset. `outNames` is required; the other lists and pointer are optional.
- `DirEntryStore()` constructs an unbound store with undefined parent ID. `DirEntryStore(parentID, isBuddyMirrored)` binds the store to a metadata path.
- Public mutators include `makeEntry`, `linkEntryInDir`, `linkInodeToDir`, `removeDir`, `unlinkDirEntry`, and `renameEntry`.
- Listing APIs are `listIncrementalEx` for normal dentries and `listIDFilesIncremental` for dentry-by-ID files.
- Query APIs include `exists`, `getEntryData`, `dirEntryCreateFromFile`, and inline helpers `getDentry`, `getDirDentry`, `getFileDentry`, `getEntryInfo`, `getFileEntryInfo`, and `getDirEntryInfo`.
- Static lifecycle helpers are `mkDentryStoreDir` and `rmDirEntryStoreDir`.
- Private unlocked helpers mirror the public methods and assume the caller has the correct lock.
- `removeBusyFile` is a private inline helper used by `DirInode` to move an inlined busy file into a durable inode form while unlinking.

## Control Flow and Locking Contract

The class owns an `RWLock`. Public methods generally lock and delegate to private `Unlocked` variants. Inline lookup wrappers also lock. `getIsBuddyMirrored` is intentionally lock-free because the mirror state should only be set during initialization or controlled conversion. `setParentID` is documented as unlocked and intended for initialization, although it is also used by directory mirror-state conversion.

Friend access is granted to `DirInode` and `MetaStore`, which lets higher-level metadata operations compose directory and inode updates.

## State and Persistence Behavior

The header exposes that the store's state is minimal: a `parentID`, a derived `dirEntryPath`, an `RWLock`, and `isBuddyMirrored`. The persistent data lives in the source-tree-shaped metadata directories and files managed by `DirEntry`, `MetaStorageTk`, and the implementation file. Inline methods always route path-sensitive operations through `getDirEntryPathUnlocked` or `getDirEntryPath`.

## Dependencies and Integration Points

The declaration depends on BeeGFS common storage definitions, `DirEntry`, metadata toolkit types, `EntryInfo`, `FileInodeStoreData`, `NumNodeID`, and list typedefs. `DirInode` embeds this class and uses it for all child dentry operations. `MetaStore` uses friend access for coordinated rename/unlink flows.

## Risks and Edge Cases

- The header relies on callers respecting the unlocked method contract; misuse can bypass `rwlock`.
- `removeBusyFile` is private but callable by friends and couples dentry-store behavior to `DirEntry::removeBusyFile`.
- `ListIncExOutArgs` uses raw pointers and allows optional null outputs; implementation code must check every optional field before writing.
- `getDirEntryPath` returns a copy under lock, while `getDirEntryPathUnlocked` returns a reference. Callers must not retain the reference across state changes.

## Test Signals

Compile-time tests should cover all inline methods, especially null optional list arguments and type-filter helpers. Behavioral tests should assert that public methods acquire locks, that `setParentID` changes both path and mirror state, and that `removeBusyFile` updates the dentry through the expected path.
