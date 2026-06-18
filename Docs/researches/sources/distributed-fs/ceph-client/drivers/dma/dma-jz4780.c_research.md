# sources/distributed-fs/ceph-client/drivers/dma/dma-jz4780.c

Purpose: DMAengine driver for Ingenic JZ47xx/X1000/X1830 DMA controllers. It supports memcpy, slave SG, and cyclic transfers using hardware descriptor blocks and `virt-dma`.

Important APIs/types/functions: `struct jz4780_dma_dev` contains DMAengine device, channel/control MMIO bases, clock, IRQ, SoC data, reserved-channel bitmap, and flexible channels. `struct jz4780_dma_chan` stores virt channel, descriptor pool, transfer types, slave config, active descriptor, and current descriptor index. `struct jz4780_dma_desc` owns hardware descriptor block, count, type, transfer type, and status. Core functions include prep callbacks, `jz4780_dma_begin`, `jz4780_dma_irq_handler`, `jz4780_of_dma_xlate`, `jz4780_dma_probe`, and remove/init/exit.

Control flow: probe validates OF data, maps channel/control registers, enables clock, reads reserved channels, configures DMAengine callbacks/caps, enables controller bits, initializes virt channels, applies a JZ4760 channel-enable workaround, requests IRQ, registers DMAengine, and registers OF DMA translation. Prep paths allocate a page-sized descriptor block from a DMA pool, compute transfer width/shift, fill hardware descriptors for SG/cyclic/memcpy, and queue via `vchan_tx_prep`. Issue-pending starts the next descriptor by programming DRT/DTC/DDA and enabling the channel. IRQ scans pending channels, reads/clears DCS, handles address/halt errors, completes descriptors or cycles to the next period, and restarts queued work.

State and persistence: State is per-channel active descriptor, descriptor pool, current hardware descriptor, slave config, transfer type, and controller registers. SoC differences are represented in static match data. No persistent storage.

Dependencies/integration: DMAengine/virt-dma, OF DMA request translation, clk, IRQ, DMA pools, Ingenic DT compatibles, and optional reserved-channel DT property.

Risks: Some SoCs need `JZ_SOC_DATA_BREAK_LINKS`, changing completion sequencing. Cyclic callbacks are emulated by unlinking descriptors when callbacks are needed. `jz4780_dma_tx_status` assumes `jzchan->desc` when checking active cookie, so paths with no active desc require care. Width 8 bytes is rejected.

Test signals: compatible-specific probe, reserved-channel xlate, SG and cyclic audio-style transfers, memcpy validation, residue during active transfer, address/halt error reporting, break-links SoC behavior, suspend/remove cleanup, and descriptor-pool exhaustion.
