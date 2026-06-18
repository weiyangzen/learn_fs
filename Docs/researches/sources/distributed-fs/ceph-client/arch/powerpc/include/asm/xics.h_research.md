<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h

Purpose: Declares common XICS interrupt-controller constants, ICP/ICS backend hooks, CPPR stack helpers, and public XICS lifecycle APIs.

Important APIs/types/functions: `XICS_IPI`, priority constants, backend init stubs, `struct icp_ops`, `struct ics`, global server/domain variables, `struct xics_cppr`, `xics_push_cppr()`, `xics_pop_cppr()`, `xics_set_base_cppr()`, `xics_cppr_top()`, per-CPU `xics_ipi_message`, and XICS setup/migration/IRQ APIs.

Control flow: Initialization selects native, hypervisor, OPAL, RTAS, or other backends; interrupt handling uses `icp_ops`, pushes CPPR priority around nested interrupts/IPIs, dispatches via an irq domain, and migrates or tears down interrupts during CPU hotplug/kexec.

State and persistence: State includes global default interrupt servers, `xics_host`, registered ICS instances, per-CPU CPPR stacks, and per-CPU IPI messages.

Dependencies and integration points: Depends on Linux interrupt/irq-domain APIs, OF nodes, SMP cpumasks, and platform-specific ICP/ICS implementations. Used by pSeries and PowerNV interrupt setup and KVM-adjacent code.

Risks: CPPR stack overflow/underflow changes interrupt priority masking. Wrong server selection can strand interrupts during hotplug or migration.

Test signals: XICS boot on pSeries/PowerNV, IPI stress, CPU hotplug, kexec teardown, IRQ affinity changes, and backend init fallback coverage.

Source read size: 177 lines, 4446 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/xics.h -->
