# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.h

## Purpose
Declares the optional MVEBU MBus initialization hook for platform xHCI drivers and provides a no-op stub when MVEBU xHCI support is not built.

## Important APIs, Types, And Functions
The only API is `xhci_mvebu_mbus_init_quirk(struct usb_hcd *hcd)`, guarded by `IS_ENABLED(CONFIG_USB_XHCI_MVEBU)`. `struct usb_hcd` is forward-declared to avoid pulling in USB HCD headers.

## Control Flow
There is no runtime flow in the enabled declaration path. In disabled builds, callers can still invoke the inline stub and receive success, allowing generic platform glue to compile and run without special preprocessor branches.

## State And Persistence
The header exposes no state. Whether MBus hardware state is programmed depends entirely on whether the C implementation is built and selected by platform match data.

## Dependencies And Integration Points
This private header is included by `xhci-plat.c` and `xhci-mvebu.c`. It decouples Armada-specific setup from the generic xHCI platform driver while keeping one callback signature in `struct xhci_plat_priv`.

## Risks And Test Signals
Risks are mostly configuration-related: a disabled or missing implementation silently turns the quirk into a no-op, which may leave DMA windows unprogrammed on affected SoCs. Test signals include build coverage with `CONFIG_USB_XHCI_MVEBU=y/m/n` and Armada runtime transfer tests proving the quirk was actually linked and called where required.
