<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile

## Purpose
This Makefile defines how the Broadcom BDC USB device controller driver is compiled.

## Important APIs, Types, And Functions
`obj-$(CONFIG_USB_BDC_UDC) += bdc.o` creates the driver object when enabled. `bdc-y` always includes `bdc_core.o`, `bdc_cmd.o`, `bdc_ep.o`, and `bdc_udc.o`. If `CONFIG_USB_GADGET_VERBOSE` is non-empty, `bdc_dbg.o` is added for verbose debug dumping.

## Control Flow
The build combines core platform probing, command submission, endpoint transfer management, gadget glue, and optional debug helpers into one module or built-in object.

## State And Persistence
There is no runtime state. The build composition is persistent in kernel build artifacts.

## Dependencies And Integration Points
The file is controlled by the Kconfig symbol in this directory and by the generic `CONFIG_USB_GADGET_VERBOSE` debug option.

## Risks
Verbose debug functions are compiled out unless `CONFIG_USB_GADGET_VERBOSE` is set, so code that expects `bdc_dbg_*()` side effects must not rely on them. Object ordering is conventional but all listed source files share internal headers and must remain consistent.

## Test Signals
Build with `CONFIG_USB_BDC_UDC=y/m` and with `CONFIG_USB_GADGET_VERBOSE` both enabled and disabled to catch missing declarations or stale debug references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/Makefile -->
