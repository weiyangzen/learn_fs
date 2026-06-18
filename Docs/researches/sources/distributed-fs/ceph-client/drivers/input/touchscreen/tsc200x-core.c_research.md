# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.c

## Purpose
`tsc200x-core.c` implements the shared controller logic for TSC2004 and TSC2005 resistive touchscreen drivers. It manages regmap register access, scan start/stop, IRQ-driven samples, pen-up detection, ESD recovery, self-test, regulator/reset handling, and PM.

## Important APIs, Types, And Functions
`tsc200x_regmap_config` defines 8-bit register, 16-bit value, read/write flag, and writable-register constraints. `struct tsc200x` keeps device/regmap/input state, last raw sample, locks, pen-up timer, ESD work, reset GPIO, IRQ, and bus command callback. `tsc200x_irq_thread()` bulk-reads X/Y/Z data, validates ranges, computes pressure, and reports input. `tsc200x_start_scan()` writes CFR registers and sends normal command. `tsc200x_do_selftest()` verifies register write/read and hardware reset behavior.

## Control Flow
Bus wrappers call `tsc200x_probe()`, which validates IRQ/regmap/cmd callback, reads properties, allocates input state, configures reset GPIO and `vio` regulator, resets and stops scanning, requests a threaded IRQ, registers input, and initializes wakeup. Input open enables scanning and optional ESD work; close disables scanning, IRQ, timers, and work. The pen-up timer emits release if no fresh IRQ arrives within 40 ms.

## State And Persistence
Runtime state includes opened/suspended flags, pen state, last raw sample for stale-data filtering, ESD timing, wake IRQ state, and cached touchscreen properties. Hardware configuration is rewritten on each scan start. No nonvolatile data is modified.

## Dependencies And Integration Points
The core integrates with regmap, input/touchscreen properties, threaded IRQs, timers, delayed work, optional reset GPIO, regulator `vio`, firmware properties `ti,x-plate-ohms`, `ti,esd-recovery-timeout-ms`, and bus wrappers for I2C/SPI command transport.

## Risks
Pressure arithmetic is integer and range-sensitive. The self-test is visible only when a reset GPIO exists and temporarily disables the device. ESD work reschedules itself and must not race with close/suspend. `__tsc200x_disable()` uses IRQ/timer/work cancellation paths that require valid IRQ state.

## Test Signals
Test valid and invalid sample packets, stale first sample suppression, pressure bounds, timer-based release, ESD reset recovery, selftest sysfs, reset/regulator failures, wakeup-source suspend/resume, and concurrent open/close with IRQ activity.
