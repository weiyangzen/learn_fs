# sources/distributed-fs/ceph-client/arch/csky/kernel/traps.c

Purpose: exception/trap dispatch, breakpoint integration, signal delivery, and oops reporting.

Important APIs/types/functions: functions: `pre_trap_init`, `trap_init`, `die`, `do_trap`, `do_trap_error`, `do_trap_misaligned`, `do_trap_bkpt`, `do_trap_illinsn`, `do_trap_fpe`, `do_trap_priv`, `trap_c`; types: `task_struct`; macros: `DO_ERROR_INFO(name,`

Control flow: Runtime flow is organized around `pre_trap_init`, `trap_init`, `die`, `do_trap`, `do_trap_error`, `do_trap_misaligned`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/cpu.h`, `linux/sched.h`, `linux/signal.h`, `linux/kernel.h`, `linux/mm.h`, `linux/module.h`, `linux/user.h`, `linux/string.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
