## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-dma-region.c

Purpose: this file implements AFU userspace DMA mapping support for Intel DFL ports. It pins userspace pages, requires physical contiguity, maps them for DMA, tracks mappings in an RB tree, and unmaps them on ioctl or final device release.

Important APIs and functions: `afu_dma_region_init()` initializes the RB root. `afu_dma_map_region()` validates page alignment and overflow, allocates `struct dfl_afu_dma_region`, pins pages with `pin_user_pages_fast(FOLL_WRITE)`, verifies contiguous PFNs, maps the first page with `dma_map_page()`, inserts the region with `afu_dma_region_add()`, and returns the IOVA. `afu_dma_unmap_region()` finds by IOVA, rejects `in_use`, removes from the tree, unmaps DMA, unpins pages, and frees memory. `afu_dma_region_find()` searches for exact-start or containing regions.

Control flow: mapping does all expensive pin/map work before acquiring `fdata->lock`, then inserts the region under lock. Failure paths unwind in reverse order. Destroy walks the RB tree and releases all residual regions, intended for last close or device teardown.

State and persistence: `struct dfl_afu` owns the RB tree. Each region persists until explicit unmap or `afu_dma_region_destroy()`. The process locked-VM accounting is incremented when pages are pinned and decremented when unpinned.

Dependencies and integration: it depends on the AFU private data from `dfl-afu.h`, Linux DMA mapping API, user page pinning, current process `mm`, and the parent device returned by `dfl_fpga_fdata_to_parent()`. AFU ioctls in `dfl-afu-main.c` expose the map/unmap ABI.

Risks: it only supports physically contiguous user pages, which can fail for otherwise valid user memory. Locked-VM accounting is charged to `current->mm` on map and uncharged using `current->mm` on unmap/destroy; if cleanup occurs from a different task context, accounting assumptions can be delicate. `dma_region_check_iova()` uses addition that should be considered for overflow in future changes. Destroy erases a node and then calls `rb_next(node)`, which is a fragile ordering pattern because the node has already been erased.

Test signals: test unaligned addresses/lengths, zero length, overflow, non-contiguous pages, pin failures, DMA mapping errors, duplicate/overlapping IOVA insertion, unmap while `in_use`, last-close cleanup, and memlock-limit enforcement.
