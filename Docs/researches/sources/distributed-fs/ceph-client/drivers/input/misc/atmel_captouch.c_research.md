<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c

Purpose: I2C input driver for an ATmega-based capacitive touch-button controller using a custom register protocol.

Important APIs/types/functions: `struct atmel_captouch_device` stores client, input, button count, keycodes, previous button state, and transfer buffer. `atmel_read()` sends register/length and validates the echoed register in the response. `atmel_captouch_isr()` reads `REG_KEY_STATE`, diffs it against `prev_btn`, and reports changed keys. Probe reads firmware keycodes and requests IRQ.

Control flow and state: probe verifies I2C functionality, reads the initial key state, allocates input, reads `autorepeat` and keycode array from device tree, registers input, and installs a threaded IRQ. IRQ reports only changed bits and then syncs.

State and persistence behavior: `prev_btn` persists in memory to detect edges. Key mapping is read from firmware and exposed through input keycode metadata. Hardware thresholds/reference/delta registers are defined but not configured by this driver.

Dependencies and integration points: depends on I2C transfer APIs, OF properties, Linux input, and threaded IRQs. Compatible is `atmel,captouch`.

Risks: `of_property_count_u32_elems(node, "linux,keymap")` is used while the array read uses `linux,keycodes`, which may be a property-name mismatch. Negative element counts are not checked before array read. No explicit `client->irq` validation before requesting IRQ.

Test signals: test valid/invalid DT key arrays, initial state read failure, echoed-register mismatch, changed-button reporting for multiple simultaneous keys, autorepeat flag, missing IRQ, and I2C short transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c -->
