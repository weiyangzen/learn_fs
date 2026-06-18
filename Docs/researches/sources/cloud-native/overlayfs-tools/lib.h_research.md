# sources/cloud-native/overlayfs-tools/lib.h

Purpose: declares fsck exit codes, global status/option flags, overlay layer data structures, scan context structures, and helper APIs.

Important APIs/types/functions: `struct ovl_layer`, `struct ovl_fs`, `struct scan_dir_data`, `struct scan_result`, `struct scan_ctx`, `struct scan_operations`, flag constants, `set_inconsistency`, `set_abort`, `set_changed`, `scan_dir`, `ask_question`, and xattr helpers.

Control flow: status helpers OR bits into caller-provided status. Callback structure defines the event hooks `scan_dir` will invoke.

State and persistence: data structures represent opened filesystem layers with paths, fds, stack index, and capability flags. No persistence in the header itself.

Dependencies/integration: shared contract between `fsck.c`, `check.c`, `lib.c`, and `mount.c`.

Risks: typo `OVL_ST_INCONSISTNECY` is part of the local API. Global flag/status constants make reentrancy unlikely. Struct ownership rules are implicit.

Test signals: compile coverage plus fsck behavior tests around every flag/status transition.
