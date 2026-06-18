<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c

## Purpose
`stmfts.c` is an I2C driver for STMicroelectronics FTS touchscreens. It handles regulator sequencing, controller reset/sleep/calibration commands, event-stack parsing, optional hover and touch-key support, optional key LED regulator control, runtime/system PM, and several read-only/sysfs controls.

## Important APIs, Types, And Functions
`struct stmfts_data` stores client, input device, LED class device, mutex, touchscreen properties, `vdd`/`avdd` regulators, optional `ledvdd`, chip/config/firmware IDs, a 256-byte event buffer, command completion, and flags for keys, LED, hover, and running state. `stmfts_read_events()` uses raw I2C transfer to read 32 eight-byte events, bypassing SMBus block size limits. `stmfts_parse_events()` dispatches contact enter/motion/leave, hover, key, error, and controller-ready events. `stmfts_command()` writes a command and waits up to one second for IRQ parsing to complete `cmd_done`.

## Control Flow
Probe verifies I2C capabilities, allocates state, initializes mutex/completion, gets regulators, allocates input, parses touchscreen properties, configures MT/pressure/orientation/distance axes and optional `KEY_MENU`/`KEY_BACK`, requests the IRQ with `IRQF_NO_AUTOEN`, powers on the controller, registers cleanup, registers input, optionally registers an LED class device for touch-key backlight, enables runtime PM, and async suspend. `stmfts_power_on()` enables regulators, reads info, enables IRQ, issues system reset, sleep out, optional tuning, full calibration, then leaves the controller asleep until input open. Input open resumes runtime PM and enables sensing; close disables sensing/key/hover and runtime-suspends.

## State And Persistence
Driver state includes chip metadata, hover enable, running flag, LED state, and command completion state. Sysfs exposes chip/config/firmware IDs, status, and read/write `hover_enable`. LED state is controlled through the LED subsystem and optional `ledvdd`. Hardware tuning/calibration is performed at power-on but not persisted by this driver.

## Dependencies And Integration Points
It uses I2C, regulators, input MT, touchscreen helpers, IRQ completions, mutex guards, LED classdev, sysfs groups, runtime PM/system PM, and OF/I2C matching. Touch-key LEDs depend on a separate `ledvdd` regulator.

## Risks
Command completion depends on IRQ delivery while power-on is running; bad IRQ wiring can turn commands into one-second timeouts. System suspend powers off regulators even if runtime state says running. Event parsing calls `input_sync()` per contact, which is simpler but can produce more syncs than frame-oriented drivers. Optional LED setup failure is non-fatal and leaves `ledvdd = NULL`.

## Test Signals
Check sysfs identity/status files, command timeouts with IRQ disabled, hover enable toggles while opened and closed, touch-key and LED behavior when `touch-key-connected` is present, runtime PM open/close, and system suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c -->
