# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1374.c

## Purpose
Maxim/Dallas DS1374 I2C RTC driver. It exposes a 32-bit seconds counter as an RTC, supports decrementer-based alarms when watchdog mode is not configured, and can alternatively register the alarm/decrementer as a watchdog device.

## Important APIs, types, and functions
- `struct ds1374` stores I2C client, RTC device, work item, mutex, exit flag, and optional watchdog device.
- `ds1374_read_rtc()` and `ds1374_write_rtc()` read/write little-endian multi-byte counter/decrementer registers using SMBus block operations.
- `ds1374_check_rtc_status()` warns on oscillator stop, clears OSF/AF, and disables alarm/decrementer control before IRQ setup.
- `ds1374_read_time()`/`set_time()` map `TOD0..3` 32-bit seconds to/from `rtc_time`.
- Alarm ops, compiled out when watchdog mode is enabled, translate absolute alarm time to a relative decrementer value, clamp past alarms to fire soon, write `WDALM0..2`, and toggle `WACE/AIE/WDALM`.
- `ds1374_irq()` disables IRQ and schedules `ds1374_work()`, which clears AF, disables alarm bits, re-enables IRQ unless exiting, and reports `RTC_AF`.
- Optional watchdog ops program the decrementer as watchdog timeout, start/stop through control bits, and register with watchdog core.
- Probe allocates RTC, initializes work/mutex, checks status, requests IRQ, sets wake capability, registers RTC, and optionally registers watchdog.
- Remove sets `exiting`, frees IRQ, and cancels work. PM callbacks toggle IRQ wake.

## Control flow
The same DS1374 decrementer is used either for alarms or watchdog depending on `CONFIG_RTC_DRV_DS1374_WDT`. Alarm programming is mutex-protected and always disables existing countdown before writing a new one. IRQ handling is deferred to workqueue because it performs SMBus I/O.

## State and persistence behavior
Hardware stores TOD counter, watchdog/alarm decrementer, control, status, and trickle charge. Software tracks workqueue exit state and mutex-protected alarm operations. In watchdog mode, watchdog timeout state is mirrored in `watchdog_device`.

## Dependencies and integration points
Depends on I2C SMBus block operations, RTC class, workqueues, PM wake, optional watchdog core, and OF/I2C ID tables (`"dallas,ds1374"`, `"ds1374"`).

## Risks
- Alarm and watchdog are mutually exclusive compile-time uses of the same hardware resource.
- Decrementer alarm must be recalculated if time changes; comments call this out.
- Past alarms are silently adjusted to fire soon rather than rejected.
- IRQ/work removal requires correct `exiting` handling to avoid enabling a freed IRQ.

## Test signals
TOD read/write endian correctness, OSF/AF clearing, alarm relative decrementer math, IRQ work one-shot disable, time-change alarm behavior, watchdog start/stop/timeout, remove while IRQ pending, and suspend/resume wake.
