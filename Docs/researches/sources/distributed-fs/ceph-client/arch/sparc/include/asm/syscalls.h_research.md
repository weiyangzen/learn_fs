# sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscalls.h

Purpose: SPARC architecture header `syscalls.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `pt_regs`; functions/helpers `sparc_fork`, `sparc_vfork`, `sparc_clone`, `sparc_clone3`; macros/constants `_SPARC64_SYSCALLS_H`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SYSCALLS_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
