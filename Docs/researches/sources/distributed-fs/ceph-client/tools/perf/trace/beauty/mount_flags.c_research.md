# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.c

Purpose: Beautifies `mount(2)` flag arguments and strips legacy mount magic before display.

Important APIs/types/functions: `syscall_arg__scnprintf_mount_flags` formats `MS_*` flags; `syscall_arg__mask_val_mount_flags` removes `MS_MGC_MSK` when it contains `MS_MGC_VAL`; `mount__scnprintf_flags` uses the generated mount flag array.

Control flow: The mask hook implements the kernel `do_mount` compatibility rule for pre-2.4 magic. The print hook passes the cleaned or original value through `strarray__scnprintf_flags`.

State and persistence: Stateless except for argument-value normalization during display.

Dependencies and integration points: Includes `<sys/mount.h>`, `linux/log2.h`, and `trace/beauty/generated/mount_flags_array.c`; called by perf trace syscall argument plumbing.

Risks: Generated table quality depends on the copied `mount.h`. Missing new flags fall back to numeric bits. Magic stripping must run in the appropriate mask hook path.

Test signals: Trace mounts with common flags and an artificial value containing `MS_MGC_VAL`; verify the magic bits are not shown.
