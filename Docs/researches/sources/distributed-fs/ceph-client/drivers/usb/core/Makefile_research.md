# Research: sources/distributed-fs/ceph-client/drivers/usb/core/Makefile

Purpose: defines the `usbcore.o` aggregate and optional USB core objects. It is the build map for core enumeration, hub, HCD, URB, message, driver binding, configuration parsing, file/minor handling, buffers, sysfs, endpoints, usbfs devio, notifications, quirks, PHY, ports, tracing, and optional platform integrations.

Important build rules: `usbcore-y` includes `usb.o hub.o hcd.o urb.o message.o driver.o config.o file.o buffer.o sysfs.o endpoint.o devio.o notify.o generic.o quirks.o devices.o phy.o port.o trace.o`. Optional objects include `of.o`, `offload.o`, `hcd-pci.o`, `usb-acpi.o`, and onboard USB platform-device data. `obj-$(CONFIG_USB) += usbcore.o`; `obj-$(CONFIG_USB_LEDS_TRIGGER_USBPORT) += ledtrig-usbport.o`. `CFLAGS_trace.o := -I$(src)` supports trace header inclusion.

Control flow and state: build-only. The object list determines which internal symbols are always present when USB is enabled and which are conditional on OF, XHCI sideband, PCI, ACPI, onboard devices, and port LED triggers.

Dependencies and integration points: ties Kconfig and source files into the kernel module or built-in `usbcore`. `devio.o` exposes `/dev/bus/usb` char operations; `devices.o` exposes topology debug/proc-style output; `config.o` parses descriptors; `buffer.o` serves HCD DMA allocation.

Risks: object ordering can matter for init/exit dependencies. Removing objects from `usbcore-y` can break internal references. `trace.o` include path must remain correct for generated trace definitions.

Test signals: full build matrix for `CONFIG_USB=y/m`, OF/ACPI/PCI variants, XHCI sideband, onboard device support, and USB port LED trigger module.
