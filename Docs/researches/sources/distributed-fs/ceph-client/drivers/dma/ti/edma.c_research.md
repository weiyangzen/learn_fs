# sources/distributed-fs/ceph-client/drivers/dma/ti/edma.c

## Purpose
This is the TI EDMA3 DMAengine driver. It supports hardware-triggered slave SG, cyclic audio-style transfers, software-triggered memcpy, interleaved memory transfers, PaRAM slot management, interrupt/error handling, DT translation, and legacy platform-data modes.

## Important APIs, Types, and Functions
Important types are `struct edma_cc`, `struct edma_chan`, `struct edma_desc`, `struct edma_pset`, `struct edmacc_param`, and `struct edma_tc`. PaRAM and channel helpers include `edma_alloc_slot()`, `edma_free_slot()`, `edma_link()`, `edma_set_chmap()`, `edma_start()`, `edma_stop()`, `edma_pause()`, `edma_resume()`, and `edma_execute()`. DMAengine operations include `edma_prep_slave_sg()`, `edma_prep_dma_memcpy()`, `edma_prep_dma_interleaved()`, `edma_prep_dma_cyclic()`, `edma_issue_pending()`, `edma_tx_status()`, `edma_terminate_all()`, and `edma_synchronize()`.

## Control Flow
Probe obtains DT or platform data, enables runtime PM, decodes EDMA hardware capabilities from `CCCFG`, allocates channel/slot bitmaps, marks reserved slots/channels, resets unused PaRAM entries, registers completion and error IRQs, allocates a dummy slot, configures TPTC queue priorities, initializes DMAengine channels, assigns default queues, and registers slave and optional memcpy DMA devices. OF xlate maps a DMA specifier to a channel and optional event queue. Prepared descriptors contain one or more PaRAM sets. `edma_execute()` writes a window of up to `MAX_NR_SG` sets to hardware, links them, starts or resumes the channel, and handles missed events. Completion IRQs call `edma_completion_handler()`, which either cycles callbacks, completes descriptors, or pauses at intermediate windows and programs the next window. Error IRQs clear missed event and queue errors and may retrigger safe in-flight transfers.

## State and Persistence
Controller state includes decoded channel/slot/queue counts, channel mask, slot-in-use bitmap, dummy slot, TPTC list, queue priority mapping, DMA devices, and per-channel active descriptor, slots, event queue, missed flag, and slave config. Descriptors persist residue, processed PaRAM count, current SG length, and cyclic/polled flags. Suspend disables interrupts for allocated channels; resume restores dummy slot, queue priorities, shadow-region access, interrupts, and channel-to-slot mappings.

## Dependencies and Integration Points
The driver depends on DMAengine, virt-dma, OF DMA, OF IRQ/address parsing, runtime PM, TI EDMA platform data, and optional TPTC child devices. It integrates with TI DMA crossbar through DT and Kconfig, with legacy `ti,edma3` bindings, newer `ti,edma3-tpcc` bindings, and platform filter-map based channel requests.

## Risks
PaRAM slot allocation is a scarce global resource, and long SG lists are chunked into windows of `MAX_NR_SG`, so missed event handling is essential. Residue computation polls hardware position and may hit a bounded busy-wait on slow devices. Cyclic mode rejects too many periods unless burst equals period length. Legacy memcpy mode without explicit memcpy channels is warned as risky. Error handling intentionally avoids recursion in null-slot cases, using a missed flag for later recovery. DT reservation masks, queue priorities, and channel-map presence must match hardware.

## Test Signals
Run DMAengine memcpy, slave SG, cyclic, and interleaved tests where hardware permits. Cover legacy and TPCC DT bindings, event queue selection, reserved slot/channel masks, `ti,edma-memcpy-channels`, xbar event map programming, TPTC phandles, completion IRQs, CC error IRQs, polled memcpy status, long SG windows exceeding `MAX_NR_SG`, suspend/resume with allocated idle channels, and invalid bus widths or bursts.
