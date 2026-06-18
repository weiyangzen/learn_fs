# sources/distributed-fs/ceph-client/drivers/input/keyboard/dlink-dir685-touchkeys.c

## Purpose

`dlink-dir685-touchkeys.c` supports the D-Link DIR-685 router's I2C Cypress MCU touchkey board. It maps a fixed set of front-panel touch bits to Linux keycodes and sets keypad backlight brightness during probe.

## Important APIs, Types, and Functions

- `struct dir685_touchkeys` stores device/client/input pointers, current key bitmap, and seven keycodes.
- `dir685_tk_probe()` allocates/registers the fixed input device, sends a brightness command, validates IRQ presence, and requests a threaded IRQ.
- `dir685_tk_irq_thread()` reads six bytes from I2C, extracts the big-endian key bitmap from bytes 4-5, diffs state, reports changed keys, and syncs.

## Control Flow

Probe initializes keycodes for up/down/left/right/enter/WPS/reserved, registers the input device, attempts to set brightness to maximum with a two-byte I2C write, and installs the IRQ thread. On IRQ, a six-byte message is read; changed bits among the fixed key set produce press/release reports.

## State and Persistence Behavior

`cur_key` persists the last 16-bit controller bitmap. Backlight brightness is written once at probe and not tracked afterward. No suspend/resume or nonvolatile state is implemented.

## Dependencies and Integration Points

The driver uses I2C master send/recv, input core, threaded IRQs, bitops, and OF/I2C matching for `dlink,dir685-touchkeys` / `dir685tk`.

## Risks and Edge Cases

The protocol is board-specific and assumes six-byte reads and key bits in the last two bytes. Short reads are handled but no recovery is attempted. `KEY_RESERVED` is cleared after capability setup for the unused seventh key. Missing IRQ fails probe after input registration, though devm/input cleanup will unwind on probe failure.

## Test Signals

Test six-byte read parsing, each mapped touchkey, simultaneous bits, short/failed reads, brightness write failure warning, missing IRQ, OF/I2C matching, and repeated press/release transitions.
