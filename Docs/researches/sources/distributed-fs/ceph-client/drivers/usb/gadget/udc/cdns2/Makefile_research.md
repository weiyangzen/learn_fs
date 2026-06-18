<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile

## Purpose
This Makefile defines the build composition for the Cadence USBHS Device Controller PCI gadget driver.

## Important APIs, Types, And Functions
It adds an include path for `cdns2-trace.o` through `CFLAGS_cdns2-trace.o := -I$(src)`. `obj-$(CONFIG_USB_CDNS2_UDC)` builds `cdns2-udc-pci.o`. The main object includes `cdns2-pci.o`, `cdns2-gadget.o`, and `cdns2-ep0.o` when the UDC config is enabled, and adds `cdns2-trace.o` when `CONFIG_TRACING` is enabled.

## Control Flow
The build links PCI probe/runtime glue, generic gadget transfer logic, EP0 handling, and optional tracepoints into one driver object.

## State And Persistence
No runtime state is represented. The file controls build artifacts and tracing availability.

## Dependencies And Integration Points
It depends on the Kconfig symbol in this directory and on the kernel tracing configuration. Trace include path handling is required because `define_trace.h` must locate the local trace header.

## Risks
If trace include paths or object membership drift, trace builds can fail while non-tracing builds pass. The main module name is tied to the PCI glue, so non-PCI reuse would require build restructuring.

## Test Signals
Compile with `CONFIG_USB_CDNS2_UDC=y/m`, with and without `CONFIG_TRACING`, and verify that `cdns2-trace.o` can include its generated trace definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/Makefile -->
