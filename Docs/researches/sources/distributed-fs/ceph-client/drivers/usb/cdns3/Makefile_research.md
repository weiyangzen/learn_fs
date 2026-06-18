# sources/distributed-fs/ceph-client/drivers/usb/cdns3/Makefile

Purpose: Maps Cadence USB Kconfig symbols to kernel objects and module composition for common CDNS USB, CDNS3, CDNSP, platform glue, gadget, host, and trace support.

Important APIs, types, and functions: Builds `cdns-usb-common-y` from `core.o drd.o`, `cdns3-y` from `cdns3-plat.o`, adds `host.o` under `CONFIG_USB_CDNS_HOST`, adds `cdns3-gadget.o cdns3-ep0.o` under `CONFIG_USB_CDNS3_GADGET`, adds trace objects under `CONFIG_TRACING`, and emits glue objects for PCI, TI, i.MX, and StarFive. CDNSP PCI builds `cdnsp-udc-pci.o` with gadget ring/memory/ep0 pieces when configured.

Control flow: The Makefile handles the special `CONFIG_USB=m` case by forcing common and cdns3 objects into `obj-m`; otherwise it uses normal `obj-$(CONFIG_...)` inclusion. Trace object CFLAGS include `-I$(src)` so generated trace headers can resolve local includes.

State and persistence behavior: Build-only behavior; no runtime state.

Dependencies and integration points: Consumes the Kconfig symbols in this folder and relies on kbuild composite object syntax. It coordinates with trace headers requiring include-path adjustment.

Risks: Module composition is sensitive to built-in versus module USB core mode. Missing trace include paths break generated trace compilation. Adding new source files requires updating the correct composite object rather than only `obj-y`.

Test signals: Build with tracing enabled/disabled, gadget-only, host-only, dual-role, `CONFIG_USB=m`, `CONFIG_USB=y`, and CDNSP PCI configurations. `modinfo` should show expected modules such as `cdns3`, `cdns3-pci`, and platform glue modules.
