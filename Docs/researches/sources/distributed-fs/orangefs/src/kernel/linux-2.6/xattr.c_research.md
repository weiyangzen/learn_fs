<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c

## Purpose
Coordinates Linux VFS extended attribute operations for OrangeFS. In generic xattr/ACL builds it exports the handler array for superblock registration; otherwise it provides manual get/set prefix dispatch for older kernels plus list/remove wrappers.

## Important APIs, Types, and Functions
Defines `pvfs2_xattr_handlers` with ACL access/default handlers, trusted handler, default handler, and NULL terminator when generic xattrs and POSIX ACL support are enabled. Older builds define `pvfs2_strcmp_prefix`, `pvfs2_setxattr`, and `pvfs2_getxattr`. All supported builds define `pvfs2_listxattr` and `pvfs2_removexattr` under `HAVE_XATTR`.

## Control Flow
Generic-handler builds route by VFS handler prefix. Older set/get paths test `trusted.` first, then ACL prefixes; ACL requests return `-EOPNOTSUPP` if the inode ACL flag is disabled, otherwise they fall through to default xattr handling. Default handling receives the original full name except trusted passes the stripped suffix. Listing delegates to `pvfs2_inode_listxattr`; removal delegates to `pvfs2_inode_removexattr` with `XATTR_REPLACE`.

## State and Persistence
No local state is stored. Handler arrays are static metadata. Persistent xattr state lives in OrangeFS objects and is accessed through inode-level get/set/list/remove upcalls.

## Dependencies and Integration Points
Integrates with ACL xattr handlers, default/trusted handlers, inode ACL flag helper `get_acl_flag`, Linux xattr callback signatures, `super.c` superblock registration, and symlink/directory/file inode operation tables that expose list/get/set/remove callbacks.

## Risks
Manual prefix dispatch treats ACL-enabled old-kernel operations by falling through to default handling rather than dedicated ACL handler logic, so behavior depends on surrounding ACL code. `pvfs2_removexattr` passes `NULL` prefix and the full name, which must match inode-level expectations. Handler ordering matters because the default empty prefix must come last.

## Test Signals
List and remove xattrs across namespaces, confirm generic handler array order, test ACL prefix behavior with ACL mount option on and off, verify trusted routing strips prefixes correctly in old builds, and compare behavior between generic and legacy xattr configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr.c -->
