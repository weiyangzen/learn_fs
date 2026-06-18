# sources/distributed-fs/ceph-client/drivers/iommu/mtk_iommu.c

## Purpose
`mtk_iommu.c` is the modern MediaTek M4U/IOMMU driver for many MT27xx/MT67xx/MT81xx/MT83xx SoCs and MM/INFRA/APU variants. It registers the IOMMU provider, parses SMI larb topology, manages shared or per-bank page tables, supports multiple IOVA regions, programs hardware, handles faults, and restores hardware state across runtime PM.

## Important APIs, Types, and Functions
Platform feature data is encoded in `struct mtk_iommu_plat_data`, which describes SoC flags, register selection, hardware lists, IOVA regions, bank counts, enabled banks, bank port masks, and larb remapping. Runtime state is `struct mtk_iommu_data`, `struct mtk_iommu_bank_data`, and `struct mtk_iommu_domain`.

Core functions include `mtk_iommu_probe()`, `mtk_iommu_remove()`, `mtk_iommu_mm_dts_parse()`, `mtk_iommu_of_xlate()`, `mtk_iommu_probe_device()`, `mtk_iommu_release_device()`, `mtk_iommu_attach_device()`, `mtk_iommu_identity_attach()`, `mtk_iommu_domain_finalise()`, `mtk_iommu_map()`, `mtk_iommu_unmap()`, `mtk_iommu_iotlb_sync()`, `mtk_iommu_sync_map()`, `mtk_iommu_iova_to_phys()`, `mtk_iommu_get_resv_regions()`, `mtk_iommu_hw_init()`, `mtk_iommu_isr()`, and runtime suspend/resume callbacks.

## Control Flow and State
Probe allocates driver state, creates an aligned protect buffer for translation faults, detects 4GB mode when applicable, maps banked MMIO resources, initializes enabled bank descriptors and IRQ numbers, obtains clocks/regmaps, parses MM larbs and SMI common topology, registers with the IOMMU core, and optionally becomes a component master. Shared-page-table SoCs insert devices into global hardware lists so sibling IOMMUs can share a domain.

OF translation stores the IOMMU data pointer and fwspec IDs. Probe-device links MM clients to larb devices. Attach chooses an IOVA region and bank from fwspec IDs and platform masks, finalizes or reuses an ARM v7s io-pgtable with MediaTek quirks, programs bank TTBR and hardware registers on first use, optionally raises the DMA mask for >4G regions, and enables the relevant SMI or infra-master routing. Identity attach disables routing.

Map/unmap delegate to io-pgtable, with 4GB mode physical remap on map and reverse remap on `iova_to_phys()`. TLB range invalidation iterates all IOMMUs sharing the hardware list, skips inactive PM domains when allowed, polls `REG_MMU_CPE_DONE`, and falls back to full flush on timeout. Fault handling decodes IOVA/PA, larb/port, layer, and write/read direction, reports the fault, clears interrupts, and flushes all TLBs. Runtime suspend saves global and per-bank registers; resume restores them, rewrites TTBRs, and flushes TLBs.

## Dependencies and Integration Points
The driver integrates with the IOMMU core, io-pgtable `ARM_V7S`, MediaTek SMI larb components, device links, runtime PM, clocks, syscon/regmap, secure monitor calls for some infra masters, device tree bindings, PCI checks, and platform IRQs. The many `mtk_iommu_plat_data` instances are critical integration points for per-SoC behavior.

## Risks and Test Signals
Risks include feature-flag combinations, multi-region group assignment, shared page-table lifetime, bank selection, PM-aware TLB flushing that may skip inactive devices, IRQ request during first bank initialization, device-link cleanup, and 4GB/34-bit/35-bit address handling. Test signals include attach/map/unmap on every compatible, multi-larb devices, multi-region devices, infra/APU paths, runtime suspend/resume with existing mappings, TLB timeout fallback, fault injection with decoded larb/port, PCI infra configuration, and reserved-region reporting.
