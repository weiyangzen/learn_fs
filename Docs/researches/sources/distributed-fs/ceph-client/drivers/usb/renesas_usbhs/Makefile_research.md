<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile

## Purpose
Builds the composite `renesas_usbhs.o` object and conditionally includes host/gadget frontends.

## Important APIs, Types, And Functions
Base objects are `common.o mod.o pipe.o fifo.o rcar2.o rcar3.o rza.o rza2.o`. `mod_host.o` is added when `CONFIG_USB_RENESAS_USBHS_HCD` is set; `mod_gadget.o` is added when `CONFIG_USB_RENESAS_USBHS_UDC` is set.

## Control Flow
`obj-$(CONFIG_USB_RENESAS_USBHS)` selects the composite object. Conditional blocks append frontend objects.

## State And Persistence
Build-time composition only.

## Dependencies And Integration Points
Must match `mod.h` conditional prototypes/stubs. SoC glue objects are always linked into the base driver.

## Risks
Mismatch with `mod.h` guards can create unresolved symbols or inactive frontends. Always-linked SoC glue must build under all supported configurations.

## Test Signals
Build all HCD/UDC enabled/disabled combinations for built-in and module driver modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile -->
