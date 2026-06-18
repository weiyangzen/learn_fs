# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uprobes.h

Purpose: SPARC architecture header `uprobes.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `arch_uprobe`, `arch_uprobe_task`, `task_struct`, `notifier_block`; functions/helpers `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`; macros/constants `_ASM_UPROBES_H`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN_SIZE`, `UPROBE_SWBP_INSN`, `UPROBE_STP_INSN`, `ANNUL_BIT`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UPROBES_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
