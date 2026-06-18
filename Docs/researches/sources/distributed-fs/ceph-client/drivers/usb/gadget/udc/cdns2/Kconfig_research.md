<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig

## Purpose
This Kconfig entry exposes the Cadence USBHS Device Controller gadget driver as `USB_CDNS2_UDC`.

## Important APIs, Types, And Functions
The symbol is a tristate named "Cadence USBHS Device Controller". It depends on `USB_PCI`, `ACPI`, and `HAS_DMA`. Help text identifies a PCI-based USB peripheral controller supporting full-speed and high-speed USB 2.0 transfers and names the module `cdns2-udc-pci.ko`.

## Control Flow
Selecting this option allows the Makefile to build the PCI/gadget/EP0 pieces and optional trace support. There is no runtime logic in Kconfig itself.

## State And Persistence
The selected value persists in the kernel build configuration.

## Dependencies And Integration Points
This config integrates with the USB PCI and ACPI stacks and requires DMA. It feeds `obj-$(CONFIG_USB_CDNS2_UDC)` in the Makefile.

## Risks
The dependencies limit this driver to PCI/ACPI builds even though the gadget logic is separated from PCI glue. Systems using non-PCI Cadence USBHS integrations would need additional glue and Kconfig changes.

## Test Signals
Build with the option disabled, built-in, and modular; verify `cdns2-udc-pci.ko` is produced for modular builds and that gadget drivers can bind on matching PCI/ACPI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Kconfig -->
