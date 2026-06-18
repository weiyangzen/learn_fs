## sources/distributed-fs/ceph-client/arch/s390/kernel/wti.c

Purpose: Supports s390 warning-track interruption, where a real-time per-CPU thread acknowledges hypervisor warning-track events and temporarily suppresses I/O interrupts during the grace period.

Important APIs and functions: Init `wti_init()`, external IRQ handler `wti_interrupt()`, per-CPU thread callback `wti_thread_fn()`, debugfs show `wti_show()`, and helpers `wti_irq_disable()`, `wti_irq_enable()`, `store_debug_data()`, and `wti_dbf_grace_period()`.

Control flow: Late init checks SCLP WTI support, registers per-CPU smpboot threads, raises their scheduler policy to near-max `SCHED_FIFO`, registers the warning-track external interrupt and IRQ subclass, registers with DIAG 49C, and creates debugfs/s390dbf reporting. On interrupt, it increments IRQ stats, disables I/O interrupts in CR6, records current PID/kernel PSW address, marks per-CPU pending, and wakes the CPU thread. The thread clears pending, acknowledges with DIAG 49C, records missed grace periods if needed, and re-enables I/O interrupts.

State and persistence: Per-CPU `wti_state` stores debug data, thread pointer, and pending flag. Global `wti_dbg` stores s390dbf state. Debugfs `wti/stat` exposes missed counts.

Dependencies and integration: Depends on SCLP feature discovery, DIAG 49C, external IRQ registration, irq subclassing, smpboot per-CPU threads, scheduler RT policy, debugfs, kallsyms `%pS`, and s390 debug feature.

Risks and test signals: Risks include leaving I/O interrupts disabled after error paths, thread scheduling delays, init cleanup leaks, and debug data from user-mode regs. Test signals include WTI interrupt counts, per-CPU `cpuwti/%u` thread wakeups, debugfs missed counters, s390dbf records, DIAG 49C registration/ack failures, and CPU hotplug behavior of smpboot threads.
