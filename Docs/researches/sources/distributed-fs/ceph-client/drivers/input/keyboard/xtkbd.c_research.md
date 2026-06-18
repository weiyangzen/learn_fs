# sources/distributed-fs/ceph-client/drivers/input/keyboard/xtkbd.c

## Purpose

This serio driver supports legacy XT keyboards. It translates XT set-like scancodes from a serio port into Linux key events and exposes an editable keycode table with repeat capability.

## Important APIs, Types, and Functions

`xtkbd_keycode[256]` is the default map. `struct xtkbd` stores the keycode table, input device, serio port, and physical path. `xtkbd_interrupt()` ignores `0xe0`/`0xe1` emulation prefixes, decodes release bit and low seven-bit key index, and reports mapped keys. `xtkbd_connect()` allocates state/input, opens serio, registers input, and installs driver data. `xtkbd_disconnect()` closes/unregisters/frees resources.

## Control Flow

The serio core calls connect for `SERIO_XT` ports. Connect initializes input identity as `BUS_XTKBD`, marks key/repeat events, copies the keymap, opens the serio device, and registers input. Each incoming byte is processed immediately; mapped scancodes emit press/release and sync, while unmapped scancodes log warnings.

## State and Persistence Behavior

The driver does not track modifier or prefix state, so `0xe0` and `0xe1` prefixes are discarded rather than extending the next code. Runtime state is limited to the keycode array and registration pointers.

## Dependencies and Integration Points

It depends on serio XT transport, input key event APIs, and manual allocation/free paths. The serio ID table matches any XT protocol ID/extra.

## Risks and Edge Cases

Ignoring emulation prefixes limits support for extended keys. `kmalloc_obj()` does not zero memory, but all fields used by the driver are initialized before use. The loop setting key bits uses `i < 255`, leaving index 255 out despite a 256-entry table. Unknown scancodes can spam kernel warnings.

## Test Signals

Test attach/detach, all mapped press/release scancodes, prefix byte handling, unmapped warning paths, keycode remapping, input repeat exposure, serio open failure cleanup, and disconnect during input activity.
