# sources/distributed-fs/ceph-client/drivers/input/keyboard/atakbd.c

## Purpose

`atakbd.c` is the Atari m68k keyboard input-layer driver. Low-level ACIA protocol handling is done by Atari architecture code; this file maps Atari scancodes to Linux keycodes and reports key events through one `input_dev`.

## Important APIs, Types, and Functions

- `atakbd_keycode[]` is the static American-layout scancode-to-keycode table.
- `atakbd_interrupt()` is installed into `atari_input_keyboard_interrupt_hook` and reports key press/release events.
- `atakbd_init()` validates Atari hardware, initializes the architecture keyboard core, allocates/registers the input device, fills key capabilities, and installs the hook.
- `atakbd_exit()` removes the hook and unregisters the input device.

## Control Flow

Module init runs only on Atari systems with ST MFP hardware. After `atari_keyb_init()` succeeds, the input device is registered and the architecture keyboard interrupt path calls `atakbd_interrupt(scancode, down)`. The callback ignores mouse-like high scancodes and reports mapped key state plus `input_sync()` for normal keyboard scancodes.

## State and Persistence Behavior

The file has a global `atakbd_dev` pointer and a static mutable keycode table exposed to the input core. It does not debounce or persist key state itself; press/release state comes from the architecture keyboard layer.

## Dependencies and Integration Points

It depends on Atari-specific headers and symbols (`MACH_IS_ATARI`, `ATARIHW_PRESENT`, `atari_keyb_init`, `atari_input_keyboard_interrupt_hook`) plus Linux input core. It is tightly coupled to m68k Atari platform code rather than generic platform discovery.

## Risks and Edge Cases

Scancode `0` or unmapped table entries can report `KEY_RESERVED` if delivered. High scancodes are logged as unhandled and may include mouse data from the shared ACIA path. The global hook/device design assumes only one Atari keyboard and careful unload ordering.

## Test Signals

Boot/module-load on Atari hardware or emulator, keymap coverage including keypad/arrows/help/undo, repeated press/release delivery, high-scancode logging, unload/reload hook cleanup, and build coverage for m68k Atari configs are useful signals.
