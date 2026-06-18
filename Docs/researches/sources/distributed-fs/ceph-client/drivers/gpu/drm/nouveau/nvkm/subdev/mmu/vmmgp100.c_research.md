# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmgp100.c

## Purpose
Implements GP100/Pascal VMM support, including MMU version 2 PTE/PDE encoding, sparse entries, PFN mapping with DMA map/unmap bookkeeping, compression tag line handling, replayable fault control methods, 64-bit PDB invalidation, and VMM construction with optional fault replay.

## Important APIs, Types, And Functions
Exports `gp100_vmm_desc_16`, `gp100_vmm_desc_12`, `gp100_vmm_valid`, `gp100_vmm_mthd`, `gp100_vmm_invalidate_pdb`, `gp100_vmm_flush`, `gp100_vmm_join`, `gp100_vmm_new_`, and `gp100_vmm_new`. Internal helpers cover PFN map/clear/unmap for 4 KiB and 2 MiB entries, sparse/invalid entries, 128-bit dual PDE writes, comptag calculations, and fault replay/cancel.

## Control Flow
Validation unpacks `gp100_vmm_map_v0` or unversioned args, optionally delegates to `valid2` for GH100, validates kind indexes, and configures compression behavior only when GSP-RM initialized the compbit store. Mapping uses `(addr >> 4)` encodings, and PFN mappings call DMA API for system pages. Fault cancel pauses GR context switching, compares the current instance, and sends a targeted invalidate; replay sends a global replay invalidate.

## State And Persistence
State includes page-table memory, DMA mappings created from PFN maps, `vmm->replay`, instance control bits for VER2/64KiB/fault replay, compression tag-line increments, and hardware fault/TLB state. `pfn_clear` invalidates valid DMA-backed entries before unmap.

## Dependencies And Integration Points
Depends on Linux DMA APIs, `engine/gr.h`, GF100 helpers, NVIF `ifc00d` method formats, and GSP-RM compression availability. GV100, TU102, GP10B, and GH100 reuse GP100 descriptors and constructors.

## Risks And Test Signals
Risks include DMA mapping leaks, PFN address shift mistakes, stale valid bits after `pfn_clear`, incorrect fault instance translation, compression exposure without GSP-RM, and 128-bit PDE partial writes. Test PFN VRAM/system mappings, sparse pages, GSP/non-GSP compression, fault replay/cancel, BAR-only flushes, context-switch pause/resume failure paths, and IOMMU-enabled systems.
