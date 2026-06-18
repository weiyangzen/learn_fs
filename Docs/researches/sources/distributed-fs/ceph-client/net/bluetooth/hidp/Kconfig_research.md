# sources/distributed-fs/ceph-client/net/bluetooth/hidp/Kconfig

## Purpose
Defines the kernel configuration entry for Bluetooth HIDP support, which carries HID reports over Bluetooth for the Human Interface Device Profile.

## APIs, Types, and Functions
The single symbol is `CONFIG_BT_HIDP`, a tristate named `BT_HIDP` with prompt `HIDP protocol support`. It depends on `BT_BREDR` and `HID`, and the help text documents built-in (`Y`) and module (`M`, module name `hidp`) builds.

## Control Flow, State, and Persistence
There is no runtime control flow. The symbol controls whether the HIDP sources are compiled and whether the module init/exit paths in `core.c` and socket registration in `sock.c` are present. The dependency on BR/EDR excludes HIDP from LE-only Bluetooth builds.

## Dependencies and Integration
Integrates with the Bluetooth Kconfig tree, the HID subsystem, and the HIDP Makefile via `obj-$(CONFIG_BT_HIDP)`. It ensures the module is built only when classic Bluetooth and HID core support are available.

## Risks and Test Signals
Risks are configuration-level: missing `BT_BREDR` or `HID` silently hides HIDP, and build coverage can be lost if only LE Bluetooth configurations are tested. Test signals are `allmodconfig`/`allyesconfig` builds, `CONFIG_BT_HIDP=m` module build and load, `CONFIG_BT_HIDP=y` built-in link, and disabled dependency configurations confirming the symbol is unavailable.
