# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enum_defs.autogen.h

Purpose: generated feature-definition header declaring which sched_ext enum constants were known when the headers were generated.

Important APIs/macros: `HAVE_*` macros cover public constants, CPU preemption reasons, dequeue/enqueue flags, DSQ IDs and flags, task states, exit codes, kfunc masks, kick flags, ops flags, idle-pick flags, slices, reenqueue flags, rq flags, scheduling state, task-group state, and wake flags.

Control flow: none; it is compile-time feature data.

State and persistence: generated static header content.

Dependencies and integration: consumed by `common.bpf.h` and compatibility code to guard references to enum names that may be absent from generated `vmlinux.h` or running kernels.

Risks: it must be regenerated when enum coverage changes. Stale `HAVE_*` definitions can make compatibility wrappers take incorrect branches or reference unavailable enum values.

Test signals: regenerate with the upstream script, compile all sched_ext examples, and ensure compatibility paths for gated enum constants compile.
