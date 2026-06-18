# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/iommu_api.c

Purpose: Manages per-mm preregistered memory ranges for sPAPR TCE/IOMMU use, allowing user or device memory ranges to be pinned, looked up, translated to host physical addresses, mapped/unmapped, and released safely.

Important APIs and types: Defines private `struct mm_iommu_table_group_mem_t` with RCU list node, use count, mapped count, page shift, user address, entry count, union of `hpages`/`hpas`, and optional device HPA. Public exports include `mm_iommu_new()`, `mm_iommu_newdev()`, `mm_iommu_put()`, `mm_iommu_lookup()`, `mm_iommu_get()`, `mm_iommu_ua_to_hpa()`, `mm_iommu_is_devmem()`, `mm_iommu_mapped_inc()`, `mm_iommu_mapped_dec()`, `mm_iommu_preregistered()`, and `mm_iommu_init()`.

Control flow: Allocation accounts locked memory for normal user pages, allocates metadata, pins pages in chunks with `pin_user_pages(FOLL_WRITE | FOLL_LONGTERM)`, computes the largest usable IOMMU page shift, converts pinned page pointers to physical addresses in the reused union storage, checks overlap under `mem_list_mutex`, then adds the range to the mm RCU list. Device memory allocations skip pinning and store a base HPA. Put decrements `used`, refuses release while mappings remain, transitions `mapped` from 1 to 0, removes the range by RCU, unpins dirty pages, and unaccounts locked memory. Lookups are RCU protected; exact get increments `used` under the mutex.

State and persistence: State lives in `mm->context.iommu_group_mem_list`, per-range `used`, atomic `mapped`, pinned page references, dirty bits embedded in low HPA bits, and locked-mm accounting. The data lasts until `mm_iommu_put()` and RCU free.

Dependencies and integration: Requires `CONFIG_SPAPR_TCE_IOMMU` integration from `mmu_context.c`, GUP pinning, RCU lists, hugetlb page size detection, and mm locked-memory accounting. External IOMMU/KVM code consumes the exported opaque pointer.

Risks: The `hpages`/`hpas` union relies on pointer-sized storage reuse and ordered conversion after pinning. Long-term pins affect migration and memory pressure. Dirty marking is encoded in low physical-address bits and assumes 4K alignment. Overlap checks and use/mapped counters must prevent freeing while device mappings exist.

Test signals: VFIO/sPAPR TCE preregistration, overlapping registration rejection, long-term pin failure unwinding, hugetlb-backed preregistered memory, device-memory lookup, dirty unpin behavior, and mm teardown warnings for non-empty lists.
