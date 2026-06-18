<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c

## Purpose
`omap-iommu.c` provides platform integration for OMAP IOMMU devices and their powerdomain/clockdomain relationships. It links IOMMU runtime state with the emulation clockdomain and relevant powerdomains.

## Important APIs, Types, and Functions
Important internals include `struct pwrdm_link`, `emu_clkdm`, and helper functions such as `_get_pwrdm(struct device *dev)` plus device link/setup callbacks in the file. It uses device tree or platform device data to locate associated powerdomains.

## Control Flow
The code resolves an IOMMU device's powerdomain from OMAP hwmod or device context, then coordinates clockdomain/powerdomain behavior required for IOMMU access. Setup is invoked during platform/IOMMU initialization and prepares runtime PM relationships before the IOMMU driver manages translations.

## State and Persistence Behavior
State is in clockdomain/powerdomain references and runtime PM-managed hardware state. No filesystem persistence exists. IOMMU page tables and mappings are owned by the IOMMU driver, not this integration layer.

## Dependencies and Integration Points
It depends on OMAP powerdomain and clockdomain frameworks, platform devices, OMAP hwmod/device data, and the OMAP IOMMU driver. It integrates with multimedia/DSP/IVA users that require IOMMU translation.

## Risks
Wrong powerdomain lookup or missing EMU clockdomain handling can leave the IOMMU inaccessible, block idle, or cause faults during device runtime suspend. Because IOMMUs sit between masters and memory, power sequencing errors can surface as unrelated device DMA faults.

## Test Signals
Boot with OMAP IOMMU users enabled, bind remoteproc/DSP or multimedia clients, exercise map/unmap and runtime PM, and check for IOMMU faults during suspend/resume. Inspect clockdomain/powerdomain state transitions while clients are active and idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-iommu.c -->
