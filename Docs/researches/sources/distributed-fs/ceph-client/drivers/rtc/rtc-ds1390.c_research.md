# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1390.c

## Purpose
Dallas/Maxim DS1390/1393/1394 SPI RTC driver. It supports basic RTC read/write and optional device-tree trickle charger setup, while explicitly leaving alarms and other extra chip-family features unsupported.

## Important APIs, types, and functions
- `struct ds1390` stores RTC device and a shared 9-byte command/data buffer.
- `ds1390_set_reg()` writes a single register by ORing the address with write bit `0x80`.
- `ds1390_get_reg()` reads a single register using `spi_write_then_read()` and the shared buffer.
- `ds1390_trickle_of_init()` reads `trickle-resistor-ohms` and `trickle-diode-disable`, builds a trickle register value for 250/2000/4000 ohm settings, and writes `DS1390_REG_TRICKLE`.
- `ds1390_read_time()` reads seven time registers starting at seconds and decodes BCD fields, including century bit in month.
- `ds1390_set_time()` writes a burst starting at seconds with the write bit set and stores century in the month high bit.
- Probe forces SPI mode 3 and 8-bit words, allocates state, verifies device readability, applies optional trickle setup, and registers the RTC.

## Control flow
All runtime operations are synchronous SPI transfers. Probe validates a basic seconds-register read before any optional charger setup or RTC registration.

## State and persistence behavior
Time and trickle charger configuration persist in hardware registers. Software state is the RTC pointer and reusable SPI buffer. No alarm state is exposed.

## Dependencies and integration points
Depends on SPI, OF properties, RTC class, and BCD helpers. Binds with OF compatible `"dallas,ds1390"` and SPI ID `"ds1390"`.

## Risks
- Alarm and status features are intentionally unavailable despite register definitions.
- SPI setup return is not checked.
- Shared transfer buffer relies on RTC core serialization for concurrent calls.
- Unsupported trickle resistor values only warn and skip charger setup.

## Test signals
Probe read failure, time read/write with century bit, DT trickle charger permutations, unsupported resistor warning, and SPI mode/bits setup behavior.
