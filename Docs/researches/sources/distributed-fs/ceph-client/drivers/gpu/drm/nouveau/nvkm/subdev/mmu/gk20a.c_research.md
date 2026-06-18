# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gk20a.c

## Purpose
Defines Tegra GK20A MMU capabilities, using GF100 VMM semantics but no VRAM allocation constructor.

## Important APIs, Types, and Functions
`gk20a_mmu` selects 40-bit DMA, GF100 classes, `.mem.umap = gf100_mem_map`, `gk20a_vmm_new`, `gf100_mmu_kind`, and `kind_sys=true`. `gk20a_mmu_new` registers it.

## Control Flow, State, and Persistence
Descriptor-only. Host/SoC memory allocation is expected outside the VRAM path; user mapping uses the GF100 mapping hook.

## Dependencies and Integration Points
Depends on GK20A VMM, GF100 map validation, and Tegra memory integration.

## Risks and Test Signals
Risks include absent `mem.vram` path, SoC aperture differences, and kind-table assumptions. Test Tegra memory handles, VMM mappings, IOMMU interaction, and user BAR mappings.
