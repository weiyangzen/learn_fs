<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c

## Purpose

`spi-xcomm.c` is an I2C-to-SPI bridge driver for the Analog Devices AD-FMCOMMS1-EBZ board. It registers an SPI controller backed by short I2C commands and also exposes one optional GPIO output through gpiolib.

The bridge supports 16 chip selects, 8-bit words, half-duplex SPI, CPOL/CPHA, 3-wire mode, and a small set of clock dividers derived from a 48 MHz bridge clock.

## Important APIs, Types, and Functions

`struct spi_xcomm` stores the I2C client, optional `gpio_chip`, cached bridge settings, chip-select bitmask, current speed, and a 63-byte command buffer.

GPIO support is provided by `spi_xcomm_gpio_add()`, `spi_xcomm_gpio_set_value()`, and `spi_xcomm_gpio_get_direction()`. Bridge configuration is handled by `spi_xcomm_sync_config()`, `spi_xcomm_chipselect()`, and `spi_xcomm_setup_transfer()`. Data movement is done by `spi_xcomm_txrx_bufs()`.

The SPI controller entry point is `spi_xcomm_transfer_one()`, installed as `transfer_one_message`. Probe allocates a devm SPI host, assigns controller capabilities, registers it, then registers the optional GPIO chip.

## Control Flow

Probe is driven by I2C ID `"spi-xcomm"`. It allocates a SPI host with `struct spi_xcomm` private data, stores the I2C client, advertises 16 chip selects, CPHA/CPOL/3WIRE mode bits, 8-bit words, half-duplex behavior, and registers `spi_xcomm_transfer_one()`.

For a SPI message, the driver sets the selected chip bit in its cached chip-select mask, then iterates each transfer. It rejects transfers with length but neither TX nor RX buffer, rejects transfers longer than 62 bytes, updates clock divider and mode bits in a local settings word, handles `cs_change` relative to whether the transfer is last, and synchronizes bridge configuration when needed.

TX transfers send command `SPI_XCOMM_CMD_WRITE` followed by payload via `i2c_master_send()`. RX transfers first sync configuration with the expected data length, then call `i2c_master_recv()`. Successful transfer byte counts are added to `msg->actual_length`, transfer delays are executed, and chip select is deasserted unless `cs_change` keeps it active.

The GPIO side channel sends `SPI_XCOMM_CMD_GPIO_SET` plus one byte over I2C whenever the GPIO output is changed.

## State and Persistence Behavior

The driver persists only in-memory cached bridge settings, selected chip bits, and current speed. Hardware state in the bridge persists until overwritten by later config or GPIO commands. The driver has no durable storage.

SPI target devices may be modified by write transfers, and the GPIO output state may remain set on the external board. Cached `current_speed` avoids recomputing divider settings unless the requested transfer speed changes.

## Dependencies and Integration Points

The file depends on I2C, SPI controller, gpiolib, unaligned big-endian helpers, and module/I2C driver infrastructure. It integrates with the board bridge firmware through command bytes `UPDATE_CONFIG`, `WRITE`, and `GPIO_SET`.

SPI integration uses `transfer_one_message` rather than `transfer_one`, sets `SPI_CONTROLLER_HALF_DUPLEX`, and finalizes messages through `spi_finalize_current_message()`. GPIO integration is optional and skipped when `CONFIG_GPIOLIB` is disabled.

## Risks and Edge Cases

The bridge buffer is 63 bytes and the SPI payload limit is 62 bytes to reserve one command byte. Larger transfers rely on upper layers splitting messages; otherwise they fail with `-EINVAL`.

The same bit (`BIT(5)`) is used by named setting `SPI_XCOMM_SETTINGS_CS_HIGH` and by the per-transfer `cs_change ^ is_last` handling. This appears intentional for bridge config, but it makes code review easy to confuse because the local variable is not named around CS hold semantics.

Clock divider selection only has divide-by-4, divide-by-16, and divide-by-64 choices. Requests below or above supported rates are rounded coarsely. `current_speed` is updated when speed changes, but if later code clears only the divider bits incorrectly, stale divider state could matter; current code starts from cached settings and sets one divider choice.

The driver supports either TX or RX per transfer, not simultaneous full-duplex. It also does not expose advanced delay, multi-IO, or DMA behavior.

## Test Signals

Tests should cover probe over I2C, SPI device creation, all advertised modes, 3-wire mode, 16 chip-select positions, `cs_change` across multi-transfer messages, 0-byte transfers, 62-byte success and 63-byte rejection, TX and RX short-count I2C errors, GPIO set behavior, and operation with gpiolib disabled.

Integration tests should verify bridge command byte ordering, big-endian config fields, clock divider selection at threshold speeds, and message finalization/status after mid-message I2C failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c -->
