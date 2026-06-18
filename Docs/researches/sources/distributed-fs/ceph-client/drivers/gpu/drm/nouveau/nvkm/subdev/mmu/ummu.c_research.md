# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/ummu.c

## Purpose
Implements the user-visible MMU object that reports memory heaps/types/kinds and exposes memory/VMM child classes.

## Important APIs, Types, and Functions
Important symbols are `nvkm_ummu_new`, `nvkm_ummu_sclass`, `nvkm_ummu_heap`, `nvkm_ummu_type`, `nvkm_ummu_kind`, and `nvkm_ummu_mthd`.

## Control Flow, State, and Persistence
Creation unpacks the MMU object request and returns DMA bits plus heap/type/kind counts. Method dispatch handles heap-size queries, type flag queries, and kind table copies. Subclass enumeration exposes a user memory class when available and a user VMM class when available.

## Dependencies and Integration Points
Depends on `umem`, `uvmm`, NVIF MMU ABI, `nvkm_mmu` heap/type arrays, and kind callbacks.

## Risks and Test Signals
Risks include out-of-range index handling, copying an absent kind table, stale class descriptors, and ABI version mismatch. Test NVIF heap/type/kind queries, child class enumeration, no-kind devices, and invalid user arguments.
