# sources/distributed-fs/ceph-client/drivers/input/misc/Kconfig

## Purpose

This Kconfig file declares the `INPUT_MISC` menu and build-time configuration symbols for miscellaneous Linux input drivers that do not fit keyboard, mouse, touchscreen, joystick, or tablet categories. It includes power keys, haptics, accelerometers, speakers, USB remotes, MFD child inputs, and virtual/input helper devices.

## Important APIs, Types, and Functions

The top-level `menuconfig INPUT_MISC` gates the menu. Symbols relevant to this work item include `INPUT_88PM860X_ONKEY`, `INPUT_88PM80X_ONKEY`, `INPUT_88PM886_ONKEY`, `INPUT_AB8500_PONKEY`, `INPUT_AD714X`, `INPUT_AD714X_I2C`, and `INPUT_AD714X_SPI`. Each option declares `tristate` visibility, dependency expressions such as `depends on MFD_88PM800`, and selected helper subsystems where needed, for example `INPUT_FF_MEMLESS` for haptics.

## Control Flow

There is no runtime control flow. Kconfig resolution determines whether each driver is built-in, modular, or omitted. Dependency expressions hide or constrain options based on enabled buses, MFD cores, architecture support, and helper frameworks. Resulting `CONFIG_*` values are consumed by the misc Makefile to include object files.

## State and Persistence Behavior

The file persists configuration state in the kernel `.config`. It does not create runtime state. Module names in help text communicate expected build artifacts and user-facing module names.

## Dependencies and Integration Points

It integrates input misc drivers with MFD, I2C, SPI, USB, ACPI, PWM, regulator, haptics, Xen, GPIO, and architecture-specific subsystems. The AD714x parent option intentionally requires users to select at least one bus connection suboption.

## Risks and Edge Cases

Dependency drift can make a driver visible without all symbols it needs or hide a driver during compile testing. Defaults of `y` for bus subdrivers under a parent option can surprise minimal builds. Help text module names can become stale after file renames. `INPUT_MISC` itself is bool and says it does not affect the kernel, but its `if INPUT_MISC` block gates all contained choices.

## Test Signals

Useful checks include allmodconfig/allnoconfig coverage, each relevant symbol as built-in and module, dependency-disabled visibility, module-name consistency with Makefile entries, compile-test matrix for MFD-backed onkey drivers, and AD714x parent with I2C-only, SPI-only, and both bus subdrivers.
