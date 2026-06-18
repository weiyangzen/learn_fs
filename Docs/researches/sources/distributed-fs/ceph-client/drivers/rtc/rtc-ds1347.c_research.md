# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1347.c

## Purpose
Dallas DS1347 low-current SPI RTC driver. It exposes basic time read/set through regmap and disables write protection during probe.

## Important APIs, types, and functions
- Regmap access table limits writable/register access to the DS1347 time/control/status range.
- `ds1347_read_time()` checks oscillator-stop flag, reads a clock burst plus century register, rereads seconds until the burst is consistent, and decodes year as `century * 100 + year - 1900`.
- `ds1347_set_time()` sets `NEOSC`, writes a clock burst and century register, then clears `NEOSC` and `OSF`.
- Probe configures SPI mode 3 and 8 bits, initializes SPI regmap with read flag `0x80`, disables write protect, allocates RTC, sets range 0000-9999, and registers it.

## Control flow
Reads use a consistency loop around the burst register and seconds register to avoid rollover. Set-time temporarily sets oscillator control, writes all time fields, writes century separately, and clears oscillator failure.

## State and persistence behavior
Hardware stores time, century, control, and status flags. Software state is just the regmap in driver data. No alarms are exposed.

## Dependencies and integration points
Depends on SPI, regmap, RTC class, BCD helpers, and SPI driver name `"ds1347"`.

## Risks
- The read consistency loop has no retry bound; pathological hardware could loop indefinitely.
- Probe calls `spi_setup()` without checking its return value.
- No alarm, NVRAM, or trickle charger functionality is exposed.
- Century math must be tested across 1900/2000/9999 boundaries.

## Test signals
OSF read failure, set-time clearing OSF/NEOSC, century round trips, inconsistent seconds rollover loop, SPI setup failure handling, and write-protect disable.
