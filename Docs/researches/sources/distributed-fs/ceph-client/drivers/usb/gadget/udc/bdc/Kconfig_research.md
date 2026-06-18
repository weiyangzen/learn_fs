<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig

## Purpose
This Kconfig entry exposes the Broadcom USB3.0 Device Controller IP driver as `USB_BDC_UDC`. It gates compilation of the BDC UDC code under the USB gadget subsystem.

## Important APIs, Types, And Functions
The only symbol is `config USB_BDC_UDC`, a tristate option named "Broadcom USB3.0 device controller IP driver(BDC)". It depends on `USB_GADGET` and `HAS_DMA`, defaults to enabled on `ARCH_BRCMSTB`, and describes the module name as `bdc`.

## Control Flow
Kconfig selection decides whether the BDC object list in the adjacent Makefile is built into the kernel or as a module. There is no runtime control flow in this file.

## State And Persistence
The configuration choice persists in the kernel build configuration. At runtime, BDC state is managed by the C files in the same directory.

## Dependencies And Integration Points
This entry integrates with kernel configuration, the USB gadget menu, Broadcom STB architecture defaults, and DMA-capable platform constraints. It is consumed by `obj-$(CONFIG_USB_BDC_UDC)` in the Makefile.

## Risks
The dependency does not express platform bus or device-tree requirements, so selecting it outside a matching Broadcom BDC platform only builds the driver; probe still depends on compatible hardware and resources. The default for `ARCH_BRCMSTB` can increase build coverage and warning exposure for that architecture.

## Test Signals
Build tests should confirm `CONFIG_USB_BDC_UDC=y` links the BDC objects, `=m` produces `bdc.ko`, and unset excludes the objects. Runtime test requires a `brcm,bdc` or `brcm,bdc-udc-v2` platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Kconfig -->
