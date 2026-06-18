# sources/distributed-fs/glusterfs/xlators/features/selinux/src/selinux.h

## Purpose
`selinux.h` defines the xattr names and private configuration type used by the SELinux translator.

## Important APIs and state
`SELINUX_XATTR` is the public key `security.selinux`; `SELINUX_GLUSTER_XATTR` is the backend key `trusted.glusterfs.selinux`. `struct selinux_priv` contains `gf_boolean_t selinux_enabled`, which is loaded from the translator option and read by all xattr FOPs.

## Dependencies and integration
The header assumes GlusterFS boolean types are available through including source context. It is included by `selinux.c` and indirectly defines the translator's external behavior for xattr key remapping.

## Risks and test signals
Changing either macro changes on-disk/backend xattr compatibility. Tests should assert public clients see `security.selinux` while storage-facing operations use `trusted.glusterfs.selinux`, and that reconfigure changes only `selinux_enabled`.
