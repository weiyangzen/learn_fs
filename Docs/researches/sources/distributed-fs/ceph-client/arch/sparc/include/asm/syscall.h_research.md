# sources/distributed-fs/ceph-client/arch/sparc/include/asm/syscall.h

Purpose: Architecture syscall helper header implementing syscall number get/set, rollback, error/return handling, argument access, and audit architecture selection for sparc32/sparc64/compat.

Important APIs/types/functions: functions/helpers `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_has_error`, `syscall_set_error`, `syscall_clear_error`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`; macros/constants `__ASM_SPARC_SYSCALL_H`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_SYSCALL_H`, `CONFIG_SPARC32`, `CONFIG_SPARC64`, `defined(CONFIG_SPARC64) && defined(CONFIG_COMPAT)`, `defined(CONFIG_SPARC64)`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State is entirely in `pt_regs` and thread flags such as sparc64 no-error; control flow toggles carry bits and writes `%i0`/syscall number slots.

Dependencies and integration points: Includes/dependencies: `uapi/linux/audit.h`, `linux/kernel.h`, `linux/compat.h`, `linux/sched.h`, `asm/ptrace.h`, `asm/thread_info.h`. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, configuration-specific build gaps, ABI compatibility breaks. Test signals: strace/seccomp/audit, syscall restart/rollback, compat argument layout, error injection, and return value tests are important.
