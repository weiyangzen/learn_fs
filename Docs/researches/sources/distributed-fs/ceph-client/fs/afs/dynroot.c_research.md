# sources/distributed-fs/ceph-client/fs/afs/dynroot.c

Purpose: `dynroot.c` implements the synthetic dynamic AFS root, presenting cells as pseudo automount directories and exposing `@cell`/`.@cell` symlinks for the workstation cell.

Important APIs and functions: exported objects are `afs_dynroot_inode_operations`, `afs_dynroot_dentry_operations`, and `afs_dynroot_iget_root()`. Key functions are `afs_dynroot_lookup()`, `afs_dynroot_lookup_cell()`, `afs_lookup_atcell()`, `afs_atcell_get_link()`, `afs_dynroot_readdir()`, `afs_dynroot_readdir_cells()`, and pseudo-inode iget helpers.

Control flow: lookup rejects create and overlong names, handles special symlinks, resolves cells via `afs_lookup_cell()`, creates automount pseudo directories with distinct dotted/undotted inode numbers, and stores the cell in `d_fsdata`. Readdir emits dot entries, optional workstation-cell symlinks, then walks `cells_dyn_ino` under `cells_lock` to emit live undotted and dotted cells.

State and persistence: dynroot inodes are pseudo, read-only, no-atime, and not server-backed. Dentry `d_fsdata` owns a cell reference released by `afs_dynroot_d_release()`. `@cell` symlink content is derived from `net->ws_cell`, with RCU pathwalk returning direct pointers and non-RCU pathwalk taking a delayed-call cell reference.

Dependencies and integration points: uses AFS cell lookup/registry, DNS resolver-backed cell discovery, automount `afs_d_automount`, mountpoint inode operations, RCU and cell locks, and VFS pseudo inode/dentry mechanics.

Risks: dotted-name handling assumes cell names have addressable leading dot storage. RCU symlink reads depend on workstation-cell lifetime. Dentry deletion policy intentionally keeps only special symlinks. Pseudo inode number allocation must avoid collisions and reserved values.

Test signals: lookup normal/dotted cells, missing cells, `@cell`, `.@cell`, overlong names; readdir with and without workstation cell; skip dead/removing cells; automount behavior; cell reference balancing; RCU/non-RCU symlink reads.
