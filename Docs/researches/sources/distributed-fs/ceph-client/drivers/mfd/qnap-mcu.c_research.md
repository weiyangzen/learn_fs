# sources/distributed-fs/ceph-client/drivers/mfd/qnap-mcu.c

## Purpose
`qnap-mcu.c` is the serdev MFD core for QNAP NAS microcontrollers connected over UART. It implements the command/reply protocol, exposes exported command helpers, reads firmware version, registers a poweroff handler, and adds EEPROM, input, LED, and hwmon child devices.

## Important APIs, Types, And Functions
`struct qnap_mcu_reply` tracks a single expected reply buffer, length, bytes received, and completion. `struct qnap_mcu` holds serdev, bus lock, reply state, variant data, and version. `qnap_mcu_exec()` and `qnap_mcu_exec_with_ack()` are exported to children. `qnap_mcu_csum()`, `qnap_mcu_verify_checksum()`, `qnap_mcu_receive_buf()`, `qnap_mcu_get_version()`, and `qnap_mcu_power_off()` implement protocol and lifecycle.

## Control Flow
Probe allocates state, selects variant data, initializes lock/completion, opens serdev, sets baud/flow/parity, reads MCU version with `%V`, registers a `SYS_OFF_MODE_POWER_OFF_PREPARE` handler, copies variant platform data into each MFD cell, and adds child devices. Commands are serialized by `bus_lock`; transmit appends XOR checksum, receive accumulates the exact expected length or early error response, completion wakes the caller, and checksum/error codes are validated before copying payload.

## State And Persistence
Runtime state is one in-flight reply and a firmware version cache. Persistent behavior is the MCU's external state: drive power, LEDs, fan, EEPROM, and poweroff command effects. Variant data includes baud rate, drive count, fan PWM range, and USB LED support.

## Dependencies And Integration Points
It depends on serdev, MFD core, reboot/sys-off APIs, `linux/mfd/qnap-mcu.h`, compatibles `qnap,ts133-mcu`, `qnap,ts233-mcu`, and `qnap,ts433-mcu`, plus child drivers named `qnap-mcu-eeprom`, `qnap-mcu-input`, `qnap-mcu-leds`, and `qnap-mcu-hwmon`.

## Risks
Only one command can be active; unsolicited data is discarded with a warning. Error replies are shorter than normal replies and depend on early detection. `memcpy(reply_data, rx, reply_data_size)` copies the requested payload size even if an error-sized reply reached completion, but errors are checked before copy. Global cell platform-data mutation in probe assumes one active variant at a time or identical static cell reuse semantics.

## Test Signals
Protocol tests for checksum, split receive, generic/checksum error replies, timeouts, ACK validation, version command, poweroff command, all variants, child command serialization, and unsolicited UART bytes are important.
