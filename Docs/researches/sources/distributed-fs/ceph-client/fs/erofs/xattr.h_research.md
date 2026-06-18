# sources/distributed-fs/ceph-client/fs/erofs/xattr.h

Purpose: Declares the EROFS xattr, ACL, and inode-fingerprint interfaces consumed by the rest of the filesystem while providing no-op fallbacks when xattr or ACL support is not compiled in.

Important APIs, types, and functions: With `CONFIG_EROFS_FS_XATTR`, it exports `erofs_xattr_handlers`, `erofs_xattr_prefixes_init()`, `erofs_xattr_prefixes_cleanup()`, and `erofs_listxattr()`. Without xattr support, prefix init/cleanup become inline no-ops, while `erofs_listxattr` and `erofs_xattr_handlers` are defined as `NULL` so VFS setup can remain simple. With `CONFIG_EROFS_FS_POSIX_ACL`, it declares `erofs_get_acl()`; otherwise the macro resolves to `NULL`. It also declares `erofs_xattr_fill_inode_fingerprint()` and `erofs_inode_has_noacl()`.

Control flow: `super.c` includes this header and unconditionally assigns `sb->s_xattr = erofs_xattr_handlers`, calls xattr-prefix init/cleanup around mount lifetime, and relies on compile-time fallbacks to do the right thing when features are disabled. Inode operation tables can similarly use `erofs_get_acl` as either a function pointer or `NULL`.

State and persistence behavior: The header owns no state. Its main persistence impact is compile-time feature selection: enabling xattrs adds runtime superblock prefix tables and per-inode xattr caches from `xattr.c`; disabling xattrs removes those behaviors without changing call sites.

Dependencies and integration points: Includes `internal.h`, POSIX ACL xattr definitions, and VFS xattr declarations. It is a small but important integration contract between EROFS superblock setup, inode operations, xattr implementation, and optional page-cache sharing.

Risks: The unconditional declarations for fingerprint/noacl helpers require compatible stubs or definitions elsewhere for configurations that disable the underlying feature. Macro-to-NULL fallbacks are convenient, but call sites must not call them as real functions when the feature is disabled. Any signature drift between this header and `xattr.c` would break multiple mount and inode-operation paths.

Test signals: Build matrix coverage is the key signal: xattrs on/off, POSIX ACL on/off, security xattrs on/off, and page-cache sharing on/off. Runtime smoke tests should mount with `user_xattr`, `nouser_xattr`, `acl`, and `noacl` under supported configurations and verify that disabled-feature configurations still mount and expose no xattr handlers.
