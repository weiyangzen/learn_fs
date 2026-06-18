# sources/distributed-fs/ceph-client/drivers/usb/class/Makefile

Purpose: maps USB class-driver Kconfig symbols to object files in the kernel build.

Important build rules: `obj-$(CONFIG_USB_ACM) += cdc-acm.o`, `obj-$(CONFIG_USB_PRINTER) += usblp.o`, `obj-$(CONFIG_USB_WDM) += cdc-wdm.o`, and `obj-$(CONFIG_USB_TMC) += usbtmc.o`. These rules let the same source build built-in, modular, or not at all according to tristate values.

Control flow: Kbuild evaluates the `obj-*` variables and includes matching object files in the directory build. No runtime code exists.

State and persistence: build state is derived from `.config` and Kbuild outputs. No runtime persistence exists.

Dependencies and integration points: tightly paired with `drivers/usb/class/Kconfig` symbols and module names. It integrates this directory into the broader USB driver build.

Risks and test signals: risks are simple but high impact: wrong symbol names or object names silently omit drivers or break builds. Test with `M=drivers/usb/class` builds for each symbol as module, built-in full kernel builds, and clean configs where symbols are disabled.
