# sources/distributed-fs/ceph-client/fs/ceph/Kconfig

## Purpose
This Kconfig file declares the CephFS client and optional CephFS features in this tree.

## Important APIs, Types, and Functions
It defines `CONFIG_CEPH_FS`, `CONFIG_CEPH_FSCACHE`, `CONFIG_CEPH_FS_POSIX_ACL`, and `CONFIG_CEPH_FS_SECURITY_LABEL`. `CEPH_FS` depends on `INET` and selects `CEPH_LIB`, `NETFS_SUPPORT`, and encryption algorithms when filesystem encryption is enabled.

## Control Flow
There is no runtime control flow. Configuration selects whether CephFS builds, whether it can use FS-Cache for persistent read-only local caching, whether POSIX ACL support is compiled, and whether security-label xattr handling is compiled.

## State and Persistence Behavior
Compile-time state controls the availability of runtime features. Enabling POSIX ACLs changes inode permission behavior and includes `acl.o`; enabling FSCACHE includes Ceph cache integration when dependency constraints are met.

## Dependencies and Integration Points
The file integrates CephFS with networking, libceph, netfs, FS encryption, FS-Cache, POSIX ACL core, and security module xattrs.

## Risks and Edge Cases
The `CEPH_FSCACHE` dependency differs for module versus built-in CephFS to ensure FS-Cache availability matches link mode. Incorrect dependencies can create invalid built-in/module combinations. ACL/security-label options change user-visible xattr and permission semantics.

## Test Signals
Build CephFS as `n`, `m`, and `y`; build with and without FS-Cache, POSIX ACLs, security labels, and encryption; verify menu dependency behavior and link outputs.
