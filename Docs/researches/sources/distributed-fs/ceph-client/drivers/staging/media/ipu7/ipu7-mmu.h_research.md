# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-mmu.h

## Purpose
Defines MMU, UAO, and ZLX register offsets/counts for IPU7, IPU7P5, and IPU8 variants, plus the software MMU state structures and public mapping API.

## Important APIs, Types, and Constants
Constants identify ISYS/PSYS MMIDs and many variant-specific block offsets: firmware read/write MMUs, data read/write MMUs, UAO planes, and ZLX blocks. Register offsets include `MMU_REG_INVALIDATE_*`, `MMU_REG_PAGE_TABLE_BASE_ADDR`, `MMU_REG_USER_INFO_BITS`, `MMU_REG_AXI_REFILL_IF_ID`, `MMU_REG_COLLAPSE_ENABLE_BITMAP`, `MMU_REG_INVALIDATION_STATUS`, IRQ registers, and ZLX config registers. `struct ipu7_mmu_info` stores L1/L2 page tables, dummy page/table PTEs, aperture, page-size bitmap, lock, and DMA mapping. `struct ipu7_mmu` stores hardware descriptors, MMID, DMA mapping, trash page state, ready lock, and TLB invalidation callback.

## Control Flow and State
The header state is allocated by `ipu7_mmu_init()`, programmed by `ipu7_mmu_hw_init()`, used by map/unmap callers, and freed by `ipu7_mmu_cleanup()`. Variant constants feed hardware descriptor construction elsewhere in the driver and are copied into per-device `ipu7_mmu_hw` arrays.

## Dependencies and Integration Points
Depends on Linux DMA/list/spinlock types and `ipu7_hw_variants` definitions from the broader IPU platform code. ISYS and PSYS bus devices use the same mapping API and hardware init/cleanup hooks.

## Risks and Test Signals
The header is dense hardware data; wrong stream counts or block register offsets cause memory translation failures that may look like firmware or DMA bugs. Test signals include successful MMU init on each supported hardware variant, correct L1/L2 block programming from descriptor counts, no out-of-bounds stream count rejection, and DMA capture buffers translating to expected physical pages.
