## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-common.c` is the C half of ARM64
exception entry. It receives saved `pt_regs` from `entry.S`, transitions RCU/lockdep/irq/context
tracking state, classifies ESR exception classes, invokes the appropriate subsystem handler, and
returns through user or kernel exit preparation.

### Important APIs, Types, And Functions
Entry/exit helpers include `arm64_enter_from_kernel_mode()`, `arm64_exit_to_kernel_mode()`,
`arm64_enter_from_user_mode()`, `arm64_exit_to_user_mode()`, syscall-specific entry/exit helpers,
`asm_exit_to_user_mode()`, `arm64_enter_el1_dbg()`, and `arm64_exit_el1_dbg()`. Interrupt helpers are
`do_interrupt_handler()`, `el1_interrupt()`, `el0_interrupt()`, and wrappers around `handle_arch_irq`
and `handle_arch_fiq`. Main handlers include `el1h_64_sync_handler()`, EL1 IRQ/FIQ/error handlers,
`el0t_64_sync_handler()`, EL0 IRQ/FIQ/error handlers, compat 32-bit handlers, `handle_bad_stack()`,
and `__sdei_handler()`.

### Control Flow
For EL1 synchronous exceptions, the handler reads `ESR_EL1`, switches on ESR class, and dispatches
aborts, PC alignment, undefined/sysreg traps, BTI, GCS, MOPS, breakpoints, single-step, watchpoints,
BRK64, FPAC, or panic for unhandled classes. EL1 interrupts are treated as normal IRQ/FIQ or
pseudo-NMI depending on PSTATE/PMR state. EL1 SError enters NMI-style accounting and calls
`do_serror()`.

For EL0, every handler first enters from user mode, applies branch-prediction hardening for
potential kernel addresses, restores DAIF to process context where appropriate, calls the specific
fault/syscall/debug/FPSIMD/SVE/SME/GCS/MOPS handler, and exits to user mode. Syscall entry also
handles the Cortex-A76 single-step erratum workaround and FPSIMD/SVE syscall ABI cleanup. Compat
32-bit handling adds CP15 and BKPT dispatch. SDEI handling is NMI-like and fixes PAN state before
calling the generic SDEI layer.

### State, Persistence, And Dependencies
State is mostly transient exception context: `pt_regs`, ESR/FAR values, DAIF state, irqentry state,
RCU/context tracking, current task flags, FPSIMD last-state markers, and optional per-CPU erratum
state. Dependencies include generic irq-entry code, context tracking, lockdep, RCU, MTE, SME/SVE,
FPSIMD, debug monitors, traps, memory abort code, system call handlers, branch predictor hardening,
SDEI, and stack overflow handling.

### Integration Points
`entry.S` branches to these C handlers. Subsystems reached from here include MM fault handling,
signals, ptrace/debug, kprobes/uprobe, syscalls, IRQ chips, SError/RAS, FPSIMD/SVE/SME lazy state,
MTE tag-fault checks, livepatch/resume-user-mode logic through generic exit code, and SDEI firmware
events.

### Risks
Ordering is critical: many functions are `noinstr` because tracing, KASAN, lockdep, or faults are
unsafe until entry state is established. Enabling interrupts too early or leaving DAIF in the wrong
state can recurse or lose accounting. Missing MTE/SME/FPSIMD entry/exit hooks breaks user ABI.
Incorrect ESR classification can turn recoverable faults into panics or vice versa. Debug exception
paths must avoid scheduling and instrumentation recursion.

### Test Signals
Exception selftests, syscall ABI tests, user and kernel fault injection, ptrace/kprobes/uprobes,
MTE async fault tests, SVE/SME syscall tests, pseudo-NMI IRQ tests, SError/RAS injection, stack
overflow tests, compat 32-bit syscall/fault tests, and objtool/noinstr validation are relevant.
