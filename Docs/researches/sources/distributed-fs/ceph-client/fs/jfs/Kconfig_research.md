# sources/distributed-fs/ceph-client/fs/jfs/Kconfig

## Purpose
Declares JFS filesystem build options and kernel dependencies.

## Important APIs, types, and functions
`JFS_FS` is the main tristate and selects buffer heads, NLS, CRC32, and legacy direct I/O. `JFS_POSIX_ACL`, `JFS_SECURITY`, `JFS_DEBUG`, and `JFS_STATISTICS` gate ACLs, security labels, debug logging, and procfs statistics.

## Control flow
Kconfig symbols drive Makefile object selection and source-level `#ifdef` paths.

## State and persistence behavior
No runtime state; controls which runtime features are compiled.

## Dependencies and integration points
Integrates with Kbuild, documentation, ACL/security frameworks, procfs, and generic block/page-cache helpers.

## Risks and test signals
Build JFS built-in/module with ACL, security, debug, and statistics toggled to catch dependency and link errors.
