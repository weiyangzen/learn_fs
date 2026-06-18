# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dpdma.c

## Purpose

This file implements the DMAengine driver for the Xilinx ZynqMP DisplayPort DMA (DPDMA) controller. It is a memory-to-device engine used by the display pipeline, supports six hardware channels, cyclic and interleaved transfers, grouped video-channel triggering, debugfs test hooks, and virtual-DMA based descriptor lifecycle management.

## Important APIs, Types, and Functions

`struct xilinx_dpdma_device` owns the DMAengine device, register base, shared IRQ, AXI clock, channel pointers, and extended-address flag. `struct xilinx_dpdma_chan` embeds `virt_dma_chan`, owns per-channel registers, running/first-frame/video-group flags, a stop wait queue, descriptor pool, error tasklet, and two hardware-facing descriptor pointers: `desc.pending` and `desc.active`. `struct xilinx_dpdma_hw_desc` mirrors the 256-byte-aligned hardware descriptor format, while `xilinx_dpdma_sw_desc` and `xilinx_dpdma_tx_desc` wrap hardware descriptors and virt-dma transactions.

The main DMAengine callbacks are `xilinx_dpdma_alloc_chan_resources()`, `xilinx_dpdma_free_chan_resources()`, `xilinx_dpdma_prep_dma_cyclic()`, `xilinx_dpdma_prep_interleaved_dma()`, `xilinx_dpdma_issue_pending()`, `xilinx_dpdma_config()`, pause/resume, terminate, and synchronize. `xilinx_dpdma_irq_handler()` services shared controller interrupts, while `xilinx_dpdma_chan_vsync_irq()`, `xilinx_dpdma_chan_done_irq()`, and `xilinx_dpdma_chan_err_task()` manage normal frame switching, callbacks, and error recovery.

## Control Flow

Probe allocates the device, gets the `axi_clk`, maps registers, initializes hardware by disabling interrupts and channels, requests the shared IRQ, sets DMAengine capabilities (`DMA_SLAVE`, `DMA_PRIVATE`, `DMA_CYCLIC`, `DMA_INTERLEAVE`, `DMA_REPEAT`, `DMA_LOAD_EOT`), initializes six virtual channels, enables the AXI clock, registers the DMAengine device and OF DMA controller, enables interrupts, and creates a debugfs testcase file.

Prep paths build cyclic or repeating interleaved descriptors. Cyclic preparation splits the buffer into periods, validates 256-byte alignment, links descriptors in a ring, sets complete interrupts and last-of-frame, and returns a virt-dma prepared transaction. Interleaved preparation validates MEM_TO_DEV, repeat/load-EOT flags, alignment, line size, and stride, then builds a single self-linked descriptor suitable for display refresh.

`xilinx_dpdma_issue_pending()` moves virt-dma issued descriptors into hardware scheduling via `xilinx_dpdma_chan_queue_transfer()`. Queueing enables the channel if stopped, removes the next virt descriptor, stamps descriptor IDs from the cookie, writes the descriptor start address, and triggers either the individual channel or a ready video group. VSYNC then verifies the pending descriptor ID has become active, completes the previous active descriptor, promotes pending to active, and queues another transfer. Descriptor-done IRQs invoke cyclic callbacks for the current active descriptor.

## State and Persistence

The driver stores transient state only. `running`, `first_frame`, `video_group`, `desc.pending`, and `desc.active` describe hardware scheduling. The virt-dma queue owns submitted-but-not-hardware-pending descriptors. Hardware descriptor pools are allocated per channel and freed with channel resources. Stop synchronization uses `wait_to_stop` and the NO_OSTAND interrupt or a polling fallback in error-task context. Debugfs state is global (`dpdma_debugfs`) and tracks one active test request and descriptor-done count.

## Dependencies and Integration Points

The driver depends on DMAengine, virt-dma, OF DMA, debugfs, wait queues, tasklets, DMA pools, and `dt-bindings/dma/xlnx-zynqmp-dpdma.h` channel IDs. It is tightly integrated with the DRM/display pipeline through `DMA_MEM_TO_DEV` transfers and the custom `struct xilinx_dpdma_peripheral_config` carried in `dma_slave_config.peripheral_config` to mark grouped video channels. OF translation exposes hardware channels by `dma_spec->args[0]`.

## Risks and Edge Cases

Correct operation depends on VSYNC ordering. If a retrigger races with VSYNC, the driver leaves the pending descriptor in place and retries on the next frame; changes in this area can cause frame drops or stale descriptors. The terminate path pauses channels and frees only descriptors that hardware cannot touch; pending and active descriptors are completed or freed later by synchronize. Video group stopping clears `video_group` flags while pausing running grouped channels, so mixed grouped and ungrouped usage needs care. Error handling disables channel interrupts, waits for outstanding transactions, disables the channel, may reschedule an errored active descriptor, and then re-enables interrupts; repeated errors can loop without higher-level throttling.

## Test Signals

Relevant tests include display pipeline bring-up with all six channels, cyclic callback cadence, interleaved repeat/load-EOT operation, grouped RGB/video-channel triggering, terminate/synchronize behavior while frames are outstanding, NO_OSTAND timeout paths, and injected descriptor/AXI/global error interrupts. The debugfs `testcase` file exposes a descriptor-done IRQ count test for a selected channel when debugfs is enabled.
