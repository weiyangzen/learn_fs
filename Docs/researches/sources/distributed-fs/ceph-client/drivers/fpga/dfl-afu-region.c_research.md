## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-region.c

Purpose: this file manages AFU MMIO region metadata used by the DFL AFU char-device ioctls and mmap path.

Important APIs and functions: `afu_mmio_region_init()` initializes the region list. `afu_mmio_region_add()` allocates a `struct dfl_afu_mmio_region`, checks for duplicate index, assigns a page-aligned file offset from `region_cur_offset`, appends the region, and increments `num_regions`. `afu_mmio_region_get_by_index()` returns metadata for `DFL_FPGA_PORT_GET_REGION_INFO`. `afu_mmio_region_get_by_offset()` finds the region containing a requested mmap file offset and size. `afu_mmio_region_destroy()` frees all devm-allocated region nodes.

Control flow: feature init in `dfl-afu-main.c` calls add for AFU and STP resources. Userspace first queries region count/info, then uses returned offsets for mmap. All list mutations and lookups hold `fdata->lock`.

State and persistence: `struct dfl_afu` owns a linked list of regions, current synthetic file offset, and region count. Regions persist for the AFU device lifetime and are not affected by individual file closes.

Dependencies and integration: it depends on `dfl-afu.h`, DFL feature private data, platform resource sizes, and AFU mmap/ioctl callers. Region flags determine read/write/mmap permissions in `afu_mmap()`.

Risks: `region->size` stores the original resource size while offset advancement uses `PAGE_ALIGN(region_size)`. Containment checks use the unaligned size, so mapping the padding area is rejected, which is intentional but must match userspace expectations. Duplicate index failure frees the devm allocation manually; future changes must avoid double-free patterns. Offset addition should be guarded if very large region sizes are introduced.

Test signals: add duplicate regions, query invalid indexes, mmap exact and out-of-range offsets, verify read/write permission flags, and check that reported offsets remain stable across opens.
