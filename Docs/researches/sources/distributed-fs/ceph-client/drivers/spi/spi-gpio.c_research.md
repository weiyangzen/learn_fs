# sources/distributed-fs/ceph-client/drivers/spi/spi-gpio.c

## Purpose

`spi-gpio.c` implements a generic GPIO-backed bitbanged SPI host. It is intended for systems without a native SPI controller, systems where the native controller driver is unavailable, or boards that need arbitrary GPIO pins for SCK/MOSI/MISO/CS. It delegates transfer timing and word shifting to the SPI bitbang framework while providing GPIO-specific line operations, chip-select handling, 3-wire turnaround handling, and descriptor/platform-data resource discovery.

## Important APIs, Types, and Functions

`struct spi_gpio` stores the embedded `spi_bitbang`, SCK/MISO/MOSI GPIO descriptors, and optional CS GPIO array. GPIO line callbacks are `setsck()`, `setmosi()`, and `getmiso()`, with `getmiso()` reading MOSI for 3-wire mode. The four `spi_gpio_txrx_word_mode*()` callbacks handle normal full-duplex modes, while `spi_gpio_spec_txrx_word_mode*()` pass controller flags into bitbang helpers so missing MOSI/MISO paths are respected.

SPI-core callbacks are `spi_gpio_chipselect()`, `spi_gpio_set_mosi_idle()`, `spi_gpio_setup()`, `spi_gpio_set_direction()`, and `spi_gpio_cleanup()`. Resource setup is split between `spi_gpio_request()` for GPIO descriptors, `spi_gpio_probe_pdata()` for legacy platform data CS GPIOs, and `spi_gpio_probe()` for controller allocation and bitbang registration.

## Control Flow

Probe allocates a SPI host, chooses descriptor mode when a firmware node exists or legacy platform-data CS setup otherwise, requests optional MOSI/MISO plus required SCK, and configures controller mode bits for 3-wire, CPHA/CPOL, CS-high, LSB-first, and MOSI idle levels. Missing MOSI sets `SPI_CONTROLLER_NO_TX`; CS handling always uses `SPI_CONTROLLER_GPIO_SS` so the local chip-select callback runs.

The bitbang framework calls the selected mode-specific word function for each word. Those functions call generated helpers from `spi-bitbang-txrx.h`, which in turn call `setsck()`, `setmosi()`, and `getmiso()`. Chip selection sets SCK to idle polarity before asserting and drives CS according to `SPI_CS_HIGH`. Direction changes switch MOSI to input only in 3-wire mode and optionally add a high-impedance turnaround clock for `SPI_3WIRE_HIZ`.

## State and Persistence Behavior

The driver keeps only volatile GPIO descriptor state and bitbang framework state. `spi->controller_state` remains reserved for bitbang internals. No hardware FIFO, DMA, IRQ, runtime PM, or persistent storage is involved. GPIO output state persists electrically until changed by later transfers or driver removal.

## Dependencies and Integration Points

The driver depends on gpiolib descriptors, platform devices, firmware nodes or legacy `spi_gpio_platform_data`, the SPI core, and `spi_bitbang`. It matches `spi-gpio` device-tree compatibles and platform alias `spi_gpio`. It integrates with normal SPI child devices through the generic controller registration path.

## Risks and Edge Cases

There is no real delay implementation: `spidelay()` is empty because software overhead dominates, so requested high precision timing is not honored. Transfer speed is CPU/scheduler/GPIO-controller dependent and usually far below hardware SPI. Missing MOSI is explicitly supported, but missing MISO relies on bitbang flags and device expectations. 3-wire direction changes can leave MOSI high unless the code avoids input mode outside 3-wire, a behavior called out in comments. Legacy platform data and descriptor firmware paths differ, so CS GPIO indexing needs board-level validation.

## Test Signals

Tests should cover all four SPI modes, LSB-first, CS-high, no-MOSI TX-disabled operation, optional MISO, 3-wire and 3-wire high-impedance turnaround, MOSI idle low/high, descriptor-based DT probe, legacy platform-data CS setup, multi-CS devices, and slow devices that rely on CPOL idle state before CS assertion.
