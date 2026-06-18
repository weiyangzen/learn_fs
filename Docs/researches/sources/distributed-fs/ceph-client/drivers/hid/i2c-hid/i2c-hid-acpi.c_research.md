# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-acpi.c

## Purpose

`i2c-hid-acpi.c` is the ACPI transport glue for HID-over-I2C devices. It obtains the HID descriptor address from the ACPI HID I2C `_DSM`, applies ACPI-specific blacklist and power handling, and then delegates protocol operation to the shared I2C-HID core.

## Important APIs, Types, and Functions

- `struct i2c_hid_acpi`: embeds `struct i2chid_ops` and stores the ACPI companion device.
- `i2c_hid_acpi_blacklist[]`: blocks ACPI IDs known not to be compatible or to cause wake/interrupt issues.
- `i2c_hid_guid`: HID I2C Device DSM GUID.
- `i2c_hid_acpi_get_descriptor`: evaluates `_DSM` function 1 to retrieve the HID descriptor address and rejects blacklisted devices.
- `i2c_hid_acpi_restore_sequence`: reissues descriptor lookup during restore.
- `i2c_hid_acpi_shutdown_tail`: powers the ACPI device to `D3cold` during shutdown tail.
- `i2c_hid_acpi_probe`: allocates transport state, fills ops, retrieves descriptor, fixes ACPI power, and calls `i2c_hid_core_probe`.

## Control Flow

The I2C driver binds to ACPI IDs `ACPI0C50` and `PNP0C50`. Probe allocates devm state, stores `ACPI_COMPANION(dev)`, installs restore/shutdown callbacks, calls `i2c_hid_acpi_get_descriptor`, and passes the resulting descriptor address to the core. Remove and shutdown are the shared core functions, and PM uses `i2c_hid_core_pm`.

## State and Persistence Behavior

Transport state is devm-managed for the I2C device lifetime. The descriptor address is retrieved at probe and passed to the core rather than stored in this file. Restore re-evaluates the ACPI method, likely to satisfy firmware/device sequencing rather than to update local state. Shutdown persists by moving ACPI power state to D3cold.

## Dependencies and Integration Points

It depends on ACPI device matching, `_DSM` evaluation, I2C driver registration, PM hooks, and the shared `i2c-hid.h` core API. It also depends on firmware implementing the HID I2C DSM GUID correctly.

## Risks and Edge Cases

- `_DSM` integer values are narrowed to `u16`; unexpected large values would truncate.
- `i2c_hid_acpi_restore_sequence` ignores descriptor lookup errors.
- A missing ACPI companion would leave `adev` null and is not explicitly checked before use.
- Blacklist maintenance is firmware-specific and may need updates for devices with misleading `PNP0C50` compatibility.

## Test Signals

- Boot ACPI HID-over-I2C touchpad/touchscreen/keyboard systems and confirm descriptor address lookup and core probe.
- Validate blacklist IDs return `-ENODEV`.
- Suspend/resume and shutdown tests should confirm restore sequence and D3cold tail do not regress wake behavior.
- Fault-inject `_DSM` failure/non-integer return and large descriptor values.
