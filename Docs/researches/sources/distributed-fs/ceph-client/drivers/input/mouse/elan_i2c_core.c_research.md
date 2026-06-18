# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_core.c

## Purpose

`elan_i2c_core.c` is the transport-independent Elan I2C/SMBus touchpad driver. It selects a backend, powers and initializes the device, queries firmware and geometry, exposes sysfs firmware/calibration/baseline controls, registers input devices, decodes IRQ reports for touchpad and optional trackpoint data, and implements suspend/resume with regulator and wakeup handling.

## Important APIs, Types, and Functions

`struct elan_tp_data` is the central per-device state. Probe and lifecycle functions include `elan_probe`, `elan_suspend`, `elan_resume`, and `elan_disable_regulator`. Initialization/query helpers include `elan_initialize`, `elan_query_product`, `elan_query_device_info`, `elan_query_device_parameters`, `elan_get_fwinfo`, and `elan_i2c_lookup_quirks`. Firmware update is handled by `elan_sysfs_update_fw`, `elan_update_firmware`, `__elan_update_firmware`, and `elan_write_fw_block`. Sysfs calibration/baseline flows use `elan_calibrate`, `calibrate_store`, `elan_acquire_baseline`, `acquire_store`, `min_show`, and `max_show`. IRQ reporting uses `elan_isr`, `elan_report_absolute`, `elan_report_contact`, and `elan_report_trackpoint`.

## Control Flow

Probe chooses native I2C if available, otherwise SMBus, allocates state, enables `vcc`, verifies the address, initializes absolute mode, queries firmware/info/geometry, sets up input devices, requests a threaded IRQ, and registers input nodes. IRQ handling completes firmware update waits when `in_fw_update` is true; otherwise it reads a transport report and dispatches by report ID. Firmware update disables IRQs, enters IAP mode, writes all pages after the boot area with per-page checksums, waits for reset, verifies IAP checksum, and reinitializes. Suspend serializes against sysfs, disables IRQ, sleeps or powers off depending on wake capability, and may disable the regulator; resume re-enables power, initializes with optional quick-wakeup quirk, then reenables IRQ.

## State and Persistence Behavior

Driver state includes queried product/firmware/checksum/IAP metadata, geometry/resolution, report features/length, pressure adjustment, mode bits, baseline cache, clickpad/middle-button flags, quirks, regulator pointer, sysfs mutex, and firmware-update completion flag. Firmware update changes persistent device flash. Baseline values persist only in memory after `baseline/acquire` and are invalidated before each acquire.

## Dependencies and Integration Points

The core integrates Linux I2C driver registration, ACPI/OF matching, firmware loader, regulator framework, PM wake IRQ/events, input MT, sysfs device groups, and transport ops from `elan_i2c.h`. Device properties can override max coordinates, physical size, trace counts, clickpad, middle button, and trackpoint presence.

## Risks and Edge Cases

Firmware update assumes the signature address derived from IC/IAP metadata is within the firmware blob before dereferencing. Geometry calculations divide by trace counts or millimeter values returned by firmware/properties. Suspend keeps IRQ disabled until resume even if initialization later fails. Trackpoint reports can arrive without a registered trackpoint device and only warn once. Baseline/calibration disable IRQs and rely on transport mode restoration on all error paths.

## Test Signals

Coverage should include I2C versus SMBus selection, regulator failure paths, device-property overrides, quirk lookup, firmware metadata for every IC type, firmware signature mismatch, update success/failure with checksum mismatch, sysfs read/write locking, calibration timeout, baseline not-ready and acquire paths, touch/high-precision/trackpoint IRQ reports, optional middle/clickpad/trackpoint properties, suspend as wake source versus powered-off, resume quick-wakeup, and both ACPI/OF/module match tables.
