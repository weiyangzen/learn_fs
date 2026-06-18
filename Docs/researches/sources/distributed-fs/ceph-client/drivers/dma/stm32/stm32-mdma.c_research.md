# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-mdma.c

## Purpose
`stm32-mdma.c` is the DMAEngine provider for the STM32 MDMA controller. It exposes slave, cyclic, and memcpy capabilities, translating DMAEngine descriptors into STM32 MDMA channel registers and hardware linked-list descriptors. The driver supports software-triggered memory copies, hardware-request peripheral transfers, cyclic audio-style transfers, and a special memory-to-memory hardware-triggered mode where STM32 DMA can trigger MDMA through `peripheral_config`.

## Important APIs, Types, and Functions
The main device state is `struct stm32_mdma_device`, which owns the DMAEngine `dma_device`, MMIO base, clock, IRQ, channel count, request count, secure-channel mask, and AHB address masks. `struct stm32_mdma_chan` wraps `virt_dma_chan` and holds the active descriptor, slave config, parsed OF channel config, burst/width residue helpers, and busy state. Descriptors are `struct stm32_mdma_desc`, a flexible array of `struct stm32_mdma_desc_node`; each node owns a DMA-pool allocated, 64-byte aligned `struct stm32_mdma_hwdesc` matching the controller linked-list layout.

Key DMAEngine entry points are `stm32_mdma_alloc_chan_resources()`, `stm32_mdma_free_chan_resources()`, `stm32_mdma_prep_slave_sg()`, `stm32_mdma_prep_dma_cyclic()`, `stm32_mdma_prep_dma_memcpy()`, `stm32_mdma_issue_pending()`, `stm32_mdma_tx_status()`, `stm32_mdma_pause()`, `stm32_mdma_resume()`, `stm32_mdma_terminate_all()`, and `stm32_mdma_synchronize()`. The low-level transfer setup path runs through `stm32_mdma_set_xfer_param()`, `stm32_mdma_setup_xfer()`, `stm32_mdma_setup_hwdesc()`, and `stm32_mdma_start_transfer()`.

## Control Flow
Probe reads `dma-channels`, `dma-requests`, and optional `st,ahb-addr-masks`, maps registers, enables/reset the controller, initializes one virtual channel per hardware channel, filters out channels marked secure by `CCR.SM`, requests the shared IRQ, registers DMAEngine, and registers OF DMA translation. OF clients pass five cells: request line, priority, transfer config, mask address, and mask data. Those populate `chan_config`.

Transfer preparation allocates one MDMA descriptor per SG entry or period, computes CTCR/CCR/CTBR fields, chooses memory width and burst size based on alignment and length, selects AHB/AXI bus bits from address masks, fills hardware descriptors, and queues via virt-dma. `issue_pending()` marks issued descriptors and starts the first queued descriptor if the channel is idle. `stm32_mdma_start_transfer()` writes the first hardware descriptor into channel registers, clears stale status, enables the channel, and raises `SWRQ` for software-request memcpy.

The IRQ handler finds the channel from `GISR0`, validates enabled interrupt bits, clears transfer/error flags, completes descriptors on channel-transfer-complete, advances `curr_hwdesc` and invokes cyclic callbacks on block-transfer-complete, and starts the next queued descriptor after non-cyclic completion.

## State and Persistence
All persistent state is runtime kernel state: MMIO registers, DMA-pool descriptors, virt-dma queues, `chan->desc`, `curr_hwdesc`, `busy`, `mem_burst`, `mem_width`, channel configuration, and runtime PM clock state. No on-disk state is written. Runtime PM disables/enables the controller clock. System suspend refuses to proceed if any channel is still enabled, then force-suspends runtime PM; resume restores clocking through PM.

## Dependencies and Integration Points
The driver depends on DMAEngine, virt-dma, OF DMA, platform devices, clocks, reset controls, runtime PM, DMA pools, scatterlists, and MMIO polling helpers. It integrates with STM32 DT bindings via `st,stm32h7-mdma`, `dma-channels`, `dma-requests`, `st,ahb-addr-masks`, and the five-cell DMA specifier. It advertises `DMA_SLAVE`, `DMA_PRIVATE`, `DMA_CYCLIC`, and `DMA_MEMCPY`, 1/2/4/8-byte widths, burst residue granularity, and descriptor reuse.

## Risks and Edge Cases
Transfer setup rejects unsupported bus widths, non-power-of-two bursts, burst-width products above 128 bytes, block lengths above 64 KiB, invalid cyclic sizes, bad OF requests, and unsupported directions. Residue calculation depends on `CLAR` matching descriptor links and rounds to memory burst granularity; this is sensitive to linked-list state and the `m2m_hw` request-active path. Pause disables the channel and waits for channel-transfer-complete, so timeout handling can leave higher layers with `-EBUSY`. The `m2m_hw` mode mutates request/mask fields from `peripheral_config` and clears mask registers for some MEM_TO_DEV SG descriptors, so client-side contract correctness matters. Secure channels are filtered only at request time.

## Test Signals
Useful signals include successful probe registration, OF channel request validation, DMAEngine memcpy tests at sizes below and above 64 KiB, slave SG with several SG entries, cyclic transfer callbacks per period, pause/resume/terminate behavior, residue/in-flight bytes during active transfers, runtime PM get/put around channel resource allocation, suspend rejection while active, and error IRQ logging from `CESR`.
