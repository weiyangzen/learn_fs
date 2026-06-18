<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c

Purpose: Implements Loongson-3 SMP bring-up, IPI delivery, secondary CPU initialization, CPU hotplug play-dead loops, and kexec handoff integration.

Important APIs/types/functions: `loongson3_smp_ops`, CSR and legacy IPI helpers, `loongson3_send_ipi_single/mask()`, `loongson3_ipi_interrupt()`, `loongson3_smp_setup()`, `loongson3_prepare_cpus()`, `loongson3_boot_secondary()`, and hotplug hooks `loongson3_cpu_disable/die()` plus `play_dead()`.

Control flow: Setup maps physical CPUs to logical CPUs while skipping reserved cores, probes CSR IPI support, initializes legacy mailbox register arrays from `smp_group[]`, enables CPU0 IPI, and records core/package IDs. Secondary boot writes start PC/SP/thread-info into CSR mailboxes or MMIO buffers. IPI interrupt clears action bits and runs scheduler or call-function handlers. Hotplug disables interrupts/TLB, waits for CPU_DEAD, and uses revision-specific CKSEG1 assembly loops to flush caches and wait for mailbox restart.

State and persistence: Uses per-CPU `cpu_state`, logical/physical CPU maps, IPI register pointer arrays, mailbox buffers, chip clock-control registers, and CPU hotplug state registration.

Dependencies and integration: Consumes `smp_group`, `loongson_sysconf`, chipcfg/freqctrl arrays from `env.c`, and MIPS SMP/core hotplug APIs.

Risks: CPU numbering, mailbox addresses, and node/package math must match firmware. Inline assembly is revision-specific and can hang a CPU if cache/mailbox assumptions are wrong. Workaround flags gate clock disable.

Test signals: Secondary CPUs should come online, reschedule/call-function IPIs should be delivered, CPU offline/online cycles should not hang, and kexec should park nonboot CPUs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c -->
