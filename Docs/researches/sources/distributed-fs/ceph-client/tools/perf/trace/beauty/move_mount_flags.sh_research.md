# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount_flags.sh

Purpose: Generates the `MOVE_MOUNT_*` flag table.

Important APIs/types/functions: It reads the beauty copy of `uapi/linux/mount.h` and emits `static const char *move_mount_flags[]` with `ilog2(hex_value) + 1` indexes.

Control flow: Optional header directory selection is followed by one grep/sed/xargs pipeline matching hexadecimal `MOVE_MOUNT_` definitions.

State and persistence: stdout-only generator.

Dependencies and integration points: The output is consumed by `move_mount.c`.

Risks: Decimal or expression-valued flags would be missed. The regex requires at least one non-underscore character after `MOVE_MOUNT_`, so unusual names could fail.

Test signals: Regenerate and inspect entries for all current `MOVE_MOUNT_*` flags; compile and trace a syscall using those flags.
