# sources/distributed-fs/ceph-client/drivers/input/keyboard/sunkbd.c

## Purpose

This serio driver supports Sun Type 4/5 serial keyboards. It probes keyboard type and layout, translates Sun scancodes into Linux keycodes, handles LEDs and sound controls, and restores device state after keyboard resets.

## Important APIs, Types, and Functions

`sunkbd_keycode[128]` is the default scancode map. `struct sunkbd` stores keycodes, input/serio pointers, a reset work item, wait queue, name/phys strings, type, enabled flag, and reset/layout handshake state. `sunkbd_interrupt()` handles reset/layout replies, all-up markers, and key events. `sunkbd_event()` sends LED, click, and bell commands. `sunkbd_initialize()` resets/probes the keyboard. `sunkbd_reinit()` restores LEDs/beeps after reset.

## Control Flow

Connect allocates state/input, opens the serio port, sends reset, waits for the keyboard ID, optionally queries Type 4 layout to distinguish Type 5, initializes input capabilities, enables event processing under `serio_pause_rx`, and registers input. Runtime bytes either complete reset/layout waits, schedule reinitialization after reset notifications, or report key press/release events if enabled. Input LED/sound events send command bytes back over serio.

## State and Persistence Behavior

The driver persists keyboard type, keymap, enabled flag, reset/layout handshake values, and desired LED/sound state via input core. After keyboard reset, delayed work waits for the ID byte and re-sends LED/click/bell state if the device is still enabled. Disconnect disables processing, cancels work, unregisters input, and closes serio.

## Dependencies and Integration Points

It depends on serio RS232 transport, Sun keyboard protocol constants, input LED/SND event callbacks, wait queues, workqueues, and serio matching for both `SERIO_SUNKBD` and probe-capable `SERIO_UNKNOWN`.

## Risks and Edge Cases

The protocol uses volatile `s8` handshake fields and wait queues; reset bytes arriving during disconnect must be coordinated with `enabled`. Unknown scancodes log warnings. The driver probes unknown serio ports, so reset timeouts must avoid false positives. All-up is ignored rather than releasing tracked keys, because the driver does not track key-down state.

## Test Signals

Test Type 4 and Type 5 identification, layout timeout, key press/release streams, unknown scancodes, LED/click/bell writes, reset notification and reinit work, disconnect during reset wait, and matching on `SERIO_UNKNOWN`.
