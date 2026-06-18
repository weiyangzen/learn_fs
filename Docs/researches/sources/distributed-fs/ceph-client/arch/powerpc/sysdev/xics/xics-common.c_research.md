<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c

Purpose: Provides common XICS interrupt-controller orchestration across ICP presentation backends and ICS source-controller backends.

Important APIs/types/functions: Defines global `icp_ops`, `xics_host`, default server variables, per-CPU `xics_cppr`, and registered `xics_ics`. Public functions include `xics_init()`, `xics_register_ics()`, `xics_setup_cpu()`, `xics_teardown_cpu()`, `xics_kexec_teardown_cpu()`, `xics_update_irq_servers()`, `xics_set_cpu_giq()`, `xics_smp_probe()`, `xics_migrate_irqs_away()`, `xics_get_irq_server()`, `xics_set_irq_type()`, `xics_retrigger()`, and `xics_mask_unknown_vec()`.

Control flow: `xics_init()` selects an ICP backend in hypervisor/native/OPAL order, installs `ppc_md.get_irq`, patches IPI EOI, selects an ICS backend in RTAS/OPAL/native order, reads interrupt-server size, updates default servers, creates the XICS irqdomain, and sets up the boot CPU. Domain mapping installs a percpu IPI chip for `XICS_IPI` and delegates normal source validation/chip data to the registered ICS. SMP setup maps/request IPIs and installs `smp_ops->cause_ipi`. CPU teardown lowers priority, flushes IPIs, and adjusts global interrupt queue membership. CPU hotplug migration masks local external delivery, leaves the GIQ, walks mapped IRQs, and resets single-server interrupts to all CPUs.

State and persistence: Persistent state includes selected backend operation table, source-controller object, irqdomain, default server/distribution server IDs, interrupt-server bit width, per-CPU CPPR stacks, IPI chip patched with backend EOI, and firmware GIQ membership.

Dependencies and integration points: Depends on XICS ICP/ICS backends, OF CPU and interrupt nodes, RTAS indicators, irqdomain hierarchy, SMP IPI framework, generic IRQ descriptors, PowerPC firmware features, and `ppc_md.get_irq`.

Risks: Common code assumes one global ICS. CPPR push/pop pairing is fragile, especially with retrigger and CPU teardown. `xics_get_irq_server()` implements only all-CPU or single-CPU delivery. Hotplug migration iterates all IRQ descriptors with interrupts disabled and relies on backend `get_server()` correctness.

Test signals: pSeries and PowerNV boot across ICP/ICS combinations, IPIs, IRQ type setting and resend, CPU hotplug/offline migration, kexec teardown, unknown-vector masking, hierarchy-domain allocation, and affinity changes with all-cpus versus single-cpu masks.

Source read size: 544 lines, 13374 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c -->
