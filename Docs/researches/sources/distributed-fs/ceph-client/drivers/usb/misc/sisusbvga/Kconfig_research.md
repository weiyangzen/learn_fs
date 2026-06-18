# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/Kconfig

Purpose: Kconfig entry for the `sisusbvga` USB2VGA dongle driver targeting Net2280/SiS315 hardware.

Important APIs and types: defines `CONFIG_USB_SISUSBVGA` as a tristate option named "USB 2.0 SVGA dongle support (Net2280/SiS315)" and depends on `USB_MUSB_HDRC || USB_EHCI_HCD`. Help text states that USB 2.0 host support is required and module name is `sisusbvga`.

Control flow: build-system selection only; enabling this symbol causes the sibling Makefile to build `sisusbvga.o`. No runtime state exists in this file.

State and persistence: kernel configuration persists the selected tristate value. Risks include dependency coverage limited to MUSB/EHCI, which may exclude other USB 2.0-capable host-controller configurations, and the old specialized hardware option defaulting to off by user choice. Test signals include Kconfig dependency visibility, module build with `M`, built-in build with `Y`, and absence when dependencies are unavailable.
