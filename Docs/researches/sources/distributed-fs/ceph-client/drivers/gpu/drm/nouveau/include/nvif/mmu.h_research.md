# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/mmu.h

## Purpose
Declares the NVIF MMU wrapper and helpers for memory type/kind discovery.

## Important APIs, Types, And Functions
Defines `struct nvif_mmu`, memory type flags (`VRAM`, `HOST`, `COMP`, `DISP`, `KIND`, `MAPPABLE`, `COHERENT`, `UNCACHED`), constructor/destructor, `nvif_mmu_kind_valid()`, and `nvif_mmu_type()`.

## Control Flow
Construction queries heap/type/kind tables. `kind_valid` rejects invalid kind indices or sentinel kind values. `type` scans for a type containing all requested flags.

## State And Persistence
MMU state caches DMA bits, heaps, types, kind count, invalid kind marker, and kind table until destructor.

## Dependencies And Integration Points
Used by `nvif/mem.h`, `nvif/vmm.h`, memory allocation, display-compatible memory selection, and compression/kind validation.

## Risks
Cache population must match server counts. Invalid kind handling is easy to get wrong because kind zero is accepted specially.

## Test Signals
MMU enumeration, type lookup, kind validation, allocation placement, and compressed/display memory tests validate behavior.
