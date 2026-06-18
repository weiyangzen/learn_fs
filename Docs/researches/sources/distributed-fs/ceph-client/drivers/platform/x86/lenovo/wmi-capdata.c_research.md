<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c

## Purpose
This driver caches Lenovo WMI capability data blocks used by Lenovo Legion "Other Mode" features. It supports Capability Data 00, Capability Data 01, and Fan Test Data WMI GUIDs, then exposes cached records to peer drivers through the Linux component framework and exported lookup helpers.

## Important APIs, Types, And Functions
`enum lwmi_cd_type` distinguishes `LENOVO_CAPABILITY_DATA_00`, `LENOVO_CAPABILITY_DATA_01`, and `LENOVO_FAN_TEST_DATA`. `struct lwmi_cd_priv` stores the WMI device, cached `cd_list`, ACPI notifier, and optional sub-master state. `struct cd_list` contains a mutex, type, count, and a flexible array of `capdata00`, `capdata01`, or `capdata_fan` records. Exported APIs are `lwmi_cd_match_add_all()`, `lwmi_cd00_get_data()`, `lwmi_cd01_get_data()`, and `lwmi_cd_fan_get_data()`. Internal setup flows include `lwmi_cd_alloc()`, `lwmi_cd_cache()`, `lwmi_cd_fan_list_alloc_cache()`, `lwmi_cd_sub_master_add()`, and component bind/unbind callbacks.

## Control Flow
Probe receives a table entry from the WMI ID context, allocates the appropriate cache, and reads all WMI block instances. Data 00 and 01 become components for `lenovo-wmi-other`. Data 00 can also become a sub-master for Fan Test Data if the fan-test capability is valid. Data 01 registers an ACPI notifier and refreshes cached data on AC adapter status changes, because capability bounds may vary with power source.

## State And Persistence
Capability data is cached in devm-managed memory and protected by `list_mutex`. The cache is refreshed for CD01 on AC power notifications; otherwise it is a probe-time snapshot. Component pointers handed to consumers are valid only while component bindings remain active. No values are written back to firmware.

## Dependencies And Integration Points
The file depends on Lenovo WMI data-block GUIDs, ACPI notifier infrastructure, `wmi-helpers.h`, `wmi-capdata.h`, and the component framework. Its main consumer is `lenovo-wmi-other`, which uses CD00 for fan support, CD01 for tunable attributes, and optional fan data for RPM constraints.

## Risks And Edge Cases
Fan Test Data is packed and variable length; incomplete buffers are ignored and large fan counts are truncated to `U8_MAX`. Missing fan-test support is represented by an `ERR_PTR(-ENODEV)` sub-component marker so master callbacks can still receive `NULL`. Component reprobe ordering is delicate; the code clears master callback state to avoid double-calling after fan-data reprobes. Unsupported or dummy ACPI objects can silently produce empty caches.

## Test Signals
Validation should cover all three GUIDs, block counts and buffer lengths, CD00/CD01 lookups by encoded attribute ID, AC adapter notifications refreshing CD01, component bind/unbind/reprobe ordering, missing Fan Test Data behavior, and integration with `lenovo-wmi-other` hwmon/firmware-attributes registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c -->
