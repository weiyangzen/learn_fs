## sources/distributed-fs/ceph-client/drivers/dma/dw-axi-dmac/dw-axi-dmac-platform.c

Purpose: Platform DMAengine provider for Synopsys DesignWare AXI DMA controllers, including SoC quirks for APB handshake registers, reset controls, alternate CFG2 layout, and channel-number phandle semantics.

Important APIs/types/functions: registers `struct platform_driver dw_driver`; implements DMAengine callbacks `device_alloc_chan_resources`, `device_free_chan_resources`, `device_prep_dma_memcpy`, `device_prep_slave_sg`, `device_prep_dma_cyclic`, `device_issue_pending`, `device_tx_status`, `device_config`, `device_pause`, `device_resume`, `device_terminate_all`, and `device_synchronize`. Core helpers include `dw_probe()`, `parse_device_properties()`, `axi_req_irqs()`, `dw_axi_dma_of_xlate()`, `axi_chan_block_xfer_start()`, `dw_axi_dma_set_hw_desc()`, and `dw_axi_dma_interrupt()`.

Control flow: probe maps registers, applies compatible flags, enables clocks/resets, parses device properties, allocates channel structures, requests IRQs, initializes virt-dma channels, registers the DMAengine device, and registers the OF DMA controller. Transfer prep creates DMA-pool LLIs, configures SAR/DAR/control fields, links descriptors, and queues via virt-dma. `issue_pending` starts the first queued descriptor by programming channel CFG/LLP/interrupt registers and enabling the channel. IRQ handling clears channel status, completes descriptors or cyclic periods, and restarts queued work.

State and persistence: `struct axi_dma_chan` stores current slave config, direction, cyclic flag, pause state, allocated descriptor count, and virt-dma state. `struct dw_axi_dma_hcfg` stores probed hardware shape. State is volatile and register-backed only; runtime PM gates clocks.

Dependencies and integration: integrates with platform resources, device properties, OF DMA lookup, runtime PM, reset/clock APIs, DMA pools, DMA mapping limits, and `../virt-dma.h`.

Risks and test signals: risks include block-size/alignment rejection, channel enable polling assumptions, cyclic LLP accounting, shared IRQ masking, APB handshake locking, and register layout quirks. Test with dmatest memcpy/slave/cyclic clients, OF phandle lookup, runtime suspend/resume, pause/resume/terminate, and SoC compatibles using CFG2/APB/reset variants.
