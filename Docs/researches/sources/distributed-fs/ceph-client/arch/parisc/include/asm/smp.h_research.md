# sources/distributed-fs/ceph-client/arch/parisc/include/asm/smp.h

Purpose: declares PA-RISC SMP CPU mapping, boot rendezvous, IPI, and CPU hotplug hooks.

Important APIs/types/functions: exports `init_per_cpu`, PDC rendezvous constants, `cpu_number_map`, `cpu_logical_map`, `raw_smp_processor_id`, IPI send functions, `NO_PROC_ID`, `ANY_PROC_ID`, `__cpu_disable`, and `__cpu_die`.

Control flow: boot code initializes per-CPU state, firmware rendezvous starts secondary CPUs, IPIs deliver function calls/NOPs, and hotplug paths disable or wait for CPUs.

State and persistence: CPU maps, per-CPU thread info, pending IPI state, and CPU lifecycle state persist in scheduler/platform data. Dependencies and integration: firmware PDC, scheduler, interrupt/IPI code, and CPU hotplug core.

Risks and test signals: bad CPU numbering or rendezvous handling breaks SMP boot. Test SMP boot, IPI selftests, CPU hotplug, and `raw_smp_processor_id` debug checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
