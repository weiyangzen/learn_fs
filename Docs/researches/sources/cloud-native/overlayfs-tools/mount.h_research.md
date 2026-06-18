# sources/cloud-native/overlayfs-tools/mount.h

Purpose: declares overlay mount-option parsing and live mount checking APIs.

Important APIs/types/functions: `struct ovl_config` with `lowerdir`, `upperdir`, `workdir`; `ovl_parse_opt`, `ovl_free_opt`, `ovl_get_dirs`, and `ovl_check_mount`.

Control flow: callers parse raw `-o` options into `ovl_config`, resolve paths into owned arrays/strings, then optionally check mounted status against a populated `ovl_fs`.

State and persistence: no persistence; ownership of allocated strings is shared by documented usage in implementation rather than explicit header comments.

Dependencies/integration: `fsck.c` consumes these APIs before opening and scanning layers.

Risks: header uses `struct ovl_fs` and `bool` without including their definitions; include order matters.

Test signals: compile and fsck option parsing tests.
