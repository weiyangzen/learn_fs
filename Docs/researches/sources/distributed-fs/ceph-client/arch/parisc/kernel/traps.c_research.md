<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c

### Purpose
`traps.c` handles PA-RISC hardware interruptions after low-level save code, producing signals, page faults, oops/panic diagnostics, breakpoints, FP emulation, and IVT initialization.

### Important APIs, Types, And Functions
Major routines include `show_regs()`, `show_stack()`, `die_if_kernel()`, `handle_break()`, `parisc_terminate()`, `handle_interruption()`, `initialize_ivt()`, and `early_trap_init()`.

### Control Flow
Register dump helpers print PSW/GPR/SR/IAOQ/IIR/ISR/IOR and unwind kernel stacks. `handle_interruption()` re-enables interrupts when appropriate, handles user-space space-ID abuse, dispatches machine checks, breakpoints, recovery/taken-branch traps, illegal/privileged instructions, FP assist, TLB/page faults, unaligned references, protection faults, and default SIGBUS/panic cases. It calls `do_page_fault()` for valid memory faults, `handle_unaligned()` for unaligned traps, `handle_fpe()` for assist exceptions, and exception fixups for kernel faults when allowed. Early trap init validates fault vectors and writes HPMC checksum fields.

### State, Persistence, And Dependencies
State includes ratelimiters, per-thread death flags, chassis status, IVT checksum words, and task signal/oops state. Dependencies include PDC/chassis, unwind, unaligned handler, math emulator, kprobes, KGDB, kfence, perf events, and page fault code.

### Integration Points
Central exception path for assembly trap vectors, page fault handling, debugging, oops reporting, and signal delivery.

### Risks
Trap code runs under hostile CPU state. Space/register checks protect gateway-page privilege transitions. Misclassifying kernel faults can panic instead of fix up, or vice versa. Early IVT checksum must satisfy firmware.

### Test Signals
Illegal instruction, breakpoints, kprobes, KGDB breaks, FP assist, page faults, unaligned access, HPMC/LPMC paths, kernel exception-table fixups, and early boot IVT validation are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c -->
