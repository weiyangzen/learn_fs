# sources/distributed-fs/ceph-client/drivers/spi/spi-dw-mmio.c

## Purpose
Provides the platform/MMIO bus glue for the DesignWare SPI core. It maps registers, obtains clocks/resets/IRQ, applies SoC-specific quirks, optionally wires DMA setup, registers the shared DW SPI controller, and handles suspend/resume/remove.

## Important APIs, Types, And Functions
`struct dw_spi_mmio` wraps `struct dw_spi` with core clock, optional APB clock, reset, and private quirk state. SoC initialization hooks include `dw_spi_mscc_ocelot_init()`, `dw_spi_mscc_jaguar2_init()`, `dw_spi_mscc_sparx5_init()`, `dw_spi_alpine_init()`, `dw_spi_pssi_init()`, `dw_spi_hssi_init()`, `dw_spi_intel_init()`, `dw_spi_mountevans_imc_init()`, `dw_spi_canaan_k210_init()`, and `dw_spi_elba_init()`. Chip-select overrides include MSCC, Sparx5, and Elba implementations. Core lifecycle functions are `dw_spi_mmio_probe()`, `dw_spi_mmio_remove()`, `dw_spi_mmio_suspend()`, and `dw_spi_mmio_resume()`.

## Control Flow
Probe allocates wrapper state, maps resource 0, records physical base, fetches IRQ, enables clocks, deasserts reset, reads `reg-io-width` and `num-cs`, runs match-data initialization, enables runtime PM, and calls `dw_spi_add_controller()`. Suspend asks the shared core to suspend, asserts reset, and disables clocks. Resume enables clocks, deasserts reset, and calls the shared resume path. Remove unregisters the shared controller, disables runtime PM, and asserts reset.

## State And Persistence
State is held in devm-managed wrapper memory and hardware registers. Quirk private data can be a syscon regmap or MSCC structure. No persistent storage exists. Hardware state such as CS override ownership, FIFO length overrides, IP variant ID, and reset/clock state is re-established at probe or resume.

## Dependencies And Integration Points
Depends on platform resources, `clk`, optional `pclk`, reset controls, ACPI/OF matching, syscon/regmap, and the DW core exported APIs. Compatible strings select quirks for Synopsys PSSI/HSSI, MSCC/Microchip, Amazon Alpine, Renesas RZN1, Intel Keem Bay/Mount Evans, Canaan K210, and AMD Pensando Elba.

## Risks
Chip-select override logic is hardware-specific and can break devices if syscon ownership or active-low semantics are wrong. Mount Evans and K210 override FIFO depth to avoid known corruption/overrun errata. Resume ignores errors from `clk_prepare_enable()` and reset deassert in this source, which is a possible robustness gap.

## Test Signals
Probe/remove on each compatible, clock/reset failure injection, CS polarity/override checks with GPIO and native CS, DMA availability for PSSI/HSSI, suspend/resume register access, and FIFO-depth errata regression tests.
