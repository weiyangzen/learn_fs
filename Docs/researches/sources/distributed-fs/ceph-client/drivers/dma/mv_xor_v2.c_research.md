# sources/distributed-fs/ceph-client/drivers/dma/mv_xor_v2.c

## Purpose
`mv_xor_v2.c` is a Linux dmaengine provider for Marvell's version 2 XOR engine. It exposes one DMA channel with `DMA_MEMCPY`, `DMA_XOR`, and `DMA_INTERRUPT` capabilities, programs a fixed-size hardware descriptor queue, and completes async_tx requests from MSI-driven interrupts.

## Important APIs, Types, and Functions
- `struct mv_xor_v2_descriptor` is the 128-byte hardware descriptor. It stores operation mode, source/destination addresses, buffer size, XOR data-buffer address packing, and a software descriptor id.
- `struct mv_xor_v2_device` holds MMIO bases, clocks, the single `dma_chan`, descriptor queue DMA address, software descriptor array, free list, queue index, pending count, lock, MSI irq, and tasklet.
- `struct mv_xor_v2_sw_desc` wraps `dma_async_tx_descriptor` and a prepared hardware descriptor.
- `mv_xor_v2_prep_dma_memcpy()`, `mv_xor_v2_prep_dma_xor()`, and `mv_xor_v2_prep_dma_interrupt()` build software descriptors for dmaengine clients.
- `mv_xor_v2_tx_submit()` assigns cookies and copies the prepared descriptor into the coherent hardware descriptor ring.
- `mv_xor_v2_issue_pending()` notifies hardware how many descriptors were submitted since the last issue.
- `mv_xor_v2_interrupt_handler()` reads completion count and schedules `mv_xor_v2_tasklet()`, which completes cookies, invokes callbacks, runs dependencies, and returns descriptors to the free list.
- `mv_xor_v2_probe()` maps DMA/global register resources, enables clocks, allocates MSI, allocates coherent descriptor queue memory, initializes dmaengine callbacks, and registers the DMA device.

## Control Flow
Probe sets a 40-bit DMA mask, enables optional register and core clocks, allocates one MSI vector, initializes a 1024-entry coherent descriptor queue, initializes all software descriptors on `free_sw_desc`, registers one channel, configures interrupt message thresholds, and enables the descriptor queue. A client prepare call removes an acknowledged descriptor from the free list and fills the in-memory hardware descriptor. `tx_submit` assigns the cookie, copies the descriptor to `hw_desq_virt[hw_queue_idx]`, increments `npendings`, and wraps the ring index. `issue_pending` writes `npendings` to `DESQ_ADD`, then resets it to zero. Completion IRQs report pending completed descriptors; the tasklet reads the completion pointer and count, maps descriptor ids back to software descriptors, completes cookies, unmaps/invokes callbacks, returns descriptors to the free list, and deallocates completed descriptors from hardware.

## State and Persistence
All runtime state is in kernel memory and hardware registers. Persistent state is not written. Important volatile state includes `free_sw_desc`, `npendings`, `hw_queue_idx`, descriptor cookies, MSI message registers, descriptor queue base/size registers, and global bandwidth/cacheability settings. Suspend writes `DESQ_STOP`; resume restores descriptor size, interrupt thresholds, and descriptor queue configuration.

## Dependencies and Integration Points
The driver integrates with platform devices using `compatible = "marvell,xor-v2"`, the Linux dmaengine and async_tx APIs, MSI allocation through `platform_device_msi_init_and_alloc_irqs()`, clocks, coherent DMA memory, and memory-mapped IO resources. It uses `dma_cookie_*`, `dma_descriptor_unmap()`, `dmaengine_desc_get_callback_invoke()`, and `dma_run_dependencies()` for dmaengine semantics.

## Risks and Edge Cases
- The ring has a fixed 1024 descriptors and no explicit check that `npendings` plus in-flight descriptors cannot overrun hardware if clients submit faster than completions.
- Free descriptor selection depends on `async_tx_test_ack()`; unacknowledged descriptors can make prepare return `NULL` even if descriptors are physically present.
- `DESC_IOD` is set only when `DMA_PREP_INTERRUPT` is requested for memcpy/XOR; clients that depend on callbacks without this flag may not get per-request interrupt behavior.
- Address high parts are masked to 16 bits, matching the configured 40-bit mask; a future wider DMA mask would require descriptor format review.
- Error/status flags in completed hardware descriptors are not inspected, so data-movement faults may be reported as successful completions unless hardware reports them elsewhere.

## Test Signals
Useful checks are successful build under `CONFIG_MV_XOR_V2`, device-tree probe with two MMIO resources and MSI support, `dmatest` memcpy coverage, async_tx XOR/RAID-style tests with one to eight sources, suspend/resume smoke tests, and interrupt coalescing validation around `MV_XOR_V2_DONE_IMSG_THRD` and timer threshold behavior.
