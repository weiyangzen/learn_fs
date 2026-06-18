# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/smp.c

Purpose: implements Octeon SMP startup, IPI delivery, CPU hotplug, and platform SMP operation registration. It supports legacy CIU mailbox IPIs and CIU3 mailbox IPIs used by CN78xx-class systems.

Important APIs and functions: `octeon_setup_smp()` registers either `octeon_smp_ops` or `octeon_78xx_smp_ops`. `octeon_send_ipi_single()` and `octeon_send_ipi_mask()` write CIU mailbox registers; `octeon_78xx_send_ipi_single()` uses `octeon_ciu3_mbox_send()`. Secondary startup uses globals `octeon_processor_boot`, `octeon_processor_sp`, `octeon_processor_gp`, and optional relocated entry. Hotplug uses `octeon_cpu_disable()`, `octeon_cpu_die()`, `play_dead()`, and `octeon_update_boot_vector()`.

Control flow: `octeon_smp_setup()` builds logical CPU maps from the CVMX core mask and optional bootloader hotplug data. `octeon_boot_secondary()` publishes stack and thread-info pointers then waits for the secondary to consume them. `octeon_init_secondary()` installs exception base, checks BIST, initializes count/timer state, and invokes the interrupt setup hook selected by `octeon-irq.c`. `octeon_prepare_cpus()` requests mailbox IRQs; the mailbox handler decodes action bits into reschedule, call-function, and I-cache flush handlers. CIU3 systems request separate per-mailbox IRQs.

State and persistence: shared boot globals form a one-at-a-time secondary CPU rendezvous. CPU hotplug state is tracked per CPU and also reflected into bootloader-resident availability masks and boot vectors. IPI delivery is transient hardware mailbox state.

Dependencies and integration points: depends on Linux `plat_smp_ops`, scheduler and generic SMP IPI handlers, Octeon interrupt setup callbacks, CVMX core numbering, bootloader data from `octeon_boot.h`, kexec support, and CPU hotplug state machine registration.

Risks: CPU numbering assumes bootloader and CVMX core masks are consistent. Boot-secondary timeout can leave partial shared state. Hotplug writes hardcoded bootloader structures and resets cores, so stale bootloader metadata is high risk. CIU3 and non-CIU3 mailbox numbering differ, requiring matching interrupt-controller setup.

Test signals: SMP boot should enumerate expected logical CPU mapping; IPIs should drive scheduler and call-function interrupts; `echo 0/1 > /sys/devices/system/cpu/cpuX/online` should offline/online cores where supported; CIU3 systems should show separate Scheduler/SMP-Call/ICache-Flush mailbox IRQs.
