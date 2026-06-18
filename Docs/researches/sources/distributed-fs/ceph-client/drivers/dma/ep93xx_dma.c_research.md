# sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c

### Purpose
`ep93xx_dma.c` is the DMAengine driver for Cirrus Logic EP93xx DMA controllers. It supports memory-to-peripheral M2P channels for fixed peripheral request lines, memory-to-memory M2M channels for memcpy and selected peripheral modes, scatter-gather through software descriptor chaining, and cyclic audio-style transfers.

### Important APIs, Types, And Functions
Core types are `struct ep93xx_dma_desc`, `struct ep93xx_dma_chan_cfg`, `struct ep93xx_dma_chan`, and `struct ep93xx_dma_engine`. Hardware abstraction callbacks in `struct ep93xx_dma_engine` split M2P and M2M operations: `m2p_hw_setup()`, `m2p_hw_submit()`, `m2p_hw_interrupt()`, `m2p_hw_synchronize()`, `m2p_hw_shutdown()`, `m2m_hw_setup()`, `m2m_hw_submit()`, `m2m_hw_interrupt()`, and `m2m_hw_shutdown()`. DMAengine entry points include `ep93xx_dma_alloc_chan_resources()`, `ep93xx_dma_free_chan_resources()`, `ep93xx_dma_prep_dma_memcpy()`, `ep93xx_dma_prep_slave_sg()`, `ep93xx_dma_prep_dma_cyclic()`, `ep93xx_dma_tx_submit()`, `ep93xx_dma_issue_pending()`, `ep93xx_dma_terminate_all()`, `ep93xx_dma_synchronize()`, and `ep93xx_dma_tx_status()`.

### Control Flow, State, And Persistence
Probe creates either an M2P engine with ten channels or an M2M engine with two channels, maps each per-channel register region, obtains per-channel IRQs and clocks, initializes descriptor queues, registers the DMAengine device, and registers OF DMA translation callbacks. Channel resource allocation enables the clock, requests the IRQ, initializes hardware, and preallocates up to 32 software descriptors. Prepared transfers split data into hardware-sized pieces, chain them via `tx_list`, and mark the first descriptor with a pending cookie. Submit either starts immediately when the active list is empty or queues the chain. Interrupts advance the active list according to the controller's double-buffer state, then tasklets complete cookies, invoke callbacks, recycle descriptors, and start queued work.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DMAengine, OF DMA, platform resources, per-channel clocks, IRQs, scatterlist DMA mappings, and legacy EP93xx channel numbering. M2P channels have fixed directions based on channel parity, while M2M channels accept runtime slave configuration for SSP/IDE or memcpy. Risks include double-buffer state-machine quirks, M2M DONE interrupts that can arrive before the channel is actually idle, cyclic descriptors that intentionally never complete cookies, maximum segment limits of `0xffff`, `BUG_ON()` assumptions during resource release, and untested IDE mode parameters. Test signals include M2P TX/RX direction filtering, M2M memcpy, SSP slave transfers with width config, cyclic callbacks, terminate/synchronize behavior, descriptor exhaustion, OF xlate rejection paths, and handling of error or spurious interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ep93xx_dma.c -->
