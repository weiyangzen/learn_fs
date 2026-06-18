# sources/distributed-fs/ceph-client/drivers/usb/isp1760/Kconfig

## Purpose
This Kconfig file exposes build-time configuration for the NXP ISP1760/1761/1763 USB controller driver. It defines the top-level `USB_ISP1760` option plus internal host and gadget role symbols used by the Makefile and C stubs.

## Important APIs, Types, And Functions
`USB_ISP1760` is a tristate depending on `USB || USB_GADGET` and selects `REGMAP_MMIO`. Internal bools `USB_ISP1760_HCD` and `USB_ISP1761_UDC` gate compilation of `isp1760-hcd.o` and `isp1760-udc.o`. The mode choice offers host-only, gadget-only, and dual-role configurations with dependency expressions that keep module/built-in relationships compatible with USB core and gadget core.

## Control Flow
Kconfig evaluation selects a default mode based on whether `USB` and/or `USB_GADGET` are enabled. Host-only selects the HCD symbol, gadget-only selects the UDC symbol, and dual-role selects both. The C code then uses `IS_ENABLED(CONFIG_USB_ISP1760_HCD)` and `IS_ENABLED(CONFIG_USB_ISP1761_UDC)` to decide runtime registration.

## State And Persistence
There is no runtime state. The selected symbols persist in the kernel configuration and determine which objects and inline stubs are built.

## Dependencies And Integration Points
The file integrates with the USB host stack, USB gadget stack, regmap MMIO, and the local Makefile. Help text documents lack of isochronous and OTG support, which matches limitations in the HCD and core code.

## Risks
The dependency expressions must keep role objects linkable in built-in and module combinations. The prompt mentions ISP1760 in gadget mode even though the implementation is primarily ISP1761/ISP1763-capable for UDC; changing role support should keep help text and C `udc_enabled` logic aligned.

## Test Signals
Build matrix coverage is the main signal: host-only, gadget-only, dual-role, module, built-in, `USB=n USB_GADGET=y`, `USB=y USB_GADGET=n`, and compile-test style configurations should all link with the expected stubs or objects.
