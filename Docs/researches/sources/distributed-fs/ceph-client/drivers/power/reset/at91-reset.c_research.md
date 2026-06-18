# sources/distributed-fs/ceph-client/drivers/power/reset/at91-reset.c

## Purpose
Atmel AT91 reset/restart and device-reset-controller driver.

## Important APIs, Types, and Functions
`struct at91_reset`, `struct at91_reset_data`, restart notifier `at91_reset()`, reset reason sysfs attribute, reset-controller ops, OF xlate, and platform probe/remove.

## Control Flow
probe maps RSTC, optional RAM controllers, slow clock, SoC match data, user-reset async configuration, registers restart handler, creates `power_on_reason`, and optionally registers reset-controller ops for device reset bits; restart powers down SDRAM then writes reset key/args.

## State and Persistence Behavior
per-device state stores bases, clock, notifier, reset-controller device, spinlock, and RAM low-power offset; hardware mode/status and device-reset bits persist until reset or rewritten.

## Dependencies and Integration Points
AT91 DDR/SDRAM headers, reset-controller framework, power-on-reason strings, OF compatible data, clocks, sysfs, restart notifier.

## Risks and Edge Cases
reset assembly relies on valid RAM controller mappings; reset reason mapping is only as accurate as RSTC status; device reset ids are range-checked but wrong DT cells can hit wrong bits; sysfs creation failure aborts probe after handler registration cleanup paths matter.

## Test Signals
restart on each compatible, reset-controller assert/deassert/status IDs, invalid xlate cells, power_on_reason contents, SAM9X60 async bit programming, and RAM-controller absence.
