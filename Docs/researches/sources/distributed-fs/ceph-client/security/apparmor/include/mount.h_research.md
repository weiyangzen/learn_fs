# sources/distributed-fs/ceph-client/security/apparmor/include/mount.h

## Purpose
`mount.h` defines AppArmor mount permission bits and declares the mount mediation API used by LSM mount hooks.

## Important APIs and types
Permission bits include `AA_MAY_PIVOTROOT`, `AA_MAY_MOUNT`, `AA_MAY_UMOUNT`, and `AA_AUDIT_DATA`/`AA_MNT_CONT_MATCH`. `AA_MS_IGNORE_MASK` lists kernel/internal mount flags ignored by policy. Public functions cover remount, bind mount, mount propagation type changes, old/new move mount paths, new mount, umount, and pivot_root.

## Control flow and integration
LSM mount hooks pass credentials, labels, paths, device/type/data strings, and flags to these functions. Implementations match policy and audit through shared domain/policy/perms infrastructure.

## State and persistence
The header owns no state. Mount decisions use current labels and loaded policy; successful mount operations change VFS state outside AppArmor.

## Dependencies
It depends on Linux fs/path structures, AppArmor domain, and policy definitions.

## Risks
Mount flag normalization via `AA_MS_IGNORE_MASK` must remain aligned with kernel VFS semantics. Move-mount and detached mount behavior is subtle and needs tests across old/new APIs.

## Test signals
Test mount, remount, bind, move, propagation change, umount, and pivot_root permissions with ignored kernel flags and audit data matching.
