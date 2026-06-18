# sources/distributed-fs/ceph-client/fs/ext2/Kconfig

Purpose: Defines build-time configuration for the deprecated ext2 filesystem driver and optional xattr, POSIX ACL, and security-label features.

Important APIs/types/functions: Kconfig symbols are `EXT2_FS`, `EXT2_FS_XATTR`, `EXT2_FS_POSIX_ACL`, and `EXT2_FS_SECURITY`. `EXT2_FS` selects `BUFFER_HEAD` and `FS_IOMAP`; ACL support selects `FS_POSIX_ACL`.

Control flow: Configuration dependency flow is linear: ext2 enables the core driver; xattrs depend on ext2; POSIX ACLs and security labels depend on xattrs. The help text directs users toward ext4 for ext2 media because this driver has a 2038 timestamp limitation.

State and persistence behavior: No runtime state. These symbols control whether source files and feature hooks are compiled, which affects on-disk xattr/ACL/security-label support availability.

Dependencies and integration points: Integrates with VFS buffer-head and iomap infrastructure, POSIX ACL framework, and xattr-based security modules such as SELinux. It also gates Makefile object selection.

Risks: Enabling ACL/security without xattr is intentionally disallowed. Disabling xattr removes ACL and security label paths at compile time, which changes user-visible filesystem semantics. The deprecation text is a maintenance signal for tests and consumers.

Test signals: Build matrix for core-only ext2, xattr-only, ACL, and security-label configurations; verify `acl.c` and `xattr_security.c` inclusion follows symbols; ensure help text and dependencies produce valid menuconfig choices.
