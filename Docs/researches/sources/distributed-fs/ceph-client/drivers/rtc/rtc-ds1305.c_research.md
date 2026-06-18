# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1305.c

## Purpose
DS1305/DS1306 SPI RTC driver. It supports basic time, one-day alarm using ALM0, optional interrupt handling through a workqueue, proc trickle-charge reporting, and 96 bytes of NVRAM through RTC nvmem.

## Important APIs, types, and functions
- `struct ds1305` stores SPI device, RTC device, work item, exit flag, 12-hour mode flag, and cached control/status/trickle registers.
- `bcd2hour()` and `hour2bcd()` support both 24-hour and 12-hour AM/PM hardware modes.
- `ds1305_get_time()` and `set_time()` perform burst SPI transfers for seven BCD time registers, using year range 2000-2099.
- `ds1305_get_alarm()` refreshes control/status cache, reports ALM0 enabled/pending, reads ALM0 registers, and rejects disabled match fields for second/minute/hour.
- `ds1305_set_alarm()` reads current time, enforces future alarm within `rtc->alarm_offset_max`, disables ALM0, writes second/minute/hour with weekday disabled, and optionally re-enables.
- `ds1305_alarm_irq_enable()` updates cached control and writes `DS1305_AEI0`.
- `ds1305_irq()` disables IRQ and schedules `ds1305_work()`, which clears alarm enables/status under `rtc_lock`, re-enables IRQ unless exiting, and reports `RTC_AF`.
- `ds1305_nvram_read/write()` build two-transfer SPI messages for NVRAM.
- Probe validates SPI mode/speed/platform data, reads control registers, configures oscillator/write-protect/trickle settings, registers RTC/NVRAM, sets alarm offset to under one day, and requests IRQ if present.

## Control flow
The driver caches control registers because alarm enable and status are interdependent. IRQ work is deferred to process context so it can use RTC locking and SPI I/O safely. Alarm programming is serialized by the RTC core ops lock as documented in comments.

## State and persistence behavior
Hardware stores time, alarms, control/status, trickle charger, and NVRAM. Software caches control/status/trickle bytes and 12-hour mode, and uses `FLAG_EXITING` during removal to avoid re-enabling IRQ after shutdown.

## Dependencies and integration points
Depends on SPI, `linux/spi/ds1305.h` platform data, RTC class, workqueues, nvmem, optional procfs, and IRQ framework.

## Risks
- Alarm range is intentionally limited to less than one day because weekday matching is disabled.
- Cached control registers can become stale if external masters modify the chip.
- IRQ clear behavior assumes ALM0/ALM1 status relationships described in comments.
- Probe setup must preserve board-specific trickle settings and write-protect behavior.

## Test signals
12/24-hour round trips, alarm range errors, IRQ workqueue clear/report, NVRAM read/write bounds, trickle proc output, SPI setup validation, and removal while IRQ work is pending.
