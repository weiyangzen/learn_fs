# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-smp.c

Purpose: IP27 SMP CPU discovery, IPI delivery, secondary launch, and SMP lifecycle hooks.

Important APIs and control flow: `cpu_node_probe()` clears node maps, walks GDA NASID table, marks nodes online/possible, and calls `node_scan_cpus()` to map enabled KL CPUs to logical CPUs, NASIDs, slices, and speeds. `intr_clear_all()` clears HUB masks and pending bits on secondary nodes. IPI functions send reschedule/call interrupts by writing HUB interrupt bits. `ip27_boot_secondary()` launches a CPU through PROM `LAUNCH_SLAVE()` with stack and thread-info pointers. `ip27_smp_setup()` clears interrupts on nonboot nodes, replicates kernel text, and maps boot CPU. The `ip27_smp_ops` structure plugs these into generic MIPS SMP.

State, persistence, and integration: state includes CPU possible maps, logical/physical mappings, `sn_cpu_info`, HUB pending registers, and replicated text. Dependencies include firmware KL CPU structures, GDA, HUB IPIs, timer init, and `per_cpu_init()`. Risks include `cpus_found` static mapping assumptions, NR_CPUS truncation, and firmware launch dependency. Test signals are discovered CPU count, secondary boot, scheduler and call-function IPIs, and per-CPU timer initialization.
