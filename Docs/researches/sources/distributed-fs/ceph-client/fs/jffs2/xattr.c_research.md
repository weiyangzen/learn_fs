# sources/distributed-fs/ceph-client/fs/jffs2/xattr.c

## Purpose
Implements JFFS2 xattr persistence and runtime operations: xattr datum nodes, inode-to-datum xrefs, cache load/reclaim, mount rebuild, VFS list/get/set helpers, inode teardown, CRC verification, and GC relocation.

## Important APIs, types, and functions
Key paths are `load_xattr_datum()`, `save_xattr_datum()`, `create_xattr_datum()`, `unrefer_xattr_datum()`, `verify_xattr_ref()`, `save_xattr_ref()`, `delete_xattr_ref()`, `check_xattr_ref_inode()`, `jffs2_build_xattr_subsystem()`, `jffs2_listxattr()`, `do_jffs2_getxattr()`, `do_jffs2_setxattr()`, `jffs2_garbage_collect_xattr_datum()`, `jffs2_garbage_collect_xattr_ref()`, and `jffs2_verify_xattr()`.

## Control flow
Mount scan creates datum stubs and temporary refs; `jffs2_build_xattr_subsystem()` verifies refs, merges duplicate `(ino,xid)` refs by sequence, binds live refs to inode caches and datums, and queues unchecked or orphan datums. Runtime get/list/set first calls `check_xattr_ref_inode()` to remove duplicate names and load datums. Set reserves and writes a raw datum, then reserves and writes a raw xref; replacements create the new ref before deleting the old one.

## State and persistence behavior
Persistent state is journaled as `JFFS2_NODETYPE_XATTR` and `JFFS2_NODETYPE_XREF` raw nodes with CRCs. In memory, `xattrindex[]` caches loaded datums, `xattr_unchecked` tracks datums needing verification, dead lists defer release, and `ic->xref` links inode attributes. `xattr_sem` serializes object mutation; `erase_completion_lock` protects raw-node chains and space accounting. Datum cache memory is reclaimed with hot/bind flags.

## Dependencies and integration points
Depends on JFFS2 scan/build, inode cache lifetime, raw node refs, flash reservation/read/write, GC, summary accounting, VFS xattr handlers, optional security/POSIX ACL handlers, MTD, and CRC32.

## Risks and test signals
High-risk areas are CRC/corruption handling, read-to-write semaphore upgrade, duplicate ref sequence selection, refcount leaks on replace/delete, cache reclaim during compare, unchecked-node accounting, and GC of dead/invalid objects. Test mount rebuild, corrupt nodes, create/replace/delete flags, eraseblock-size limits, namespace list visibility, inode deletion, and GC relocation.
