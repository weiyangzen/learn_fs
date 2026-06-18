# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1343.c

## Purpose
Dallas/Maxim DS1343/DS1344 SPI RTC driver. It provides time, alarm, sysfs glitch-filter/trickle charger visibility, NVRAM, IRQ wake support, and PM wake handling.

## Important APIs, types, and functions
- `struct ds1343_priv` stores RTC device, regmap, and IRQ.
- Sysfs attributes `glitch_filter` and `trickle_charger` read/update `DS1343_CONTROL_REG` and report trickle charger configuration.
- `ds1343_nvram_read/write()` expose 96 bytes starting at `DS1343_NVRAM`.
- Time ops bulk read/write seven BCD registers, using range 2000-2099.
- Alarm ops require an IRQ, read pending/enabled from status/control, read/write ALM0 second/min/hour/day, and toggle A0IE.
- `ds1343_thread()` handles alarm IRQ in threaded context, clears `IRQF0`, reports `RTC_AF`, and disables A0IE under `rtc_lock()`.
- Probe configures SPI mode 3 and inverted CS-high handling, initializes regmap, enables INTCN, disables oscillator stop and alarms, clears status flags, registers sysfs group/RTC/NVRAM, requests threaded IRQ, and enables wake IRQ.
- PM callbacks enable/disable IRQ wake when the device may wake.

## Control flow
Probe normalizes control/status registers before RTC registration. Alarm IRQs are one-shot: status is cleared and A0IE is disabled. Sysfs and RTC ops share the same regmap.

## State and persistence behavior
Hardware stores BCD time, alarm, control/status, trickle charger, glitch filter, and NVRAM. Software stores IRQ availability. Wake ability is attached only when IRQ request succeeds.

## Dependencies and integration points
Depends on SPI, regmap, RTC, nvmem, PM wake IRQ helpers, sysfs attribute groups, and SPI IDs `"ds1343"`/`"ds1344"`.

## Risks
- SPI chip-select polarity adjustment is unusual (`mode ^= SPI_CS_HIGH`) and board-definition sensitive.
- Alarm operations return `-EINVAL` without IRQ, so feature exposure depends on IRQ presence.
- `rtc_add_group()` failure is logged but not fatal.
- Sysfs string parsing for glitch filter accepts only exact prefixes.

## Test signals
SPI mode/CS setup, alarm IRQ threaded one-shot behavior, sysfs glitch_filter read/write, trickle charger display cases, NVRAM access, PM wake enable/disable, and no-IRQ behavior.
