# sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.h

## Purpose

`IncompleteInode.h` declares the RAII object used while raw metadata is being reconstructed, especially for buddy resync. It represents an open metadata file or directory that can still receive content and xattrs.

## Important APIs and Types

`IncompleteInode` owns an integer fd, a `hasContent` flag, and a set of xattr names written during the current fill pass. Copy construction and copy assignment are disabled. Move construction and move assignment transfer ownership through `swap`. Public mutation methods are `setXattr`, `setContent`, and `clearUnsetXAttrs`.

## Control Flow and State

The default object has fd `-1` and no content. Move assignment uses copy-and-swap with a temporary constructed from the moved source, leaving only one live object owning the descriptor. The private `fileName` helper exists for diagnostic output.

## Persistence and Dependencies

The class depends only on storage error definitions in the header, with implementation details in the cpp. It does not know the metadata path directly; it owns only the fd returned by `open` or `mkdir` plus `open`.

## Integration Points

Instances are produced by `MetaStore::beginResyncFor` and then consumed by resync logic. Because it is move-only, callers can return it in `std::pair<FhgfsOpsErr, IncompleteInode>` without accidental descriptor duplication.

## Risks and Test Signals

Callers must check the accompanying error code before writing to a default fd `-1` object. Tests should verify that moves do not double-close fds, default objects are harmless, and cleanup removes only attributes absent from `xattrsSet`.
