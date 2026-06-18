# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/isp_mmu.h

## Purpose
This header declares AtomISP's classic two-level ISP MMU abstraction. It defines ISP page-table geometry, address translation macros, the hardware-client callback contract, MMU state, and map/unmap/TLB-flush APIs used by HMM buffer binding.

## Important APIs, Types, And Functions
- Page-table constants define 4 KiB pages, 10-bit L1 and L2 indexes, 1024 entries per level, and 2-level address decomposition.
- Macros convert ISP virtual addresses to L1/L2 indexes, align sizes, convert page counts to sizes, and test PTE validity.
- `struct isp_mmu_client` supplies hardware-specific behavior: driver name, PTE valid mask, null PTE, page-directory base conversion, TLB flush callbacks, and physical/PTE conversion helpers.
- `struct isp_mmu` stores the selected client, L1 page-table address/PTE, L2 page-table refcounts, physical base address, and `pt_mutex`.
- `isp_mmu_init()` and `isp_mmu_exit()` manage page table lifetime.
- `isp_mmu_map()` and `isp_mmu_unmap()` update mappings for contiguous physical pages at an ISP virtual address.
- `isp_mmu_flush_tlb_all()` and `isp_mmu_flush_tlb_range()` dispatch to client callbacks.

## Control Flow
HMM initializes an `isp_mmu` with a hardware client, maps each allocated BO page range into ISP virtual space, asks the hardware client to flush TLBs after mapping changes, and unmaps ranges during free/unbind. Map/unmap are internally mutex protected, but comments explicitly state they do not flush TLBs; callers must do that separately.

## State And Persistence
MMU state includes allocated L1/L2 page tables, L2 reference counts, the MMU client's callback table, and the hardware-facing page-directory base. Mappings persist in memory and hardware-visible page tables until unmapped or MMU exit.

## Dependencies And Integration Points
This header depends on kernel types/mutex/slab support and is consumed by `hmm_bo.h` and platform-specific MMU clients such as `sh_mmu_mrfld`. It bridges HMM buffer allocation to ISP hardware address translation.

## Risks
- TLB flushing is caller responsibility after map/unmap, making stale translations a likely integration bug.
- `ISP_PT_TO_VIRT` is defined with `do { ... } while (0)` and does not return a value, so it is unusable as an expression despite its name.
- Page size is required to match the kernel page size; unusual configurations would need careful review.
- `unsigned int` ISP virtual addresses limit address width and require range validation at callers.
- Client callbacks are partly mandatory by comment; init must enforce required callbacks to avoid null dereferences.

## Test Signals
Tests should cover address-index macros, size/page-count conversions, mapping and unmapping one page and multi-page ranges, L2 refcount behavior, TLB flush callback invocation by callers, null-PTE handling, physical/PTE conversion round trips for each hardware client, and invalid range/overflow handling.
