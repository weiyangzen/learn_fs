# sources/distributed-fs/ceph-client/drivers/dma/uniphier-mdmac.c

## Purpose
`uniphier-mdmac.c` is a slave-only dmaengine driver for the Socionext UniPhier MIO DMAC. It uses the shared `virt-dma` helper to handle cookies, descriptor queues, callbacks, and freeing while the driver programs one SG segment at a time into MDMAC channel registers.

## Important APIs, Types, and Functions
Driver-specific state is in `struct uniphier_mdmac_device`, `struct uniphier_mdmac_chan`, and `struct uniphier_mdmac_desc`. A descriptor stores the original SG list, SG length, current SG index, and transfer direction. Important routines are `uniphier_mdmac_next_desc`, `uniphier_mdmac_handle`, `uniphier_mdmac_start`, `uniphier_mdmac_abort`, `uniphier_mdmac_interrupt`, `uniphier_mdmac_prep_slave_sg`, `uniphier_mdmac_terminate_all`, `uniphier_mdmac_tx_status`, `uniphier_mdmac_issue_pending`, and probe/remove channel setup.

## Control Flow
Probe counts IRQs to determine channel count, sets a 32-bit DMA mask, maps registers, enables the clock, initializes the dmaengine capability mask, creates each channel with a channel-specific IRQ, registers the dmaengine device, and registers an OF DMA controller using `of_dma_xlate_by_chan_id`.

Preparation validates a slave direction, allocates a small descriptor with `GFP_NOWAIT`, stores the SG list and direction, and calls `vchan_tx_prep`. `issue_pending` moves submitted descriptors to the issued list with `vchan_issue_pending` and starts the hardware if the channel has no current descriptor. Starting removes the next issued descriptor, stores it in `mc->md`, and calls `uniphier_mdmac_handle`. `handle` chooses fixed or incrementing source/destination modes based on direction, writes source/destination addresses, transfer size, clears and enables the DONE interrupt, and starts the channel through the common command register.

The IRQ handler locks the virt-dma channel, reads detected interrupts, ignores shared-line interrupts for other channels, clears latched bits, and checks `mc->md`. A `NULL` current descriptor means an abort is in progress. Otherwise it advances `sg_cur`, completes the descriptor with `vchan_cookie_complete` at the end of the SG list, pulls the next descriptor if available, and programs the next segment.

## State and Persistence
The only durable state is hardware register state during runtime. Queue state is owned by `virt_dma_chan`; the active descriptor is tracked in `mc->md`. Termination marks the active descriptor terminated, clears `mc->md`, polls for abort acknowledgment, gathers all queued descriptors, unlocks, then frees them through `vchan_dma_desc_free_list`.

## Dependencies and Integration Points
The driver depends on clk, OF DMA, platform IRQ/resource APIs, `readl_poll_timeout`, dmaengine, and `virt-dma`. It advertises `DMA_PRIVATE`, supports `DMA_MEM_TO_DEV` and `DMA_DEV_TO_MEM`, and reports segment-level residue granularity.

## Risks and Review Signals
Residue accounting reads `CH_SIZE` for the active segment and then adds queued SG lengths from `sg_cur`, so tests should validate whether the hardware register reports remaining bytes rather than programmed bytes. The code does not consume `dma_slave_config` addresses; the register side is represented by address zero and fixed mode, so this is tightly coupled to MIO DMAC hardware semantics. Remove handles terminate failures by returning early to avoid freeing live hardware state, which intentionally leaks resources in a severe failure. Test signals include shared IRQ filtering, abort polling timeout, residue for active and queued SG elements, clock disable on probe/remove error paths, and OF channel translation.
