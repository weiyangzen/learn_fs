<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c

## Purpose

`tusb6010_omap.c` implements the MUSB DMA-controller adapter for TUSB6010 on OMAP systems. It maps MUSB endpoint DMA requests to Linux DMAEngine channels named `dmareq0` through `dmareq4`, programs TUSB endpoint transfer-size registers, and handles TUSB-specific errata around DMA alignment, transfer-size corruption, shared request lines, and short-packet completion.

## Important APIs, Types, and Functions

`struct tusb_dma_data` binds a TUSB DMA request number to a DMAEngine channel. `struct tusb_omap_dma_ch` is per-active-MUSB-DMA-channel state: endpoint, direction, DMA request data, address, packet size, transfer length, and completed length. `struct tusb_omap_dma` owns the MUSB `dma_controller`, TUSB base, request pool, and multichannel flag.

The MUSB-facing callbacks are `tusb_omap_dma_allocate()`, `tusb_omap_dma_release()`, `tusb_omap_dma_program()`, `tusb_omap_dma_abort()`, `tusb_dma_controller_create()`, and `tusb_dma_controller_destroy()`. Internal helpers manage request mapping: `tusb_omap_use_shared_dmareq()`, `tusb_omap_free_shared_dmareq()`, `tusb_omap_dma_allocate_dmareq()`, `tusb_omap_dma_free_dmareq()`, and `tusb_omap_dma_cb()`.

## Control Flow

Controller creation masks TUSB DMA interrupts, clears endpoint mapping, configures burst/request timing, allocates up to five generic `struct dma_channel` wrappers, requests one DMAEngine channel in single-channel mode or all request channels in multichannel mode, and returns a populated `dma_controller`. Channel allocation rejects endpoint zero, chooses an unused wrapper, records endpoint/direction, and either maps a dedicated request line for TUSB rev 3+ or uses request 0 dynamically.

Programming rejects odd addresses, transfers smaller than 32 bytes, transfers larger than one packet, and addresses that would use the corrupt async DMA path. It also refuses if the previous endpoint transfer-size register is nonzero. On success it maps CPU memory, configures DMAEngine for sync or async FIFO physical address and bus width, prepares a single slave transfer, programs MUSB TX/RX CSR DMA bits, writes packet-size and transfer-size registers, and issues pending DMA. Callback computes actual length from TUSB remaining count, works around corrupted remaining values, copies final 1-31 bytes by PIO, frees shared DMA request state, marks the channel free, calls `musb_dma_completion()`, and manually terminates short TX packets with `TXPKTRDY`.

## State and Persistence Behavior

State lives in allocated controller/channel objects and in static `dma_channel_pool[MAX_DMAREQ]`, making the implementation effectively singleton-oriented. Hardware state persists in `TUSB_DMA_EP_MAP`, endpoint transfer-size registers, DMA request configuration, and MUSB endpoint CSR bits until cleared or overwritten.

## Dependencies and Integration Points

The file depends on MUSB DMA controller APIs, DMAEngine slave configuration, TUSB register definitions, TUSB MUSB glue-provided endpoint FIFO addresses, and platform DMA channel naming. It is selected through `tusb_ops` in `tusb6010.c`.

## Risks and Test Signals

Risk areas include singleton static channel pool, partial cleanup paths, DMA map return values not checked, use of `phys_to_virt()` on DMA addresses, shared request release mismatch, and several hardware errata assumptions. Tests should exercise endpoint allocation/release, rev 2 shared request use, rev 3 multichannel use, aligned and unaligned buffers, rejected small/large transfers, short TX packet termination, RX tail PIO copy, abort while busy, DMAEngine request failures, and controller destroy after partial allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c -->
