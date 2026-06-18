<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile

Purpose: Kbuild manifest for the USB serial core and converter modules.

Important APIs/types/functions: `usbserial-y := usb-serial.o generic.o bus.o`; optional `usbserial-$(CONFIG_USB_SERIAL_CONSOLE) += console.o`; relevant object rules for `aircable.o`, `ark3116.o`, `belkin_sa.o`, `ch341.o`, `cp210x.o`, `cyberjack.o`, and `cypress_m8.o`.

Control flow and state: no runtime flow; Kbuild composes the core aggregate and selected per-device objects as built-in or modules. No runtime state is owned.

Dependencies and integration points: USB serial Kconfig, core registration symbols, converter modules using `module_usb_serial_driver()`, and optional helper objects like `usb_wwan.o`.

Risks and test signals: risks are object-list drift and missing core/helper objects. Test built-in/module matrices, `USB_SERIAL_CONSOLE`, converter module generation, and unresolved-symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/Makefile -->
