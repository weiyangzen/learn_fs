# sources/distributed-fs/ceph-client/arch/sparc/include/asm/smp_32.h

Purpose: SPARC32 SMP header for sun4m/sun4d CPU startup, cross-call/IPI message IDs, logical/physical CPU mapping, interrupt handlers, and `sparc32_ipi_ops`.

Important APIs/types/functions: types `seq_file`, `sparc32_ipi_ops`; functions/helpers `cpu_panic`, `sun4m_init_smp`, `sun4d_init_smp`, `smp_callin`, `smp_store_cpu_info`, `smp_resched_interrupt`, `smp_call_function_single_interrupt`, `smp_call_function_interrupt`, `smp_bogo`, `smp_info`, `xc0`, `xc1`, `xc2`, `xc3`, `xc4`, `arch_send_call_function_single_ipi`, plus 4 more; macros/constants `_SPARC_SMP_H`, `raw_smp_processor_id`, `MSG_CROSS_CALL`, `MBOX_STOPCPU`, `MBOX_IDLECPU`, `MBOX_IDLECPU2`, `MBOX_STOPCPU2`, `hard_smp_processor_id`, `smp_setup_cpu_possible_map`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SMP_H`, `__ASSEMBLER__`, `CONFIG_SMP`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State persists in CPU maps, boot-time SMP ops, mailbox message bits, atomic CPU state, and per-CPU call-function state.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/head.h`, `linux/cpumask.h`, `asm/ptrace.h`, `asm/asi.h`, `linux/atomic.h`. Integration points include memory-management, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps. Test signals: Secondary CPU bring-up, IPI broadcast/single delivery, CPU panic/stop, `/proc/cpuinfo`, and hard CPU id mapping are tests.
