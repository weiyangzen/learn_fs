# sources/distributed-fs/ceph-client/drivers/usb/cdns3/Kconfig

Purpose: Defines kernel configuration switches for Cadence USBSS/CDNS3 and CDNSP dual-role, gadget, host, PCI, and SoC glue support.

Important APIs, types, and functions: The main symbols are `USB_CDNS_SUPPORT`, `USB_CDNS_HOST`, `USB_CDNS3`, `USB_CDNS3_GADGET`, `USB_CDNS3_HOST`, `USB_CDNS3_PCI_WRAP`, `USB_CDNS3_TI`, `USB_CDNS3_IMX`, `USB_CDNS3_STARFIVE`, `USB_CDNSP_PCI`, `USB_CDNSP_GADGET`, and `USB_CDNSP_HOST`. The file selects `USB_XHCI_PLATFORM` when host support is relevant and selects `USB_ROLE_SWITCH` from common support.

Control flow: Kconfig nesting gates feature visibility: common support first, CDNS3-specific gadget/host/wrapper choices only under `USB_CDNS3`, and CDNSP gadget/host choices only under `USB_CDNSP_PCI`.

State and persistence behavior: Configuration symbols persist in the kernel build configuration and drive object inclusion at build time. They do not create runtime state directly.

Dependencies and integration points: Integrates with the Linux USB, USB gadget, USB PCI, ACPI, HAS_DMA, ARCH_K3, ARCH_MXC, ARCH_STARFIVE, and COMPILE_TEST configuration ecosystem. The Makefile consumes these symbols to choose object files.

Risks: Mismatched dependency expressions can build impossible host/gadget combinations. Defaults tying glue drivers to `USB_CDNS3` can pull wrappers into builds unexpectedly. Gadget dependency expressions require either built-in gadget support or gadget support matching the CDNS3 module mode.

Test signals: `allyesconfig`, `allmodconfig`, architecture defconfigs for TI/NXP/StarFive, compile-test builds, module/built-in combinations for `USB=m` and `USB=y`, and menuconfig visibility checks.
