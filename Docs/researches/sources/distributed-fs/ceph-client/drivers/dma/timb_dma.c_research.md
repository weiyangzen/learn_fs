# sources/distributed-fs/ceph-client/drivers/dma/timb_dma.c

## Purpose
`timb_dma.c` is a Linux dmaengine platform driver for the Timberdale FPGA DMA engine. It exposes private slave DMA channels, with even/odd channel pairing used to distinguish RX (`DMA_DEV_TO_MEM`) and TX (`DMA_MEM_TO_DEV`) instances. It relies on board-supplied `struct timb_dma_platform_data` rather than device tree discovery.

## Important APIs, Types, and Functions
The central types are `struct timb_dma`, `struct timb_dma_chan`, and `struct timb_dma_desc`. `timb_dma` embeds a `struct dma_device`, the global MMIO base, one tasklet, and a flexible channel array. Each channel owns an MMIO subregion, `active_list`, `queue`, `free_list`, direction, bytes-per-line, descriptor pool sizing, and an `ongoing` flag. Each descriptor contains a dmaengine `txd`, a DMA-mapped byte descriptor list, its length, and an interrupt flag.

Key dmaengine hooks are `td_alloc_chan_resources`, `td_free_chan_resources`, `td_prep_slave_sg`, `td_tx_submit`, `td_issue_pending`, `td_tx_status`, and `td_terminate_all`. Hardware programming is concentrated in `td_fill_desc`, `__td_start_dma`, `__td_finish`, `__td_start_next`, `__td_dma_done_ack`, `td_irq`, and `td_tasklet`.

## Control Flow
Probe validates platform data, reserves and maps the MMIO resource, programs 32-bit addressing in `TIMBDMA_ACR`, clears and disables interrupts, installs a shared IRQ, initializes each configured channel, and registers the dmaengine device. Per-channel setup computes RX/TX register base from channel id and platform RX flag, initializes lists and locks, and stores descriptor count, descriptor element count, direction, and video-specific bytes-per-line.

`td_alloc_chan_resources` preallocates a platform-data-controlled number of `timb_dma_desc` objects. Each descriptor owns a software descriptor byte array that is mapped once with `dma_map_single`. `td_prep_slave_sg` checks the requested direction, takes an ACKed descriptor from `free_list`, fills one 8-byte hardware descriptor per SG element, rejects unaligned or too-large SG lengths, syncs the list for device access, and returns the dmaengine descriptor. `td_tx_submit` assigns a cookie and either starts immediately when no active descriptor exists or queues the descriptor. The engine is started by writing the descriptor list physical address to RX/TX descriptor low registers; RX additionally writes bytes-per-line and enables RX.

Completion is interrupt and tasklet driven. `td_irq` reads `TIMBDMA_IPR`, disables all Timberdale interrupts, and schedules `td_tasklet`. The tasklet filters `TIMBDMA_ISR` through `__td_ier_mask`, acknowledges completed channels, calls `__td_finish`, starts the next queued descriptor if present, and rewrites `TIMBDMA_IER` for currently interrupting transfers. `td_issue_pending` can also poll/ack completion and start the next queued descriptor. `td_terminate_all` moves queued descriptors to free and calls `__td_finish` on the active descriptor.

## State and Persistence
All runtime state is in memory and hardware registers. The driver does not persist anything across unload. Channel list state is protected by `td_chan->lock`; tasklet paths use the same lock. Descriptor buffers are mapped for DMA for the lifetime of channel resources and freed in `td_free_chan_resources`.

## Dependencies and Integration Points
The driver depends on dmaengine core helpers, Linux DMA mapping, platform resources, interrupts, MMIO accessors, and `linux/timb_dma.h` platform data. It registers a platform driver named `timb-dma` and uses `DMA_SLAVE` plus `DMA_PRIVATE` capabilities.

## Risks and Review Signals
The driver assumes valid platform data and fixed RX/TX channel parity. TX stop is explicitly unsupported in the commented-out branch of `__td_finish`, so termination may not halt TX hardware cleanly. `td_prep_slave_sg` checks `desc_usage > desc_list_len` before appending, which deserves boundary review because equality before an append can still overflow by one descriptor. Error paths after descriptor allocation must return descriptors to the free list; the no-space path currently returns `NULL` without putting the descriptor back. Tests should exercise SG length alignment, descriptor-list capacity, RX/TX direction mismatch, IRQ completion with queued follow-on transfers, terminate while active, and module probe/remove cleanup.
