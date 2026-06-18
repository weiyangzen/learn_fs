# sources/distributed-fs/ceph-client/drivers/input/touchscreen/zforce_ts.c

## Purpose
`zforce_ts.c` is an I2C multitouch driver for Neonode zForce controllers. It implements the framed command/response protocol, configures resolution and scan frequency, reports up to two contacts, and supports wakeup-aware suspend.

## Important APIs, Types, And Functions
`struct zforce_ts` stores I2C/input handles, touchscreen properties, reset/interrupt GPIOs, suspend flags, boot/version fields, and command completion state. `zforce_send_wait()` sends a framed command and waits for the matching response. `zforce_start()` initializes, sets resolution, scan frequency, dual-touch config, requests data, and waits for calibration. `zforce_irq_thread()` drains packets while the level interrupt GPIO is active, handles notifications/responses, and completes commands. `zforce_touch_event()` reports MT slots and area/orientation.

## Control Flow
Probe obtains GPIOs using modern or legacy bindings, enables `vdd`, registers reset cleanup, initializes input axes from legacy properties plus touchscreen properties, requests IRQ, releases reset, waits for bootcomplete, queries status/version, stops the device, marks wakeup capable, and registers input. Input open starts the controller; close deactivates it. Suspend may start the device solely for wakeup, enable IRQ wake, or stop/disable IRQ when not a wake source; resume reverses that state.

## State And Persistence
Runtime state includes command wait/result, boot/version info, suspended/suspending flags, and input MT tracking. Hardware configuration is applied at each start. No persistent controller storage is changed.

## Dependencies And Integration Points
It uses I2C, GPIO descriptors, regulator `vdd`, input MT, touchscreen property parsing, completions, PM wakeup helpers, OF matching, and asynchronous probe preference.

## Risks
`zforce_send_wait()` assigns `ret = ts->command_result` but returns `0`, so nonzero command result payloads may not propagate as intended. Touch IDs are decremented before slot selection; invalid zero IDs would underflow. Level IRQ draining depends on optional GPIO state. Suspend has careful wakeup/event behavior and needs race testing.

## Test Signals
Test bootcomplete timeout, command response matching and timeout, nonzero command result propagation, packet framing errors, coordinate bounds, invalid touch IDs, open/close start-stop errors, wakeup and non-wakeup suspend/resume, legacy GPIO/property bindings, and reset cleanup.
