# sources/cloud-native/overlayfs-tools/check.h

Purpose: declares the filesystem scan/fix entry point used by the fsck executable.

Important APIs/types/functions: `int ovl_scan_fix(struct ovl_fs *ofs);`.

Control flow: callers pass a fully populated and opened overlay filesystem description. The implementation performs multi-pass validation and optional repair.

State and persistence: no header state; implementation may mutate upper/lower layers and global status according to flags.

Dependencies/integration: requires `struct ovl_fs` from `lib.h` to be visible before inclusion; used by `fsck.c`.

Risks: minimal header hides destructive behavior, so caller-side safeguards such as mount checks and read-only checks are essential.

Test signals: compile coverage plus `fsck.overlay` fixture tests.
