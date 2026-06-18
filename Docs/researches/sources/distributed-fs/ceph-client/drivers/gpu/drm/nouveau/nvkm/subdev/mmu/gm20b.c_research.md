# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/gm20b.c

## Purpose
Defines Tegra GM20B MMU descriptors with GM200-style VMMs and external/host memory mapping.

## Important APIs, Types, and Functions
`gm20b_mmu` uses `gm20b_vmm_new`; `gm20b_mmu_fixed` uses `gm20b_vmm_new_fixed`; both expose only `.mem.umap = gf100_mem_map`, use `gm200_mmu_kind`, and set 40-bit DMA. `gm20b_mmu_new` selects fixed mode from `device->fb->page`.

## Control Flow, State, and Persistence
Descriptor selection mirrors GM200 but omits a VRAM allocator constructor. Base.c handles user type enumeration and VMM construction.

## Dependencies and Integration Points
Depends on Tegra memory, GF100 map code, GM20B VMM backends, and FB page-mode state.

## Risks and Test Signals
Risks include wrong fixed-mode selection, missing VRAM allocation path, and SoC aperture differences. Test GM20B user memory handles, VMM maps, IOMMU faults, fixed-page mode, and kind queries.
