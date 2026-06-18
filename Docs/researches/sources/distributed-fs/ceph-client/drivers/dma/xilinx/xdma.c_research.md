# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xdma.c

## Purpose
`xdma.c` is the AMD/Xilinx DMA/Bridge Subsystem driver for PCIe-attached XDMA platform devices. It exposes H2C and C2H slave DMA channels and supports normal SG transfers, cyclic transfers, interleaved transfers, repeat/load-EOT semantics, and exported user interrupt helpers.

## Important APIs, Types, and Functions
Core types are `struct xdma_device`, `struct xdma_chan`, `struct xdma_desc`, and `struct xdma_desc_block`. The driver uses `virt-dma` for dmaengine queueing and callback dispatch, `regmap` for MMIO access, and DMA pools for hardware descriptor blocks. Important functions include `xdma_alloc_channels`, `xdma_channel_init`, `xdma_alloc_desc`, `xdma_link_sg_desc_blocks`, `xdma_link_cyclic_desc_blocks`, `xdma_fill_descs`, `xdma_xfer_start`, `xdma_xfer_stop`, `xdma_prep_device_sg`, `xdma_prep_dma_cyclic`, `xdma_prep_interleaved_dma`, `xdma_issue_pending`, `xdma_terminate_all`, `xdma_synchronize`, `xdma_tx_status`, `xdma_channel_isr`, `xdma_irq_init/fini`, and exported `xdma_enable_user_irq`, `xdma_disable_user_irq`, and `xdma_get_user_irq`.

## Control Flow
Probe reads platform data, IRQ resource range, and MMIO resource, creates a regmap, detects available H2C and C2H channels by reading channel identifiers, initializes each channel, registers dmaengine capabilities, registers the dmaengine device, and assigns channel/user interrupt vectors. Channel allocation scans up to `pdata->max_dma_channels`, validates direction-specific identifier magic, initializes `virt_dma_chan`, and records register base and transfer direction.

Channel resources allocate a descriptor-block DMA pool on the parent PCI device. Prep paths allocate enough descriptor blocks, fill hardware descriptors with split chunks no larger than `XDMA_DESC_BLEN_MAX`, and then call `vchan_tx_prep`. SG prep uses `dma_slave_config` source or destination address as the device-side address and increments it by SG length. Cyclic prep limits period size and period count to one descriptor block. Interleaved prep creates descriptors for the template frame segments and records repeat/cyclic metadata.

`issue_pending` promotes submitted descriptors and starts the channel if possible. `xdma_xfer_start` clears run/stop, validates request direction, points hardware at the first uncompleted descriptor block, programs adjacent descriptor count, starts the engine, marks the channel busy, clears stop state, and reinitializes the last-interrupt completion. The ISR reads clear-on-read status, marks errors, reads completed descriptor count, and updates descriptor progress. Non-cyclic SG may restart at the next descriptor block when a hardware completion reports exactly the maximum block count. Cyclic and repeat interleaved transfers invoke `vchan_cyclic_callback`; finite transfers remove the descriptor from the issued list and complete the cookie.

## State and Persistence
Runtime state is volatile: per-channel busy/stop flags, completions, slave config, descriptor pools, virt-dma lists, descriptor progress counters, and hardware registers. Termination stops the engine, completes and terminates the active descriptor, drains all virt-dma lists into the terminated list, and synchronization waits for a final interrupt if hardware is still busy before killing callbacks.

## Dependencies and Integration Points
The driver depends on platform data from `linux/platform_data/amd_xdma.h`, exported AMD XDMA user IRQ API declarations, PCI parent discovery for descriptor pools, regmap MMIO, dmaengine, `virt-dma`, and constants from `xdma-regs.h`. It registers as platform driver id `xdma` and exports user IRQ control symbols for companion drivers.

## Risks and Review Signals
The code assumes platform data is present; probe dereferences `pdata` before checking for `NULL`. `xdma_issue_pending` ignores `xdma_xfer_start` errors. Interleaved repeat logic uses list inspection around the active node and should be stress-tested with `DMA_PREP_REPEAT` and `DMA_PREP_LOAD_EOT`. Error interrupts mark `desc->error` but do not obviously complete or terminate the descriptor immediately, so client-visible error progress should be verified. Test signals include channel detection for missing H2C/C2H channels, IRQ-vector packing with user IRQs, SG splitting across descriptor blocks, cyclic residue, terminate/synchronize while busy, missing PCI parent handling, and exported user IRQ boundary checks.
