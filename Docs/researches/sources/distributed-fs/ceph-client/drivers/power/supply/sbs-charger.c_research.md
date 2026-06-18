# sources/distributed-fs/ceph-client/drivers/power/supply/sbs-charger.c

## Purpose
SBS smart-charger driver exposing charger status as a mains power supply. It reports battery presence, AC online state, charger status, and simple health from SBS charger status bits.

## Important APIs, Types, and Functions
`struct sbs_info` holds the I2C client, power supply, regmap, optional polling work, and last status register value. `sbs_get_property()` decodes `last_state`. `sbs_check_state()` refreshes the status register and notifies on changes. Probe sets up regmap, power supply, and either IRQ or polling.

## Control Flow
Probe initializes an SMBus-style 8-bit register/16-bit little-endian regmap, reads initial charger status, registers the power supply, then uses threaded IRQ when available or a 500 ms delayed-work polling loop otherwise. IRQ and polling both call `sbs_check_state()`.

## State and Persistence
Only `last_state` is cached. There is no persistent storage or runtime writes to charger configuration.

## Dependencies and Integration Points
Depends on I2C, regmap, power_supply, optional IRQ, and delayed work. It matches `sbs,sbs-charger` or I2C ID `sbs-charger`.

## Risks and Test Signals
Health assignment has an ordering issue: cold sets COLD, then a missing `else` before hot can be overwritten by GOOD when hot is not set. IRQ returns `IRQ_NONE` if status did not change, which can matter on shared lines. Test status bit decoding, polling mode, IRQ mode, cold/hot health, and regmap endianness.
