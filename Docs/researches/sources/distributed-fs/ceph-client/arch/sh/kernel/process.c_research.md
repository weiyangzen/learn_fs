# sources/distributed-fs/ceph-client/arch/sh/kernel/process.c

Purpose: manages architecture task state allocation, FPU/xstate lifetime, and stack protector state.

Important APIs and control flow: `arch_dup_task_struct()` forces lazy FPU state to memory, copies the task struct, and deep-copies `thread.xstate` when present. `free_thread_xstate()` and `arch_release_task_struct()` free per-task FPU/emulation state. `arch_task_cache_init()` creates the `task_xstate` cache when `xstate_size` is nonzero. `init_thread_xstate()` chooses hard FPU, software FPU, or no xstate size based on CPU flags and config. Stack protector guard is exported for non-SMP/global use when configured.

State, dependencies, and risks: persistent state includes `task_xstate_cachep`, `xstate_size`, and optional `__stack_chk_guard`. Dependencies include SH FPU helpers, boot CPU feature detection, slab caches, and task lifecycle hooks. Risks include shallow-copy hazards if xstate allocation fails after task copy, incorrect xstate size for CPU/emulator combination, and stale lazy FPU state. Test signals are fork/clone with FPU state, task exit cleanup, software-FPU builds, and stackprotector boot.
