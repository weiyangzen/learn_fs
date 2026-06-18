<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S

### Purpose
`entry.S` implements MIPS low-level return paths from exceptions, interrupts, syscalls, forks, and kernel threads, plus the instruction hazard barrier helper.

### Important APIs, Types, And Functions
Important exported labels are `ret_from_exception`, `ret_from_irq`, `__ret_from_irq`, `ret_from_kernel_thread`, `ret_from_fork`, `syscall_exit`, `restore_all`, `restore_partial`, `work_pending`, `syscall_exit_partial`, and `mips_ihb`.

### Control Flow
Return paths inspect saved status to determine user versus kernel return. User returns disable interrupts, check thread flags for reschedule, signal, notify, and syscall-trace work, call `schedule`, `do_notify_resume`, or `syscall_trace_leave` as needed, then restore registers. Kernel returns optionally perform preemption scheduling if interrupts were enabled and preempt count permits. Fork paths call `schedule_tail` then either kernel-thread function or syscall exit.

### State, Persistence, And Dependencies
State is the saved `pt_regs` frame on stack, `thread_info` flags/preempt count/current regs, IRQ flags, rseq debug state, and trace IRQ state. Dependencies include generated asm offsets, stackframe macros, irqflags, thread-info layout, and scheduler/tracing C functions.

### Integration Points
All exception/syscall/interrupt entry code returns through these labels. Signal delivery, ptrace/syscall tracing, preemption, rseq, and scheduler integration depend on this file.

### Risks
Ordering around interrupt disable and thread-flag sampling prevents missed reschedules/signals. Offset mismatches or instrumentation in this file would be catastrophic. Partial restore paths must preserve static registers around trace calls.

### Test Signals
Boot, syscall stress, signal delivery during syscalls, ptrace/seccomp tracing, preemption on interrupt return, rseq debug, fork/kernel-thread startup, and IRQ flag tracing validate this code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/entry.S -->
