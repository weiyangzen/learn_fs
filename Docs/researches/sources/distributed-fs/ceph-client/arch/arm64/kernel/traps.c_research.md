## sources/distributed-fs/ceph-client/arch/arm64/kernel/traps.c

### Purpose
`traps.c` handles ARM64 synchronous exception fallout, undefined instruction emulation, user signal injection, kernel oops processing, system-register traps, stack-overflow panic, SError severity handling, BUG/CFI/KASAN/UBSAN breakpoints, and ESR class reporting.

### Important APIs, Types, And Functions
Important APIs include `aarch32_opcode_cond_checks`, `dump_kernel_instr`, `die`, `arm64_force_sig_fault`, `arm64_force_sig_fault_pkey`, `arm64_force_sig_mceerr`, `arm64_force_sig_ptrace_errno_trap`, `arm64_notify_die`, `arm64_skip_faulting_instruction`, `force_signal_inject`, `arm64_notify_segfault`, `do_el0_undef`, `do_el1_undef`, `do_el0_sys`, `do_el0_cp15`, `esr_get_class_string`, `bad_el0_sync`, `panic_bad_stack`, `arm64_serror_panic`, `arm64_is_fatal_ras_serror`, `do_serror`, and debug breakpoint handlers.

### Control Flow
Kernel fatal paths serialize through `die_lock`, enter oops state, notify die chains, print modules/registers/code bytes, optionally kexec crash, taint, and kill or panic. User fault paths record fault code/address and send appropriate SIGILL/SIGSEGV/SIGBUS/SIGTRAP. Undefined EL0 instructions first try AArch32 breakpoints, MRS emulation, and deprecated instruction emulation before SIGILL. System-register traps match ESR masks against hook tables for cache maintenance, CTR, CNTVCT/CNTFRQ, CPUID MRS, and WFI, then advance PC or signal. Compat CP15 traps validate condition codes and emulate timer reads. SError paths panic for non-RAS or fatal RAS errors. BRK handlers classify BUG, CFI, KASAN, and UBSAN traps.

### State, Persistence, And Dependencies
State includes `show_unhandled_signals`, static die and ratelimit counters, current task fault fields, per-CPU overflow stacks, ESR-derived state, signal queues, taint/oops flags, and architecture feature/erratum state. There is no filesystem persistence.

### Integration Points
The file sits behind exception entry assembly, debug monitors, signal delivery, kprobes, kexec crash, EFI fixups, MTE/KASAN/UBSAN/CFI, timer and cache emulation, CPU feature registers, stacktrace dumping, and compat AArch32 support.

### Risks
Signal-vs-oops classification must be exact to avoid killing the kernel for user faults or resuming after fatal kernel faults. Emulation must advance PC and IT/BTYPE state correctly. Cache maintenance and counter emulation interact with errata and userspace ABI. Oops paths are reentrancy-sensitive.

### Test Signals
Run undefined-instruction, trapped MRS, cache maintenance, WFI, CNTVCT/CNTFRQ, compat CP15, BTI/GCS/FPAC/MOPS, BUG/WARN, CFI, KASAN, UBSAN, stack overflow, SError, EFI fixup, and kexec crash tests.
