<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h

Purpose: central physical and virtual address map constants for PXA chip selects and internal peripheral regions.

Important definitions: chip selects `PXA_CS0_PHYS` through `PXA_CS5_PHYS`, PXA300/PXA3xx CS variants, `PERIPH_PHYS/VIRT/SIZE`, static memory controller mapping `SMEMC_VIRT`, dynamic memory controller `DMEMC_VIRT`, NAND DFI bus `NAND_VIRT`, and internal memory controller `IMEMC_VIRT`.

Control flow: no runtime code; included by mapping and SoC headers to feed `iotable_init()` descriptors and direct IO macros.

State and persistence: none, but these constants define the persistent virtual layout expected by low-level PXA code.

Dependencies and integration: consumed by `generic.c`, `pxa25x.c`, `pxa27x.c`, `pxa3xx.c`, and SoC headers. It assumes `IOMEM()` is available through ARM headers.

Risks and test signals: incorrect ranges break early MMIO mapping, reset, timers, NAND, and memory-controller access. Test by booting each SoC family and validating early console, timer, IRQ, and NAND/SMEMC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h -->
