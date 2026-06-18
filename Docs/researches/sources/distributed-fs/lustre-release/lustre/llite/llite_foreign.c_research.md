<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c

## Purpose

`llite_foreign.c` applies llite policy for Lustre foreign files and directories. A foreign LOV/LMV layout describes an object whose payload semantics are owned outside normal Lustre data layout. This file currently recognizes `LU_FOREIGN_TYPE_SYMLINK` and makes such regular files or directories behave like symlinks from the VFS perspective, while also protecting those external references from accidental removal.

## Important APIs, Types, And Functions

- `ll_manage_foreign(struct inode *inode, struct lustre_md *lmd)`: entry point that inspects file LOV or directory LMV metadata and installs fake-symlink inode operations for supported foreign types.
- `ll_foreign_is_openable(struct dentry *dentry, unsigned int flags)`: tells atomic-open logic whether a fake symlink should be opened or should instead drive VFS symlink following.
- `ll_foreign_is_removable(struct dentry *dentry, bool unset)`: checks whether a foreign file/directory may be removed, with an `unset` mode that marks the inode as explicitly removable.
- `ll_manage_foreign_file()` / `ll_manage_foreign_dir()`: private helpers that switch `inode->i_op` to foreign symlink operation tables.
- `should_preserve_foreign_file()` / `should_preserve_foreign_dir()`: policy helpers for protecting fake symlinks unless `LLIF_FOREIGN_REMOVABLE` has been set.

## Control Flow

`ll_manage_foreign()` is called after metadata/layout information is available. For regular files it first checks `lmd->layout`; if a layout buffer is present and has `LOV_MAGIC_FOREIGN`, it applies file policy immediately. If metadata did not carry the layout but a CL object exists, it performs a small `cl_object_layout_get()` into a `lov_foreign_md` header-sized buffer; `-ERANGE` is accepted because the magic/type header is enough for policy. For directories it checks the supplied `lmd->lsm_obj`, then falls back to `lli_lsm_obj` under `lli_lsm_sem`.

When a foreign type is `LU_FOREIGN_TYPE_SYMLINK`, the file helper assigns `ll_foreign_file_symlink_inode_operations` and clears `IOP_NOFOLLOW`; the directory helper assigns `ll_foreign_dir_symlink_inode_operations`. Other foreign types are logged and left unchanged.

`ll_foreign_is_openable()` prevents fake symlinks from being opened when the VFS should follow them, unless `O_NOFOLLOW` was requested. `ll_foreign_is_removable()` repeats the foreign layout lookup and returns false when policy says the fake symlink should be preserved. With `unset=true`, it sets `LLIF_FOREIGN_REMOVABLE` for supported symlink types so a later removal can proceed.

## State And Persistence Behavior

The file mutates only in-memory inode state: `inode->i_op`, `inode->i_opflags`, and `LLIF_FOREIGN_REMOVABLE` in `ll_inode_info`. It reads persistent LOV/LMV foreign metadata from MDT/CL layout state, but it does not change the foreign layout itself. Removal permission is a client-side policy gate; actual unlink/rmdir persistence occurs in the calling metadata operation.

## Dependencies And Integration Points

This file depends on `llite_internal.h`, LOV foreign metadata (`lov_foreign_md`), LMV foreign metadata (`lmv_foreign_md` / `lmv_stripe_object`), CL layout queries, `ll_foreign_file_symlink_inode_operations`, and `ll_foreign_dir_symlink_inode_operations` implemented in `llite_foreign_symlink.c`. It integrates with open, lookup, getattr, unlink, and rmdir paths in other llite code.

## Risks And Edge Cases

- Header-only CL layout reads intentionally tolerate `-ERANGE`; this relies on the foreign magic/type fields fitting in the small local struct.
- Endianness handling differs: file type uses `le32_to_cpu()` in logging and type checks in some places, while directory metadata is compared directly in several branches. Tests should confirm actual LMV layout byte order.
- Fake symlink behavior changes `i_op` on an inode whose mode may still be regular or directory. All VFS paths must be aware of `d_is_symlink()` versus `S_ISLNK()`.
- Cached inodes may not reflect feature enable/disable until revalidation, as noted in the implementation comments.
- If no CL object or LMV object is cached, removal policy logs uncertainty and allows removal.
- `unset=true` both reports preservation and marks the inode removable; callers must use the flag only for deliberate administrative removal.

## Test Signals

Tests should cover regular foreign symlink management from metadata-carried layout and from CL layout lookup, foreign directory symlink management from supplied and cached LMV, non-symlink foreign types, open without `O_NOFOLLOW` returning not-openable, open with `O_NOFOLLOW`, removal prevention, `unset=true` followed by allowed removal, missing CL/LMV cache behavior, and cached-inode behavior across feature toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c -->
