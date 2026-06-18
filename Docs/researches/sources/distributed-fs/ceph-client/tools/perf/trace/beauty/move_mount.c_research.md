# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/move_mount.c

Purpose: Formats `move_mount(2)` flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_move_mount_flags` is the exported formatter and delegates to `move_mount__scnprintf_flags`, which includes the generated `move_mount_flags_array.c` and defines `MOVE_MOUNT_` prefix metadata.

Control flow: The formatter reads `arg->val` and passes it directly to `strarray__scnprintf_flags`.

State and persistence: No persistent state and no argument masking.

Dependencies and integration points: Depends on perf beauty helpers and generated output from `move_mount_flags.sh`.

Risks: Unknown future flags print numerically. Correctness depends on generated entries being indexed by bit position.

Test signals: Trace `move_mount` calls with `MOVE_MOUNT_F_*` values and combined flags; verify symbolic output with and without prefixes.
