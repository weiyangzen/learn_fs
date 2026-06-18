# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.c

Purpose: shared helpers for ChromeOS Vivaldi keyboards that expose the physical function-row map through HID feature reports and sysfs.

Important APIs, types, and functions: `vivaldi_feature_mapping()` parses Google vendor function-row physical-map usages. It assumes `hid_get_drvdata(hdev)` begins with `struct vivaldi_data`, fetches the feature report with `hid_hw_raw_request()`, feeds it back through `hid_report_raw_event()` so field values are decoded, and stores each ordinal value in `data->function_row_physmap`. `function_row_physmap_show()` delegates formatting to `vivaldi_function_row_physmap_show()`. `vivaldi_is_visible()` hides the sysfs file until at least one function-row key was discovered. `vivaldi_attribute_groups` exports the sysfs attribute group.

Control flow: during feature mapping, only fields whose logical usage is the Google function-row physical map and whose usage page is ordinal are processed. The helper handles unnumbered reports by accounting for the report-ID byte behavior of `hid_hw_raw_request()`.

State and persistence: updates `struct vivaldi_data` in HID drvdata with `num_function_row_keys` and physical map entries. Sysfs exposes current in-memory data; no persistent storage.

Dependencies and integration: depends on HID feature reports, `input/vivaldi-fmap.h`, sysfs attribute groups, and exported symbols for use by Vivaldi-specific HID drivers.

Risks: drvdata layout is a documented assumption; embedding drivers must place `struct vivaldi_data` first. Feature report fetching can fail and only warns. Incorrect report-ID length handling would cause `-EOVERFLOW` or bad field values.

Test signals: no KUnit tests. Validate by binding Vivaldi keyboards and reading `function_row_physmap` sysfs, including unnumbered feature-report devices.
