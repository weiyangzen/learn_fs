<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/jfs/xattr.c

## Purpose
`xattr.c` implements JFS extended attributes and security-xattr initialization. It reads, validates, lists, creates, replaces, removes, and persists EA lists either inline in the inode or in allocated extents, while translating legacy OS/2 attribute names into Linux xattr namespaces.

## Important APIs, types, and functions
The internal buffer descriptor is `struct ea_buffer` with flags `EA_INLINE`, `EA_EXTENT`, `EA_NEW`, and `EA_MALLOC`. Storage helpers include `ea_write_inline`, `ea_write`, `ea_read_inline`, `ea_read`, `ea_get`, `ea_release`, and `ea_put`. Public JFS-facing APIs are `__jfs_setxattr`, `__jfs_getxattr`, `jfs_listxattr`, `jfs_xattr_handlers`, and, under security config, `jfs_init_security`. Namespace helpers are `is_known_namespace`, `name_size`, `copy_name`, and the OS/2-specific get/set handlers.

## Control flow
Reads acquire `xattr_sem`, call `ea_get`, validate EA-list size, scan entries with `FIRST_EA/NEXT_EA/END_EALIST`, detect malformed bounds, and return value size or data. Listing first computes filtered output size, hides `trusted.*` from callers without `CAP_SYS_ADMIN`, prefixes unknown on-disk names with `os2.`, then copies names if the caller supplied a buffer. Sets start a transaction in the VFS wrapper, lock `commit_mutex`, acquire `xattr_sem`, load or allocate a large enough EA buffer, remove an existing entry if replacing, append the new entry if a value is supplied, validate size accounting and `USHRT_MAX` value limits, update the list size, and commit through `ea_put`.

`ea_put` chooses inline storage, preallocated extent storage, or fresh extent writing, invalidates and frees old extent blocks through transaction EA map locks, updates `JFS_IP(inode)->ea`, adjusts inline-space availability, and refunds quota for old blocks. Security initialization iterates LSM-provided xattrs and writes them under the `security.` prefix inside the creating transaction.

## State and persistence behavior
Persistent EA state is a `jfs_ea_list` referenced by the inode `dxd_t` EA descriptor, either `DXD_INLINE` in `i_inline_ea` or `DXD_EXTENT` in allocated blocks. Runtime state includes the xattr rwsem, transaction locks, metapage buffers, kmalloc scratch buffers for large lists, quota reservations, and inline EA availability (`INLINEEA` mode bit). Unknown non-Linux-prefixed on-disk names are preserved but exposed under `os2.`.

## Dependencies and integration points
The implementation depends on VFS xattr handlers, POSIX ACL xattr formats, LSM security initialization, JFS block allocator, quota, transaction EA logging (`txEA`), metapage I/O, inode inline storage, and namespace constants from Linux xattr headers. `super.c` installs `jfs_xattr_handlers`; `namei.c` calls security initialization during inode creation and cleanup paths free EA extents.

## Risks and test signals
Risks include corrupt EA-list size causing overreads, large allocation failures, quota rollback on new extent allocation, inline-area ownership conflicts with xtree root expansion, value length overflow, namespace translation surprises, and synchronous metapage write errors that are hard to propagate. Tests should cover inline-to-extent and extent-to-inline transitions, create/replace/remove flags, zero-length values, `USHRT_MAX` boundary rejection, malformed EA images, permission filtering for trusted names, OS/2 unknown-prefix round trips, security xattr initialization, and fault injection for dbAlloc/metapage/quota failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/xattr.c -->
