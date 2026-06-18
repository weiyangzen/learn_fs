# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsXAttrHandlers.h

## Purpose
Declares BeeGFS xattr handler arrays and the security xattr initialization API used by inode creation and superblock setup.

## Important APIs and Types
`FhgfsXAttr_init_security()` is exported for create paths to initialize LSM-provided security xattrs. Depending on const-handler kernel macros, the header declares `fhgfs_xattr_handlers`, `fhgfs_xattr_handlers_acl`, `fhgfs_xattr_handlers_selinux`, and `fhgfs_xattr_handlers_noacl` with the correct pointer constness. It also declares `FhgfsXAttr_getSecurity()` for kernels using xattr handler callbacks.

## Control Flow
The header itself has no runtime flow. Compile-time branching ensures the same implementation can be assigned to `super_block->s_xattr` across kernels with different handler constness and callback signatures.

## State and Persistence
No owned state. The declared arrays are static module-global handler tables defined in `FhgfsXAttrHandlers.c`.

## Dependencies and Integration Points
Includes Linux xattr APIs and is consumed by `FhgfsOpsSuper.c` during mount and by inode creation/security paths.

## Risks
Constness/signature mismatches across kernel versions can break module builds. Consumers should only reference arrays that exist under the same `KERNEL_HAS_GET_ACL` conditions.

## Test Signals
Compile matrix over handler constness variants, mount with each xattr config combination, and create-path tests that call `FhgfsXAttr_init_security()`.
