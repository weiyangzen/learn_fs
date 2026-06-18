# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/livepatch.h

Purpose: initializes PowerPC livepatch per-thread stack metadata.

Important APIs/types/functions: `klp_init_thread_info(struct task_struct *p)` sets `task_thread_info(p)->livepatch_sp` to `end_of_stack(p) + 1` for `CONFIG_LIVEPATCH_64`; otherwise it is an empty inline.

Control flow: task initialization calls the helper so livepatch stack scanning starts with a sentinel-adjusted stack pointer.

State and persistence: writes `thread_info.livepatch_sp` for each task on 64-bit livepatch builds.

Dependencies and integration points: depends on scheduler task stack helpers and integrates with kernel livepatch consistency checking.

Risks: off-by-one stack initialization can make livepatch stack scanning miss or overrun the valid stack region. Disabled builds intentionally carry no metadata.

Test signals: build with `CONFIG_LIVEPATCH_64`, run livepatch transition tests, validate stack scanning across newly forked tasks, and build non-livepatch configs.
