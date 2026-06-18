<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c

Purpose: generic dispatch layer for IOMMU page-table backends. It maps `enum io_pgtable_fmt` values to backend init functions, validates custom allocator support, allocates page-table ops, stores common config, and frees page tables after flushing.

Important APIs/types/functions: `io_pgtable_init_table[]`, `check_custom_allocator()`, exported `alloc_io_pgtable_ops()`, and exported `free_io_pgtable_ops()`.

Control flow: allocation rejects out-of-range formats, invalid custom allocator pairs, missing backend functions, or backend allocation failure. On success it stamps the format, cookie, and copied config into the returned `io_pgtable` and returns the ops table. Free converts ops back to `io_pgtable`, flushes all TLBs through generic callbacks, and invokes the backend free function.

State and persistence: global static init table reflects build-time enabled backends. Allocated backends own their private state; this file only initializes shared metadata.

Dependencies and integration: depends on Linux `io-pgtable.h` and backend symbols from ARM LPAE, DART, and ARMv7S under Kconfig guards. IOMMU drivers use it instead of directly constructing backend state.

Risks: `check_custom_allocator()` dereferences `io_pgtable_init_table[fmt]` before `alloc_io_pgtable_ops()` checks that the backend exists, so a custom allocator with a disabled format could fault in this snapshot. Free assumes the page table walker is already inaccessible apart from the final TLB flush.

Test signals: allocation for each enabled/disabled format, custom allocator accepted only for supporting formats, free after map/unmap, and negative tests for invalid enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable.c -->
