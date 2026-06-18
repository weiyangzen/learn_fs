<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c

## Purpose
`e3x0-button.c` is a platform input driver for the NI Ettus Research USRP E3x0 power button. It reports `KEY_POWER` from separate press and release IRQ lines.

## Important APIs, Types, and Functions
`e3x0_button_press_handler()` reports `KEY_POWER` down, emits a wakeup event, and syncs input. `e3x0_button_release_handler()` reports key up. `e3x0_button_suspend()` and `e3x0_button_resume()` toggle IRQ wake on the named `press` IRQ if the device may wake the system.

## Control Flow
Probe retrieves `press` and `release` IRQs by name, allocates a devm input device, sets name/phys/parent and `EV_KEY/KEY_POWER`, requests both IRQs with devm, registers input, and marks the device wake-capable. Runtime behavior is direct IRQ-to-input reporting with no deferred work.

## State and Persistence Behavior
The input core tracks key state. Wake capability is device-lifetime state managed during suspend/resume. There is no persistent storage or private driver allocation beyond the input device.

## Dependencies and Integration Points
The driver integrates with platform devices, OF compatible `ettus,e3x0-button`, input, IRQ, and PM wake support. Firmware must provide named `press` and `release` IRQ resources.

## Risks and Test Signals
Risks are mostly resource-description errors and wake IRQ enable/disable failures not being checked. Tests should validate missing IRQ handling, press/release event order, wake event generation, input registration failure cleanup, and suspend/resume behavior with wakeup enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c -->
