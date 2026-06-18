<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c

Purpose: Implements an OPAL-backed XICS ICP fallback for PowerNV systems.

Important APIs/types/functions: Entry point is `icp_opal_init()`. Backend operations are `icp_opal_get_irq()`, `icp_opal_eoi()`, `icp_opal_set_cpu_priority()`, `icp_opal_teardown_cpu()`, `icp_opal_flush_ipi()`, and SMP `icp_opal_cause_ipi()`/`icp_opal_ipi_action()` plus `icp_opal_flush_interrupt()`.

Control flow: Init checks for `ibm,opal-intc` and installs `icp_opal_ops`. Interrupt retrieval first handles KVM-latched interrupts, then calls `opal_int_get_xirr()`, maps/pushes CPPR or masks/EOIs unknown vectors. EOI calls `opal_int_eoi()` and forces external IRQ replay when OPAL reports more pending work. Priority setting maps requests at or above default priority to lowest priority because OPAL XIVE cannot represent the XICS "IPIs only" priority.

State and persistence: Persistent state is global `icp_ops`, per-CPU CPPR stack, OPAL CPPR/MFRR/XIRR state, and KVM host IPI latches.

Dependencies and integration points: Depends on OPAL interrupt calls, PowerNV firmware feature/nodes, XICS common code, KVM PowerPC hooks, and force-external-replay machinery.

Risks: Priority semantics are approximate on OPAL XIVE, as the source comment warns. OPAL errors during get_xirr return no interrupt without detailed recovery. Replay behavior is required to avoid losing pending interrupts after EOI.

Test signals: PowerNV XICS fallback boot, OPAL interrupt delivery, IPI delivery/clear, offline CPU flush loop, CPPR priority behavior during CPU hotplug, and forced replay on OPAL EOI positive return.

Source read size: 202 lines, 4441 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c -->
