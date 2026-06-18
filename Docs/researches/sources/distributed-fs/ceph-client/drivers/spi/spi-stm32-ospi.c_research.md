# sources/distributed-fs/ceph-client/drivers/spi/spi-stm32-ospi.c

## Purpose

`spi-stm32-ospi.c` is the STM32MP25 OCTO SPI memory controller driver. It targets SPI NOR/NAND flash subnodes, supports `spi_mem` exec, status polling, direct-map reads, single/dual/quad/octal widths, DMA fallback to polling, GPIO chip-select message emulation, runtime PM, reset control, and optional reserved-memory mapping for memory-mapped reads.

## Important APIs, Types, and Functions

`struct stm32_ospi` stores controller/device handles, clock/reset, IRQ, MMIO and memory-map regions, DMA channels and completions, per-CS prescalers, cached CR/DCR state, current functional mode, status timeout, and a mutex. Key helpers include `stm32_ospi_abort()`, `stm32_ospi_poll()`, `stm32_ospi_wait_cmd()`, `stm32_ospi_tx_dma()`, `stm32_ospi_xfer()`, `stm32_ospi_wait_poll_status()`, and `stm32_ospi_send()`. `stm32_ospi_mem_ops` provides `exec_op`, `dirmap_create`, `dirmap_read`, and `poll_status`.

## Control Flow

Probe first validates that one or two flash children are present, allocates a host, gathers MMIO/clock/IRQ/reset/DMA/reserved-memory resources, configures DMA, initializes the mutex and SPI controller fields, enables runtime PM, acquires/deasserts reset, and registers the controller. Setup records per-CS prescaler and writes base CR/DCR1. `exec_op` chooses indirect read or write mode, locks, and calls `stm32_ospi_send()`. `poll_status` programs match/mask registers and automatic-poll mode. Direct-map reads choose memory-mapped mode when the requested range fits the mapped window, otherwise indirect read.

`stm32_ospi_send()` selects CS and functional mode, programs data length, prescaler, command/address/dummy/data bus widths, instruction register, address register, optional auto-poll wait, and data transfer. Data transfer uses memory copy, DMA, or FIFO polling. On errors or memory-mapped reads it aborts and clears flags.

## State and Persistence Behavior

State is volatile. The driver caches CR and DCR1 for resume, stores per-CS prescalers, and keeps DMA channels until remove. Runtime suspend only gates the clock. System suspend releases reset and force-suspends runtime PM; resume reacquires reset and restores cached CR/DCR1.

## Dependencies and Integration Points

The file depends on `spi_mem`, DMAengine, reserved-memory mapping, GPIO descriptors, reset controls, clocks, IRQ completions, mutexes, pinctrl PM, and runtime PM. It integrates with flash drivers through `spi_mem` and can emulate simple SPI messages by converting transfers into `spi_mem_op` structures.

## Risks and Edge Cases

In `stm32_ospi_resume()`, if `reset_control_acquire()` fails after `pm_runtime_resume_and_get()`, the function returns without dropping the runtime PM reference. `stm32_ospi_send()` updates `OSPI_DCR2` with `|=` for the prescaler without clearing `DCR2_PRESC_MASK`, so changing to a lower prescaler after a higher one can leave stale bits. Direct-map address bound uses `addr + nbytes + 1`, which is conservative but can overflow a 32-bit `addr_max`. DMA has a timeout; FIFO polling also has bounded timeouts.

## Test Signals

Validate one and two flash child nodes, invalid flash-node counts, all supported bus widths, per-CS prescaler changes, indirect read/write, status polling completion and false-timeout handling, direct-map read bounds, GPIO-CS message emulation with dummy transfers, DMA success/fallback/timeout, suspend/resume error branches, and reset acquire/release sequencing.
