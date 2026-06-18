<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig

## Purpose

This Kconfig file defines build options for the Wilco Embedded Controller core and optional debugfs, event, and telemetry interfaces.

## Important APIs, Types, And Functions

The symbols are `WILCO_EC`, `WILCO_EC_DEBUGFS`, `WILCO_EC_EVENTS`, and `WILCO_EC_TELEMETRY`. The core is tristate and depends on X86 or compile testing, ACPI, `CROS_EC_LPC`, `LEDS_CLASS`, and `HAS_IOPORT`. Optional drivers depend on the core.

## Control Flow

Selecting `WILCO_EC` enables the base eSPI/MEC mailbox driver. Enabling optional symbols builds separate modules that bind to platform children or ACPI devices and expose raw debug access, event forwarding, or telemetry.

## State And Persistence

The file contributes no runtime state; it controls which runtime modules can exist.

## Dependencies And Integration Points

It integrates Wilco EC support into the Chrome platform driver menu and expresses required subsystem dependencies for IO ports, ACPI, Chrome EC LPC MEC access, LEDs, debugfs, character devices, and telemetry paths.

## Risks

The core requires `LEDS_CLASS` because keyboard backlight support is built into the base object, so systems wanting only mailbox/sysfs still inherit the LED dependency. Optional debugfs exposes raw EC command access and should not be enabled on production builds.

## Test Signals

Check allmodconfig and minimal configs, dependency pruning when ACPI or HAS_IOPORT is absent, module names in help text, and successful builds for each optional symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig -->
