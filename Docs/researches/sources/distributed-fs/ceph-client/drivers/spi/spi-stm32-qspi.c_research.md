# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-qspi.c

## Purpose

`spi-stm32-qspi.c` is the STM32 QuadSPI memory controller driver for `st,stm32f469-qspi`. It implements `spi_mem` operations, status polling, direct-map reads through the memory-mapped aperture, DMA/polling data movement, GPIO-CS message emulation, runtime PM, and reset handling for up to two NOR flash chip selects.

## Important APIs, Types, and Functions

`struct stm32_qspi` tracks the SPI controller, MMIO and memory-map bases, clock/rate, per-flash CS and prescaler, completions, functional mode, DMA channels, cached CR/DCR state, status timeout, and a mutex. Data paths are `stm32_qspi_tx_poll()`, `stm32_qspi_tx_dma()`, and `stm32_qspi_tx_mm()`. Command sequencing is centralized in `stm32_qspi_send()`, with helpers for busy waits, command completion, automatic-poll match completion, and abort. `stm32_qspi_mem_ops` supplies `exec_op`, `dirmap_create`, `dirmap_read`, and `poll_status`.

## Control Flow

Probe maps the register and memory-map resources, requests IRQ, enables the clock, optionally resets the controller, sets up DMA channels, configures controller hooks, enables runtime PM, and registers the SPI controller. Setup validates speed and dual-flash GPIO requirements, computes a per-chip prescaler, writes base CR and max DCR FSIZE. `exec_op` resumes runtime PM, locks, sets indirect read/write mode, sends the operation, unlocks, and autosuspends. `poll_status` programs PSMKR/PSMAR, sets automatic-poll mode, and sends. Direct-map read builds a local op with requested offset/length and selects memory-mapped mode when it fits in `mm_size`.

## State and Persistence Behavior

There is no persistent storage. Runtime state consists of per-CS prescalers, cached CR/DCR for resume, functional mode, DMA channel availability, and in-flight completions. Runtime suspend gates the clock; system resume restores cached CR/DCR after force-resuming PM.

## Dependencies and Integration Points

The driver depends on `spi_mem`, DMAengine, GPIO descriptors, reset controls, named memory resources `qspi` and `qspi_mm`, IRQ completions, mutexes, pinctrl PM, and runtime PM. It integrates with flash drivers through `spi_mem` and with the generic SPI message path by translating dummy/data transfers to memory operations.

## Risks and Edge Cases

`stm32_qspi_send()` returns only `err` after abort; if `err_poll_status` or abort timeout occurs while `err` is zero, the error can be logged but reported as success. The direct-map bound check uses `addr + nbytes + 1` in a 32-bit variable, which can overflow and is stricter than a typical inclusive end check. DMA setup returns immediately on `dma_get_slave_caps()` errors without releasing already acquired channels in those branches. Polling/status IRQ handling always returns `IRQ_HANDLED`, even for interrupts without `SR_SMF`.

## Test Signals

Test exec reads/writes, no-data commands, automatic status polling success/timeout/error propagation, direct-map reads at aperture boundaries, dual-flash mode requiring CS GPIOs, DMA RX/TX success and fallback to polling, DMA timeout, suspend/resume CR/DCR restore, reset failure, and message emulation with dummy bytes.
