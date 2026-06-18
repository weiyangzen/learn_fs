# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ttable.h

Purpose: sparc64 trap-table macro library for boot vector, trap entry/return wrappers, syscall traps, IRQ/NMI traps, TSB miss vectors, spill/fill handlers, and kprobe/uprobe/kgdb trap selection.

Important APIs/types/functions: macros/constants `_SPARC64_TTABLE_H`, `BOOT_KERNEL`, `CLEAN_WINDOW`, `TRAP`, `TRAP_7INSNS`, `TRAP_SAVEFPU`, `TRAP_NOSAVE`, `TRAP_NOSAVE_7INSNS`, `TRAPTL1`, `TRAP_ARG`, `TRAPTL1_ARG`, `SYSCALL_TRAP`, `TRAP_UTRAP`, `LINUX_32BIT_SYSCALL_TRAP`, `LINUX_64BIT_SYSCALL_TRAP`, `GETCC_TRAP`, `SETCC_TRAP`, `BREAKPOINT_TRAP`, plus 56 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TTABLE_H`, `__ASSEMBLER__`, `CONFIG_COMPAT`, `CONFIG_TRACE_IRQFLAGS`, `CONFIG_KPROBES`, `CONFIG_UPROBES`, `CONFIG_KGDB`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is architectural trap level/register-window state plus `thread_info` saved-window buffers; macros branch through `etrap`, `rtrap`, fixup labels, and optional tracing subsections.

Dependencies and integration points: Includes/dependencies: `asm/utrap.h`, `asm/pil.h`, `asm/thread_info.h`. Integration points include memory-management, syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Trap-table assembly build, syscall entry, IRQ/NMI levels, window spill/fill faults, compat 32-bit stack handling, and kprobe/uprobe/kgdb traps are required tests.
