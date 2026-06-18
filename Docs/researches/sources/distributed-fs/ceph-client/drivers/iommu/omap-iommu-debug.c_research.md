# sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c

## Purpose
`omap-iommu-debug.c` implements debugfs support for OMAP IOMMU devices. It exposes read-only files for register dumps, TLB entries, page-table contents, and TLB-entry count under a global `omap_iommu` debugfs directory.

## Important APIs, Types, and Functions
Public entry points are `omap_iommu_debugfs_init()`, `omap_iommu_debugfs_exit()`, `omap_iommu_debugfs_add()`, and `omap_iommu_debugfs_remove()`. Internal read/show helpers are `debug_read_regs()`, `tlb_show()`, `pagetable_show()`, `omap_iommu_dump_ctx()`, `omap2_iommu_dump_ctx()`, `__dump_tlb_entries()`, `omap_dump_tlb_entries()`, and `dump_ioptable()`. The `pr_reg` macro formats register values from `iommu_read_reg()`.

## Control Flow and State
Init creates the root debugfs directory. Each OMAP IOMMU device gets a child directory with `nr_tlb_entries`, `regs`, `tlb`, and `pagetable`. Reads first reject detached devices (`!obj->domain`). Register dumping uses runtime PM get/put around hardware access. TLB dumping saves the current iotlb lock state, walks valid TLB entries, restores the lock state, and prints CAM/RAM pairs. Page-table dumping locks `obj->page_table_lock`, walks first-level and second-level OMAP page-table entries, and prints populated mappings.

State is debug-only: a global root dentry, each object's `debug_dir`, transient buffers, and read serialization through `iommu_debug_lock`. It does not persist data.

## Dependencies and Integration Points
The file depends on OMAP-specific headers `omap-iommu.h` and `omap-iopgtable.h`, debugfs, seq_file helpers, runtime PM, uaccess helpers, and platform data register definitions. It is an observability companion to the OMAP IOMMU driver rather than part of the fast map/unmap path.

## Risks and Test Signals
Risks include reading hardware while detached, large user `count` allocations for the register file, runtime PM failures ignored by `pm_runtime_get_sync()`, page-table walks racing with updates outside the local lock protocol, and debugfs availability in production builds. Test signals include debugfs creation/removal, register reads while attached/detached, valid TLB dump formatting, populated 1-level and 2-level page-table output, and module exit cleanup.
