# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmm.c

## Purpose
Implements the common virtual memory manager: VMA allocation/free, page-table reference counting, sparse mappings, raw/PFN mappings, memory map/unmap, page-table bootstrapping, VMM construction/destruction, and reference lifetime.

## Important APIs, Types, and Functions
Important APIs include `nvkm_vmm_new`, `nvkm_vmm_new_`, `nvkm_vmm_get_locked`, `nvkm_vmm_get`, `nvkm_vmm_put_locked`, `nvkm_vmm_put`, `nvkm_vmm_map`, `nvkm_vmm_unmap`, `nvkm_vmm_unmap_locked`, `nvkm_vmm_pfn_map`, `nvkm_vmm_pfn_unmap`, `nvkm_vmm_raw_get/put/unmap/sparse`, `nvkm_vmm_boot`, `nvkm_vmm_join/part`, `nvkm_vmm_ref`, and `nvkm_vmm_unref`.

## Control Flow, State, and Persistence
The core walk engine `nvkm_vmm_iter` deconstructs virtual addresses into per-level PTE indices, allocates software/hardware page tables on demand, applies PTE map/clear callbacks, tracks flush depth, and unwinds partial failures. VMA state is stored in a list plus RB trees for address lookup and size-ordered free lookup. Allocation splits free VMAs, optionally preallocates PTEs or sparse PTEs, and records page/ref state. Put unmaps memory, drops PTE references, merges split regions, and returns space to the free tree.

## Dependencies and Integration Points
Depends on `vmm.h` backend descriptors, MMU page-table cache, `nvkm_memory` mapping/tag APIs, FB tag handling, R535 vaspace deletion, and chip-specific flush/join/part/valid callbacks.

## Risks and Test Signals
Risks include page-table reference leaks, dual large/small page transition errors, sparse state corruption, VMA split/merge bugs, PFN DMA unmap ordering, flush-depth mistakes, raw managed-range misuse, and destructor cleanup of bootstrapped VMMs. Test VMM allocation fragmentation, sparse get/put, mixed page sizes, map replacement, PFN map/unmap, raw managed VMM operations, bootstrapped BAR VMMs, concurrent map/ref locks, and fault injection in page-table allocation.
