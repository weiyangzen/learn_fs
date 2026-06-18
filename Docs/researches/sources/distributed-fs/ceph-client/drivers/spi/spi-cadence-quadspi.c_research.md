# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence-quadspi.c

## Purpose

`spi-cadence-quadspi.c` is the Cadence QSPI/OSPI `spi-mem` controller driver used by several SoCs, including Cadence generic, TI K2G/AM654, Intel LGM/SoCFPGA, AMD Versal/Versal2/Pensando, StarFive JH7110, Mobileye EyeQ5, and Renesas RZ/N1 variants. It exposes NOR/NAND flash operations through `spi_controller_mem_ops` rather than ordinary message transfers. The driver supports short STIG register commands, indirect SRAM-backed reads and writes, direct AHB-window reads/writes, optional memcpy DMA for mapped reads, and Versal OSPI indirect DMA.

## Important APIs, Types, and Functions

The central state is `struct cqspi_st`, which stores platform resources, clocks, register windows, AHB window, FIFO geometry, IRQ completions, optional DMA channel, runtime PM state, quirk flags, refcounts, current chip-select/clock, and per-CS `struct cqspi_flash_pdata`. `struct cqspi_driver_platdata` binds SoC quirks, capabilities, and optional indirect DMA callbacks.

Key `spi-mem` entry points are `cqspi_exec_mem_op()`, `cqspi_supports_mem_op()`, and `cqspi_get_name()` in `cqspi_mem_ops`. `cqspi_mem_process()` chooses among `cqspi_command_read()`, `cqspi_command_write()`, `cqspi_read()`, and `cqspi_write()`. Read/write setup is handled by `cqspi_read_setup()`, `cqspi_write_setup()`, DTR helpers `cqspi_enable_dtr()` and `cqspi_setup_opcode_ext()`, and controller tuning helpers `cqspi_configure()`, `cqspi_chipselect()`, `cqspi_config_baudrate_div()`, `cqspi_delay()`, and `cqspi_readdata_capture()`.

I/O engines are `cqspi_indirect_read_execute()`, `cqspi_indirect_write_execute()`, `cqspi_direct_read_execute()`, and `cqspi_versal_indirect_read_dma()`. Lifecycle and PM are implemented by `cqspi_probe()`, `cqspi_remove()`, `cqspi_runtime_suspend()`, `cqspi_runtime_resume()`, `cqspi_suspend()`, and `cqspi_resume()`.

## Control Flow

Probe allocates a controller, parses global OF properties, parses each flash child into `f_pdata`, enables clocks, maps the controller and AHB windows, resets optional reset lines, applies matched quirk data, requests the IRQ, detects/configures FIFO depth, initializes the controller, optionally enables runtime PM, requests an optional DMA memcpy channel for direct reads, and registers the SPI controller.

Every memory operation first validates lifetime/refcount state, resumes runtime PM unless the SoC disables it, then calls `cqspi_mem_process()`. That function configures chip-select and clock, then routes small register-style operations through STIG command registers and address-bearing bulk operations through direct, indirect, or DMA paths. Indirect reads/writes program start address and byte count registers, enable interrupt masks, start the indirect engine, drain/fill the SRAM window, wait for completion bits, and cancel on timeout. Direct mode copies through the AHB memory window, with optional DMA memcpy for valid direct-read buffers.

## State and Persistence Behavior

The driver has no file-backed persistence. Persistent effects are flash-visible writes, erase/status commands, reset-pin toggles, and controller register programming. Runtime state persists for the probed controller: FIFO configuration, direct/indirect mode selection, current chip select, current SCLK, optional DMA channel, and refcounts used to block in-flight operations during removal.

Runtime PM disables the controller and clocks on suspend and fully reinitializes controller registers on resume. Remove clears the externally visible refcount, waits for in-flight operations where needed, releases DMA, disables the controller, and disables clocks.

## Dependencies and Integration Points

The file integrates with the Linux `spi-mem` core, platform/OF probing, runtime PM, reset controllers, clock bulk APIs, DMA engine memcpy, DMA mapping, completions, IRQ handling, ZynqMP firmware OSPI mux control for Versal DMA, and memory-mapped I/O accessors. Device-tree child nodes provide chip-select, timing, and maximum-frequency data. SoC compatibility strings select quirk bundles such as disabled DAC mode, slow SRAM, APB/AHB hazard workarounds, no IRQ reads, external DMA, write-protect control, and no indirect mode.

## Risks and Edge Cases

The read/write path has many mode interactions: DTR disables direct write in some cases, write-completion polling is disabled for devices that need status-address/dummy-address phases, and RZ/N1 forbids DTR and indirect mode. Refcount handling is nontrivial: `inflight_ops` starts at 1 and is conditionally decremented only when greater than 1, so lifetime changes need careful review. Indirect read timeouts may still succeed if FIFO bytes are available; the code distinguishes timeout-with-data from timeout-without-data. Direct DMA only works for valid kernel linear buffers; nonvalid buffers fall back to CPU copy. Versal DMA has several cleanup paths that must restore mux, DMA bits, and mappings.

## Test Signals

Build coverage should include multiple compatible strings and DTR support. Runtime validation should exercise STIG reads/writes up to 8 bytes, SDR and 8-8-8 DTR operations, direct AHB reads/writes, indirect read/write, slow-SRAM read, no-IRQ read, RZ/N1 no-indirect mode, Versal DMA with aligned and remainder bytes, timeout/cancel paths, runtime suspend/resume, remove during blocked operations, and flash child parsing errors. Fault injection should cover clock/reset/IRQ/DMA failures and invalid child `reg` or timing properties.
