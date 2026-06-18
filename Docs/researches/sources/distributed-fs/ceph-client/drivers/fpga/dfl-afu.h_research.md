## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu.h

Purpose: this header defines shared private data structures and helper prototypes for the DFL AFU compound driver.

Important types and APIs: `struct dfl_afu_mmio_region` describes a userspace-visible MMIO window with index, flags, size, synthetic file offset, physical address, and list node. `struct dfl_afu_dma_region` describes a pinned DMA mapping with user VA, length, IOVA, page array, RB node, and `in_use` flag. `struct dfl_afu` is the per-port private object containing MMIO offset/count state, region list, DMA RB root, and user-message count. Prototypes cover port enable/disable, MMIO region management, DMA region management, and exported port error feature ops/groups.

Control flow and integration: `dfl-afu-main.c` owns `struct dfl_afu` allocation and lifecycle, while `dfl-afu-region.c`, `dfl-afu-dma-region.c`, and `dfl-afu-error.c` operate through these shared definitions. The explicit comment requires callers to hold `fdata->lock` for low-level port enable/disable helpers.

State and persistence: this header defines but does not instantiate state. The structures clarify which AFU state persists for device lifetime (MMIO regions), per mapping (DMA regions), and per hardware port (`dfl_afu` private pointer).

Dependencies and risks: it depends on `dfl.h` and Linux MM types. Because helpers share mutable `struct dfl_afu`, lock discipline is an important contract not enforced by the compiler. The `in_use` flag is present for consumers outside the DMA file but must be managed consistently by future AFU operations.

Test signals: compile all AFU objects together, validate lockdep coverage for helper callers, and ensure structure fields stay ABI-internal and are not assumed by userspace.
