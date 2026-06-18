# sources/cloud-native/overlayfs-tools/mount.c

Purpose: parses overlay mount options, resolves lower/upper/work directories, scans live mounts, and detects whether a target overlay layer is currently mounted.

Important APIs/types/functions: `ovl_resolve_lowerdirs`, `ovl_get_dirs`, `ovl_free_opt`, `ovl_parse_opt`, `ovl_scan_mount_init`, `ovl_scan_mount_exit`, and `ovl_check_mount`.

Control flow: mount option strings are split with kernel-compatible helpers. Directory options are realpath-resolved; lowerdir lists are split on unescaped colons. Live mount scanning reads `/proc/mounts`, filters `overlay` entries, skips relative path mounts, resolves options, and compares every target lower/upper/work path against mounted entries.

State and persistence: no writes. Allocates and frees path arrays and mount entry structures.

Dependencies/integration: used by `fsck.c` for user option parsing and mounted-safety checks; depends on `overlayfs.c` split helpers and constants in `overlayfs.h`.

Risks: relative-path mounted overlays cannot be reliably checked and are skipped with a FIXME. Any one matching lower path marks the target mounted because fsck may modify lower layers.

Test signals: unit tests should cover escaped colons/commas, too many lower layers, relative live mounts, hard matches on lower/upper/work, and invalid paths.
