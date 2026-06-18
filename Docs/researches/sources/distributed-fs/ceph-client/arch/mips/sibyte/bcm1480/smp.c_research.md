# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/smp.c

Purpose: BCM1480 SMP support. It uses IMR mailboxes for IPIs and CFE calls to enumerate, stop, and start secondary CPUs.

Important APIs and control flow: mailbox register arrays address each CPU's mailbox set/clear/status registers. `bcm1480_smp_init()` sets CP0 interrupt mask bits. IPI helpers write the action in the high mailbox bits. `bcm1480_boot_secondary()` calls `cfe_cpu_start()` with `smp_bootstrap`, stack, and thread-info. `bcm1480_smp_setup()` initializes CPU maps and probes secondaries by calling `cfe_cpu_stop()`. `bcm1480_mailbox_interrupt()` reads/clears the mailbox, increments IRQ stats, and dispatches scheduler or call-function IPIs.

State, persistence, and integration: state includes CPU maps, mailbox registers, CFE CPU state, and `bcm1480_smp_ops`. Dependencies include CFE firmware, physical/logical CPU maps, clockevent init, and IRQ mapping of mailbox IP3. Risks include firmware start/stop failure, action bit packing limits, mailbox clearing correctness, and probing by stopping CPUs. Test signals are detected secondary count, successful CPU online, mailbox interrupt counts, scheduler IPIs, and call-function IPIs.
