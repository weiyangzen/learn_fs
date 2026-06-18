# sources/distributed-fs/ceph-client/drivers/firewire/device-attribute-test.c

### Purpose
`device-attribute-test.c` is a KUnit test file included directly by `core-device.c` when `CONFIG_FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST` is enabled. It validates FireWire device and unit sysfs attribute helpers and modalias ID extraction against simple and legacy AV/C configuration ROM layouts.

### Important APIs, Types, And Functions
The test data are `simple_avc_config_rom[]` and `legacy_avc_config_rom[]`. Test cases are `device_attr_simple_avc()` and `device_attr_legacy_avc()`, registered through `device_attr_test_cases` and `device_attr_test_suite`. The tests call internal static helpers from `core-device.c`, including `is_fw_device()`, `is_fw_unit()`, `fw_device()`, `fw_unit()`, `fw_parent_device()`, `show_immediate()`, `show_text_leaf()`, `config_rom_attributes[]`, and `get_modalias_ids()`.

### Control Flow, State, And Persistence
Each test builds static fake `fw_device` and `fw_unit` instances with the same device types used by production code and points them at an in-memory ROM. It allocates a page buffer, asserts type conversion helpers, checks immediate sysfs values and text leaf strings, frees the buffer, and verifies extracted modalias id arrays. The simple AV/C case expects root vendor/model text and unit specifier/version values. The legacy case checks a vendor directory layout where root/vendor/unit directories contribute different IDs and text leaf visibility.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on being textually included in `core-device.c` so it can access static functions and device types; it is intentionally not standalone. It integrates with KUnit and `FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST`. Risks include fragile coupling to `config_rom_attributes[]` ordering, static fake devices bypassing full device initialization, and ROM length comments using quadlets while production paths use byte lengths elsewhere. Test signals are direct: KUnit TAP output for `firewire-device-attribute`, expected sysfs strings, negative lookups for absent attributes, and modalias ID arrays for both AV/C layouts.
