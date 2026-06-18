# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-cpm.c

## Purpose
Implements CPM/QE buffer-descriptor mode support for the classic Freescale MPC8xxx SPI driver. It allocates parameter RAM and buffer descriptors, maps dummy and real DMA buffers, starts CPM transfers, services CPM/QE completion interrupts, and releases CPM resources.

## Important APIs, Types, And Functions
Exports `fsl_spi_cpm_reinit_txrx()`, `fsl_spi_cpm_bufs()`, `fsl_spi_cpm_bufs_complete()`, `fsl_spi_cpm_irq()`, `fsl_spi_cpm_init()`, and `fsl_spi_cpm_free()`. Internal helpers include `fsl_spi_cpm_bufs_start()`, `fsl_spi_alloc_dummy_rx()`, `fsl_spi_free_dummy_rx()`, and `fsl_spi_cpm_get_pram()`. State is stored in shared `struct mpc8xxx_spi` from `spi-fsl-lib.h`.

## Control Flow
Initialization only runs when `SPI_CPM_MODE` is set. It allocates a shared dummy RX buffer, resolves QE/CPM subblock and parameter RAM, allocates TX/RX BDs in MURAM, maps zero-page dummy TX and dummy RX DMA buffers, initializes PRAM fields, and returns to the parent driver. For a transfer, `fsl_spi_cpm_bufs()` maps real buffers or selects dummy buffers, does 16-bit TX byte-order conversion when needed, enables RXB interrupt, records `xfer_in_progress`, and starts the first chunk. IRQ handling reads completed length from RX BD, clears events, subtracts from remaining count, restarts if bytes remain, or completes the parent transfer.

## State And Persistence
Runtime state includes PRAM pointer, BD pointers, DMA addresses, map flags, current transfer pointer, count, and globally refcounted dummy RX memory. Hardware state lives in CPM/QE parameter RAM and BDs. No persistent storage is used.

## Dependencies And Integration Points
Depends on CPM1/CPM2 or QE APIs, MURAM allocation, DMA mapping, OF properties, and the classic Freescale SPI register definition. It is called by `spi-fsl-spi.c` when platform data or OF mode selects CPM/QE.

## Risks
Resource unwinding is complex because PRAM, BDs, dummy buffers, and DMA mappings are allocated from different subsystems. Chunking is capped by `PAGE_SIZE`. 16-bit conversion allocates a temporary TX buffer but this source does not visibly free that converted buffer, making ownership worth auditing in context. Bad BD lengths trigger `WARN_ON`.

## Test Signals
CPM1, CPM2, QE fixed/dynamic PRAM, dummy TX/RX transfers, large transfers split over multiple BD starts, DMA map failures, 16-bit word transfers, IRQ completion, and cleanup/refcount behavior are important.
