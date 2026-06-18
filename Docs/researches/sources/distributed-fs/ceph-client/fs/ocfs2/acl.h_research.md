# sources/distributed-fs/ceph-client/fs/ocfs2/acl.h

## Purpose
`acl.h` declares the OCFS2 ACL on-disk entry format and ACL functions used by inode and creation paths. It is the interface between ACL implementation, xattr storage, and inode operation wiring.

## Important APIs and Types
`ocfs2_acl_entry` is the serialized little-endian ACL entry with `e_tag`, `e_perm`, and `e_id`. Exported functions are `ocfs2_iop_get_acl()`, `ocfs2_iop_set_acl()`, `ocfs2_acl_chmod()`, and `ocfs2_init_acl()`. Initialization accepts journal, inode, dinode buffer, and allocation-context inputs needed for xattr creation.

## Control Flow and Integration
Inode operations use the get/set hooks. Attribute-change paths call `ocfs2_acl_chmod()`. Creation paths call `ocfs2_init_acl()` to inherit default ACLs or apply umask. `acl.c` performs locking, xattr reads/writes, and journal updates behind these declarations.

## State and Persistence Behavior
The header has no runtime state. It defines persistent ACL xattr entry layout, so endian fields and size assumptions must remain compatible with existing volumes. The declared functions persist ACL xattrs, inode modes, and ctime through OCFS2 journaling.

## Dependencies and Integration Points
It includes POSIX ACL xattr definitions and is included by `acl.c` plus OCFS2 inode/namei code that wires ACL behavior.

## Risks
Changing `ocfs2_acl_entry` would break on-disk compatibility. Prototype changes ripple into VFS hooks and creation paths. Idmapped behavior would require coordinated interface and implementation changes.

## Test Signals
Build all callers, then test ACL xattr byte compatibility, default ACL inheritance, chmod behavior, and creation paths that require allocation contexts.
