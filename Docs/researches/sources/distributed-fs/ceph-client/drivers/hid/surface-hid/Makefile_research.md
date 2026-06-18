# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/Makefile

Purpose: object selection for Surface HID support.

Important entries: `surface_hid_core.o` follows `CONFIG_SURFACE_HID_CORE`, `surface_hid.o` follows `CONFIG_SURFACE_HID`, and `surface_kbd.o` follows `CONFIG_SURFACE_KBD`.

Control flow: Kconfig selections drive which translation units are compiled into built-in code or modules.

State and persistence: no runtime state.

Dependencies and integration: pairs with `Kconfig` and the parent HID Makefile to include SSAM HID transports in the kernel build.

Risks: core must be selected whenever either frontend transport is enabled; Kconfig handles that.

Test signals: kernel build with `SURFACE_HID=m/y`, `SURFACE_KBD=m/y`, and both disabled.
