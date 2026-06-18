<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c

Purpose: handles generic SH FPU state initialization and lazy restore.

Important APIs/types/functions: `init_fpu()`, `__fpu_state_restore()`, `fpu_state_restore()`.

Control flow: initializes hard or soft FPU save area, enables FPU when restoring current task, restores state, disables as appropriate, and marks TS_USEDFPU.

State and persistence: per-task FPU state is stored in `thread.xstate`; CPU FPU enable status is transient.

Dependencies/integration: integrates scheduler lazy FPU handling, traps, and hard/soft FPU layouts.

Risks: incorrect lazy flags leak FPU state across tasks or fault recursively.

Test signals: test context switching with FPU users, signal FPU preservation, and no-FPU configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/fpu.c -->
