# sources/distributed-fs/ceph-client/fs/hfsplus/xattr_security.c

Purpose: this file implements the `security.*` xattr handler for HFS+ and the LSM initialization hook used when new inodes are created.

Important APIs and functions: `hfsplus_security_getxattr()` and `hfsplus_security_setxattr()` pass `XATTR_SECURITY_PREFIX` and `XATTR_SECURITY_PREFIX_LEN` into the common HFS+ xattr helpers. `hfsplus_initxattrs()` iterates the `struct xattr` array produced by LSMs, constructs full `security.<name>` strings, and writes them with `__hfsplus_setxattr()`. `hfsplus_init_security()` calls `security_inode_init_security()` with that callback. `hfsplus_xattr_security_handler` exposes the VFS handler.

Control flow: normal VFS get/set calls enter the handler and delegate directly to `hfsplus_getxattr()` or `hfsplus_setxattr()`. During inode creation, LSM code calls the init callback with one or more name/value pairs; empty names are skipped, each valid name is prefixed and written, and the loop stops at first error.

State and persistence: the file itself stores no state. It triggers persistent HFS+ xattr writes through `__hfsplus_setxattr()`, which may create the attributes file and update catalog flags. Security labels therefore become part of the on-disk HFS+ attributes tree.

Dependencies and integration: it depends on Linux security hooks, NLS sizing, HFS+ xattr helpers, and Linux xattr namespace constants. It integrates with inode creation paths through `hfsplus_init_security()` and with VFS xattr dispatch through the exported handler object.

Risks: `xattr_name` uses the same maximum HFS+ attribute string allocation as the common implementation. Very long LSM-generated names must fit that bound once prefixed. Initialization stops on the first failed label, so partial label sets can be created if an earlier write succeeds and a later one fails. The comment header says `xattr_trusted.c` even though the file implements security labels, which is documentation noise rather than behavior.

Test signals: create files under SELinux/Smack-style configurations, verify security labels persist and list/get correctly, inject multiple init labels with one failing write, and test empty-name entries. Mounts where the attributes tree is absent should exercise lazy creation from the security initialization path.
