# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c

### Purpose
85xx/QorIQ SMP, CPU hotplug, timebase synchronization, and kexec support. It starts secondary CPUs through ePAPR spin tables or hardware threads, selects MPIC or doorbell IPIs, and binds PM callbacks into SMP operations.

### Important APIs, Types, And Functions
Key types/functions include `struct epapr_spin_table`, `mpc85xx_give_timebase()`, `mpc85xx_take_timebase()`, `smp_85xx_start_cpu()`, `smp_85xx_kick_cpu()`, `smp_85xx_ops`, hotplug `smp_85xx_cpu_offline_self()` and `qoriq_cpu_kill()`, kexec `mpc85xx_smp_kexec_cpu_down()` and `mpc85xx_smp_machine_kexec()`, and public `mpc85xx_smp_init()`.

### Control Flow
Initialization chooses MPIC IPI operations if an `open-pic` node exists, or doorbell IPIs when `CPU_FTR_DBELL` is present. It initializes RCPM or PMC PM ops, then installs timebase/hotplug/kexec callbacks. CPU bring-up maps the firmware spin table, optionally resets the core, writes PIR and entry address, flushes caches, and marks CPU state. PPC64 SMT paths may wake a sibling hardware thread from an online sibling.

### State, Persistence, And Dependencies
State includes static timebase handshake fields, global `smp_85xx_ops`, `smp_ops`, `booting_thread_hwid`, PACA CPU start flags, `kexec_down_cpus`, and PM ops. No durable persistence. Dependencies include OF CPU nodes, MPIC, doorbells, text entry addresses, cache flushes, QorIQ PM/RCPM, kexec, and CPU hotplug APIs.

### Integration Points
Used by nearly every 85xx board setup. It coordinates with firmware spin tables, power-management registers, interrupt controllers, and PowerPC core SMP/kexec code.

### Risks
High concurrency and boot-critical risk: barriers, cache flushes, spin-table endianness, timebase freeze, SMT sibling handling, and kexec CPU teardown must be exact. Failures hang secondary CPUs or corrupt timekeeping.

### Test Signals
Boot SMP 32-bit and 64-bit systems, online/offline CPUs, test kexec/crash paths, verify IPIs via MPIC and doorbell systems, and check synchronized timebase across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/smp.c -->
