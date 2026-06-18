# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_i2c.c

## Purpose
`wacom_i2c.c` is an I2C input driver for Wacom EMR pen digitizers. It queries feature report 3 for device limits and reports stylus proximity, buttons, eraser, coordinates, and pressure from interrupt packets.

## Important APIs, Types, And Functions
`struct wacom_features` holds max X/Y/pressure and firmware version. `struct wacom_i2c` stores client/input, receive buffer, proximity state, and current tool. `wacom_query_device()` sends an I2C feature-report request and decodes little-endian feature fields. `wacom_i2c_irq()` receives a 19-byte report and emits `BTN_TOOL_PEN`, `BTN_TOOL_RUBBER`, `BTN_TOUCH`, stylus buttons, `ABS_X`, `ABS_Y`, and `ABS_PRESSURE`.

## Control Flow
Probe validates plain I2C support, queries features, allocates input state, configures axes and keys, requests a threaded IRQ, disables it until open, and registers input. Open enables the IRQ; close disables it. PM suspend disables the IRQ and resume enables it unconditionally.

## State And Persistence
Runtime state tracks whether a tool is in proximity and whether the current tool is pen or rubber. Device features are read at probe and used for input limits. No persistent configuration is written.

## Dependencies And Integration Points
It depends on I2C transfers, unaligned little-endian helpers, threaded IRQs, and input stylus event conventions.

## Risks
Resume enables IRQ even if the input device was closed before suspend, which may alter IRQ balance depending on PM path. The IRQ handler ignores short positive reads and treats all errors as handled. Feature version is stored in a `char`, though read as 16-bit.

## Test Signals
Test query transfer failures and short transfer detection, open/close IRQ balancing, pen versus eraser transitions, button/proximity reports, suspend/resume while closed and open, and malformed packet lengths.
