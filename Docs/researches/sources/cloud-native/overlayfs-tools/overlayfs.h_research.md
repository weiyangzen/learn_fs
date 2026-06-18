# sources/cloud-native/overlayfs-tools/overlayfs.h

Purpose: defines overlayfs constants and declares option-splitting helpers shared by fsck and mount parsing.

Important APIs/types/functions: `OVERLAYFS_SUPER_MAGIC`, `OVERLAY_NAME`, `OVL_MAX_STACK`, option prefixes, trusted overlay xattr names, `ovl_split_lowerdirs`, and `ovl_next_opt`.

Control flow: constants guide mount detection, layer-count validation, and xattr reads/writes.

State and persistence: no state.

Dependencies/integration: included by `fsck.c`, `check.c`, `mount.c`, and `overlayfs.c`.

Risks: constants must stay aligned with Linux overlayfs. Only trusted xattr namespace is supported.

Test signals: fsck/check tests covering every xattr name and max stack boundary.
