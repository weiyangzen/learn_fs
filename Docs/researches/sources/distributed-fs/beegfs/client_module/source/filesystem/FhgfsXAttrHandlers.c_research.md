# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.c

## Purpose
Implements BeeGFS xattr handler tables and operations for user, security/SELinux, and POSIX ACL extended attributes across kernel xattr API versions.

## Important APIs and Functions
ACL handlers `FhgfsXAttrSetACL()` and `FhgfsXAttrGetACL()` map POSIX ACL xattrs to BeeGFS remote xattr operations and update file mode bits for access ACLs. `FhgfsXAttr_getUser()`/`setUser()` and `FhgfsXAttr_getSecurity()`/`setSecurity()` reapply namespace prefixes before delegating to `FhgfsOps_getxattr`, `FhgfsOps_setxattr`, or removal helpers. `FhgfsXAttr_init_security()` invokes LSM initialization using `security_inode_init_security()`. Handler arrays expose all, ACL-only, SELinux-only, and user-only combinations.

## Control Flow
VFS strips namespace prefixes before handler calls; handlers allocate prefixed names and call BeeGFS inode xattr operations. ACL set validates empty handler names, owner/capability, symlink exclusion, ACL parse/equivalence, and mode update via `FhgfsOps_setattr()` before setting/removing the ACL xattr. Security initialization checks directory security state, then applies each generated LSM xattr in the security namespace.

## State and Persistence
Local state is transient allocations for prefixed names and ACL parsing. Persistent effect is remote metadata mutation through BeeGFS xattr and setattr RPC paths. Handler arrays are static module state selected into `sb->s_xattr` by mount config.

## Dependencies and Integration Points
Depends on Linux xattr, POSIX ACL, LSM hooks, idmapped/user namespace helpers, `FhgfsOpsInode`, `FhgfsOpsHelper`, and superblock config selection in `FhgfsOpsSuper.c`.

## Risks
Name length handling differs between the older dynamic prefix helpers and `beegfs_xattr_set()`, which uses `XATTR_NAME_MAX` and `snprintf`; long names need careful validation. Several paths allocate before remote calls and must free on all exits. ACL mode updates and remote xattr updates are separate operations, so partial failure after chmod-like setattr can leave mode changed without the intended ACL. `FhgfsXAttr_security_xattr_enabled()` checks `i_security` and `s_security`; behavior depends on kernel security structure availability.

## Test Signals
Exercise get/set/remove for `user.*` and `security.*`, ACL access/default set including equivalent-mode ACLs and empty ACL removal, owner/capability denial, symlink ACL denial, SELinux inode creation labels, long names, `XATTR_CREATE`/`XATTR_REPLACE`, and mount configs enabling/disabling ACL and SELinux handlers.
