# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/iommu_pt.h

## Purpose

`iommu_pt.h` is the shared template implementation that turns a Generic PT format into Linux `iommu_domain` page-table operations. It implements IOVA-to-physical lookup, mapping, unmapping, dirty tracking, table allocation/freeing, dynamic top growth, DMA-incoherent table cache maintenance, and initialization/deinitialization.

## Important APIs, Types, and Functions

- Generated namespace macros such as `DOMAIN_NS` and `NS`.
- Range validation helpers `make_range_ul`, `make_range_u64`, and `make_range`.
- Lookup walker `__iova_to_phys` and exported `DOMAIN_NS(iova_to_phys)`.
- Dirty walker `DOMAIN_NS(read_and_clear_dirty)` and test-only `set_dirty`.
- Table lifecycle helpers `_table_alloc`, `table_alloc_top`, `pt_iommu_new_table`, `__collect_tables`, and `NS(deinit)`.
- Mapping path: `compute_best_pgsize`, `clear_contig`, `__map_range_leaf`, `__map_range`, `__map_single_page`, `increase_top`, `check_map_range`, `NS(map_range)`.
- Unmapping path: `__unmap_range`, `NS(unmap_range)`, and `gather_range_pages`.
- Initialization: `pt_init_common`, `pt_iommu_init_domain`, `pt_iommu_zero`, generated `pt_iommu_init`, and optional hardware-info export.

## Control Flow

Generated `map_range` validates permissions, output-address limits, and IOVA ranges, computes the best page size, grows the root if `PT_FEAT_DYNAMIC_TOP` requires it, then either uses a single-page fast path or recursive mapping walkers. Mapping allocates lower tables atomically and can replace empty table subtrees with larger leaves only after ensuring no existing mappings are present. Unmap recursively clears leaves, frees fully covered lower tables, records the unmapped byte count, and moves freed tables to the IOTLB gather list. Dirty read walks mapped leaves, records dirty IOVAs, optionally clears dirty bits, and schedules IOTLB ranges.

## State and Persistence Behavior

Persistent state is in `struct pt_iommu`, format-specific `pt_common`, the root pointer encoded in `top_of_table`, and allocated page-table pages. Dynamic top updates use driver-provided locking and `change_top` callbacks. Freed page-table pages are delayed through `iommu_iotlb_gather`. DMA-incoherent formats use page-list start/stop and targeted flushes; a software bit marks table pointers whose cache flush has completed.

## Dependencies and Integration Points

This template depends on `pt_iter.h`, format callbacks from `pt_common.h`, Linux IOMMU APIs, `iommu-pages.h`, dirty bitmap APIs, and driver callbacks for dynamic top. Wrapper files compile it once per format and export symbols in `GENERIC_PT_IOMMU`.

## Risks and Edge Cases

- Correctness depends on format callbacks obeying atomic table-install, alignment, and descriptor-classification contracts.
- Partial unmap of a large leaf unmaps the whole leaf and returns that size, matching current IOMMU API expectations but surprising for older split-map assumptions.
- Dynamic top readers are lockless, so `top_of_table` pointer/level packing and hardware `change_top` ordering are critical.
- DMA-incoherent table updates rely on software-bit acquire/release and cache flush ordering.
- `DOMAIN_NS(iova_to_phys)` returns negative range errors cast as `phys_addr_t` for invalid range before later returning 0 on walk miss.

## Test Signals

KUnit should exercise map/unmap across all page sizes, table-to-leaf replacement, dynamic top growth, disjoint gather behavior, DMA-incoherent cache flushes, dirty read/clear, failed overmaps, malformed ranges, deinit leak checks, and 32-bit host truncation paths.
