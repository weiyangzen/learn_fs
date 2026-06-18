# sources/distributed-fs/ceph-client/drivers/hid/hid-icade.c

Translates ION iCade Bluetooth keyboard-style events into gamepad-style input events. iCade sends separate keyboard letters for button press and release; this driver maps them to directional keys and game buttons.

`struct icade_key` stores target key code and whether the source usage means press or release. `icade_usage_table` maps HID keyboard usages to target controls. `icade_find_translation()` bounds-checks lookups. `icade_input_mapping()` maps translated keyboard usages to EV_KEY targets and ignores the rest. `icade_event()` consumes source key-up events and translates source key-down events into press/release values on target controls. `icade_input_mapped()` finalizes EV_KEY capability bits while suppressing normal mapping.

The translation table is static and there is no per-device state or persistence. Dependencies include Bluetooth HID matching, HID input mapping/event hooks, Linux input key/button codes, and ION IDs from `hid-ids.h`.

Risks include table dependence on HID keyboard usage numbers, ignored non-table keys, and event synchronization relying on HID/input flow rather than explicit `input_sync()` here. Test signals include every press/release pair, ignored fake key-up events, unmapped usage suppression, Bluetooth match, key capability bits, and gamepad userspace interpretation.
