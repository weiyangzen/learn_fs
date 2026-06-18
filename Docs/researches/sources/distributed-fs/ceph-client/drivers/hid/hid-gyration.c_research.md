# sources/distributed-fs/ceph-client/drivers/hid/hid-gyration.c

Adds input quirks for Gyration remote controls. It maps Logitech-vendor-page usages to Linux media keys and converts one Generic Desktop event into a press/release pulse.

`gyration_input_mapping()` checks `HID_UP_LOGIVENDOR`, enables repeat, and maps usages to keys such as `KEY_HOME`, `KEY_DVD`, `KEY_PVR`, color keys, `KEY_MEDIA`, and `KEY_CAMERA`. `gyration_event()` detects Generic Desktop usage `0x82` and emits a synthetic press and release with `input_event()` and `input_sync()`.

There is no driver-private state. Input repeat and keybits are runtime input-device state. Dependencies are HID input hooks, Linux input key codes, and Gyration IDs from `hid-ids.h`.

Risks include a fixed vendor usage table that may not cover all remote variants and the event pulse path relying on mapped `usage->type`/`usage->code`. Test signals include each mapped vendor usage, repeat behavior, Generic Desktop `0x82` pulse handling, unrecognized fallback, and all matched products.
