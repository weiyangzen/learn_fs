# sources/distributed-fs/ceph-client/drivers/dma/bcm2835-dma.c

Purpose: DMAengine driver for the BCM2835/Raspberry Pi DMA controller. It supports private slave, cyclic audio-style, and memcpy transfers over hardware control-block chains and uses `virt-dma` for descriptor queuing.

Important APIs/types/functions: `struct bcm2835_dmadev` holds the DMA device, MMIO base, and mapped zero page. `struct bcm2835_chan` stores `virt_dma_chan`, slave config, DREQ, channel MMIO, IRQ, lite-channel flag, and control-block pool. `struct bcm2835_desc` contains direction, frame count, cyclic flag, total size, and a flexible control-block array. Main callbacks are `bcm2835_dma_prep_dma_memcpy`, `bcm2835_dma_prep_slave_sg`, `bcm2835_dma_prep_dma_cyclic`, `bcm2835_dma_issue_pending`, `bcm2835_dma_tx_status`, `bcm2835_dma_terminate_all`, and `bcm2835_dma_xlate`.

Control flow: probe maps registers, maps a zero page, reads `brcm,dma-channel-mask`, resolves per-channel IRQs including legacy shared IRQ handling, initializes channels, registers an OF DMA controller, then registers the DMAengine device. Each channel allocates a DMA pool for 32-byte aligned control blocks when resources are requested. Prep routines calculate frame counts, allocate one CB per frame, fill source/destination/length/info fields, chain CBs via `next`, and use `vchan_tx_prep`. Issue-pending starts the next queued descriptor if idle by writing first CB address and `ACTIVE`. IRQ clears INT while keeping ACTIVE, completes non-cyclic descriptors only when the current CB address becomes zero, and calls cyclic callbacks for cyclic descriptors.

State and persistence: Active state is per-channel: `desc`, queued virt-dma descriptors, DMA pool, slave config, DREQ, IRQ flags, and hardware registers. The zero-page DMA mapping lives for the device lifetime. No persistent state survives driver unload.

Dependencies/integration: DMAengine, OF DMA translation, `virt-dma`, DMA pools, IRQ framework, BCM2835 DT properties and interrupts. The xlate callback takes a DREQ ID from the DMA spec and returns an exclusive slave channel.

Risks: lite channels have a 64 KiB minus 4 limit, so frame splitting must be correct. Cyclic period lengths not dividing buffer length are allowed with a warning but may create latency artifacts. Shared IRQ filtering depends on the INT bit. The zero-page optimization is disabled for lite channels. Suspend fails with `-EBUSY` if any DMA address register remains nonzero.

Test signals: DT probe with named and legacy interrupts, slave SG and cyclic audio transfers with period callbacks, memcpy validation across lite and full channels, residue checks while active, terminate-all abort path, suspend-busy behavior, and IRQ sharing tests.
