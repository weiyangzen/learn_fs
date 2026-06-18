# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmtu102.c

## Purpose
Defines TU102/Turing VMM support by reusing GV100/GP100 page-table logic with a different MMU flush register sequence.

## Important APIs, Types, And Functions
Exports `tu102_vmm_flush` and `tu102_vmm_new`. The local function table uses `gv100_vmm_join`, `gf100_vmm_part`, `gf100_vmm_aper`, `gp100_vmm_valid`, `gp100_vmm_mthd`, and GP100 descriptor arrays.

## Control Flow
Flush constructs a PAGE_ALL invalidate type and, for BAR mappings, adds HUB_ONLY and ALL_PDB. It writes the PDB base to `0xb830a0`, clears high bits at `0xb830a4`, triggers `0xb830b0`, and polls until bit 31 clears. If RM provided `vmm->rm.bar2_pdb`, that PDB overrides the normal page directory.

## State And Persistence
Persistent state is GP100/GV100 page-table and instance memory plus Turing flush hardware state. No local heap state is introduced.

## Dependencies And Integration Points
Depends on `subdev/timer.h`, GP100 descriptors/methods, and GV100 join state. GH100 also uses this flush path.

## Risks And Test Signals
Risks include incorrect BAR2 PDB selection, flush timeout, overly broad ALL_PDB invalidation, and mismatch with GP100 descriptor assumptions. Test BAR mappings, RM-provided BAR2 PDB, replay fault paths, sparse/large pages, and repeated map/unmap under engine load.
