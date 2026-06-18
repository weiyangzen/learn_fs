## sources/distributed-fs/ceph-client/arch/loongarch/kernel/traps.c

### Purpose
`traps.c` is the central LoongArch exception and interrupt handling implementation. It maps exception codes to low-level handlers, prints register/stack diagnostics, handles breakpoints, FPU/SIMD/LBT lazy enable traps, alignment/bounds/address errors, reserved instructions, hardware watchpoints, vector table setup, IRQ stack switching, die/oops behavior, and trap initialization.

### Important APIs, Types, And Functions
Global exports include `exception_table`, `show_stack`, `show_regs`, `show_registers`, `die`, `do_fpe`, `do_ade`, `do_ale`, `do_bce`, `do_bp`, `do_watch`, `do_ri`, `do_fpu`, `do_lsx`, `do_lasx`, `do_lbt`, `do_reserved`, `cache_parity_error`, `handle_loongarch_irq`, `do_vint`, `per_cpu_trap_init`, `set_handler`, `set_merr_handler`, and `trap_init`. It uses `exception_handlers`, `eentry`, `tlbrentry`, and CSR printers for CRMD/PRMD/EUEN/ECFG/ESTAT.

### Control Flow
Boot-time trap init configures vector size and exception vector base, initializes default reserved handlers, installs TLB/cache handlers and per-exception handlers, and flushes I-cache. At runtime low-level assembly dispatches to handlers by exception code. Breakpoint handling decodes the break code and delegates to kgdb, kprobes, uprobes, BUG, divzero/overflow, or SIGTRAP paths. Lazy FPU/LSX/LASX/LBT handlers enable and restore context under preemption disable. `do_vint` switches to a per-CPU IRQ stack when necessary, calls the generic arch IRQ handler, and restores the original stack.

### State, Persistence, And Dependencies
Persistent state includes installed exception handler code, vector base CSRs, per-CPU ASID cache initialization, active_mm setup for early CPUs, unaligned access sysctls, and die counter. Dependencies include low-level handler symbols from assembly, TLB/cache init, kprobes/uprobes/kgdb/perf/hw-breakpoint hooks, FPU/SIMD/LBT helpers, unwinder, signal delivery, exception tables, kexec crash handling, and generic IRQ entry code.

### Integration Points
Entry assembly, MMU/TLB code, debug subsystems, perf, signal handling, kexec crash dump, SMP IRQ stacks, and CPU initialization all depend on this file. `kprobes.c`, `ptrace.c`, `stacktrace.c`, and `process.c` consume or feed trap state.

### Risks
Exception handlers are `noinstr` paths where tracing, lock ordering, and IRQ state must be controlled carefully. Breakpoint dispatch ordering matters because kgdb/kprobes/uprobes/BUG all share break instructions. Lazy FPU/SIMD/LBT paths can corrupt task state if ownership flags and hardware enables diverge. Vector installation copies code into executable memory and requires I-cache flushing. `do_watch` single-step skip logic around LL/SC and self-loops is subtle.

### Test Signals
Run exception selftests for SIGSEGV/SIGBUS/SIGILL/SIGTRAP/SIGFPE, kprobes/uprobes/kgdb breakpoints, BUG/WARN, unaligned access emulation, bounds-check faults, FP/LSX/LASX/LBT first-use traps, hardware watchpoints and ptrace single-step, IRQ stack unwinding, crash_kexec-on-oops, and CPU bring-up trap initialization.
