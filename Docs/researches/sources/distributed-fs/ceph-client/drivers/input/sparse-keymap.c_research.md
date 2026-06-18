# sources/distributed-fs/ceph-client/drivers/input/sparse-keymap.c

## Purpose
`sparse-keymap.c` provides shared helpers for drivers whose firmware scan codes are sparse rather than dense arrays. It copies a `struct key_entry` table into the input device, sets event capabilities, implements input-core get/set keycode callbacks, and reports key or switch events by scancode.

## Important APIs, types, and functions
Exported APIs are `sparse_keymap_setup()`, `sparse_keymap_entry_from_scancode()`, `sparse_keymap_entry_from_keycode()`, `sparse_keymap_report_entry()`, and `sparse_keymap_report_event()`. Internal helpers locate entries by input keymap index or scancode and compute the user-visible key index among `KE_KEY` entries.

## Control flow
Setup counts entries through `KE_END`, devm-duplicates the map, optionally invokes a caller setup callback for each entry, and sets `EV_KEY`, `EV_SW`, `EV_MSC`, `MSC_SCAN`, key bits, or switch bits according to entry type. Keycode get/set use `INPUT_KEYMAP_BY_INDEX` or scalar scancode lookup. Reporting emits MSC scan and key state for keys, optional autorelease, or switch state for `KE_SW` and `KE_VSW`; unknown scan codes are reported as `KEY_UNKNOWN` for diagnostics.

## State and persistence
The copied keymap is stored in `input_dev->keycode` and freed with the device via devm. Runtime remapping mutates the copied `key_entry.keycode` and updates `dev->keybit`; it does not change the original static map or persist across driver rebind.

## Dependencies and integration points
The helper is part of the input core support library and depends on `linux/input/sparse-keymap.h`, input keymap callbacks, devres allocation, and input event reporting. Platform hotkey and special-button drivers commonly call it during probe.

## Risks
`map_size` includes the `KE_END` entry and is assigned to `keycodemax`, so users of index-based APIs must remember that only `KE_KEY` entries are indexable. Setkeycode clears the old key bit only when no other entry uses it, but it does not validate whether the new keycode is in a desired driver-specific range. Unknown scancodes intentionally emit `KEY_UNKNOWN`, which can surprise tests expecting no event.

## Test signals
Unit-style tests should cover setup with key, switch, virtual-switch, and custom setup callbacks; get/set by index and scancode; duplicate keycodes; unknown scancode reporting; autorelease behavior; and preservation of switch semantics.
