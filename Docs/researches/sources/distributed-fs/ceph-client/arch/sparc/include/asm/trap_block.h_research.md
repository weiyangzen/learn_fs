# sources/distributed-fs/ceph-client/arch/sparc/include/asm/trap_block.h

Purpose: sparc64 trap-block layout and assembly offsets for per-CPU trap-time data: current thread, PGD physical address, mondo queues, fault info, TSB huge-page data, IRQ worklist, and per-CPU base.

Important APIs/types/functions: types `thread_info`, `trap_per_cpu`, `cpuid_patch_entry`, `sun4v_1insn_patch_entry`, `sun4v_2insn_patch_entry`; functions/helpers `init_cur_cpu_trap`, `setup_tba`, `real_hard_smp_processor_id`; macros/constants `_SPARC_TRAP_BLOCK_H`, `TRAP_PER_CPU_THREAD`, `TRAP_PER_CPU_PGD_PADDR`, `TRAP_PER_CPU_CPU_MONDO_PA`, `TRAP_PER_CPU_DEV_MONDO_PA`, `TRAP_PER_CPU_RESUM_MONDO_PA`, `TRAP_PER_CPU_RESUM_KBUF_PA`, `TRAP_PER_CPU_NONRESUM_MONDO_PA`, `TRAP_PER_CPU_NONRESUM_KBUF_PA`, `TRAP_PER_CPU_FAULT_INFO`, `TRAP_PER_CPU_CPU_MONDO_BLOCK_PA`, `TRAP_PER_CPU_CPU_LIST_PA`, `TRAP_PER_CPU_TSB_HUGE`, `TRAP_PER_CPU_TSB_HUGE_TEMP`, `TRAP_PER_CPU_IRQ_WORKLIST_PA`, `TRAP_PER_CPU_CPU_MONDO_QMASK`, `TRAP_PER_CPU_DEV_MONDO_QMASK`, `TRAP_PER_CPU_RESUM_QMASK`, plus 9 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_TRAP_BLOCK_H`, `__ASSEMBLER__`, `CONFIG_SMP`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into TLB/MMU, SMP, scheduler/task paths rather than through standalone functions.

State and persistence behavior: Persistent per-CPU state lives in `trap_block[NR_CPUS]`; assembly macros load CPU id, trap block base, PGD physical address, and IRQ work addresses directly.

Dependencies and integration points: Includes/dependencies: `linux/threads.h`, `asm/hypervisor.h`, `asm/asi.h`, `asm/scratchpad.h`. Integration points include TLB/MMU, SMP, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: CPU bring-up, hypervisor mondo queues, TLB miss handlers, per-CPU variable access, and offset stability tests are critical.
