## sources/distributed-fs/ceph-client/arch/arm64/include/asm/exception.h

Purpose: declares arm64 exception vector C handlers and syndrome handling entry points.

Important APIs/types/functions: defines `__exception_irq_entry`, `disr_to_esr`, vector handlers for EL1t/EL1h/EL0 64-bit/EL0 32-bit sync/IRQ/FIQ/error, IRQ stack call helpers, memory abort, undefined, BTI, GCS, breakpoint/watchpoint, single-step, BRK, FP/SVE/SME, sysreg, svc, FPAC, MOPS, SError, and bad-stack panic handlers.

Control flow: assembly vectors enter these C handlers with `pt_regs`; handlers decode ESR and dispatch to subsystem-specific fault handling.

State and persistence: operates on pt_regs, signal state, task state, debug state, and fault accounting maintained elsewhere.

Dependencies and integration: depends on ESR definitions, ptrace regs, interrupt annotations, hardware breakpoints, syscall entry, and signal/fault subsystems.

Risks: prototype mismatch with assembly vectors or wrong handler routing causes crashes or incorrect user signals. Test signals are syscall tests, page-fault tests, debug exception tests, SError injection, compat exception tests, and bad-stack handling.
