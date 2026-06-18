<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c

### Purpose
`smp.c` implements PA-RISC SMP startup, IPI delivery, CPU hotplug shutdown, and SMP call-function/reschedule hooks.

### Important APIs, Types, And Functions
Important state includes `smp_init_current_idle_task`, `cpu_now_booting`, per-cpu `ipi_lock`, and `cpu_data.pending_ipi`. Main functions are `ipi_interrupt()`, `ipi_send()`, `smp_cpu_init()`, `smp_callin()`, `smp_boot_one_cpu()`, `smp_prepare_cpus()`, `__cpu_up()`, `__cpu_disable()`, `__cpu_die()`, and `arch_cpuhp_cleanup_dead_cpu()`.

### Control Flow
IPI senders set a pending bit under the target CPU's lock and poke the CPU HPA. The interrupt handler drains bits, dispatching reschedule, call-function, stop, test, and KGDB requests. Booting a secondary records the idle task, sends a rendezvous interrupt through firmware-visible HPA, and waits until the CPU marks itself online. Hotplug disable removes topology, migrates IRQs, flushes caches/TLBs, disables interrupts, and rendezvous-locks with firmware cleanup.

### State, Persistence, And Dependencies
Per-CPU pending IPI bits, locks, topology, `time_keeper_id`, and CPU online/present masks persist. Dependencies include PDC rendezvous, IRQ migration, clockevent init, cache/TLB flushes, KGDB, and scheduler CPU hotplug.

### Integration Points
Provides generic SMP operations for reschedule IPIs, smp-call-function, CPU bringup/offline, and KGDB CPU roundup.

### Risks
IPI state is bitmask-based and must be ordered with barriers. CPU startup relies on firmware rendezvous vectors and busy-wait timeouts. Hotplug must not leave the timekeeping master offline.

### Test Signals
SMP boot, repeated CPU online/offline, reschedule/call-function stress, KGDB roundup, interrupt migration, and timer operation on secondary CPUs are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c -->
