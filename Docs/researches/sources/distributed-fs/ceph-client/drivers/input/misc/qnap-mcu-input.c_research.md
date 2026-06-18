# sources/distributed-fs/ceph-client/drivers/input/misc/qnap-mcu-input.c

## Purpose
`qnap-mcu-input.c` exposes QNAP MCU power-button state and MCU-controlled beeper commands through the Linux input subsystem. It polls the MCU for a slow power-key state and accepts `SND_BELL`/`SND_TONE` events to trigger MCU beeps.

## Important APIs, Types, and Functions
`struct qnap_mcu_input_dev` stores the input device, parent `struct qnap_mcu`, device pointer, beep work, and pending beep type. `qnap_mcu_input_poll()` sends `@CV` to read power state. `qnap_mcu_input_event()` validates sound events and schedules work. `qnap_mcu_input_beeper_work()` sends `@C2` for bell or `@C3` for tone through `qnap_mcu_exec_with_ack()`. Probe sets polling interval and input capabilities.

## Control Flow
Probe obtains the parent MCU from driver data, allocates input, configures `KEY_POWER`, `SND_BELL`, and `SND_TONE`, initializes beep work, sets up input polling at 500 ms, and registers the device. Polling sends a command, validates that the first three reply bytes echo the command, converts ASCII state byte `reply[3] - 0x30`, and reports `KEY_POWER`. Sound events reject unsupported or negative values, ignore value zero, remember the beep type, and schedule an asynchronous MCU command.

## State and Persistence Behavior
Persistent state is limited to the pending `beep_type` and the input poller registration. The MCU owns actual beep duration and power-key state. No local debounce or power-key persistence is maintained beyond input core's current key state.

## Dependencies and Integration Points
The driver depends on the QNAP MCU MFD interface, platform child enumeration, input polling, workqueues, and UAPI input event codes. It integrates with MCU command protocol and userspace evdev sound/key consumers.

## Risks and Edge Cases
The poller silently ignores MCU command errors, so userspace may see stale key state. A malformed echo logs an error every poll, potentially noisy on protocol mismatch. `reply[3] - 0x30` is not range-checked, so malformed ASCII can report values outside 0/1. `beep_type` is updated without locking before scheduling work; rapid sound events coalesce to the last type before the worker runs.

## Test Signals
Validate probe with a parent MCU, normal `@CV` replies for press/release, malformed echo handling, MCU errors, bell/tone events, zero/negative sound values, close canceling pending beep work, and polling interval behavior.
