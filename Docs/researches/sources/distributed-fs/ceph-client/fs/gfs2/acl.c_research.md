# sources/distributed-fs/ceph-client/fs/gfs2/acl.c

## Purpose
Implements POSIX ACL get/set support for GFS2 by mapping ACLs to system extended attributes under the inode glock.

## Important APIs, Types, And Functions
`gfs2_acl_name()` maps `ACL_TYPE_ACCESS` and `ACL_TYPE_DEFAULT` to POSIX ACL xattr names. `__gfs2_get_acl()` reads ACL xattr data with `gfs2_xattr_acl_get()` and converts it via `posix_acl_from_xattr()`. `gfs2_get_acl()` is the VFS-facing getter and acquires a shared inode glock if needed. `__gfs2_set_acl()` serializes an ACL with `posix_acl_to_xattr()`, writes it through `__gfs2_xattr_set()`, and updates the cached ACL. `gfs2_set_acl()` validates ACL entry count, obtains quota accounting, takes an exclusive glock if needed, updates mode bits for access ACLs, writes the ACL, and marks the inode dirty if mode changed.

## Control Flow
Get rejects RCU lookup with `-ECHILD`, avoids disk access when no extended attributes exist, and conditionally locks. Set checks maximum ACL entries, acquires quota state, locks exclusively unless already held, possibly rewrites inode mode, writes xattr state, then unwinds lock and quota references.

## State And Persistence
ACLs persist as GFS2 system xattrs. Access ACL updates may persist inode mode changes, ctime, and dirty inode state. Cached ACL state is updated after successful writes.

## Dependencies And Integration Points
Depends on GFS2 xattr, glock, quota, transaction/inode dirtying paths, and Linux POSIX ACL conversion APIs. Used by inode operation tables elsewhere in GFS2.

## Risks
Set must coordinate quota and glock state or cluster-visible ACL/mode updates can race. Entry-count limits scale with block size. RCU ACL lookup is unsupported. Mode updates must remain consistent with ACL xattr writes.

## Test Signals
Test access/default ACL get/set/remove, oversized ACL rejection, mode-bit changes from access ACLs, concurrent cluster lookup under glocks, no-eattr fast path, and quota failure unwinding.
