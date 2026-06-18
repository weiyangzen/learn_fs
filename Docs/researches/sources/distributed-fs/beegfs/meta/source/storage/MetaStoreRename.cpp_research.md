# sources/distributed-fs/beegfs/meta/source/storage/MetaStoreRename.cpp

## Purpose

`MetaStoreRename.cpp` implements the rename-related methods of `MetaStore`, including same-directory rename, overwrite validation and cleanup, remote rename insertion, source serialization, and source completion. It handles both inlined and non-inlined file inodes and coordinates dentry updates with later inode disposal.

## Important APIs and Functions

`renameInSameDir` locks the meta store and parent directory, performs the dentry rename, updates ctime, and unlinks overwritten entries after lock release if needed. `performRenameEntryInSameDir` loads and validates the source, references inlined file inodes when necessary, checks overwrite legality, and calls `DirInode::renameDirEntryUnlocked`. `checkRenameOverwrite` enforces POSIX-like no-op for same inode and rejects directory overwrites. `unlinkOverwrittenEntry` and `unlinkOverwrittenEntryUnlocked` reuse normal unlink helpers.

Remote rename support includes `moveRemoteFileInsert`, which deserializes the source inode or dentry into the destination directory, handles overwrite name removal, fixes buddy mirror flags, restores RST info, and unlinks overwritten inlined entries. `moveRemoteFileBegin` serializes either an inlined inode through the appropriate `InodeFileStore` or a non-inlined dentry. `moveRemoteFileComplete` deletes the source inode object from the global or per-directory store.

## Control Flow and State

Same-directory rename first renames the dentry and only then cleans up an overwritten inode. For overwritten busy files, cleanup can return `INUSE`; the code releases locks and calls `unlinkInodeLater`, falling back to direct unlink if the busy reference disappeared. The source file is referenced only for inlined non-directory files, because non-inlined inodes may live on another metadata server.

Remote insert removes the destination name dentry first but keeps the ID dentry for potential recovery. It creates a new `FileInode`, deserializes metadata, adjusts buddy mirror state from the destination parent, deserializes RST data if present, and calls `mkMetaFileUnlocked`.

## Persistence and Dependencies

The implementation persists through `DirInode` dentry operations, `FileInode` serialization, `MetaStore::mkMetaFileUnlocked`, and unlink helpers. It depends on raid/stripe headers, stat/mkfile helpers, `Program`, and Boost lexical casts for logging.

## Integration Points

Network rename handlers call these methods for local same-dir and cross-server rename phases. `InodeFileStore::moveRemoteBegin` and `moveRemoteComplete` provide source-side inode serialization/deletion. `MetaStore` unlink/disposal logic handles overwritten files.

## Risks and Test Signals

Risks include partial overwrite recovery, stale inlined state, remote servers with different serialization versions, RST preservation, and lock release before `unlinkInodeLater`. Tests should cover same-inode rename no-op, file-over-file overwrite, directory overwrite rejection, busy overwritten file disposal, remote insert with existing target, RST round trip, buddy mirrored destination correction, non-inlined source dentry serialization, and failed remote completion cleanup.
