## sources/distributed-fs/beegfs/client_module/source/os/OsCompat.h

**Purpose:** Declares and defines kernel-version compatibility wrappers for VFS permissions, writeback errors, ACL xattrs, page completion, iterator write checks, rbtree traversal, umask, mmap locks, inode locks, access checks, and RDMA NUMA node lookup.

**Important APIs/types/functions:** Provides `fhgfs_set_wb_error`, `os_generic_permission`, `os_inode_permission`, `is_32bit_api`, UID/GID accessors for older kernels, `OsCompat_initKmemCache` prototypes, list/rbtree fallback macros, `os_posix_acl_from_xattr`, `os_posix_acl_to_xattr`, `page_endio`, `os_generic_write_checks`, `beegfs_hasMappings`, `os_inode_lock`, `os_inode_unlock`, `os_access_ok`, and optional `ibdev_to_node`.

**Control flow:** Most helpers select the correct kernel API variant using feature macros. Permission helpers choose idmapped mount, user-namespace mount, or legacy signatures. Page completion records mapping-level writeback errors and completes read/write pages appropriately.

**State and persistence behavior:** The header itself stores no state. Its wrappers manipulate kernel state such as inode permissions, mapping writeback error sequences, page uptodate/writeback flags, and mmap/inode locks.

**Dependencies and integration points:** Included widely by BeeGFS filesystem code. Integrates with Linux VFS, ACL, mmap, writeback, namespace/idmap, RDMA, and list/rbtree APIs.

**Risks:** Permission wrappers must be used in the right context; `os_inode_permission` is documented for helpers/ioctls and direct `generic_permission` should remain inside `->permission` paths to avoid recursion. Writeback error migration from page flags to `mapping_set_error` must be consistent with wait/check callers. Compile-time feature detection must track kernel API changes precisely.

**Test signals:** Compile against kernels before and after idmapped mounts, Linux 6.12 writeback changes, iterator write-check changes, mmap tree layout changes, inode lock renames, and RDMA header moves. Runtime tests should cover permission checks on idmapped mounts, page read/write error propagation, and mmap mapping detection.
