<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c

## Purpose
DMAEngine slave driver for MOXA ART SoC APB/AHB DMA, supporting up to four peripheral channels with virt-dma queued scatterlist transfers.

## Important APIs, Types, And Functions
`moxart_dmadev` owns the DMAEngine device and four `moxart_chan` objects. `moxart_chan` holds a virt-dma channel, active descriptor, slave config, request line, SG index, and error flag. `moxart_desc` stores direction, device address, data width encoding, transfer cycles, and a flexible array of SG address/length pairs. `moxart_slave_config`, `moxart_prep_slave_sg`, `moxart_dma_start_desc`, `moxart_dma_interrupt`, and `moxart_tx_status` implement configuration, descriptor prep, execution, completion, and residue/error reporting.

## Control Flow
Probe maps the shared DMA base, parses IRQ, initializes four channels at fixed register strides, registers one shared IRQ, registers the DMAEngine device, and registers OF xlate that assigns a request line number. Slave config programs burst mode, address increment, bus width, APB/AHB selection, and request-line fields based on direction. Prep validates direction and width, copies SG entries into a flexible descriptor, and queues it through virt-dma. Issue-pending starts the next descriptor if idle. Each SG segment programs source/dest and cycle count then enables DMA and interrupts. The shared IRQ scans allocated channels, clears finish/error status, starts the next SG or completes the virt descriptor, and records errors. tx_status reports queued or in-flight residue and returns `DMA_ERROR` when the channel error flag is set.

## State And Persistence
State includes channel allocation flags, request-line number, active descriptor, SG index, transfer cycle counter, slave config, error flag, and APB DMA registers. It is runtime-only.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, OF DMA, platform IRQ/MMIO resources, and compatible `moxa,moxart-dma`. It advertises private slave DMA and integrates with clients through one DT argument specifying request line.

## Risks And Edge Cases
`moxart_set_transfer_params` uses `len >> es_bytes[d->es]`; if `es_bytes` stores byte counts, this shifts by 1/2/4 rather than dividing by 1/2/4, so cycle programming deserves verification. There is no explicit validation that SG lengths align to data width or fit `APB_DMA_CYCLES_MASK`. Terminate frees the active descriptor directly under lock and disables interrupts, so races with shared IRQ handling must be considered. Error status is sticky until the next prep clears `ch->error`.

## Test Signals
Test all supported bus widths, MEM_TO_DEV and DEV_TO_MEM, multi-SG chaining, error interrupt reporting, residue during active SG, terminate while active, and DT request-line mapping. Hardware tests should validate programmed cycle counts for byte/halfword/word transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/moxart-dma.c -->
