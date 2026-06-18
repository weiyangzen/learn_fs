# sources/distributed-fs/ceph-client/drivers/video/backlight/apple_bl.c

## Purpose
This platform driver provides vendor backlight control for Intel-based Apple systems by triggering firmware SMI commands through legacy I/O ports.

## Important APIs, types, and functions
`struct hw_data` describes I/O resource range, backlight ops, and raw set callback. Two implementations exist: Intel chipset ports `0xb2/0xb3` and Nvidia chipset ports `0x52e/0x52f`. Key functions are chipset get/set/update helpers, `apple_bl_probe`, `apple_bl_remove`, and module init/exit. ACPI matching uses `APP0002`.

## Control flow
Module init first asks ACPI video which backlight provider should be used and registers only for vendor backlight mode. Probe discovers the PCI host bridge vendor, selects the chipset implementation, tests whether brightness SMI responds, reserves the I/O port range, registers a platform-type backlight with max 15, reads current brightness, and updates status. Remove unregisters and releases the I/O region.

## State and persistence
Global `apple_backlight_device` and `hw_data` hold runtime state. Actual brightness is firmware/platform state exposed through port-triggered SMI side effects.

## Dependencies and integration points
It depends on x86 ACPI, PCI host bridge detection, I/O port access, ACPI video backlight arbitration, and the backlight core.

## Risks and test signals
Risks include SMI side effects, firmware non-response under EFI, global state assumptions, conflict with apple-gmux or ACPI video, and direct port I/O. Test signals include machines with Intel and Nvidia chipsets, `acpi_backlight=` mode variations, I/O region conflict, get/set brightness 0-15, suspend/resume through `BL_CORE_SUSPENDRESUME`, and non-Apple ACPI false positives.
