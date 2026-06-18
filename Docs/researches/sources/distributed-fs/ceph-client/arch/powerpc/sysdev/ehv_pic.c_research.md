<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c

Purpose: IRQ controller driver for the ePAPR Embedded Hypervisor PIC, including support for direct MPIC EOI mode.

Important APIs/types/functions: `ehv_pic_init()`, `ehv_pic_get_irq()`, IRQ chip callbacks for mask/unmask/EOI/affinity/type, domain ops `ehv_pic_host_match()`, `ehv_pic_host_map()`, `ehv_pic_host_xlate()`, global `global_ehv_pic`, `hwirq_intspec`, and optional `mpic_percpu_base_vaddr`.

Control flow: init locates `epapr,hv-pic`, allocates an `ehv_pic`, creates a linear domain, optionally maps `fsl,hv-mpic-per-cpu`, sets affinity support, records core-interrupt mode from `has-external-proxy`, and installs the domain as default. IRQ dispatch reads EPR in coreint mode or uses `ev_int_iack()`, maps 0xffff to no IRQ, otherwise finds the Linux IRQ. Mapping selects normal hypervisor EOI or direct MPIC EOI based on interrupt spec flags, installs `handle_fasteoi_irq`, and applies default type.

State and persistence: persistent global state includes the IRQ domain, copied irq_chip, direct EOI MMIO mapping, per-hwirq intspec flags, and default-domain registration.

Dependencies and integration points: depends on ePAPR/FSL hypervisor interrupt calls, OF interrupt specs, Linux irqdomain/chip APIs, SMP affinity selection, and optional MPIC per-CPU EOI registers.

Risks: `hwirq_intspec` is indexed by firmware-provided hwirq and assumes it is within `NR_EHV_PIC_INTS`. Direct EOI requires a valid MPIC mapping. Type conversion uses a compact firmware encoding and must preserve polarity/sense bits.

Test signals: interrupt delivery in legacy and coreint modes, affinity changes, OF trigger-type mapping, direct MPIC EOI interrupts, and no default-domain conflicts validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ehv_pic.c -->
