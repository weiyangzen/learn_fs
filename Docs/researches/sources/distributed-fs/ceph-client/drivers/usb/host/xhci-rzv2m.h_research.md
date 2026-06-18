# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.h

## Purpose
Declares the optional RZ/V2M xHCI hook functions used by the Renesas platform wrapper and provides compile-time stubs when RZ/V2M support is disabled.

## Important APIs, Types, And Functions
The header declares or stubs `xhci_rzv2m_start(struct usb_hcd *hcd)` and `xhci_rzv2m_init_quirk(struct usb_hcd *hcd)` behind `IS_ENABLED(CONFIG_USB_XHCI_RZV2M)`.

## Control Flow
In enabled builds, `xhci-rcar.c` match data calls the real init and start hooks. In disabled builds, start is a no-op and init returns `-EINVAL`, making accidental selection of RZ/V2M match data fail rather than silently proceeding without required reset handling.

## State And Persistence
No state is defined. Runtime state belongs to the RZ/V2M implementation and generic platform HCD.

## Dependencies And Integration Points
Private compile-time boundary between `xhci-rcar.c` and `xhci-rzv2m.c`. It relies on the caller including suitable USB HCD type declarations.

## Risks And Test Signals
Risks include disabled-build stubs causing probe failure for RZ/V2M compatibles, declaration drift, and missing type visibility. Test signals include builds with `CONFIG_USB_XHCI_RZV2M` enabled and disabled, plus RZ/V2M platform probe confirming the real hooks are linked.
