# sources/distributed-fs/ceph-client/rust/kernel/iommu/pgtable.rs

## Purpose
`iommu/pgtable.rs` wraps Linux `io_pgtable_ops` for Rust users. It supports allocating typed IOMMU page tables, mapping and unmapping pages, and accessing ARM64 LPAE S1 configuration values.

## Important APIs, Types, and Functions
`prot` exports IOMMU protection flags. `Config` carries quirks, page-size bitmap, IAS/OAS, and coherent-walk settings. `IoPageTable<F>` owns an `io_pgtable_ops` pointer parameterized by an `IoPageTableFmt`. `IoPageTableFmt` provides the C format enum. `IoPageTable::new`, unsafe `new_raw`, `raw_ops`, `raw_pgtable`, `raw_cfg`, unsafe `map_pages`, and unsafe `unmap_pages` form the main API. `NOOP_FLUSH_OPS` supplies no-op TLB callbacks. `ARM64LPAES1` implements the format and exposes unsafe `ttbr` plus `mair`.

## Control Flow
Construction fills `io_pgtable_cfg`, points TLB ops at no-op flush callbacks, sets the device pointer, and calls `alloc_io_pgtable_ops`. Mapping obtains the non-null `map_pages` function, passes IOVA, physical address, page size/count, protection flags, allocation flags, and a mapped-byte out parameter, then returns both mapped length and `Result`. Unmapping calls `unmap_pages` and returns the unmapped byte count. Drop frees the ops.

## State and Persistence
The page table and its configuration live in kernel memory allocated by io-pgtable code and persist until `IoPageTable` drops. The devres constructor ties lifetime to device unbind; unsafe `new_raw` requires callers to drop before device unbind. Mappings persist until unmapped or table destruction.

## Dependencies and Integration Points
It integrates with Linux `io-pgtable.h`, device devres, allocation flags, physical addresses, IOMMU protection flags, and GPU firmware users that manage their own IOTLB invalidation using ranges.

## Risks
Mapping/unmapping are unsafe because callers must serialize access to the affected IOVA range and avoid overlaps. No-op flush ops are correct only for users that handle invalidation elsewhere. `ttbr` is unsafe because users must stop device use before dropping the table. Partial map/unmap results require caller cleanup logic.

## Test Signals
Tests should cover allocation failure, raw/devres lifetime, map success and partial failure cleanup, unmap counts, ARM64 `ttbr`/`mair` reads, page-size/protection combinations, and external TLB invalidation integration.
