<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c

## Purpose
DMAEngine driver for Marvell MMP peripheral DMA controllers, including legacy 32-bit PDMA and Spacemit K1 64-bit/LPAE PDMA variants. It supports memcpy, slave SG, and cyclic DMA.

## Important APIs, Types, And Functions
`mmp_pdma_device` owns hardware, physical channels, operation table, and DMAEngine device. `mmp_pdma_chan` is a software channel with pending/running lists, descriptor pool, physical-channel binding, request-line mapping, and cyclic state. `mmp_pdma_phy` represents a hardware channel. `mmp_pdma_ops` abstracts 32-bit versus 64-bit register/descriptor address handling and run bits. Key functions include `lookup_phy`, `start_pending_queue`, `mmp_pdma_tx_submit`, descriptor prep for memcpy/slave SG/cyclic, `mmp_pdma_residue`, IRQ handlers, and `dma_do_tasklet` completion cleanup.

## Control Flow
Probe maps registers, enables optional clock/reset, selects ops from DT compatible, determines channel count, requests either one shared IRQ or per-channel IRQs, initializes physical and software channels, sets DMAEngine capabilities and masks, registers the device, and registers OF xlate. Channel resources create a DMA pool and reset state. Prep functions build linked hardware descriptors in the pool, assign source/destination and `DCMD`, link descriptors through DDADR, mark final descriptors with STOP/ENDIRQEN, and for cyclic link the last descriptor back to the first. Submit assigns cookies to all child descriptors and moves them to the pending list. Issue-pending calls `start_pending_queue`, which allocates a free physical channel if needed, maps request lines, writes the first descriptor address, and starts hardware. IRQ clears DCSR/DINT, schedules the channel tasklet, and the tasklet completes cookies through ENDIRQEN descriptors, invokes callbacks, frees descriptor entries, marks idle, and starts queued work.

## State And Persistence
State includes DMA pool descriptors, pending/running descriptor lists, physical-channel ownership, request-line DRCMR mappings, DALGN byte-align bits, cyclic first descriptor, channel idle flag, slave config, and hardware registers. State is runtime-only and tied to channel resource allocation.

## Dependencies And Integration Points
Depends on DMAEngine core helpers, platform data or device tree, OF DMA xlate, DMA pools, optional clocks/resets, platform IRQs, and compatible data `marvell,pdma-1.0` or `spacemit,k1-pdma`. It exposes private slave, memcpy, and cyclic capabilities and sets DMA masks according to hardware address width.

## Risks And Edge Cases
In `mmp_pdma_prep_slave_sg`, the loop uses `sg_dma_len(sgl)` instead of `sg_dma_len(sg)`, which can mis-size every entry after the first. 64-bit descriptors write low/high fields, but some slave paths assign `new->desc.dsadr` or `dtadr` directly for device addresses, bypassing ops high-word helpers. `mmp_pdma_residue` depends on current source/destination register values falling inside descriptor bounds and has special cyclic behavior. Terminate disables hardware and frees lists without callback completion. Physical-channel priority/ownership and request-line mapping are shared across channels and require `phy_lock`/`desc_lock` ordering discipline.

## Test Signals
Run dmatest memcpy, slave SG with multi-entry SG lists, cyclic audio-style transfers, 64-bit DMA addresses on Spacemit K1, shared and per-channel IRQ configurations, tx_status residue polling, terminate while active, and OF xlate request-line mapping. A targeted test should catch the `sg_dma_len(sgl)` multi-SG length issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c -->
