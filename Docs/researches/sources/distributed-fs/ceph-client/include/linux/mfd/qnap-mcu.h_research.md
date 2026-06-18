# sources/distributed-fs/ceph-client/include/linux/mfd/qnap-mcu.h

## Purpose
`qnap-mcu.h` defines the shared interface for a QNAP MCU MFD core and its child devices. It centralizes variant data and command execution helpers for features such as drive bays, fan control, and LEDs.

## Important APIs, Types, And Constants
The file forward-declares `struct qnap_mcu`. `struct qnap_mcu_variant` records serial baud rate, number of drives, minimum and maximum fan PWM values, and whether a USB LED exists. `qnap_mcu_exec()` sends command bytes and receives a reply. `qnap_mcu_exec_with_ack()` sends command bytes and expects an acknowledgment without exposing a caller-provided reply buffer.

## Control Flow And State
Child drivers compose MCU command frames and call the core execution function. The core likely serializes commands over UART/serdev, validates reply size, and returns status. Variant data selected by compatible string determines valid fan PWM ranges, drive count, and optional LED functionality. The ack helper is a convenience path for state-changing commands where a structured reply is not needed.

## State And Persistence Behavior
The header has no stateful implementation, but MCU state is external and can include fan PWM duty, LED state, drive presence/status, and controller firmware behavior. Runtime state is hidden inside `struct qnap_mcu`. Commands may change persistent or semi-persistent MCU settings depending on firmware.

## Dependencies And Integration Points
The header depends on `linux/types.h`. It integrates with MFD core, hwmon/fan, LED, storage-bay, or platform child drivers. Command buffer size and reply layout are firmware ABI, so all child drivers depend on the same framing semantics.

## Risks
Command/reply buffers are raw `u8` arrays with explicit sizes, so callers must avoid stack lifetime mistakes, undersized replies, and protocol mismatches. Fan PWM min/max are variant-specific and should be enforced before sending commands. A wrong variant can expose non-existent drives or LEDs.

## Test Signals
Tests should cover command serialization, reply length validation, ack success/failure paths, timeout/error propagation, variant selection, fan PWM clamping, and optional USB LED handling. Hardware-in-loop tests should confirm command ordering and concurrent child access.
