# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/Kconfig

## Purpose

`i2c-hid/Kconfig` defines the build-time configuration for HID-over-I2C support. It exposes the top-level `I2C_HID` menu and transport-specific ACPI, Open Firmware, Elan, Goodix, and shared core symbols.

## Important APIs, Types, and Functions

- `menuconfig I2C_HID`: top-level tristate gated by `I2C`, defaulting to `y`.
- `I2C_HID_ACPI`: ACPI transport driver, depends on ACPI and selects `I2C_HID_CORE`.
- `I2C_HID_OF`: generic Open Firmware/manual-board-file transport, selects core.
- `I2C_HID_OF_ELAN` and `I2C_HID_OF_GOODIX`: OF-specific vendor drivers for Elan and Goodix devices, depend on OF and select core.
- `I2C_HID_CORE`: internal shared core tristate with DRM dependency constraint.

## Control Flow

Selecting a transport symbol pulls in the shared core. The `DRM || !DRM` dependency prevents built-in I2C-HID code from depending incorrectly on modular DRM panel-related code.

## State and Persistence Behavior

Kconfig has no runtime state. It controls which objects are built-in, modular, or absent, which in turn controls runtime binding availability.

## Dependencies and Integration Points

It integrates with the kernel Kconfig system, I2C, ACPI, OF, DRM dependency handling, and the Makefile in the same directory.

## Risks and Edge Cases

- Top-level `I2C_HID` defaults to `y`, so dependency mistakes can affect many builds.
- Transport drivers must select core; missing selects would produce link failures or unbound devices.
- The DRM dependency expression is intentionally unusual and should be preserved unless the panel dependency changes.

## Test Signals

- Build all combinations: built-in core/transport, modular transport, ACPI-only, OF-only, and DRM modular/built-in cases.
- Confirm menu help/module names match Makefile outputs.
- Run `make oldconfig`/`allyesconfig` style coverage to catch dependency regressions.
