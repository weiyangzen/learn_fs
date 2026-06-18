# sources/distributed-fs/ceph-client/drivers/spi/spi-sc18is602.c

## Purpose

`spi-sc18is602.c` is an SPI host driver for NXP SC18IS602/602B/603 I2C-to-SPI bridge chips. It registers a SPI controller behind an I2C client and translates each SPI message into one or more I2C command/data transactions.

## Important APIs, Types, and Functions

`struct sc18is602` stores the SPI host, device, cached control byte, oscillator frequency, selected SPI speed, I2C client, chip id, a 201-byte command/data buffer, queued transmit length, receive index, and optional reset GPIO. `sc18is602_wait_ready()` polls the bridge by trying an I2C read after a transfer-time-based sleep. `sc18is602_setup_transfer()` encodes CPHA/CPOL/LSB-first and selects one of four clock divisors. `sc18is602_txrx()` coalesces SPI transfers into bridge-sized I2C messages and performs readback when needed.

SPI hooks are `sc18is602_transfer_one()` as `transfer_one_message`, `sc18is602_setup()`, and `sc18is602_max_transfer_size()`. Probe validates I2C functionality, resets the bridge, determines chip-select count and clock, assigns SPI capabilities, and registers the controller.

## Control Flow

On each SPI message, `transfer_one_message()` resets the queued length, iterates transfers, checks aggregate buffer size, programs bridge control if mode/speed changed, decides whether this transfer must flush based on `cs_change` or message end, and calls `sc18is602_txrx()` for nonzero lengths. TX-only transfers are buffered until a read, CS change, or message end because one I2C message corresponds to one complete SPI CS assertion. RX-only transfers append dummy bytes and force a bridge transaction, then read back enough bytes to copy the RX segment.

## State and Persistence Behavior

The driver caches only the bridge control byte, selected speed, transfer staging buffer, and optional reset GPIO state. There is no persistent storage. The bridge's own mode register persists until changed or reset, so redundant control writes are skipped.

## Dependencies and Integration Points

The driver depends on I2C master transfers, SMBus byte-data write, optional platform data for SC18IS603 clock frequency, firmware property `clock-frequency`, optional reset GPIO, and SPI core message handling. It exposes 8-bit words, CPHA/CPOL/LSB-first, four chip selects for SC18IS602/602B, and two for SC18IS603.

## Risks and Edge Cases

Maximum message staging is 200 payload bytes plus the CS command byte. `sc18is602_check_transfer()` rejects only the current staged aggregate; clients must respect max message size. Readiness polling treats any successful one-byte I2C receive as ready and retries only ten times. Timing is based on selected SPI speed, so wrong clock-frequency data can make waits too short. SC18IS602 rejects CS2 explicitly despite advertising four chip selects for the family. Coalescing behavior means `cs_change` boundaries are semantically important.

## Test Signals

Test all chip ids, reset GPIO, clock-frequency override for SC18IS603, all four mode combinations, LSB-first, all divisor ranges, TX-only coalescing, RX-only dummy writes, full-duplex readback, `cs_change` flushing, buffer-limit rejection, I2C short write/read, and bridge-not-ready timeout.
