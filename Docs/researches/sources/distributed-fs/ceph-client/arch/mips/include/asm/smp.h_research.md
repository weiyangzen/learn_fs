<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h

Purpose: Provides MIPS architecture SMP declarations, CPU mapping helpers, IPI action bits, hotplug hooks, and arch-level IPI wrappers.

Important APIs/types/functions: `raw_smp_processor_id`, logical/physical CPU maps, sibling/core/foreign masks, `NO_PROC_ID`, IPI action flags `SMP_RESCHEDULE_YOURSELF`, `SMP_CALL_FUNCTION`, `SMP_ICACHE_FLUSH`, `smp_bootstrap`, `start_secondary`, `calculate_cpu_foreign_map`, hotplug hooks `__cpu_disable`, `__cpu_die`, `play_dead`, kexec helpers, and `mips_smp_ipi_allocate/free`.

Control flow: Boot code maps physical CPU IDs to logical IDs, starts secondaries through platform ops, then uses `arch_smp_send_reschedule` and call-function wrappers to deliver IPIs. Hotplug and kexec paths either call arch hooks or become no-ops depending on configuration.

State and persistence: Global CPU masks and mapping arrays describe topology and active CPUs. IPI allocation state is managed by implementation code. The current CPU ID is read from `current_thread_info()->cpu`.

Dependencies and integration points: Depends on Linux cpumask/thread headers, `asm/smp-ops.h`, and MIPS topology/hotplug implementation files.

Risks: CPU map array bounds depend on `CONFIG_MIPS_NR_CPU_NR_MAP` and `NR_CPUS`. IPI action bit semantics must stay in sync with interrupt handlers. Hotplug stubs can hide unsupported operations.

Test signals: SMP boot, topology reporting, IPI/call-function stress, CPU hotplug, kexec on nonboot CPUs, and UP build coverage are relevant.

Source read size: 139 lines, 3730 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h -->
