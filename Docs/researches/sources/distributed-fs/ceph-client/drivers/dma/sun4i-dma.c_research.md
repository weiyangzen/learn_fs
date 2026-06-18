# sources/distributed-fs/ceph-client/drivers/dma/sun4i-dma.c

## Purpose
`sun4i-dma.c` is the DMAEngine provider for older Allwinner A10/sun4i and suniv/F1C100s DMA controllers. The hardware has separate normal DMA and dedicated DMA channel banks, no hardware linked-list support, and differing endpoint limits per SoC. The driver presents a virtual-channel DMAEngine interface for memcpy, slave SG, and cyclic transfers while serializing SG segments in software.

## Important APIs, Types, and Functions
`struct sun4i_dma_config` captures SoC variant properties: normal/dedicated channel counts, virtual channel counts, data-width encoders, burst conversion, SDRAM DRQ IDs, max burst, and reset availability. `struct sun4i_dma_dev` owns the DMAEngine device, physical channels, virtual channels, used-channel bitmap, MMIO base, clock, reset, IRQ, and global lock. `struct sun4i_dma_pchan` represents one hardware channel. `struct sun4i_dma_vchan` wraps `virt_dma_chan` plus endpoint, config, current physical channel, active promise, and active contract. `struct sun4i_dma_contract` is the virt-dma descriptor and contains lists of pending and completed `struct sun4i_dma_promise` segments.

Core functions include `generate_ndma_promise()`, `generate_ddma_promise()`, `generate_dma_contract()`, `__execute_vchan_pending()`, `configure_pchan()`, `sun4i_dma_prep_dma_memcpy()`, `sun4i_dma_prep_slave_sg()`, `sun4i_dma_prep_dma_cyclic()`, `sun4i_dma_interrupt()`, `sun4i_dma_tx_status()`, and `sun4i_dma_terminate_all()`.

## Control Flow
Probe selects variant data from OF, maps registers, obtains IRQ, enables the clock, optionally deasserts reset, sets DMAEngine capabilities, allocates physical channels, virtual channels, and the used bitmap, initializes normal and dedicated register bases, clears bootloader-left IRQ state, registers the IRQ, registers DMAEngine, and registers OF translation.

Clients request channels through two DMA specifier cells: dedicated-vs-normal and endpoint. `sun4i_dma_of_xlate()` validates both and stores them in the chosen vchan. Preparation builds a contract. Memcpy creates one promise using SDRAM-to-SDRAM DRQ IDs. Slave SG creates one promise per SG segment with endpoint DRQ/address mode fields. Cyclic preparation may double the hardware programmed period and use half-transfer interrupts to reduce reprogramming frequency.

`issue_pending()` calls `__execute_vchan_pending()`, which finds a suitable physical channel from the normal or dedicated bank, takes the first pending contract and promise, enables half/end interrupts, and writes channel registers. The IRQ handler processes half and end interrupt bits. End interrupts move the active promise to the completed list; cyclic contracts immediately select the next promise, reprogram the same pchan, and invoke the cyclic callback. Non-cyclic completions release the pchan and scan all vchans for more work.

## State and Persistence
The driver persists only in-memory state: promise and contract lists, physical-channel ownership bitmap, active `processing` and `contract` pointers, vchan endpoint/type config, and hardware channel registers. No persistent storage is used. Removing the driver disables the IRQ and unregisters OF DMA; devm allocations cover the rest.

## Dependencies and Integration Points
The driver depends on DMAEngine, virt-dma, OF DMA, platform devices, clocks, optional reset controls, spinlocks, bitmaps, and MMIO access. It exposes `DMA_PRIVATE`, `DMA_MEMCPY`, `DMA_CYCLIC`, and `DMA_SLAVE`, 1/2/4-byte widths, burst residue granularity, and a 4-byte copy alignment. Compatible strings are `allwinner,sun4i-a10-dma` and `allwinner,suniv-f1c100s-dma`.

## Risks and Edge Cases
SG and cyclic preparation have TODO paths where allocation failure after partial promise creation can leak earlier promises until caller cleanup is possible. The software-SG model depends on promptly handling interrupts; long IRQ work is mitigated by only looping once for newly pending interrupts. Dedicated DMA uses hard-coded SPI timing parameters for all supported slave transfers, which is documented as empirical. `sun4i_dma_tx_status()` only reports hardware residual for the first pending promise when a pchan exists. Termination clears configuration and disables IRQs, but stale interrupts can still arrive and are guarded by null `vchan` checks.

## Test Signals
Exercise probe on both A10 and F1C100s variants, OF xlate rejection for invalid type/endpoint, memcpy through normal and dedicated channels, slave SG with multiple segments, cyclic audio-style callbacks with half interrupts enabled, residue reporting during active and queued contracts, terminate while IRQs are pending, and channel reuse after release.
