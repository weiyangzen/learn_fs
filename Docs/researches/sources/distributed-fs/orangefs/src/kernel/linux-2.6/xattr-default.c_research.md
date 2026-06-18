<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c

## Purpose
Implements the generic/default extended attribute namespace handler for OrangeFS, including unprefixed xattr names. It maps Linux xattr get/set callbacks to OrangeFS inode xattr operations using `PVFS2_XATTR_NAME_DEFAULT_PREFIX`.

## Important APIs, Types, and Functions
Provides `pvfs2_xattr_set_default`, `pvfs2_xattr_get_default`, and, for generic xattr kernels, `pvfs2_xattr_default_handler`. Callback signatures are selected by kernel feature macros covering 4.4-style handler arguments, 2.6.33-style handler flags, and older inode-based callbacks. It calls `convert_to_internal_xattr_flags`, `pvfs2_inode_setxattr`, and `pvfs2_inode_getxattr`.

## Control Flow
Set rejects an empty xattr name, denies operation unless the inode is a regular file or a non-sticky directory, converts Linux create/replace flags to internal flags, and forwards prefix/name/value/size to the inode-level setter. Get rejects empty names and forwards prefix/name/buffer/size to the inode-level getter.

## State and Persistence
No local state is stored. Successful operations persist xattr key/value state in the remote OrangeFS object through inode-level upcalls. The handler object is static registration metadata for the VFS.

## Dependencies and Integration Points
Compiled only under `HAVE_XATTR`; the handler is used by `xattr.c` and by `super.c` when it installs `sb->s_xattr = pvfs2_xattr_handlers`. It depends on VFS mode bits, sticky directory semantics, Linux xattr flags, and OrangeFS xattr prefix constants.

## Risks
The default handler deliberately catches empty-prefix names, so prefix routing order in `pvfs2_xattr_handlers` is important. Permission policy is local and narrow: sticky directories are denied, but other access checks depend on higher VFS layers and server behavior. Kernel-signature compatibility branches can drift.

## Test Signals
Set/get unprefixed xattrs on regular files and directories, reject empty names, reject sticky directory and non-regular/non-directory targets, validate create/replace flag mapping, and compile-test all supported handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-default.c -->
