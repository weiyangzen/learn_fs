# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp10b.c

## Purpose
Defines GP10B/Tegra Pascal VMM support by reusing GP100 descriptors and methods with GK20A aperture restrictions and host-oriented page flags.

## Important APIs, Types, And Functions
Exports `gp10b_vmm_new`. The local function table uses `gp100_vmm_join`, `gf100_vmm_part`, `gk20a_vmm_aper`, `gp100_vmm_valid`, `gp100_vmm_flush`, `gp100_vmm_mthd`, and `gp100_vmm_invalidate_pdb`.

## Control Flow
Construction delegates to `gp100_vmm_new_`, retaining GP100 argument parsing and optional fault replay state. Page descriptors expose high-level sparse address levels and 21/16/12-bit host page mappings.

## State And Persistence
No local state is allocated. Persistent state is GP100-format page tables and instance memory, with aperture behavior limited by the integrated GPU memory model.

## Dependencies And Integration Points
Depends on `vmm.h`, GK20A aperture helper, GP100 descriptors, and GP100 method handling. It integrates with platform-specific Pascal mobile MMU creation.

## Risks And Test Signals
Risks are incorrect aperture acceptance, fault replay behavior on mobile hardware, and descriptor mismatch for host-only pages. Test NCOH/system memory maps, sparse mappings, replay/cancel methods, and BAR flush paths on GP10B platforms.
