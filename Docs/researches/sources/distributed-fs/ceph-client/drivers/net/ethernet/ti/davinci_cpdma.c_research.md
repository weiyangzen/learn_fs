# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/davinci_cpdma.c

## Purpose
`davinci_cpdma.c` implements the TI CPDMA/CPPI 3.0 descriptor engine used by DaVinci EMAC and related Ethernet blocks. It abstracts descriptor memory allocation, TX/RX channel state, DMA mapping, queue submission, completion processing, channel teardown, interrupt masking, descriptor weighting, and TX rate limiting.

## Important APIs, Types, and Functions
Important internal types are `struct cpdma_desc`, `struct cpdma_desc_pool`, `struct cpdma_ctlr`, and `struct cpdma_chan`. The exported controller API is `cpdma_ctlr_create()`, `cpdma_ctlr_start()`, `cpdma_ctlr_stop()`, `cpdma_ctlr_destroy()`, `cpdma_ctlr_int_ctrl()`, `cpdma_ctlr_eoi()`, and channel-state readers. The exported channel API includes `cpdma_chan_create()`, `cpdma_chan_destroy()`, `cpdma_chan_start()`, `cpdma_chan_stop()`, submit variants for mapped/unmapped and idle/active paths, `cpdma_chan_process()`, `cpdma_check_free_tx_desc()`, stats, weight, and TX rate helpers.

## Control Flow and State
`cpdma_ctlr_create()` copies parameters, builds a descriptor pool backed either by internal SRAM/ioremap or coherent DMA memory, and initially splits descriptors equally between RX and TX. `cpdma_ctlr_start()` optionally soft-resets hardware, clears HDP/CP registers, disables stale interrupts, enables TX/RX control, activates existing channels, and programs shapers. `cpdma_chan_submit_si()` enforces per-channel descriptor limits, allocates one descriptor, maps or syncs the packet buffer, fills hardware and software descriptor fields, appends it to the channel chain, and writes RX free count when needed. `cpdma_chan_process()` pops completed descriptors up to a quota, checks ownership, acknowledges completion, handles EOQ requeue, unmaps/syncs data, frees the descriptor, and calls the client handler outside the channel lock. `cpdma_chan_stop()` enters teardown, disables channel interrupts, writes teardown, waits for teardown completion, drains completed descriptors, then frees any remaining descriptors with `-ENOSYS`.

## Dependencies and Integration Points
This code depends on DMA mapping APIs, `gen_pool`, MMIO accessors, CPDMA register offsets, and client callbacks supplied through `cpdma_handler_fn`. DaVinci EMAC consumes it for packet TX/RX, NAPI polling, and TX timeout recovery. Extended-register operations are gated by `has_ext_regs`; callers on older hardware must tolerate `-ENOTSUPP`.

## Risks and Test Signals
The most sensitive paths are descriptor pool sizing, teardown waits, DMA sync/unmap correctness for externally mapped buffers, EOQ misqueue recovery, and TX rate/weight configuration under nested controller/channel locks. `cpdma_control_get()` and `_set()` index `controls[control]` before range validation, so invalid enum values are a latent bounds risk if externally reachable. Test signals include RX/TX under descriptor exhaustion, active/idle submit behavior, teardown during traffic, host-error recovery, interrupt mask toggling, SRAM versus coherent descriptor pools, weighted descriptor split failures, and BQL/queue wake behavior in EMAC.
