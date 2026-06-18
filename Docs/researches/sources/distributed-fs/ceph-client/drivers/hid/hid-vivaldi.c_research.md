# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi.c

Purpose: HID driver for ChromeOS Vivaldi keyboards, wiring the common function-row mapping helper and sysfs attribute group into HID devices in `HID_GROUP_VIVALDI`.

Important APIs, types, and functions: `vivaldi_probe()` devm-allocates `struct vivaldi_data`, attaches it as drvdata, parses HID, and starts hardware with default connections. `vivaldi_table[]` matches any bus/vendor/product in the Vivaldi HID group. The `hid_driver` sets `.feature_mapping = vivaldi_feature_mapping` and `.driver.dev_groups = vivaldi_attribute_groups`.

Control flow: probe only allocates state and starts HID; feature parsing and sysfs visibility are handled by common helpers during HID setup.

State and persistence: per-device `vivaldi_data` is devm-managed and persists for the HID device lifetime. It backs the function-row sysfs output. No persistent storage.

Dependencies and integration: depends on HID core, `input/vivaldi-fmap.h`, and `hid-vivaldi-common`. The match is group-based rather than VID/PID-specific.

Risks: because common code assumes drvdata begins with `struct vivaldi_data`, this driver must keep drvdata exactly that type or a struct embedding it first. Probe has no custom remove because devm and HID core handle resources.

Test signals: no automated tests. Validate by enumerating a Vivaldi keyboard, confirming HID parse/start, and reading the function row physical map sysfs file when the feature exists.
