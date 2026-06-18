# sources/distributed-fs/ceph-client/drivers/input/matrix-keymap.c

## Purpose

This shared helper implements matrix-keypad binding support for input drivers. It parses row/column dimensions and encoded keymap entries, validates them, allocates or fills keycode arrays, and sets input key capabilities.

## Important APIs, Types, and Functions

`matrix_keypad_parse_properties()` reads `keypad,num-rows` and `keypad,num-columns`. `matrix_keypad_build_keymap()` is the exported conversion API used by many keypad drivers. `matrix_keypad_parse_keymap()` reads `linux,keymap` or a caller-specified property into temporary memory. `matrix_keypad_map_key()` decodes `KEY_ROW`, `KEY_COL`, and `KEY_VAL`, validates bounds, stores the keycode at `MATRIX_SCAN_CODE()`, and sets the key bit.

## Control Flow

Callers set `input_dev->dev.parent`, provide dimensions and optionally platform `matrix_keymap_data` and storage. The build function computes `row_shift` from columns, allocates managed storage if needed, assigns input keycode metadata, sets `EV_KEY`, then either maps platform entries or parses firmware property entries. After successful mapping it clears `KEY_RESERVED`.

## State and Persistence Behavior

The helper owns no global state. It mutates the caller's input device keycode pointer, keycode size/count, event bits, and key bitmask. When it allocates storage, memory is devm-managed by the input parent device.

## Dependencies and Integration Points

It depends on the generic device property API, input subsystem key bitmaps, matrix-keypad encoding macros, and devm allocation. It is exported for GPL and non-GPL symbol users as currently declared (`EXPORT_SYMBOL_GPL` for parse properties, `EXPORT_SYMBOL` for build keymap).

## Risks and Edge Cases

`size > max_keys` rejects keymaps with more entries than matrix cells, but sparse maps larger than cells are invalid even if duplicates exist. Duplicate scan codes overwrite prior keycodes while leaving the old key bit set. Keycode values are not checked against `KEY_MAX` here. Callers that pass wrong dimensions produce incorrect row shifts and scan-code indexing.

## Test Signals

Test missing/malformed properties, invalid rows/columns in entries, duplicate entries, automatic allocation, caller-supplied keymap storage, custom property names, sparse keymaps, oversized keymap arrays, and integration with drivers that use non-power-of-two column counts.
