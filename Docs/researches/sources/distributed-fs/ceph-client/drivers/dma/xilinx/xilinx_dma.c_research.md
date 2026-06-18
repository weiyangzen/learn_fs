# sources/distributed-fs/ceph-client/drivers/dma/xilinx/xilinx_dma.c

## Purpose

This file is the Linux DMAengine platform driver for several Xilinx soft DMA IP blocks: AXI DMA, AXI CDMA, AXI VDMA, and AXI MCDMA. It binds OF compatibles `xlnx,axi-dma-1.00.a`, `xlnx,axi-cdma-1.00.a`, `xlnx,axi-vdma-1.00.a`, and `xlnx,axi-mcdma-1.00.a`, exposes DMAengine channels, translates DT DMA phandles, allocates hardware descriptors, and drives transfers through memory-mapped control/status registers.

## Important APIs, Types, and Functions

Core state is split across `struct xilinx_dma_device`, which owns the mapped register base, clocks, DMAengine `dma_device`, channel array, address width, and IP-specific config, and `struct xilinx_dma_chan`, which owns per-channel register offsets, descriptor queues, DMA direction, IRQ, tasklet, state flags, transfer callbacks, and VDMA configuration. Hardware descriptor layouts are represented by `xilinx_vdma_desc_hw`, `xilinx_axidma_desc_hw`, `xilinx_aximcdma_desc_hw`, and `xilinx_cdma_desc_hw`, wrapped in per-segment structures that carry list nodes and DMA addresses.

The DMAengine entry points are wired in `xilinx_dma_probe()`: `device_alloc_chan_resources`, `device_free_chan_resources`, `device_terminate_all`, `device_synchronize`, `device_tx_status`, `device_issue_pending`, and `device_config` are shared, while prep callbacks differ by IP. AXI DMA supports `device_prep_slave_sg`, `device_prep_peripheral_dma_vec`, and `device_prep_dma_cyclic`; CDMA supports `device_prep_dma_memcpy`; VDMA supports `device_prep_interleaved_dma`; MCDMA supports `xilinx_mcdma_prep_slave_sg()`. The VDMA runtime control API `xilinx_vdma_channel_set_config()` is exported for consumers that need parking, genlock, frame count, delay, fsync source, reset, or vertical flip control.

Transfer control is abstracted by per-channel function pointers. `xilinx_vdma_start_transfer()`, `xilinx_dma_start_transfer()`, `xilinx_cdma_start_transfer()`, and `xilinx_mcdma_start_transfer()` each program the descriptor registers required by their IP, set interrupt coalescing/delay fields, run the channel, and move queued descriptors to `active_list`. Stop behavior uses either `xilinx_dma_stop_transfer()` or CDMA's idle wait in `xilinx_cdma_stop_transfer()`.

## Control Flow

Probe selects an IP config from the OF match data, enables the correct clock set, maps registers, reads DT properties such as address width, SG length width, VDMA frame stores, flush-on-fsync mode, and AXI-stream metadata support, configures the DMA mask, fills DMAengine capability bits, probes child channel nodes, registers the DMAengine device, and registers an OF DMA controller translator. Channel probing reads direction-specific compatible strings, data width, DRE presence, IRQ delay, genlock, vertical flip support, and IRQ lines, then chooses start/stop callbacks and resets the channel.

Client flow follows normal DMAengine ordering. Prep functions allocate a software transaction descriptor, fill one or more hardware segments, and return `dma_async_tx_descriptor`. `xilinx_dma_tx_submit()` assigns a cookie, chains the descriptor into `pending_list`, and marks cyclic state when needed. `xilinx_dma_issue_pending()` calls the selected start routine under the channel spinlock. Interrupt handlers acknowledge status, flag unrecoverable errors, complete active descriptors into `done_list`, restart pending work when possible, and schedule a tasklet. The tasklet calls `xilinx_dma_chan_desc_cleanup()`, invokes callbacks outside the spinlock, runs dependencies, and frees or recycles descriptor storage.

## State and Persistence

The driver keeps all state in RAM and hardware registers; there is no on-disk persistence. Queue state is held in `pending_list`, `active_list`, `done_list`, and `free_seg_list`, protected by `chan->lock`. AXI DMA and MCDMA preallocate coherent descriptor rings and recycle segments through `free_seg_list`; VDMA and CDMA allocate descriptors from DMA pools. Flags such as `idle`, `err`, `cyclic`, `terminating`, `desc_pendingcount`, and `desc_submitcount` model hardware progress and cleanup decisions. Register state is restored through reset/start paths rather than saved persistently.

## Dependencies and Integration Points

The file depends on DMAengine core APIs, OF DMA registration, Linux platform driver probing, IRQ handling, tasklets, DMA pools/coherent allocation, clock framework, and 64-bit MMIO helpers. DT bindings are critical: channel compatibles decide direction and register offsets, `xlnx,datawidth` and `xlnx,include-dre` determine alignment constraints, `xlnx,addrwidth` controls DMA mask and 64-bit descriptor programming, and VDMA-specific `xlnx,num-fstores` is mandatory. The driver integrates with async_tx callbacks, DMA metadata support through descriptor APP words when `xlnx,axistream-connected` is set, and external VDMA users via `xilinx_vdma_channel_set_config()`.

## Risks and Edge Cases

Descriptor ownership is sensitive: AXI DMA/MCDMA recycle preallocated descriptors while VDMA/CDMA free pool allocations, so wrong IP type checks would corrupt memory. Several paths rely on hardware status bits and timeout loops; a stuck reset or halt leaves `chan->err` set and may require system-level recovery. Cyclic AXI DMA has special handling that moves done descriptors back to active and uses a synthetic tail descriptor, which is a high-risk area for regressions. MCDMA interrupt demultiplexing uses SER masks and channel IDs, so off-by-one handling or DT channel numbering errors can route completions to the wrong channel. VDMA has additional risks around frame store counts, parking, genlock, vertical flip, and flush-on-fsync recoverable error masking.

## Test Signals

Useful validation signals include successful probe messages for each IP type, DT probe failures for missing mandatory properties, DMAengine memcpy tests for CDMA, cyclic audio-style tests for AXI DMA, VDMA interleaved frame transfer tests, MCDMA multichannel SG tests, IRQ completion counts, callback residue values, and forced error/status-bit tests that exercise reset and termination. Static checks should cover lock ordering around callbacks, descriptor list transitions, DMA mask/address width handling, and cleanup paths after partial probe failure.
