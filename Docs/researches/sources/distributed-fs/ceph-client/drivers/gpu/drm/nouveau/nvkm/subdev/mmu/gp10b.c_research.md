# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gp10b.c

## Purpose
Defines Tegra GP10B MMU support with GP100-style 47-bit VMM layout or GM20B fallback.

## Important APIs, Types, and Functions
`gp10b_mmu` uses `.mem.umap = gf100_mem_map`, `gp10b_vmm_new`, and `gm200_mmu_kind`. `gp10b_mmu_new` checks `GP100MmuLayout`; false selects `gm20b_mmu_new`.

## Control Flow, State, and Persistence
Descriptor selection is config-driven and persists for all VMMs created under this MMU. VRAM allocation is not exposed through `.mem.vram`.

## Dependencies and Integration Points
Depends on core options, Tegra memory, GP10B VMM implementation, GM20B fallback, and GF100 mapping validation.

## Risks and Test Signals
Risks include wrong layout on SoC firmware, absent VRAM allocation path, and high address-width issues. Test both layout options, Tegra mappings, IOMMU behavior, raw VMM operations, and user class negotiation.
