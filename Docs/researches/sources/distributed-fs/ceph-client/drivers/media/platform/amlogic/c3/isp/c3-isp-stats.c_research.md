
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-stats.c

## Purpose

`c3-isp-stats.c` implements the ISP metadata-capture video node for AF, AWB, and AE statistics. It manages DMA-contiguous buffers, programs hardware DMA target addresses and sizes, returns completed stats buffers on frame-end IRQs, and exposes a fixed `V4L2_META_FMT_C3ISP_STATS` capture interface.

## Important APIs, Types, And Functions

`c3_isp_stats_cfg_dmawr_addr()` lays out one stats buffer as AWB first, AE second, and AF third, then writes `VIU_DMAWR_BADDR0/1/2`. `c3_isp_stats_pre_cfg()` selects the newer AF stats mode, sets AE luma filter mode, programs AF/AWB/AE DMA sizes in 16-byte units, and primes the first queued buffer.

VB2 operations validate buffer size, derive DMA address with `vb2_dma_contig_plane_dma_addr()`, queue buffers under `buff_lock`, and return active/pending buffers with error on stream stop. Public entry points are `c3_isp_stats_register()`, `c3_isp_stats_unregister()`, `c3_isp_stats_pre_cfg()`, and `c3_isp_stats_isr()`.

## Control Flow

Userspace allocates and queues metadata-capture buffers. On stream pre-configuration, the driver programs stats module modes and sizes, then removes the first pending buffer and points the hardware DMA engine at its contiguous DMA memory. On each frame-end IRQ, `c3_isp_stats_isr()` completes the current buffer with sequence, timestamp, and `V4L2_FIELD_NONE`, then immediately dequeues and programs the next pending buffer if available.

Registration builds a video node named `c3-isp-stats` with `V4L2_CAP_META_CAPTURE | V4L2_CAP_STREAMING`, VB2 DMA-contig memory operations, `V4L2_BUF_TYPE_META_CAPTURE`, and `min_queued_buffers = 2`.

## State And Persistence

`struct c3_isp_stats` holds the fixed metadata format, VB2 queue, pending list, spinlock, current buffer pointer, and mutex. Each `struct c3_isp_stats_buffer` stores a DMA address captured during buffer initialization. There is no persistent storage; statistics live in user-provided DMA buffers and register state is reprogrammed each stream.

## Dependencies And Integration Points

This module depends on DMA-contiguous VB2 memory, C3 ISP stats ABI structures in `c3-isp-config.h`, register definitions in `c3-isp-regs.h`, the core IRQ path in `c3-isp-dev.c`, and media links from the ISP core stats source. It is synchronized with resizer stream start through `c3_isp_stats_pre_cfg()`.

## Risks

The DMA layout assumes `struct c3_isp_stats_info` is large enough and ordered compatibly with AWB, AE, then AF structures. `c3_isp_stats_cfg_dmawr_addr()` programs addresses shifted by register macros, so buffer alignment must satisfy hardware requirements. If no next pending buffer exists at frame end, stats DMA may continue pointing at the completed buffer until another pre-config path updates it. IRQ completion runs under a spinlock and calls VB2 completion, so lock ordering must remain compatible with VB2 expectations.

## Test Signals

V4L2 tests should verify fixed metadata format, queue minimums, buffer-size rejection, and streamoff error-return of active and pending buffers. Hardware tests should queue several buffers, start streaming, and confirm each frame returns one stats buffer with monotonically increasing sequence and plausible AWB/AE/AF regions. Register dumps should confirm DMA sizes match ABI structure sizes divided by 16 bytes and base addresses are correctly aligned.
