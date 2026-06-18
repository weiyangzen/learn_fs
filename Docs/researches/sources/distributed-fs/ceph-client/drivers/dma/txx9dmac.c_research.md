# sources/distributed-fs/ceph-client/drivers/dma/txx9dmac.c

## Purpose
`txx9dmac.c` implements the TXx9 SoC DMA controller driver. It supports both a public memcpy channel and private slave DMA channels, with channel capabilities determined by platform data and the companion register/header definitions in `txx9dmac.h`.

## Important APIs, Types, and Functions
The implementation uses `struct txx9dmac_dev` for the controller and `struct txx9dmac_chan` for per-channel dmaengine devices. It operates on `struct txx9dmac_desc`, where a first descriptor returned to the client may own child descriptors in `tx_list` for multi-segment transfers. Important functions include the register access wrappers, `txx9dmac_desc_get/put/alloc`, `txx9dmac_dostart`, `txx9dmac_dequeue`, `txx9dmac_scan_descriptors`, `txx9dmac_handle_error`, `txx9dmac_prep_dma_memcpy`, `txx9dmac_prep_slave_sg`, `txx9dmac_issue_pending`, `txx9dmac_terminate_all`, and the controller/channel probe paths.

## Control Flow
The module registers two platform drivers: the parent `txx9dmac` controller and the child `txx9dmac-chan` channels. Parent probe maps controller registers, records whether registers are 64-bit, disables the controller, optionally registers a shared controller IRQ, programs the master control register, and stores `txx9dmac_dev`. Channel probe creates a separate `dma_device`, sets either memcpy or slave hooks, registers per-channel IRQs when no shared IRQ is present, initializes lists and locks, resets the channel, and registers the channel with dmaengine.

Transfer prep allocates one or more DMA-mapped descriptors. Memcpy prep splits large transfers by `TXX9_DMA_MAX_COUNT` and applies documented TX49 errata workarounds around suspicious transfer lengths. Slave prep validates `struct txx9dmac_slave`, direction, and register width, then builds chained descriptors from the SG list. Descriptors link through their hardware `CHAR` field; when simple-chain support is not configured, SAIR/DAIR/CCR fields are written per descriptor.

Submit assigns the dmaengine cookie and queues the descriptor on `dc->queue`. `txx9dmac_issue_pending` scans active descriptors, dequeues pending descriptors into `active_list`, starts idle hardware with `txx9dmac_dostart`, and dynamically extends an active chain on hardware that supports `SMPCHN`. Interrupt handlers disable the IRQ and schedule tasklets. Tasklets read either per-channel CSR or shared MCR bits and call `txx9dmac_scan_descriptors`, which compares the hardware chain pointer to active descriptors, completes descriptors that the hardware passed, handles abnormal chain completion, and restarts queued work.

## State and Persistence
Runtime state is held in per-channel `active_list`, `queue`, `free_list`, `descs_allocated`, and `ccr`, plus controller register state. Descriptors are DMA-mapped one by one and recycled through the free list after callbacks. Suspend and shutdown turn the controller off; resume recreates the master control register but does not persist queued transfers.

## Dependencies and Integration Points
The file depends on dmaengine, platform devices, raw MMIO accessors, DMA mapping, tasklets, and platform data structures from `asm/txx9/dmac.h`. It also depends heavily on compile-time choices in `txx9dmac.h`, including 32-bit versus 64-bit register layout and TX49 simple-chain behavior.

## Risks and Review Signals
The driver intentionally pretends some erroneous descriptors completed because dmaengine has limited error reporting here. Locking is delicate because callbacks are invoked while the channel lock is held in some completion paths, relying on dmaengine callback rules. Dynamic chain extension is hardware-feature-sensitive and should be tested with and without `SMPCHN`. Probe ordering between parent and channel platform devices is important. Test signals include memcpy splitting at errata boundaries, slave direction validation, shared and per-channel IRQ modes, abnormal CSR flags, terminate/reset behavior, suspend/resume MCR restoration, and descriptor reuse after async ACK.
