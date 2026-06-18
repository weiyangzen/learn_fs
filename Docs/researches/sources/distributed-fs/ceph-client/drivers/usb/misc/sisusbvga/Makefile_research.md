# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Makefile

Purpose: Build glue for the in-tree sisusb driver.

Important APIs and types: single assignment `obj-$(CONFIG_USB_SISUSBVGA) += sisusbvga.o`, tying the Kconfig symbol to the object built from the implementation source.

Control flow: kbuild includes `sisusbvga.o` only when `CONFIG_USB_SISUSBVGA` is enabled as built-in or module. No runtime behavior or state exists.

State and persistence: build output depends on `.config`. Risks are minimal; missing helper object names would matter only if the implementation were split. Test signals are compile/link success for `CONFIG_USB_SISUSBVGA=m` and `=y`.
