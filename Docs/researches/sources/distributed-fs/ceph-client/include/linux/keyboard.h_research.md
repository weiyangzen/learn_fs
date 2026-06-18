# sources/distributed-fs/ceph-client/include/linux/keyboard.h

## Purpose

`keyboard.h` is the kernel-side keyboard notifier and keymap declaration header. It exposes the global keymap arrays from the VT/keyboard layer and the notifier payload used by consumers that need to observe keyboard events. The source was read as a complete 21-line file.

## Important APIs, Types, and Functions

The header declares `key_maps[MAX_NR_KEYMAPS]`, `plain_map[NR_KEYS]`, `struct keyboard_notifier_param`, `register_keyboard_notifier()`, and `unregister_keyboard_notifier()`. The notifier payload carries the `vc_data` console, key press direction, shift mask, LED state, and event value, which may be keycode, Unicode value, or keysym depending on notification stage.

## Control Flow

There is no local executable flow. Keyboard drivers and VT input paths update state and invoke notifier blocks; interested subsystems register a `notifier_block` and inspect `keyboard_notifier_param` for each keyboard transition.

## State and Persistence Behavior

The header declares global keymap storage but owns no lifetime logic. Notifier registrations persist until unregistered, so clients must unregister before module removal.

## Dependencies and Integration Points

It depends on `uapi/linux/keyboard.h` for keymap sizing and constants and integrates with the console/VT keyboard event pipeline.

## Risks and Edge Cases

The value field is stage-dependent, so consumers must know the notification context. Notifier callbacks run in the input path and should avoid blocking or mutating keymaps without proper synchronization.

## Test Signals

Compile coverage with VT enabled, notifier registration/unregistration smoke tests, keyboard event delivery tests, and module unload tests that verify no stale notifier remains.
