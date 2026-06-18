# sources/distributed-fs/ceph-client/mm/hmm.c

## Purpose

`hmm.c` implements the core heterogeneous memory management range-fault walker and HMM DMA mapping helpers. HMM lets device drivers mirror CPU page-table state into device page tables or DMA mappings while coordinating with MMU interval notifiers. The file converts CPU PTE/PMD/PUD/hugetlb entries into `HMM_PFN_*` encoded PFNs, optionally faults pages in, handles device-private/exclusive/migration entries, and provides helper functions to allocate, map, and unmap DMA addresses for HMM PFN arrays.

Primary users in this tree include GPU SVM code and RDMA ODP code. The grep results show integration in DRM GPU SVM (`drivers/gpu/drm/drm_gpusvm.c`, Nouveau, AMDGPU/KFD), RDMA ODP (`drivers/infiniband/core/umem_odp.c`, mlx5, rxe), Hyper-V memory regions, and accelerator code.

## Important APIs, Types, and Functions

The main exported page-table API is `hmm_range_fault(struct hmm_range *range)`. The caller supplies a range with `start`, `end`, `notifier`, `notifier_seq`, `hmm_pfns`, `default_flags`, `pfn_flags_mask`, and optional `dev_private_owner`. The output array stores encoded PFNs plus flags such as `HMM_PFN_VALID`, `HMM_PFN_WRITE`, `HMM_PFN_ERROR`, order bits, and preserved DMA/P2P flags.

Internal walker state is `struct hmm_vma_walk`, which stores the range and the last unprocessed address. `hmm_walk_ops` hooks into generic pagewalk with `hmm_vma_walk_pud()`, `hmm_vma_walk_pmd()`, `hmm_vma_walk_hole()`, `hmm_vma_walk_hugetlb_entry()`, and `hmm_vma_walk_test()`.

Fault-decision helpers are `hmm_pte_need_fault()` and `hmm_range_need_fault()`. They combine per-PFN request bits with range defaults to decide whether a missing, read-only, or nonpresent entry requires a read or write fault. `hmm_vma_fault()` invokes `handle_mm_fault()` with `FAULT_FLAG_REMOTE` and optional `FAULT_FLAG_WRITE`, returning `-EBUSY` after a fault so `hmm_range_fault()` restarts safely from the recorded address.

Entry conversion helpers include `pte_to_hmm_pfn_flags()`, `pmd_to_hmm_pfn_flags()`, `pud_to_hmm_pfn_flags()`, `hmm_vma_handle_pte()`, `hmm_vma_handle_pmd()`, and `hmm_vma_handle_absent_pmd()`. They preserve input/output DMA flags through `HMM_PFN_INOUT_FLAGS`, report unsupported mappings as `HMM_PFN_ERROR`, and handle device-private pages owned by the caller without forcing migration back to system memory.

The exported DMA helpers are `hmm_dma_map_alloc()`, `hmm_dma_map_free()`, `hmm_dma_map_pfn()`, and `hmm_dma_unmap_pfn()`. They maintain `struct hmm_dma_map` arrays for PFNs and optional DMA addresses, support DMA IOVA state where possible, reject devices that require sync or limited addressing, and handle PCI P2PDMA states.

## Control Flow

`hmm_range_fault()` requires the caller to hold the mm mmap lock. It initializes `last` to `range->start`, checks `mmu_interval_check_retry()` against `range->notifier_seq`, and calls `walk_page_range()` from the last unprocessed address to the end. If a handler returns `-EBUSY` after faulting or waiting on migration, the loop retries; entries before `last` have already been stored, while later entries retain their input request flags.

For holes and unsupported VMAs, the walker either faults if requested or fills output entries with zero/no-valid or `HMM_PFN_ERROR`. For PTEs, `hmm_vma_handle_pte()` distinguishes empty/UFFD-WP markers, nonpresent softleaf entries, device-private pages owned by the caller, swap/device/migration entries, special mappings without normal pages, and normal present PTEs. Migration entries wait and return `-EBUSY`; swap or device entries fault when requested; unknown nonpresent entries fail.

For huge mappings, PMD/PUD/hugetlb handlers compute a base PFN plus page offset, attach valid/write/order flags, and populate each page-sized slot in `hmm_pfns[]`. The code generally avoids splitting huge mappings and relies on MMU notifier invalidation to handle concurrent splits. Hugetlb write faults drop the hugetlb VMA lock before calling `hmm_vma_fault()` to avoid deadlock.

DMA mapping starts with `hmm_dma_map_alloc()`, which allocates PFN storage, optional DMA storage, and possibly an IOVA range. `hmm_dma_map_pfn()` converts the encoded HMM PFN to `struct page`/physical address, handles already-mapped entries, consults PCI P2PDMA state, then either links an IOVA, maps a physical address, or returns a P2P bus address. `hmm_dma_unmap_pfn()` reverses the operation if the PFN has both valid and DMA-mapped bits, clearing DMA/P2P flags afterward.

## State and Persistence Behavior

`hmm_range_fault()` mutates the caller-provided `hmm_pfns[]` array in place. It preserves `HMM_PFN_DMA_MAPPED`, `HMM_PFN_P2PDMA`, and `HMM_PFN_P2PDMA_BUS` bits from input to output so callers can reuse DMA state across faults or permission upgrades. It does not pin pages; validity is tied to the caller's MMU interval notifier sequence, and callers must retry if invalidation races are detected.

DMA helpers persist allocations in `struct hmm_dma_map`: PFN arrays, optional DMA address arrays, and IOVA state. `hmm_dma_map_pfn()` sets mapping flags in `pfn_list[idx]`; `hmm_dma_unmap_pfn()` clears them. P2P bus mappings set `HMM_PFN_P2PDMA_BUS` and do not require normal DMA unmap.

## Dependencies and Integration Points

The file depends on generic pagewalk, MMU interval notifiers, `handle_mm_fault()`, softleaf swap/device/migration entry helpers, THP and hugetlb support, device-private memory, memory hotplug, DMA mapping APIs, DMA IOVA helpers, and PCI P2PDMA. It exports symbols for device drivers rather than core user APIs.

Callers must coordinate with `mmu_interval_read_begin()`/retry and usually hold driver-specific locks that protect mirrored device page tables. RDMA ODP uses the DMA helpers to back hardware page tables; GPU SVM uses `hmm_range_fault()` to resolve CPU mappings for device faults and migrations.

## Risks and Edge Cases

The API is race-sensitive. `hmm_range_fault()` reads CPU page tables without pinning pages, so the notifier sequence is the validity contract. Callers that ignore `-EBUSY` or fail to retry on interval invalidation can program stale device mappings. Permission upgrades must preserve and resync DMA state correctly when an already mapped PFN gains write permission.

Fault policy is subtle because request bits can come from range defaults or individual PFN entries. Unsupported VMAs return `HMM_PFN_ERROR` only when no fault was requested; if a valid PFN was requested, they return hard failure. Device-private entries owned by the caller are reported directly, while other device/private/exclusive/swap entries usually require faulting or fail.

DMA helper restrictions are important. Devices requiring DMA sync or limited addressing are rejected because HMM cannot transfer buffer ownership under normal streaming DMA rules. P2PDMA path selection must match the target device; clearing only some mapping bits on errors would leak stale state, so the error paths and unmap paths deserve careful testing.

## Test Signals

Test signals come from driver selftests and runtime paths that exercise device faults: RDMA ODP page fault tests, GPU SVM fault/migration tests, P2PDMA mapping coverage, hugetlb/THP ranges, migration-entry waits, and MMU notifier invalidation retries. In-tree users contain assertions such as RDMA ODP checks that faulted ranges have `HMM_PFN_VALID` and not `HMM_PFN_ERROR`. DMA tests should verify map/unmap idempotence, IOVA and non-IOVA backends, P2PDMA bus mappings, and permission-upgrade remapping.
