# sources/distributed-fs/ceph-client/drivers/hid/hid-quirks.c

## Purpose

`hid-quirks.c` is the HID core quirk registry and lookup implementation. It combines static VID/PID tables, build-config-gated special-driver routing, ignore lists, mouse-interface ignore lists, and runtime module-parameter quirks into the bitmask returned to HID bus drivers. The file decides when a HID device should be ignored, when generic HID should defer to a specialized driver, and when device-specific parser/transport workarounds such as `HID_QUIRK_NOGET`, `HID_QUIRK_MULTI_INPUT`, `HID_QUIRK_ALWAYS_POLL`, or `HID_QUIRK_NO_INIT_REPORTS` should be enabled.

## Important APIs, Types, and Functions

- `hid_quirks[]`: alphabetically sorted static HID quirk table. Each row maps a bus/vendor/product match to a quirk bitmask in `driver_data`.
- `hid_have_special_driver[]`: compile-time conditional table of devices that should be routed to a specialized HID driver when that driver is enabled.
- `hid_ignore_list[]` and `hid_mouse_ignore_list[]`: static device tables for whole-device ignore and mouse-interface-only ignore behavior.
- `hid_ignore(struct hid_device *hdev)`: exported predicate used by HID transports to decide whether generic HID should bind at all.
- `struct quirks_list_struct`, `dquirks_list`, and `dquirks_lock`: runtime quirk list and serialization for module-parameter-provided overrides.
- `hid_modify_dquirk()`, `hid_exists_dquirk()`, `hid_remove_all_dquirks()`: dynamic quirk add/replace, lookup, and cleanup helpers.
- `hid_quirks_init(char **quirks_param, __u16 bus, int count)` and `hid_quirks_exit(__u16 bus)`: exported module lifecycle hooks for parsing `vendor:product:quirks` strings and removing bus-scoped dynamic entries.
- `hid_gets_squirk()` and `hid_lookup_quirk()`: static plus dynamic quirk resolution, with dynamic entries taking precedence.

## Control Flow

Normal lookup starts in `hid_lookup_quirk()`. It first handles special version-sensitive cases that bypass the table path: NCR USB devices always get `HID_QUIRK_NO_INIT_REPORTS`, and older Jabra Speak firmware revisions are ignored. It then locks `dquirks_lock`; if a dynamic quirk matches, its `driver_data` becomes the complete result, otherwise `hid_gets_squirk()` derives static bits from ignore tables, special-driver tables, the generic quirk table, and `hdev->initial_quirks`.

Ignore handling is separate. `hid_ignore()` first honors explicit `HID_QUIRK_NO_IGNORE` and `HID_QUIRK_IGNORE` bits already present on the device. It then evaluates hard-coded vendor/product/name/version ranges that cannot be represented cleanly in static tables, including Code Mercenaries IOWarrior, Logitech Harmony and AudioHub lookalike filtering, SoundGraph iMON ranges, Hanwang tablet ranges, Jess Yurex USBNONE, Velleman comedi devices, an Atmel V-USB radio, ELAN devices handled by elan-i2c, and Jieli devices distinguished by name and serial. It finally checks mouse-interface ignore and the static ignore table.

Runtime quirk setup in `hid_quirks_init()` parses strings as hex `vendor:product:quirks`, fills a `struct hid_device_id` with the caller-supplied bus, and calls `hid_modify_dquirk()`. Replacement builds a temporary `hid_device` and list item, searches for an existing matching item with `hid_match_one_id()`, replaces or appends under `dquirks_lock`, and frees the temporary device.

## State and Persistence Behavior

Static quirk tables are read-only for the kernel image lifetime. Dynamic quirks persist in `dquirks_list` until `hid_quirks_exit()` removes entries for a bus or `HID_BUS_ANY`. Dynamic entries are intentionally stronger than static quirks: if `hid_exists_dquirk()` returns a match, `hid_lookup_quirk()` does not OR in static bits. `hdev->initial_quirks` is preserved only through the static path.

## Dependencies and Integration Points

The file depends on HID matching APIs (`hid_match_id`, `hid_match_one_id`), Linux list/mutex/slab helpers, `hid-ids.h` VID/PID constants, and ELAN ACPI IDs from `linux/input/elan-i2c-ids.h`. Exported functions are consumed by HID transport modules and HID core initialization. Kconfig conditionals in `hid_have_special_driver[]` connect this file to many optional drivers such as Apple, Logitech, RMI, Retrode, Roccat, Sony, and multitouch-related drivers.

## Risks and Edge Cases

- Dynamic quirks replace static lookup rather than merging with it, so a module parameter can accidentally drop important static ignore or special-driver bits.
- `hid_modify_dquirk()` allocates `q_new` before knowing whether a replacement is needed; the ownership is correct, but future changes must keep the replacement/free path balanced.
- The static tables are long and manually sorted; duplicate or unsorted entries can hide maintenance errors.
- `hid_ignore()` contains name/serial string checks for reused USB IDs. Those are necessarily brittle and depend on transport-provided strings being initialized and NUL-terminated.
- The ELAN loop uses `strlen(elan_acpi_id[i].id)` as the sentinel; malformed table entries would affect matching.
- Version-specific bypasses in `hid_lookup_quirk()` return immediately and do not honor dynamic quirks.

## Test Signals

Useful signals include unit-style tests for static table matches, dynamic override precedence, malformed quirk parameter parsing, replacement of an existing dynamic quirk, bus-scoped dynamic cleanup, and explicit `NO_IGNORE`/`IGNORE` precedence. Integration coverage should confirm that devices in `hid_have_special_driver[]` get `HID_QUIRK_HAVE_SPECIAL_DRIVER` only when their Kconfig driver is enabled, ignored devices do not bind to generic HID, and mouse-ignore entries only affect USB mouse interfaces.
