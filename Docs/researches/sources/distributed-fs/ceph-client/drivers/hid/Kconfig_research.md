# sources/distributed-fs/ceph-client/drivers/hid/Kconfig

## Purpose

This Kconfig file is the HID subsystem configuration hub. It gates the common HID core, userspace interfaces, generic HID binding, haptics, special vendor drivers, sensor hub drivers, HID-BPF, and bus-specific HID transports such as USB, I2C, Intel ISH, AMD SFH, Surface HID, and Intel THC.

## Important APIs, Types, and Functions

The important exported symbols are configuration symbols rather than C APIs. `HID_SUPPORT` is the top-level menu option. `HID` enables the core and depends on `INPUT`; `HIDRAW`, `UHID`, `HID_GENERIC`, `HID_BATTERY_STRENGTH`, and `HID_HAPTIC` toggle core-facing facilities. The long "Special HID drivers" menu maps device/vendor support to module symbols consumed by `drivers/hid/Makefile`, for example `HID_MULTITOUCH`, `HID_WACOM`, `HID_SENSOR_HUB`, and `HID_KUNIT_TEST`. The file sources sub-Kconfig files for `bpf`, `i2c-hid`, `intel-ish-hid`, `amd-sfh-hid`, `surface-hid`, `intel-thc-hid`, and `usbhid`.

## Control Flow

Kconfig evaluation first exposes `HID_SUPPORT`; if selected, it offers the core `HID` symbol and, under `if HID`, the core options and per-device drivers. The final `source` lines import transport and extension menus. `usbhid/Kconfig` is sourced outside the `if HID` block but still inside `HID_SUPPORT`, preserving historical USB HID configuration behavior.

## State and Persistence Behavior

The file persists only build-time choices in kernel configuration. Runtime state is indirect: selecting symbols controls which object files are built and which modules can bind hardware. Defaults such as `HID_GENERIC=y` when `HID=y` determine baseline behavior for devices without special drivers.

## Dependencies and Integration Points

This file integrates with the top-level input stack, kernel module build rules, and subdirectory Kconfigs. Several symbols depend on other subsystems such as `LEDS_CLASS`, `POWER_SUPPLY`, `NEW_LEDS`, `I2C`, `SPI`, `USB_HID`, `BPF`, `BPF_SYSCALL`, `BPF_JIT`, and `KUNIT`. The AMD SFH and HID-BPF entries researched in this item are included through `source` statements near the end.

## Risks and Test Signals

Dependency drift is the main risk: a driver can be selectable while required libraries or transports are absent, or a Makefile object can reference a missing symbol. Test signals include `allmodconfig`, `allyesconfig`, architecture-specific randconfigs, and checking that every `HID_*` symbol referenced by `drivers/hid/Makefile` has a matching Kconfig entry or intentional external definition.
