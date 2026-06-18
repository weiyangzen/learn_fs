<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c

## Purpose
`i2c-hid-dmi-quirks.c` supplies system-specific overrides for broken I2C-HID devices, primarily low-cost laptops whose touchpads do not expose usable HID/I2C-HID descriptors. It also supplies a DMI-scoped HID quirk for a platform where an ELAN touchscreen reports inverted axes.

## Important APIs, Types, and Functions
`struct i2c_hid_desc_override` groups an override I2C-HID descriptor, a HID report descriptor, its size, and the expected I2C device name. `sipodev_desc` is the large static descriptor bundle for SIPODEV/SP1064-compatible touchpads exposed as `SYNA3602:00`. `i2c_hid_dmi_desc_override_table` maps DMI vendor/product strings to that override. `i2c_hid_dmi_quirk_table` maps system identity to a `hid_device_id` carrying HID quirk bits. Exported helpers are `i2c_hid_get_dmi_i2c_hid_desc_override`, `i2c_hid_get_dmi_hid_report_desc_override`, and `i2c_hid_get_dmi_quirks`.

## Control Flow
The core calls the descriptor override helpers before doing normal I2C descriptor/report descriptor reads. Each helper first checks `dmi_first_match`; if no system match exists or the runtime I2C name differs from the override name, it returns `NULL`. On a match it returns the static descriptor pointer and, for report descriptors, writes the static size into the caller-provided size pointer. After normal descriptor parsing, the core calls `i2c_hid_get_dmi_quirks` with VID/PID; if the current system and HID identity match the DMI table, the returned quirk bits are ORed into `hid->initial_quirks`.

## State and Persistence Behavior
All override data is static and read-only after module load. No runtime state is stored. The returned descriptor pointers reference static arrays whose lifetime is the module lifetime, so the core must not free them. The core distinguishes override descriptors from allocated descriptors and only frees non-override report descriptors.

## Dependencies and Integration Points
The file depends on DMI matching, HID IDs/quirk bits, and the local `i2c-hid.h` declarations. It integrates only with `i2c-hid-core.c`, allowing the protocol core to stay generic while encoding platform-specific exceptions here.

## Risks and Edge Cases
DMI matches are exact and narrow; BIOS vendor/product spelling changes can miss needed overrides. Conversely, broad reuse of `sipodev_desc` across many systems assumes identical touchpad wiring and logical descriptor behavior. The descriptor override is selected by I2C name after DMI match, reducing false positives but depending on ACPI naming stability. Static descriptor contents are opaque byte arrays; malformed sizes or report contents would fail HID parsing or produce incorrect input semantics.

## Test Signals
Test by booting matched systems and confirming the core logs descriptor override use, HID parsing succeeds, multitouch and mouse reports work, and no I2C descriptor reads are required from the broken device. For the Dynabook quirk, verify ELAN coordinates are inverted as expected and unrelated ELAN devices do not inherit the quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-dmi-quirks.c -->
