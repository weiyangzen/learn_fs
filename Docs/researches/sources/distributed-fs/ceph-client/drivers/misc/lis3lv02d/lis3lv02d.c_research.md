# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/lis3lv02d.c

## Purpose
`lis3lv02d.c` is the shared core for ST LIS3-family accelerometers. It abstracts bus operations behind function pointers, detects sensor type, provides sysfs attributes, exposes an input polled joystick device, optionally registers `/dev/freefall`, handles IRQ/click/freefall events, manages runtime PM power transitions, and parses OF/platform configuration.

## Important APIs, types, and functions
The exported singleton is `struct lis3lv02d lis3_dev`. Exported functions are `lis3lv02d_init_device`, `lis3lv02d_joystick_enable`, `lis3lv02d_joystick_disable`, `lis3lv02d_poweroff`, `lis3lv02d_poweron`, `lis3lv02d_remove_fs`, and `lis3lv02d_init_dt`. Important internals include `lis3lv02d_get_xyz`, `lis3lv02d_set_odr`, `lis3lv02d_selftest`, `lis3_context_save/restore`, interrupt handlers, miscdevice file operations, and sysfs callbacks for `selftest`, `position`, and `rate`.

## Control flow
Transport probe fills bus callbacks and calls `lis3lv02d_init_device`. The core reads `WHO_AM_I`, selects precision/rate/scale/read-data tables, allocates register cache, creates a faux sysfs device, powers on the chip, enables runtime PM, registers an input device, applies platform/OF interrupt and click/wakeup settings, requests IRQs when available, and registers `/dev/freefall`. Data reads use block read when available or per-axis reads, scale raw values, and apply axis remapping. Sysfs access briefly runtime-resumes the device and schedules delayed suspend. Remove paths disable joystick/freefall, destroy sysfs, power off if needed, disable runtime PM, and free cache.

## State and persistence
Core state lives in the global `lis3_dev`, including bus callbacks, register cache, platform data, input/misc devices, IRQ state, wait queue, async queue, axis mapping, ODR tables, and wake-thread counters. Register context is saved before regulator poweroff and restored after poweron when a transport supplies `reg_ctrl`. OF platform data is dynamically allocated and stored in `lis3->pdata`.

## Dependencies and integration points
The core depends on input polling, faux devices, miscdevice, runtime PM, IRQ threading, regulators via transports, OF parsing, wait queues, fasync, and `linux/lis3lv02d.h` platform-data definitions. It is consumed by both I2C and SPI glue.

## Risks
The singleton design limits safe multi-device support. I2C read helpers used by transports may return success even when the byte value is negative-truncated, so error propagation depends on callback correctness. Power/sysfs/runtime-PM interactions are subtle because sysfs visitors schedule delayed suspend while input and misc opens hold runtime PM references. Interrupt behavior varies sharply by sensor type and platform data.

## Test signals
Tests should cover all supported `WHO_AM_I` variants, axis remap module parameter validation, sysfs position/rate/selftest, input registration and polling, freefall misc read/poll/fasync, click key events, IRQ-driven data-ready selftest counts, runtime suspend/resume register restoration, OF property parsing, and remove while sysfs delayed suspend is pending.
