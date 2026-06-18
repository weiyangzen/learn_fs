# sources/distributed-fs/ceph-client/drivers/input/tablet/Kconfig

## Purpose
This Kconfig file defines the tablet-driver menu and build-time configuration symbols for USB Acecad, Aiptek, Hanwang, KB Gear, Pegasus, and serial Wacom protocol 4 tablets.

## Important APIs, types, and functions
The key symbols are `INPUT_TABLET`, `TABLET_USB_ACECAD`, `TABLET_USB_AIPTEK`, `TABLET_USB_HANWANG`, `TABLET_USB_KBTAB`, `TABLET_USB_PEGASUS`, and `TABLET_SERIAL_WACOM4`. USB drivers depend on `USB_ARCH_HAS_HCD` and select `USB`; the Wacom serial driver selects `SERIO`.

## Control flow
`menuconfig INPUT_TABLET` gates the submenu but does not by itself build code. When enabled, users can select individual tristate drivers, each with help text documenting supported hardware and module names.

## State and persistence
Configuration state is persisted in the kernel `.config`. The file has no runtime state, but its symbol values control which objects are compiled into vmlinux or modules.

## Dependencies and integration points
These options feed the tablet Makefile through `obj-$(CONFIG_...)` entries. They also surface dependency expectations: USB host support for USB tablets, input event userspace interfaces for practical use, and serio for serial Wacom devices.

## Risks
The USB options select `USB` but depend only on `USB_ARCH_HAS_HCD`, so build coverage should ensure this remains valid across architectures. Help text can become stale if device ID coverage changes. `INPUT_TABLET` being a bool menu gate may hide individual symbols if disabled.

## Test signals
Kconfig tests should verify all symbols are visible with their dependencies met, module names match Makefile targets, Wacom pulls in `SERIO`, USB drivers pull in `USB`, and all combinations compile as built-in and modules where allowed.
