# sources/distributed-fs/ceph-client/drivers/net/usb/Makefile

Purpose: Maps USB networking Kconfig symbols to kbuild object files. It is the build integration point that turns enabled USB net driver symbols into built-in objects or modules.

Important entries: `obj-$(CONFIG_USB_USBNET) += usbnet.o` builds the common framework. `obj-$(CONFIG_USB_NET_AX8817X) += asix.o` builds the ASIX composite object, and `asix-y := asix_devices.o asix_common.o ax88172a.o` defines its constituent translation units. `obj-$(CONFIG_USB_NET_AQC111) += aqc111.o` builds the Aquantia driver. Other mappings cover CDC, RNDIS, Realtek, SMSC, LAN78xx, QMI, MBIM, Zaurus, and many older adapters.

Control flow: kbuild expands each `obj-$(CONFIG_...)` assignment according to the symbol value. `y` links into the built-in kernel object for this directory, `m` builds a module, and empty omits it. The `asix-y` aggregate means all three ASIX source files are linked together into the single `asix` driver module/object.

State and persistence: There is no runtime state. The file persists object composition and module naming. For this group, changing the ASIX source split requires keeping the `asix-y` list in sync; changing Kconfig symbol names requires matching edits here.

Dependencies and integration: Depends on symbols defined by `drivers/net/usb/Kconfig` and on kbuild composite-object conventions. The driver registration functions in each C file (`module_usb_driver`) become module init/exit for the corresponding object produced here.

Risks and test signals: Risks are symbol/object drift, leaving a new source file out of a composite object, accidentally changing module names, or building a source without its declared Kconfig dependency. Test by compiling ASIX and AQC111 as modules and built-ins, confirming `asix.o` includes `asix_devices.o`, `asix_common.o`, and `ax88172a.o`, and checking `modules.order`/modpost for expected names and unresolved symbols.
