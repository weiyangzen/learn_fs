# sources/distributed-fs/ceph-client/drivers/input/touchscreen/zinitix.c

## Purpose
`zinitix.c` is an I2C multitouch driver for Zinitix BT/AT touchscreen controllers. It controls regulators, performs the vendor power-on sequence, configures controller registers, reports up to five MT contacts, and optionally reports capacitive key events.

## Important APIs, Types, And Functions
`struct bt541_ts_data` stores client/input, touchscreen properties, regulators, mode, keycodes, version cache, and variant-specific icon status register. I2C helpers perform two-step register reads and little-endian writes. `zinitix_send_power_on_sequence()` sends vendor initialization commands. `zinitix_init_touch()` resets the controller, caches version data, chooses icon status register, programs resolution/finger count/buttons/mode/interrupt flags, and clears pending interrupts. `zinitix_ts_irq_handler()` reads `struct touch_event`, reports keys and per-finger MT events, then clears interrupt status.

## Control Flow
Probe checks I2C support, gets regulators with compatibility names for older DTs, requests a no-auto-enable threaded IRQ, parses optional `linux,keycodes`, initializes and registers input, validates `zinitix,mode` as mode 2, and leaves the device off until open. Open enables regulators, delays, performs power sequence and controller init, then enables IRQ. Close disables IRQ and regulators. Suspend/resume stop/start only if input is enabled.

## State And Persistence
Version information and icon register selection are cached after first init. Runtime power is regulator-backed. Controller configuration is rewritten on each start. No flash or nonvolatile state is changed.

## Dependencies And Integration Points
It integrates I2C, regulator bulk APIs, input MT, touchscreen properties, optional `linux,keycodes`, OF compatible table, IRQF_NO_AUTOEN, and system sleep PM.

## Risks
If `zinitix_start()` fails after regulators are enabled, the error path does not immediately disable them. The driver only supports touch mode 2. Many register constants are unused, indicating broader hardware features not implemented. IRQ handler always attempts to clear interrupt even after read failure.

## Test Signals
Test regulator naming fallback, power-on sequence failures and cleanup, required touchscreen size properties, keycode parsing limits, mode validation, version/icon-register selection, finger down/move/up and key events, interrupt clear on failures, and suspend/resume while input is open.
