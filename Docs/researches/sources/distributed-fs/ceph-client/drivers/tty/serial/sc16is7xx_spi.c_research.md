# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_spi.c

## Purpose
SPI transport wrapper for SC16IS7xx chips. It validates SPI mode, applies default SPI transfer settings, creates per-UART SPI regmaps, and delegates UART lifecycle to the bus-neutral core.

## Important APIs, Types, And Functions
`SC16IS7XX_SPI_READ_BIT` marks SPI reads. `sc16is7xx_spi_probe()` sets `bits_per_word` to 8, rejects non-mode-0 transfers, defaults speed to 4 MHz when unspecified, calls `spi_setup()`, obtains match data, and builds regmaps with per-port masks. `sc16is7xx_spi_remove()` calls `sc16is7xx_remove()`. The SPI ID table mirrors the I2C aliases.

## Control Flow
`module_spi_driver()` registers the driver. Probe performs bus setup before match-data validation, copies shared regmap config, and for each UART sets `read_flag_mask` to port mask OR `BIT(7)` because regmap otherwise substitutes its own default read bit. Write masks contain only the port selector. The core receives `spi->irq`.

## State And Persistence
The wrapper keeps no private runtime state. Regmaps are devm-managed and core state is stored through `dev_set_drvdata()` in `sc16is7xx_probe()`.

## Dependencies And Integration Points
Depends on SPI core, regmap-SPI, units macros for MHz defaults, module tables, and the SC16IS7xx namespace. OF matching uses the common `sc16is7xx_dt_ids`.

## Risks
SPI read-mask handling is subtle: omitting the explicit read bit would cause bad addressing. SPI mode validation is strict because variants support only mode 0. Defaulting speed may be too conservative or too high for marginal boards depending on wiring, but is bounded at 4 MHz.

## Test Signals
Probe with valid and invalid SPI modes, verify correct register reads on port 0 and port 1, run RX/TX under interrupts and polling fallback, and test unspecified `spi-max-frequency` paths.
