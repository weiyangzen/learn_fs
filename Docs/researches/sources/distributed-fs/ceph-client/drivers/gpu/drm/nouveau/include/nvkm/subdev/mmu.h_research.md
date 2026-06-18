# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mmu.h

## Purpose

This header defines the MMU and virtual-memory manager interfaces: VMA allocation state, VMM address-space lifetime, page-table joins, mapping descriptors, user memory/VMM lookup, memory heap/type capabilities, and generation-specific MMU constructors.

## Important APIs, Types, and Functions

Important types include `struct nvkm_vma`, `struct nvkm_vmm`, `struct nvkm_vmm_map`, and `struct nvkm_mmu`. Important APIs are `nvkm_vmm_new`, `nvkm_vmm_ref`, `nvkm_vmm_unref`, `nvkm_vmm_boot`, `nvkm_vmm_join`, `nvkm_vmm_part`, `nvkm_vmm_get`, `nvkm_vmm_put`, `nvkm_vmm_map`, `nvkm_vmm_unmap`, `nvkm_umem_search`, and `nvkm_uvmm_search`.

## Control Flow

Callers create a VMM over an address range, optionally bootstrap/join backing page-directory memory, allocate VMAs from managed free trees, map NVKM memory or scatter/PFN sources into a VMA, and unmap/put regions when no longer needed. MMU constructors publish heap/type capabilities and invalidation synchronization used by engines.

## State and Persistence Behavior

VMAs persist address, size, page selection/ref state, sparse/busy/mapped/no-compression flags, mapped memory, and compression tags. VMMs persist managed ranges, free/used trees, page directory roots, engine refs, null page, replay flag, and optional GSP RM handles. MMU state persists DMA width, memory heaps/types, default VMM, PTC/PTP lists, and invalidation mutex.

## Dependencies and Integration Points

It integrates with memory objects, GPU objects, BAR mappings, FIFO/GR TLB invalidation, GSP RM VMM objects, user NVIF handles, and all GPU memory allocation paths.

## Risks

VMA split/part/mapref state is subtle and can leak page-table refs or expose stale mappings. Compression-tag mismatch corrupts compressed surfaces. Missing invalidation synchronization causes GPU faults after remap. Sparse mappings must not be treated as resident memory.

## Test Signals

Exercise VMM creation/destruction, VMA allocation splitting, map/unmap with memory/SG/PFN sources, compression tags, sparse mappings, GSP external VMM handles, engine ref accounting, and fault replay paths.
