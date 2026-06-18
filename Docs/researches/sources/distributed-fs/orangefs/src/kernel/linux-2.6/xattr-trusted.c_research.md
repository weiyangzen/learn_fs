<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c

## Purpose
Implements OrangeFS handling for the Linux `trusted.*` extended attribute namespace. It enforces `CAP_SYS_ADMIN` locally before forwarding trusted xattr gets and sets to the OrangeFS inode-level xattr implementation.

## Important APIs, Types, and Functions
Provides `pvfs2_xattr_set_trusted`, `pvfs2_xattr_get_trusted`, and optional `pvfs2_xattr_trusted_handler`. Like the default handler, callback signatures vary by kernel feature macros. It calls `capable(CAP_SYS_ADMIN)`, `convert_to_internal_xattr_flags`, `pvfs2_inode_setxattr`, and `pvfs2_inode_getxattr` with `PVFS2_XATTR_NAME_TRUSTED_PREFIX`.

## Control Flow
Set logs the requested name and size, rejects empty names, denies callers without admin capability, converts flags, then forwards to the inode setter. Get follows the same empty-name and capability checks before forwarding to the inode getter.

## State and Persistence
No local state is kept. Trusted xattr data is persisted remotely through OrangeFS xattr upcalls. The static handler is registration metadata used by generic xattr routing.

## Dependencies and Integration Points
Compiled under `HAVE_XATTR` and registered by `xattr.c` when generic xattr handlers are available. It integrates with Linux capability checks and server-side OrangeFS xattr storage. Older callback paths are reached through the manual prefix router in `xattr.c`.

## Risks
Local capability checks must match Linux trusted-xattr semantics; any bypass in older manual routing would expose trusted namespace data. The code relies on the name passed after prefix stripping in older paths and after handler routing in generic paths. No object-type restrictions are enforced here beyond what VFS/server layers provide.

## Test Signals
Verify trusted xattr get/set success as an admin-capable caller, `-EPERM` as an unprivileged caller, `-EINVAL` for empty suffixes, create/replace flag behavior, and both generic-handler and manual-prefix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/xattr-trusted.c -->
