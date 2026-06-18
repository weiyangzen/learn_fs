# sources/distributed-fs/ceph-client/drivers/hid/hid-tivo.c

Purpose: supplies key mapping overrides for TiVo Slide Bluetooth and USB remotes whose vendor and consumer usages do not map to the desired Linux input keys through generic HID.

Important APIs, types, and functions: `tivo_input_mapping()` is the only behavior hook. It uses `hid_map_usage_clear()` through `tivo_map_key_clear()` to remap TiVo vendor page usages and selected consumer page usages to `KEY_MEDIA`, `KEY_TV`, keypad plus/minus, `KEY_ENTER`, and `KEY_INFO`. `tivo_devices[]` matches Bluetooth and USB TiVo Slide variants.

Control flow: HID input mapping calls the driver for each usage. If the usage page is TiVo vendor or consumer and the usage code is recognized, the function maps and returns `1`, preventing generic mapping. Unknown usages return `0` so generic HID mapping can proceed.

State and persistence: stateless; no drvdata, allocations, probe, remove, or persistent data.

Dependencies and integration: integrates with HID input mapping and Linux input key codes. Device IDs come from `hid-ids.h`, and the module registers a `hid_driver` named `tivo_slide`.

Risks: mappings are exact constants; new remote firmware or alternate usage codes fall through to generic behavior. Because the function overrides consumer usages that already have defaults, regressions would be user-visible key semantics rather than crashes.

Test signals: no in-tree tests. Validation is by pairing/connecting the listed remotes and checking evtest/libinput events for TiVo, Live TV, thumbs up/down, Enter/Last, and Info.
