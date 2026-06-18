# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgk20a.c

## Purpose
Provides the Tegra GK20A VMM function tables. It narrows the aperture model for integrated GPU memory and reuses GK104/GF100 descriptors and operations.

## Important APIs, Types, And Functions
Exports `gk20a_vmm_aper` and `gk20a_vmm_new`. It defines two `nvkm_vmm_func` tables for 16-bit and 17-bit big pages, using `gf100_vmm_join`, `gf100_vmm_part`, `gf100_vmm_valid`, `gf100_vmm_flush`, and `gf100_vmm_invalidate_pdb`.

## Control Flow
`gk20a_vmm_aper` accepts only `NVKM_MEM_TARGET_NCOH`, returning aperture 0, but the function tables currently reference `gf100_vmm_aper`, so the local aperture helper is available to related mobile variants rather than used by `gk20a_vmm_new` itself. Construction delegates to `gf100_vmm_new_`.

## State And Persistence
No local state is stored. Page tables and instance memory follow the GF100/GK104 layout, with supported page flags emphasizing host/noncoherent integrated-memory mappings.

## Dependencies And Integration Points
Depends on `core/memory.h`, GK104 descriptor arrays, and GF100 helper exports. It is selected by platform-specific MMU construction for GK20A-class chips.

## Risks And Test Signals
The notable risk is aperture-policy drift: if code expects `gk20a_vmm_aper` but the table uses `gf100_vmm_aper`, invalid memory targets may be accepted. Test integrated-memory mappings, NCOH-only paths, 4 KiB and large-page mappings, and build warnings for unused/local aperture behavior.
