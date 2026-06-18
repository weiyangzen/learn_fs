<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/host/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/Makefile` maps USB host-controller Kconfig symbols to built objects and composite module object lists. It is the build-side companion for the host `Kconfig`. The source was read as a complete 90-line file.

## Important APIs, Types, and Functions

Key composite object lists are `fhci-y`, `xhci-hcd-y`, `xhci-mtk-hcd-y`, `xhci-plat-hcd-y`, and `xhci-rcar-hcd-y`. Important object mappings include `obj-$(CONFIG_USB_EHCI_HCD) += ehci-hcd.o`, EHCI platform drivers such as `ehci-pci.o`, `ehci-platform.o`, `ehci-exynos.o`, `ehci-atmel.o`, `ehci-brcm.o`, Freescale `fsl-mph-dr-of.o` plus `ehci-fsl.o`, OHCI/UHCI/FHCI/xHCI families, BCMA/SSB bridge drivers, and smaller host controllers such as `max3421-hcd.o` and `xen-hcd.o`.

## Control Flow

Kbuild expands object lists according to the final `.config`. Some modules are composite, for example `xhci-hcd.o` is built from xHCI core, ring, hub, debug, trace, optional debug capability, debugfs, and sideband pieces. Platform wrappers are added only when their config symbol is enabled. Freescale EHCI pulls in both common Freescale DR glue and the EHCI-specific object.

## State and Persistence Behavior

The file has no runtime state. Its output is the compiled object/module graph, which persists as build artifacts and determines driver registration availability.

## Dependencies and Integration Points

It integrates with Kconfig symbols, generated trace include paths through `CFLAGS_xhci-trace.o := -I$(src)`, and Linux Kbuild composite-object conventions. Every source file in this work item except `Kconfig` itself is either directly mapped here or included into `ehci-hcd.c`.

## Risks and Edge Cases

Kconfig/Makefile drift can silently omit a driver or build an object without its required core. Optional fragments guarded by `ifneq ($(CONFIG_*),)` must match bool/tristate expectations. Composite xHCI additions can change module dependencies and link order. Freescale double mapping is intentional; removing one object can break OF/platform data setup.

## Test Signals

Build `drivers/usb/host/` under representative configs and confirm expected `.o` and `.ko` outputs. Use `make M=drivers/usb/host` with EHCI, OHCI, xHCI, BCMA, SSB, Freescale, Exynos, Atmel, Broadcom STB, and debugfs/test-mode permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Makefile -->
