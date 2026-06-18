# sources/distributed-fs/ceph-client/drivers/base/physical_location.h

## Purpose
Provides the driver-core internal interface for optional physical-location support, with ACPI-backed declarations when enabled and harmless stubs when disabled.

## Important APIs, Types, And Functions
When `CONFIG_ACPI` is enabled, declares `dev_add_physical_location()` and `dev_attr_physical_location_group`. Otherwise it defines `dev_add_physical_location()` as an inline function returning `false` and provides an empty `attribute_group`.

## Control Flow
Including code can call `dev_add_physical_location()` and reference the attribute group without surrounding every use in ACPI preprocessor conditionals. The compiled behavior is selected at build time.

## State And Persistence
The header stores no runtime state. In non-ACPI builds, the empty static attribute group avoids exposing physical-location sysfs files.

## Dependencies And Integration
Includes `<linux/device.h>` for `struct device` and `struct attribute_group`. It pairs directly with `physical_location.c` and the driver-core code that installs optional device groups.

## Risks And Test Signals
Risks are mostly ABI and build-integration issues: the empty group must remain safe for users that iterate attribute groups, and declarations must match `physical_location.c`. Test signals are ACPI and non-ACPI build coverage plus device registration paths that include the group unconditionally.
