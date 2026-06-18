<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c

## Purpose
ACPI DSM-backed SAR data driver for Intel modem platforms. It exposes the current device mode and selected RF table indexes to userspace through sysfs.

## Important APIs, Types, And Functions
`sar_get_data()` retrieves regulatory configuration package data with DSM command 2. `parse_package()` decodes per-device-mode band, antenna, and SAR table indexes into `context->config_data`. `sar_get_device_mode()` uses DSM command 1, updates the selected data, and notifies sysfs. Attributes `intc_data` and `intc_reg` expose current values and allow selecting regulatory mode.

## Control Flow
Probe allocates `wwan_sar_context`, parses the SAR DSM UUID, loads configuration for all three regulatory modes, reads current BIOS device mode, creates sysfs attributes, and installs an ACPI notify handler. Notify event `0x80` refreshes the device mode. Writing `intc_reg` changes the regulatory index and recomputes exposed table indexes.

## State And Persistence
The context stores ACPI handle/GUID, selected regulatory mode, current SAR data, and dynamically allocated device-mode arrays per regulatory table. State is in memory and freed on remove; authoritative sensor/device mode comes from BIOS DSM.

## Dependencies And Integration Points
Depends on ACPI platform devices, DSM, sysfs, and userspace modem control software that consumes `intc_data`.

## Risks And Test Signals
Risks include weak ACPI package validation, partial default-zero entries after parse failures, memory lifetime of per-regulatory arrays, and no locking around notify/sysfs updates. Test malformed DSM packages, regulatory writes outside `0..2`, ACPI event refresh, sysfs notifications, and userspace modem SAR table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c -->
