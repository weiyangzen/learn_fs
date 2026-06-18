# sources/distributed-fs/ceph-client/fs/ceph/acl.c

## Purpose
`acl.c` implements CephFS POSIX ACL get/set and create-time ACL initialization. It maps Linux POSIX ACL operations to Ceph xattrs and MDS setattr/xattr requests.

## Important APIs, Types, and Functions
Important functions are `ceph_set_cached_acl`, `ceph_get_acl`, `ceph_set_acl`, `ceph_pre_init_acls`, and `ceph_init_inode_acls`. It uses POSIX ACL xattr names `system.posix_acl_access` and `system.posix_acl_default`, Ceph inode/client helpers, `struct ceph_acl_sec_ctx`, and Ceph pagelists for create-time xattr batches.

## Control Flow
`ceph_get_acl` rejects RCU lookups with `-ECHILD`, selects the xattr name by ACL type, probes xattr size with `__ceph_getxattr`, allocates a buffer, retries up to ten times on `-ERANGE`, converts xattr bytes with `posix_acl_from_xattr`, treats missing/zero data as no ACL, logs other failures as `-EIO`, and caches only when Ceph xattr-shared caps are issued. `ceph_set_acl` rejects snapshot inodes, validates access/default ACL semantics, updates mode with `posix_acl_update_mode` for access ACLs, writes the mode/ctime through `__ceph_setattr` if needed, writes the ACL xattr through `__ceph_setxattr`, and attempts to roll back mode/ctime if xattr write fails. `ceph_pre_init_acls` computes inherited ACLs for create, drops equivalent access ACLs, encodes one or two xattr name/value pairs into a Ceph pagelist, and stores ACL pointers plus pagelist in `ceph_acl_sec_ctx`. `ceph_init_inode_acls` installs those ACLs into the new inode cache.

## State and Persistence Behavior
ACL persistence is through Ceph xattrs and mode updates on the MDS. In-memory ACL cache state is only trusted when `CEPH_CAP_XATTR_SHARED` is currently issued; otherwise cached ACLs are forgotten to avoid stale permission data. Create-time ACL state is staged in `ceph_acl_sec_ctx` until the MDS create request and then cached in the inode.

## Dependencies and Integration Points
The file depends on Linux POSIX ACL core, xattr conversion helpers, Ceph inode caps, Ceph xattr and setattr helpers, MDS client pagelist encoding, snapshots, and Ceph logging. It is compiled only when `CONFIG_CEPH_FS_POSIX_ACL` is enabled.

## Risks and Edge Cases
ACL xattr size can change between probe and read, so bounded `-ERANGE` retry is required. Mode rollback after xattr failure is best effort and can itself fail. ACL operations on snapshots must be read-only. Cache correctness depends on xattr-shared caps; caching without them would expose stale ACLs. Create-time pagelist reservation must handle memory failures without leaking ACL refs or pagelists.

## Test Signals
Test get/set access and default ACLs, setting default ACLs on non-directories, ACL removal, mode changes induced by access ACLs, snapshot rejection, MDS/xattr failures with rollback, `-ERANGE` retries, create inheritance with one and two ACL xattrs, and ACL cache invalidation when xattr caps are absent.
