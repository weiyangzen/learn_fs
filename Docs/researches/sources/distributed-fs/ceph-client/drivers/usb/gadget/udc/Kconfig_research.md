# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/Kconfig

Purpose: Kconfig menu defining USB peripheral controller driver options under "USB Peripheral Controller".

Important APIs, types, and functions: this is declarative Kconfig. It defines controller symbols such as `USB_AT91`, `USB_LPC32XX`, `USB_ATMEL_USBA`, `USB_FSL_USB2`, `USB_SNP_CORE`, `USB_AMD5536UDC`, `USB_NET2280`, `USB_ASPEED_UDC`, and `USB_DUMMY_HCD`, and sources submenus for `bdc`, `aspeed-vhub`, and `cdns2`.

Control flow: integrated SoC controllers are listed before licensed/discrete/PCI controllers, with dummy HCD last. Dependencies restrict symbols to matching architectures, buses, DMA, OF, EXTCON, PHY, or USB PCI support. Some symbols select shared support, such as `USB_AMD5536UDC` selecting `USB_SNP_CORE`.

State and persistence: selected Kconfig symbols become build configuration state, not runtime state. Tristate options control built-in versus module builds and indirectly force gadget drivers to compatible linkage.

Dependencies and integration points: integrates with the kernel configuration system and the UDC Makefile. It is the entry point for enabling platform-specific UDC drivers that libcomposite and legacy gadget drivers bind to.

Risks: incorrect dependencies can expose drivers on unsupported builds or hide valid compile-test coverage. `select` relationships can force shared core code unexpectedly. Help text and module names must stay synchronized with Makefile object names.

Test signals: run `make olddefconfig`, `allmodconfig`, and architecture-specific configs; verify each selected symbol builds its Makefile object; check compile-test dependencies; and confirm dummy HCD remains last for default selection behavior.
