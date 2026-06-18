<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h -->
# sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h

## Purpose

`foreign_symlink.h` is the public llite declaration point for foreign fake-symlink support. It exposes sysfs attribute handlers that configure the feature and the inode-operation tables used when a Lustre foreign regular file or directory is presented to the Linux VFS as a symlink.

## Important APIs, Types, And Functions

- `foreign_symlink_enable_show()` / `foreign_symlink_enable_store()`: sysfs show/store for enabling fake-symlink interpretation on a mount.
- `foreign_symlink_prefix_show()` / `foreign_symlink_prefix_store()`: sysfs show/store for the absolute local prefix prepended to parsed foreign LOV/LMV values.
- `foreign_symlink_upcall_show()` / `foreign_symlink_upcall_store()`: sysfs show/store for the userspace upcall executable that provides parsing format information.
- `foreign_symlink_upcall_info_store()`: sysfs binary-format store used by the upcall to install parsed constant-string and substring descriptors.
- `ll_foreign_file_symlink_inode_operations`: inode operations for regular foreign files faked as symlinks.
- `ll_foreign_dir_symlink_inode_operations`: inode operations for foreign directories faked as symlinks.

## Control Flow

Other llite files include this header when they need to reference foreign-symlink sysfs handlers or swap an inode's `i_op` table. `llite_foreign.c` selects these operation tables when metadata/layout state identifies a foreign object of `LU_FOREIGN_TYPE_SYMLINK`. `llite_foreign_symlink.c` implements the declarations and uses the sysfs handlers to update fields in `struct ll_sb_info`.

## State And Persistence Behavior

The header declares no state. Runtime state lives in `ll_sb_info`: feature bits, prefix string and length, upcall path, parsed upcall item array, item count, mount namespace pointer, and the read/write semaphore protecting those fields. The configuration is mount-local and not persisted by this header.

## Dependencies And Integration Points

The prototypes depend on kernel `kobject`, `attribute`, `inode_operations`, and sysfs-style show/store conventions. The operation tables integrate with VFS symlink traversal through `.get_link`, stat through `.getattr`, permission checks, xattr listing, and directory lookup rejection for fake directory symlinks.

## Risks And Edge Cases

The header itself is low risk, but it exports a contract where sysfs stores must be mount-namespace aware and operation tables must be safe for inodes whose underlying mode is not `S_IFLNK`. Any signature drift with kernel `inode_operations` or sysfs handlers will break compile compatibility.

## Test Signals

Compile coverage should include builds with the current kernel `getattr`/`get_link` signatures. Integration tests should verify that enabling the feature causes `llite_foreign.c` to install the exported operation tables and that the sysfs attributes invoke the declared handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h -->
