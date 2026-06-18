# sources/distributed-fs/beegfs/meta/source/storage/MetaFileHandle.h

## Purpose

`MetaFileHandle.h` declares a move-only handle that carries a referenced `FileInode*` plus, when needed, the parent `DirInode*` whose per-directory file store owns that inode. It lets `MetaStore` return file references without losing the directory lifetime dependency.

## Important APIs and Types

`MetaFileHandle` has a default null state, a constructor from inode and parent pointers, deleted copy operations, move construction/assignment through `swap`, pointer-like `operator->`, dereference, `get`, and a safe-bool conversion.

## Control Flow and State

The class does not release resources in its destructor. It is a transport handle, and `MetaStore::releaseFile` or close paths must be called explicitly. The parent pointer is private and friend-only because only `MetaStore` understands whether a file came from the global store or a per-directory store.

## Persistence and Dependencies

The header includes `DirInode` and `FileInode`. It owns no persistent state and performs no disk I/O.

## Integration Points

`MetaStore` returns `MetaFileHandleRes` from reference APIs and uses `MetaFileHandle` in open, close, stat-like, rename, unlink, hardlink, fsck, and reinline/deinline flows. The handle ensures parent directory references are carried alongside inodes loaded from a `DirInode::fileStore`.

## Risks and Test Signals

The main risk is misuse: the handle is not RAII, so leaks or double releases are possible if callers do not follow `MetaStore` release conventions. Tests should cover move behavior, boolean conversion, null handles, and paired release paths for global versus per-directory file stores.
