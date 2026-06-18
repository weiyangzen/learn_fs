# sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.cpp

## Purpose

`IncompleteInode.cpp` implements a small RAII wrapper used during buddy resync to create a raw metadata inode and then fill its metadata content or xattrs. It supports incremental construction before the metadata object is considered complete.

## Important APIs and Functions

The destructor closes the owned file descriptor and logs close failures. `setXattr` writes an xattr with `fsetxattr`, records the xattr name in `xattrsSet`, and converts `errno` to `FhgfsOpsErr`. `setContent` writes either xattrs or file contents depending on configuration. `clearUnsetXAttrs` lists existing xattrs and removes user namespace attributes not set through this object. `fileName` resolves `/proc/self/fd/<fd>` for logging.

## Control Flow and State

`setContent` delegates to `setXattr` when extended attributes are enabled. When xattrs are disabled, only `META_XATTR_NAME` may be represented as file contents; other attributes return `FhgfsOpsErr_INVAL`. Repeated content writes truncate the file to the new size before writing. `clearUnsetXAttrs` builds a set from `flistxattr`, skips attributes already set, and removes only `user.*` attributes, deliberately leaving system, trusted, and security namespaces alone.

## Persistence and Dependencies

The file uses POSIX fd APIs (`fsetxattr`, `flistxattr`, `fremovexattr`, `ftruncate`, `write`, `readlink`, `close`) and `Program::getApp()->getConfig()->getStoreUseExtendedAttribs()`. It is persistent only through the fd supplied by `MetaStore::beginResyncFor`.

## Integration Points

`MetaStore::beginResyncFor` returns `IncompleteInode` to the buddy resyncer. The resync caller fills metadata through `setContent` and `setXattr`, then can call `clearUnsetXAttrs` to remove stale user metadata from preexisting files or directories.

## Risks and Test Signals

Partial writes are treated as errors but do not retry, so tests should simulate short writes if possible. The content mode only supports one metadata payload and should reject arbitrary attributes. Tests should cover move construction/assignment, fd close behavior, xattr cleanup filtering, repeated content truncation, and xattr-disabled mode.
