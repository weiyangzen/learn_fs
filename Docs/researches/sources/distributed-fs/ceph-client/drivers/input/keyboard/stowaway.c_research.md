# sources/distributed-fs/ceph-client/drivers/input/keyboard/stowaway.c

## Purpose

This serio driver supports Stowaway RS232 keyboards. It maps one-byte Stowaway scancodes to Linux keycodes, reports press/release events, and registers as a serio protocol driver for `SERIO_STOWAWAY`.

## Important APIs, Types, and Functions

`skbd_keycode[128]` is the static scancode-to-keycode map. `struct skbd` stores an editable keycode table, input device, serio port, and physical path. `skbd_interrupt()` decodes the release bit and key mask. `skbd_connect()` allocates state/input, opens the serio port, initializes input capabilities, and registers the device. `skbd_disconnect()` closes and unregisters resources.

## Control Flow

When a matching serio port appears, connect allocates driver state and input, copies the default map, sets bus/vendor/product IDs, marks key and repeat capability, opens the serio device, and registers input. Each received byte is handled synchronously by the serio interrupt callback: the low seven bits select a keycode, bit 7 means release, and nonzero mapped keys are reported then synced.

## State and Persistence Behavior

There is no protocol state machine; only the keycode array and input registration persist. The driver does not track key-down state itself and trusts the keyboard's make/break stream.

## Dependencies and Integration Points

It depends on the serio core, RS232 transport, input key events, and `SERIO_STOWAWAY` protocol matching. Users can inspect or remap the exposed keycode table via normal input mechanisms.

## Risks and Edge Cases

Unknown or zero-mapped scancodes are silently ignored, so hardware variants may appear to drop keys. There is no resynchronization or error handling for corrupt serial bytes. Allocation uses manual cleanup paths, and connect failure must close the serio port only after it was opened.

## Test Signals

Test serio attach/detach, every mapped scancode press and release, zero-mapped scancode ignoring, input keycode remapping, repeat capability exposure, open failure unwind, and disconnect while events are in flight.
