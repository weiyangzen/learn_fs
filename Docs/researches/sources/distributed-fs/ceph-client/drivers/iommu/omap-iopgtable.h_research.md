# sources/distributed-fs/ceph-client/drivers/iommu/omap-iopgtable.h

## Purpose
This header defines the OMAP IOMMU page-table descriptor layout and index/translation helpers for the two-level OMAP hardware page table used by `omap-iommu.c`.

## Important APIs, Types, And Functions
The file defines L1 directory geometry with `IOPGD_SHIFT`, `IOPGD_SIZE`, `IOPGD_MASK`, `PTRS_PER_IOPGD`, and `IOPGD_TABLE_SIZE`; section and supersection geometry with `IOSECTION_*` and `IOSUPER_*`; and L2 page-table geometry with `IOPTE_SHIFT`, `IOLARGE_SHIFT`, `PTRS_PER_IOPTE`, and `IOPTE_TABLE_SIZE`. Descriptor encodings include `IOPGD_TABLE`, `IOPGD_SECTION`, `IOPGD_SUPER`, `IOPTE_SMALL`, and `IOPTE_LARGE`, with predicate macros for each kind.

`omap_iommu_translate()` combines a descriptor base address with an IOVA offset under a size mask. `iopgd_index()`, `iopgd_offset()`, `iopgd_page_paddr()`, `iopgd_page_vaddr()`, `iopte_index()`, and `iopte_offset()` locate page-directory and page-table entries.

## Control Flow
The header is macro and inline helper only. At runtime map/unmap/iova-to-phys paths use these helpers to choose L1 versus L2 descriptors, calculate table offsets, and translate descriptor values back to CPU physical addresses.

## State And Persistence
It defines no storage itself. It defines the layout of persistent OMAP page directories and L2 tables that are allocated, DMA-synchronized, and freed by the implementation.

## Dependencies And Integration Points
It depends on Linux bit helpers and assumes OMAP page tables are addressable through `phys_to_virt()` for L2 table access. It is consumed by OMAP IOMMU map, unmap, fault-dump, and iova-to-phys code.

## Risks
The macros assume 32-bit IOVA space and descriptor fields. `iopgd_page_vaddr()` assumes a direct physical-to-virtual mapping for page tables; platforms where DMA address, physical address, and CPU direct-map assumptions differ are risky. Incorrect size masks would cause either wrong physical translations or freeing the wrong entries.

## Test Signals
Exercise map/unmap and iova-to-phys for 4 KiB, 64 KiB, 1 MiB, and 16 MiB mappings. Boundary tests should cover L1/L2 index transitions and large/supersection alignment failures.
