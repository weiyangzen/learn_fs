# sources/distributed-fs/ceph-client/drivers/spi/spi-lm70llp.c

## Purpose

`spi-lm70llp.c` is a parport-backed SPI bitbang host for the National Semiconductor/TI LM70EVAL-LLP temperature-sensor evaluation board. It creates an SPI controller and instantiates an `lm70` SPI device for the hwmon LM70 protocol driver.

## Important APIs, Types, And Functions

`struct spi_lm70llp` wraps `struct spi_bitbang`, the parallel port/device, the created LM70 SPI device, and board info. Low-level board helpers manipulate parport data/status bits: `assertCS()`, `deassertCS()`, `clkHigh()`, `clkLow()`, `setsck()`, `setmosi()`, and `getmiso()`. SPI bitbang integration is through `lm70_chipselect()` and `lm70_txrx()`. Parport lifecycle is `spi_lm70llp_attach()` and `spi_lm70llp_detach()`.

## Control Flow, State, And Persistence

The parport driver claims one exclusive global instance. Attach allocates an SPI host, configures `spi_bitbang` for SPI mode 0 and 3-wire operation, registers and claims the parport device, starts bitbang, powers the board through data pins, and creates the child `lm70` device. Detach stops bitbang, powers down the board, releases/unregisters parport resources, and releases the host.

Runtime state is primarily physical parport output levels and the global `lm70llp` pointer enforcing exclusivity. No persistent storage is used.

## Dependencies And Integration Points

The file depends on Linux parport, SPI core, and `spi_bitbang`; it includes `spi-bitbang-txrx.h` for the CPHA0 big-endian bitbang routine. It integrates with the hwmon `lm70` SPI protocol driver through `spi_new_device()` and matching modalias.

## Risks And Test Signals

Risks include the intentionally incomplete `setmosi()` path, board-specific inverted MISO wiring, global singleton behavior, lack of actual LM70 detection, and parport timing delays. Test signals are successful parport exclusive claim, child `lm70` bind, plausible temperature reads, detach/reload cleanup, and logic-analyzer confirmation of CS/SCLK/SIO behavior.
