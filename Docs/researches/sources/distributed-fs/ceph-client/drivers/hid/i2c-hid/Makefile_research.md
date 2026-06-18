# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Makefile

## Purpose

`i2c-hid/Makefile` maps HID-over-I2C Kconfig symbols to object files. It builds the shared core object and the ACPI/OF transport modules selected by configuration.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_I2C_HID_CORE) += i2c-hid.o`: builds the shared module/built-in aggregate.
- `i2c-hid-objs = i2c-hid-core.o`: core aggregate contents.
- `i2c-hid-$(CONFIG_DMI) += i2c-hid-dmi-quirks.o`: conditionally adds DMI quirks.
- Transport objects: `i2c-hid-acpi.o`, `i2c-hid-of.o`, `i2c-hid-of-elan.o`, and `i2c-hid-of-goodix.o`.

## Control Flow

Kbuild expands each `obj-*` line according to the selected Kconfig value. If `I2C_HID_CORE=m`, the aggregate module is `i2c-hid.ko`; if built-in, it is linked into the kernel. Transport symbols build their own objects/modules and depend on the core symbol through Kconfig selects.

## State and Persistence Behavior

There is no runtime state. The file determines object composition and whether DMI quirks are compiled into the core aggregate.

## Dependencies and Integration Points

It integrates directly with `i2c-hid/Kconfig`, Kbuild composite-object syntax, and the transport/core source files in the directory.

## Risks and Edge Cases

- The Kconfig help promises module names; Makefile object names must stay aligned.
- DMI quirks are only included when `CONFIG_DMI` is enabled, so quirk behavior differs across architectures/configs.
- Adding a new transport requires both Kconfig and Makefile changes.

## Test Signals

- Build with `CONFIG_DMI=y` and `n` and inspect `i2c-hid.o` contents.
- Build each transport as module and built-in.
- Verify `modinfo` names match help text for ACPI/OF transports.
