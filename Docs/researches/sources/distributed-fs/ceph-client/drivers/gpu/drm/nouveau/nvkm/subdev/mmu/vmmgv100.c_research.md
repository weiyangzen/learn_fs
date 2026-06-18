# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgv100.c

## Purpose
Provides GV100/Volta VMM support, primarily by extending GP100 instance join setup with additional per-entry page-directory base replication state.

## Important APIs, Types, And Functions
Exports `gv100_vmm_join` and `gv100_vmm_new`. The local `gv100_vmm` table uses GP100 descriptors, validation, flush, method handling, and PDB invalidation.

## Control Flow
`gv100_vmm_join` first performs `gp100_vmm_join`, then reads the instance PDB pointer from `0x200/0x204`, clears offset `0x21c`, populates 64 replicated entries at `0x2a0/0x2a4/0x2a8`, and writes a mask at `0x298/0x29c`. Only bit 0 is enabled in the current mask.

## State And Persistence
Persistent state is written to the GPU instance block after normal GP100 join state. No additional heap state is owned by the file.

## Dependencies And Integration Points
Depends on GP100 descriptors, GF100 part/aper helpers, and NVKM instance memory write helpers. TU102 and GH100 reuse `gv100_vmm_join`.

## Risks And Test Signals
Risks include wrong instance offsets, stale replicated PDB entries, mask mismatch, and failure to preserve GP100 join bits for replay/64 KiB mode. Test VM bind/unbind, multi-engine use, BAR mappings, replay faults, and suspend/resume across GV100-class hardware.
