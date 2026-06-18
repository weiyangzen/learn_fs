# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_trusted.c

Purpose: this file provides the HFS+ `trusted.*` xattr namespace handler.

Important APIs and functions: `hfsplus_trusted_getxattr()` delegates reads to `hfsplus_getxattr()` with `XATTR_TRUSTED_PREFIX`. `hfsplus_trusted_setxattr()` delegates writes/removes to `hfsplus_setxattr()` with the same prefix. `hfsplus_xattr_trusted_handler` registers the handler prefix and callbacks for VFS xattr dispatch.

Control flow: VFS dispatch supplies an unprefixed trusted xattr suffix. The handler constructs the full namespace indirectly by passing the suffix and trusted prefix to the common HFS+ wrapper, which allocates a full name, calls the internal HFS+ xattr implementation, and frees the temporary name.

State and persistence: this file has no local state. Successful writes persist into the HFS+ attributes B-tree and cause catalog xattr flags and inode ctime to be updated by the common implementation.

Dependencies and integration: it depends on Linux trusted xattr namespace constants, NLS sizing through included HFS+ headers, and the common HFS+ xattr helpers. Listing permissions for trusted attributes are enforced in `xattr.c` via `can_list()`, not here.

Risks: trusted attributes should only be visible to privileged callers; this file relies on the VFS xattr framework and common listing helper for permission behavior rather than adding checks in each callback. Prefix construction inherits the common fixed-size buffer constraints.

Test signals: set/get/remove `trusted.*` attributes as privileged users, verify unprivileged list behavior through common listing, confirm `XATTR_CREATE`/`XATTR_REPLACE` semantics, and verify that deleting the last trusted xattr clears the catalog `HFSPLUS_XATTR_EXISTS` flag through `hfsplus_removexattr()`.
