# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux-messages.h

## Purpose
This header defines stable GlusterFS log/message IDs for the SELinux translator.

## Important APIs
`GLFS_MSGID(SL, ...)` registers IDs for invalid volfile configuration, out-of-memory paths, memory-accounting initialization failure, missing `trusted.glusterfs.selinux` xattr, and missing `security.selinux` xattr. The comments explicitly require append-only maintenance to avoid ID reuse.

## Dependencies and integration
It includes `glusterfs/glfs-message-id.h` and is consumed by `selinux.c` for `gf_msg()` calls in init and xattr rename paths.

## Risks and test signals
Removing or reordering IDs can break log compatibility and diagnostics. New log points should append IDs, not repurpose existing names. Tests are mainly compile-time plus log-path validation for invalid volfiles, memory-accounting failure, and xattr rename failure.
