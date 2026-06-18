# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dma3.c

## Purpose
`stm32-dma3.c` is the DMAEngine provider for the newer STM32 DMA3 controller, currently matched for `st,stm32mp25-dma3`. It supports DMA slave, private channels, cyclic transfers, memcpy, hardware linked lists, channel security/CID filtering, semaphore-controlled channels, residue/in-flight reporting, runtime PM, and system suspend safety checks.

## Important APIs, Types, And Functions
Key types are `struct stm32_dma3_ddata`, `struct stm32_dma3_chan`, `struct stm32_dma3_swdesc`, `struct stm32_dma3_lli`, `struct stm32_dma3_hwdesc`, and `struct stm32_dma3_dt_conf`. A software descriptor owns a flexible array of DMA-pool-backed hardware descriptors. A channel stores virtual DMA state, hardware id/IRQ, FIFO size, max burst, semaphore state, DT config, DMA slave config, current software descriptor, transfer-complete event mode, and DMA status.

Important functions include descriptor allocation/free (`stm32_dma3_chan_desc_alloc`, `stm32_dma3_chan_desc_free`), hardware descriptor construction (`stm32_dma3_chan_prep_hw`, `stm32_dma3_chan_prep_hwdesc`), start/stop/suspend/reset (`stm32_dma3_chan_start`, `stm32_dma3_chan_stop`, `stm32_dma3_chan_suspend`, `stm32_dma3_chan_reset`), preparation APIs (`stm32_dma3_prep_dma_memcpy`, `stm32_dma3_prep_slave_sg`, `stm32_dma3_prep_dma_cyclic`), status/residue (`stm32_dma3_tx_status`, `stm32_dma3_chan_set_residue`), channel filtering/OF translation (`stm32_dma3_filter_fn`, `stm32_dma3_of_xlate`), RIF/CID validation (`stm32_dma3_check_rif`), and probe/PM functions.

## Control Flow
Probe maps registers, enables the clock, resets hardware, initializes DMAEngine capabilities, reads hardware channel/request/master-port/FIFO configuration, applies platform AXI burst limits, allocates channel state, reserves secure or inaccessible channels through `stm32_dma3_check_rif`, registers the DMAEngine device and individual channels, requests per-channel IRQs, registers the OF DMA controller, and enables runtime PM.

OF translation receives request line, channel config, and transfer config. It filters generic DMA channels by optional `dma-channel-mask`, semaphore availability, and FIFO-size match, then stores the DT config. Resource allocation resumes the device, creates a DMA pool for aligned hardware descriptors, and takes the channel semaphore when required.

Preparation computes how many linked-list items are needed, allocates DMA-visible descriptors, computes CTR1/CTR2/CCR fields for direction, widths, ports, bursts, packing/unpacking, request mode, and transfer-complete event mode, then links descriptors either linearly or cyclically. `issue_pending` starts the first queued descriptor by writing the first hardware descriptor to channel registers and enabling `CCR_EN`. IRQs check the masked interrupt status, complete or callback cyclic transfers on TCF, reset and mark error on user setting, update link, or data transfer errors, and clear status flags.

## State And Persistence
State lives in `stm32_dma3_ddata`, per-channel structures, DMA-pool descriptor memory, channel registers, and optional hardware semaphores. Runtime suspend only disables the clock. System suspend refuses if any registered channel has `CCR_EN` set. Resume reacquires semaphores for channels that had them before low power, because register reset can drop semaphore state.

## Dependencies And Integration Points
The driver depends on DMAEngine, `virt-dma`, OF DMA, platform resources, clocks, optional reset controls, DMA pools, runtime PM, bitfield helpers, and iopoll. It integrates with STM32 resource isolation/CID hardware through SECCFGR/CCIDCFGR/CSEMCR, with device-tree clients through three DMA spec cells, and with dmatest/memcpy users through DMA_MEMCPY support.

## Risks
Hardware linked-list addressing is limited by `CLLR_LA` and 32-byte descriptor alignment; oversized descriptor counts must be rejected. Residue requires temporarily suspending an active channel and reasoning about FIFO bytes, pack/unpack mode, and current linked-list pointer, so races and timeout handling are significant. Security/CID handling can deny channels depending on boot firmware configuration. Semaphore state can be lost during low power and must be reacquired. User-setting errors indicate invalid prepared register combinations and trigger reset, so width, port, burst, and packing decisions are high-risk.

## Test Signals
Useful signals include successful probe with revision log, channel availability under secure/CID configurations, DMAEngine memcpy across multiple block sizes including block-limit boundaries, slave SG with refactored and non-refactored linked lists, cyclic callbacks, residue and in-flight bytes during pack/unpack transfers, semaphore allocation/free and suspend/resume reacquisition, system suspend refusal for enabled channels, and IRQ-path tests for TCF, USEF, ULEF, and DTEF.
