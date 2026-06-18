# sources/distributed-fs/ceph-client/fs/f2fs/xattr.c

## Purpose
`xattr.c` implements F2FS extended attribute support. It provides VFS xattr handlers for user, trusted, security, and F2FS-specific advise attributes, reads and writes the combined inline and external xattr storage format, initializes security xattrs, exposes list/get/set operations, detects corrupted xattr layouts, and manages a slab cache for common inline-sized xattr buffers.

## Important APIs, Types, And Functions
The VFS-visible handlers are `f2fs_xattr_user_handler`, `f2fs_xattr_trusted_handler`, `f2fs_xattr_advise_handler`, `f2fs_xattr_security_handler`, and `f2fs_xattr_handlers`. Public F2FS functions are `f2fs_getxattr()`, `f2fs_listxattr()`, `f2fs_setxattr()`, optional `f2fs_init_security()`, `f2fs_init_xattr_cache()`, and `f2fs_destroy_xattr_cache()`.

Storage helpers include `xattr_alloc()`, `xattr_free()`, `read_inline_xattr()`, `read_xattr_block()`, `lookup_all_xattrs()`, `read_all_xattrs()`, `write_all_xattrs()`, `__find_xattr()`, `__find_inline_xattr()`, and `__f2fs_setxattr()`. The common in-memory buffer contains the inline xattr area followed by the external xattr node block, plus padding.

## Control Flow
VFS get/set calls enter generic handlers that validate the namespace and mount options, then call F2FS get/set. `f2fs_getxattr()` validates name length, takes `i_xattr_sem` unless an inode folio is already provided by metadata initialization, calls `lookup_all_xattrs()`, checks the value fits the supplied buffer and backing area, copies the value, and returns its size.

`f2fs_listxattr()` reads all xattrs, walks entries with `list_for_each_xattr`, maps internal indexes to namespace prefixes through `f2fs_xattr_prefix()`, enforces list permissions such as trusted requiring `CAP_SYS_ADMIN`, and emits null-terminated names. It detects entries that cross the valid xattr area and marks the filesystem for fsck.

`f2fs_setxattr()` performs checkpoint and quota readiness checks, initializes dquot state, balances the filesystem, locks global F2FS operations and the inode xattr semaphore, and delegates to `__f2fs_setxattr()`. The inner setter reads all xattrs, finds the entry, honors `XATTR_CREATE` and `XATTR_REPLACE`, computes free space, removes the old entry with `memmove`, writes a new aligned entry if a value is present, terminates the list with zero, and persists through `write_all_xattrs()`. Directory xattr updates request checkpoint or add an xattr-dir inode entry depending on fsync mode.

## State And Persistence Behavior
F2FS xattrs can live partly inline in the inode node page and partly in a separate xattr node referenced by `F2FS_I(inode)->i_xattr_nid`. `write_all_xattrs()` allocates a new xattr node nid when the new header size exceeds inline capacity, writes inline bytes back to the inode folio, writes external bytes to the xattr node folio, or truncates the external node when the updated set fits inline. New xattr buffers are initialized with `F2FS_XATTR_MAGIC` and refcount 1 if no xattrs existed.

Encryption context xattrs trigger `f2fs_set_encrypted_inode()`. Advise xattrs update `F2FS_I(inode)->i_advise` rather than the normal entry table. Security xattrs are initialized through LSM `security_inode_init_security()`. Corruption detection sets `SBI_NEED_FSCK` and calls `f2fs_handle_error(..., ERROR_CORRUPTED_XATTR)`.

## Dependencies And Integration Points
This file depends on VFS xattr APIs, POSIX ACL xattr handlers, Linux security hooks, F2FS node folio helpers, dnode allocation, checkpoint readiness, quota initialization, global operation locks, inode dirtying, encryption state, fsync policy, and error handling from `super.c`. Its format constants and macros come from `xattr.h`.

## Risks
The main risks are bounds errors in variable-length xattr entry walking, inconsistent inline versus external xattr updates, nid allocation failure handling, and races with inode metadata initialization. The code must preserve zero-terminated entry lists and 4-byte alignment. Any missed validation can turn malformed on-disk xattrs into out-of-bounds reads or writes. The setter also has to avoid creating metadata updates when the filesystem is in checkpoint error or checkpoint-disabled no-space states.

## Test Signals
Useful tests include xfstests for xattrs, ACLs, SELinux/security labels, trusted namespace permissions, create/replace/remove semantics, inline-to-external and external-to-inline transitions, long name and large value rejection, fault injection on nid allocation and folio reads, corrupted xattr image handling, fscrypt policy xattr setting, and fsck-required flag propagation.
