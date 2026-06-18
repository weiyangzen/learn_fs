## sources/distributed-fs/ceph-client/arch/s390/kernel/traps.c

Purpose: Handles s390 program-check exceptions, maps them to signals or kernel fixups/panics, integrates kprobes/uprobes/PER events, validates monitor-call BUG support, and initializes trap lowcore state.

Important APIs and functions: `trap_init()`, `__do_pgm_check()`, `do_report_trap()`, `do_per_trap()`, `kernel_stack_invalid()`, `is_valid_bugaddr()`, `__warn_args()`, and the `pgm_check_table[128]`. Trap handlers cover illegal, privileged, execute, protection/DAT, addressing, specification, data, floating-point/vector, transaction, monitor event, secure-storage, and default exceptions.

Control flow: Program-check entry copies lowcore interruption fields into `pt_regs`, short-circuits guest faults for KVM by storing `gmap_teid`/`gmap_int_code`, enters irqentry state, updates timers and last-break for user mode, captures transaction diagnostic block, records user PER events or dispatches kernel PER to kprobes, restores interrupt state according to interrupted PSW, indexes `pgm_check_table`, then disables IRQs and exits irqentry. Individual handlers notify die chains, signal users, run exception-table fixups, or die/panic in kernel mode.

State and persistence: Updates current thread trap/PER fields, `pt_regs`, lowcore program-check data, BUG report state, and control-register/PSW machine-check enablement during `trap_init()`.

Dependencies and integration: Integrates with fault handlers, kprobes, uprobes, generic BUG, ptrace/PER, entry-common IRQ accounting, KMSAN entry-register handling, exception tables, FPU state saving, and KVM guest-fault handling.

Risks and test signals: Risks are wrong signal codes, lost PER events, incorrect guest fault bypass, re-enabling wrong PSW bits, and BUG/monitor-call decoding. Test signals include user SIGILL/SIGFPE/SIGSEGV cases, kprobe/uprobe breakpoints, hardware single-step/PER, kernel exception-table fixups, KVM SIE guest faults, and boot-time monitor-call self-test.
