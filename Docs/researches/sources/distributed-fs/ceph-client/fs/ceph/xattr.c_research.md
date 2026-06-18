# sources/distributed-fs/ceph-client/fs/ceph/xattr.c

## Purpose
`xattr.c` implements CephFS extended attribute handling, including virtual `ceph.*` attributes, cached xattr rb-tree construction from MDS blobs, local dirty updates under xattr caps, synchronous MDS xattr updates, xattr listing, and security-label initialization support.

## Important APIs, Types, And Functions
Important functions include `__ceph_getxattr()`, `ceph_listxattr()`, `__ceph_setxattr()`, `ceph_sync_setxattr()`, `__ceph_build_xattrs_blob()`, `__ceph_destroy_xattrs()`, `ceph_security_xattr_wanted()`, `ceph_security_xattr_deadlock()`, `ceph_security_init_secctx()`, and `ceph_release_acl_sec_ctx()`. Virtual xattrs are described by `struct ceph_vxattr` tables for directories, files, and common attributes.

## Control Flow
Getxattr first checks for virtual `ceph.*` names and refreshes stats/caps as needed, otherwise it ensures shared xattr caps or fetches xattrs from the MDS, builds the rb-tree from the encoded blob, and copies the value. Setxattr rejects snapshots, handles read-only virtual attributes, chooses synchronous MDS updates for `ceph.*`, missing caps, or oversized blobs, and otherwise preallocates memory/blob/cap flush state, updates the rb-tree, marks xattr caps dirty, and later encodes a blob for cap flush.

## State, Persistence, And Dependencies
Per-inode xattr state is `ci->i_xattrs`: encoded blob, preallocated blob, rb-tree, dirty flag, counts, sizes, and versions protected by `i_ceph_lock`. Persistent xattr state is authoritative on the MDS; local dirty state is flushed through caps.

## Integration Points
The file integrates with MDS getattr/setxattr requests, cap dirty tracking, snap cap snapshots, layout/pool metadata, quota realm checks, fscrypt auth, POSIX ACL/security label creation, LSM hooks, and VFS xattr handlers.

## Risks
Risks include lock dropping during xattr tree builds, stale blob/version races, max-xattr-size transitions, security xattr deadlocks while filling traces, memory ownership for blob/name/value allocations, and read-only virtual attribute semantics.

## Test Signals
Test virtual xattrs, user/trusted/security xattrs, listxattr sizing, local dirty update versus sync fallback, max size overflow, concurrent cap grants while building xattrs, quota xattr realm validation, fscrypt/security-label configs, and snapshot read-only behavior.
