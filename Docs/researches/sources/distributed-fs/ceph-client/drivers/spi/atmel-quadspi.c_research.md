# sources/distributed-fs/ceph-client/drivers/spi/atmel-quadspi.c

## Purpose

`atmel-quadspi.c` is a platform SPI memory controller driver for Atmel/Microchip QSPI and OSPI blocks. It implements `spi_controller_mem_ops` rather than generic SPI message transfer and is intended for memory-like devices such as SPI NOR, SPI NAND, Octal SPI flash, and related serial memories.

The driver covers older SAMA5D2/SAM9X60 style QSPI registers and newer SAMA7G5/SAM9X7/SAMA7D65 variants with generic clock, read/write instruction-code registers, octal/DTR support, DMA, DLL, and pad calibration.

## Important APIs, types, and functions

- `struct atmel_qspi_caps` describes per-compatible hardware capabilities: `max_speed_hz`, `has_qspick`, `has_gclk`, `has_ricr`, `octal`, `has_dma`, `has_2xgclk`, `has_padcalib`, and `has_dllon`.
- `struct atmel_qspi` stores mapped register and AHB memory windows, clocks, capability and operation tables, completions, DMA channels, cached mode/clock registers, and AHB mapping size.
- `struct atmel_qspi_ops` selects variant-specific `set_cfg()` and `transfer()` functions.
- `atmel_qspi_supports_op()` validates SPI-MEM operations against bus-width modes and hardware quirks.
- `atmel_qspi_set_cfg()` handles legacy QSPI instruction-frame programming, including 1/2/3/4-byte address cases and the 16-bit address workaround.
- `atmel_qspi_sama7g5_set_cfg()` programs the newer RICR/WICR/IFR path, DTR flags, octal protocol type, and write-access count.
- `atmel_qspi_transfer()` and `atmel_qspi_sama7g5_transfer()` move data through the memory-mapped AHB window, optionally using DMA on newer parts.
- `atmel_qspi_exec_op()` enforces AHB window bounds, resumes runtime PM, programs config, transfers, and autosuspends.
- `atmel_qspi_setup()`, `atmel_qspi_set_cs_timing()`, and SAMA7G5 helpers manage speed, clock rate, CS timing, DLL, and pad calibration.

## Control flow

Probe allocates a SPI controller, reads OF match capabilities, maps `qspi_base` and `qspi_mmap`, obtains clocks, optionally initializes DMA, requests the IRQ, enables runtime PM, initializes the controller, and registers with the SPI core.

Runtime SPI-MEM flow is:

1. SPI core calls `supports_op()` and possibly `adjust_op_size()` at the framework level.
2. `exec_op()` checks the memory-window bounds and address size, resumes the device, and calls the selected `set_cfg()`.
3. `set_cfg()` translates `spi_mem_op` fields into IAR/ICR/IFR or RICR/WICR/IFR registers and serial-memory mode.
4. `transfer()` either waits for command completion for no-data commands, copies through the AHB aperture, or uses DMA for large SAMA7G5 read/write data operations.
5. The IRQ handler accumulates pending status bits and completes `cmd_completion` when the desired mask is observed.

System and runtime PM disable and re-enable clocks, restore key register state, and for newer parts use `atmel_qspi_sama7g5_init()`/`suspend()` to manage QSPI enable, DLL lock, pad calibration, and generic clock.

## State and persistence behavior

Persistent hardware state includes QSPI mode register, serial clock register, instruction-frame registers, DLL/pad calibration, timeout, and clock rates. Software caches `aq->mr`, `aq->scr`, and `target_max_speed_hz` so setup and resume can restore intended behavior. The AHB memory window maps flash access; data is not stored by the driver except transiently through caller buffers and DMA mappings.

Runtime PM autosuspends after 500 ms. Device-managed allocations clean up mappings, clocks, IRQs, and DMA channels, while `remove()` unregisters the controller and disables the hardware when possible.

## Dependencies and integration points

The driver depends on platform device resources named `qspi_base` and `qspi_mmap`, clocks (`pclk`, optionally `qspick` or `gclk`), an IRQ, optional DMA channels `rx`/`tx`, OF compatible data, PM runtime, DMAengine, and the SPI-MEM framework. OF compatibles include `atmel,sama5d2-qspi`, `microchip,sam9x60-qspi`, `microchip,sama7g5-{qspi,ospi}`, `microchip,sam9x7-ospi`, and `microchip,sama7d65-{qspi,ospi}`.

## Risks and edge cases

- The AHB window bound check rejects operations that exceed `mmap_size`; there is no fallback to regular SPI mode.
- The legacy 16-bit address workaround is delicate and depends on dummy-cycle count and matching opcode/address bus widths.
- DMA is used only for newer-capability parts and large addressed transfers; DMA mapping or channel failure falls back only where code explicitly chooses PIO.
- Newer DLL and pad-calibration paths have several poll timeouts; failures can break resume or setup.
- Error paths during DMA transfer must unmap scatterlists and terminate timed-out channels correctly.
- The driver assumes one chip select (`num_chipselect = 1`), matching controller limitations.
- The source currently contains a duplicated `return ret;` in `atmel_qspi_init()` after the serial-memory-mode call; it is unreachable/no-op but worth cleaning.

## Test signals

Build with `CONFIG_SPI_ATMEL_QUADSPI` across OF/PM/DMA variants. Runtime tests should execute SPI-MEM reads, writes, erase/status no-data commands, dual/quad/octal reads where supported, 1/2/3/4-byte addresses, DMA and non-DMA transfer sizes, suspend/resume, runtime autosuspend, and clock-rate setup. Hardware register tracing should confirm LASTXFER/CSRA or CMD_COMPLETED completion paths and proper RICR/WICR use on newer SoCs.
