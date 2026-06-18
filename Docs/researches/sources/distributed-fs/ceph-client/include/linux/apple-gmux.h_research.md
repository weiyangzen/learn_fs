# sources/distributed-fs/ceph-client/include/linux/apple-gmux.h

## Purpose
Defines Apple gmux detection helpers and register/port constants for the GPU mux microcontroller found in dual-GPU Mac systems.

## Important APIs, Types, And Functions
Constants cover gmux ACPI HID, PIO ports for version, display/DDC/external switching, discrete power, brightness, indexed I/O, and MMIO command selection. `enum apple_gmux_type` distinguishes PIO, indexed, and MMIO. With `CONFIG_APPLE_GMUX`, helpers include `apple_gmux_is_indexed()`, `apple_gmux_is_mmio()`, `apple_gmux_detect()`, and `apple_gmux_present()`. Disabled builds return false.

## Control Flow, State, And Persistence
`apple_gmux_detect()` optionally finds the ACPI PNP device, checks I/O resources first, reads version bytes, probes indexed mode on invalid version bytes, otherwise tests MEM resources for MMIO by mapping 16 bytes and reading the command register. It temporarily references ACPI/PNP/device objects and releases them before return.

## Dependencies And Integration Points
Depends on ACPI, I/O port/MMIO helpers, PNP resources, and device references. Integrated by backlight, GPU switching, runtime PM, and Apple-specific quirk code.

## Risks And Test Signals
Detection performs real I/O; probing the wrong resource can have side effects. The disabled-config prototype for `apple_gmux_detect()` uses a different second-argument type than the enabled path, so callers must include under compatible expectations. Tests should cover PIO, indexed, and MMIO machines, false-positive ACPI devices, reference cleanup, backlight control, and no-gmux systems.
