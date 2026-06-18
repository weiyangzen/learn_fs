# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgm20b.c

## Purpose
Defines GM20B/Tegra Maxwell VMM function tables. It reuses GM200 sparse descriptors while applying the GK20A aperture policy and mobile page capability flags.

## Important APIs, Types, And Functions
Exports `gm20b_vmm_new` and `gm20b_vmm_new_fixed`. Local 16-bit and 17-bit function tables use `gm200_vmm_join`, `gk20a_vmm_aper`, `gf100_vmm_valid`, and `gf100_vmm_flush`.

## Control Flow
`gm20b_vmm_new` delegates to `gm200_vmm_new_`, allowing NVIF-selected big-page mode. `gm20b_vmm_new_fixed` delegates to `gf100_vmm_new_`, deriving the page mode from the framebuffer page configuration. Both tables support 27-bit sparse levels plus 16/17-bit and 12-bit pages.

## State And Persistence
The file stores no local state. Page-table state follows GM200 layouts; aperture state is constrained through `gk20a_vmm_aper`.

## Dependencies And Integration Points
Depends on GM200 descriptors and GK20A aperture behavior. It is used by mobile/Tegra MMU setup where system memory and noncoherent mappings differ from discrete GPUs.

## Risks And Test Signals
Risks include accepting unsupported VRAM/system-coherent targets, choosing the wrong constructor mode, and sparse entry handling on integrated GPUs. Test NCOH mappings, NVIF bigpage selection, sparse maps, and fixed constructor paths.
