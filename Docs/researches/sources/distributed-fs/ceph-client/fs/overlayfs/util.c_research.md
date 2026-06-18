# sources/distributed-fs/ceph-client/fs/overlayfs/util.c

## Purpose
`util.c` provides shared OverlayFS utility logic for write access, credential override, stack allocation, dentry/inode path selection, flag management, copy-up synchronization, origin/whiteout/metacopy/redirect/protection xattrs, fs-verity validation, volatile sync status, and copying real inode attributes to overlay inodes.

## Important APIs, types, and functions
Write helpers include `ovl_get_write_access()`, `ovl_start_write()`, `ovl_want_write()`, `ovl_put_write_access()`, `ovl_end_write()`, and `ovl_drop_write()`. Path and state helpers include `ovl_workdir()`, `ovl_override_creds()`, `ovl_can_decode_fh()`, `ovl_indexdir()`, `ovl_index_all()`, `ovl_verify_lower()`, stack alloc/copy/free helpers, `ovl_alloc_entry()`, `ovl_free_entry()`, dentry revalidation helpers, and real path accessors.

Flag and copy-up APIs include `ovl_path_type()`, `ovl_dentry_*`, `ovl_has_upperdata()`, `ovl_set_upperdata()`, `ovl_inode_update()`, `ovl_dir_modified()`, `ovl_copy_up_start()`, `ovl_copy_up_end()`, and `ovl_already_copied_up()`. Xattr/security helpers include `ovl_init_uuid_xattr()`, `ovl_check_setxattr()`, `ovl_set_impure()`, `ovl_check_protattr()`, `ovl_set_protattr()`, in-use locks, `ovl_need_index()`, nlink transaction helpers, metacopy helpers, redirect parsing, fs-verity helpers, `ovl_sync_status()`, and `ovl_copyattr()`.

## Control flow
Copy-up start locks the overlay inode interruptibly, rechecks whether copy-up already happened, and takes upper mount write access; end releases both. Path selection prefers upper where appropriate but can return lower or lowerdata for metacopy/data-only files. Memory barriers pair upperdata/lowerdata publication with readers. Nlink operations may force copy-up for indexed lower aliases, store persistent nlink xattrs before mutation, and clean orphaned index entries when nlink reaches zero.

Xattr helpers use the selected namespace, tolerate missing optional support by downgrading `ofs->noxattr`, and parse strict formats for metacopy, redirect, UUID, and protection attributes. fs-verity validation loads lower verity info if needed and compares stored metacopy digest with actual lower data digest.

## State and persistence
Persistent state includes OverlayFS xattrs for UUID, impure, origin, metacopy, redirect, xwhiteout, nlink, and protattr. In-memory state includes dentry flags stored in `d_fsdata`, inode flags, upper dentry publication, lowerdata publication, directory version, in-use inode state, volatile mount error sequence, and attribute copies.

## Dependencies and integration points
`namei.c`, `readdir.c`, `super.c`, copy-up, dir, inode, fileattr, and export code all use these helpers. External dependencies include VFS write/freeze APIs, exportfs, fs-verity, fileattr, xattrs, idmapped mount helpers, and credentials.

## Risks
Memory ordering mistakes can expose partially initialized upper or lowerdata paths. Xattr format looseness could accept corrupt metadata; overly strict behavior could break upgrades. Copy-up/nlink/index cleanup races can corrupt hardlink accounting. Volatile sync status must preserve data-loss signaling.

## Test signals
Test copy-up races, metacopy data copy-up on write/truncate, lazy lowerdata publication, redirect validation, fs-verity require/on modes, protattr append/immutable preservation, in-use locking, index cleanup after unlink/rename, xattr unsupported upper fallback, idmapped ownership copying, and volatile syncfs error returns.
