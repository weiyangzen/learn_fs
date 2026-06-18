# sources/distributed-fs/ceph-client/arch/sparc/include/asm/perf_event.h

Purpose: Perf helper that synthesizes a `pt_regs` snapshot for caller sampling by reading `%pstate`, `%asi`, `%pil`, `%i7`, and `%i6`.

Important APIs/types/functions: macros/constants `__ASM_SPARC_PERF_EVENT_H`, `perf_arch_fetch_caller_regs`.

Control flow: The file is driven by preprocessor gates such as `__ASM_SPARC_PERF_EVENT_H`, `CONFIG_PERF_EVENTS`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: No persistent state is owned; the macro mutates a caller-supplied `pt_regs` and encodes the current control registers into `tstate`.

Dependencies and integration points: Includes/dependencies: `asm/ptrace.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Perf sampling backtraces, interrupt-context samples, and register-window frame-pointer validity are the practical tests.
