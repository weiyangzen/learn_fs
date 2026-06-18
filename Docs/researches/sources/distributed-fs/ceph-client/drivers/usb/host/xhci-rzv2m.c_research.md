# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.c

## Purpose
Provides RZ/V2M-specific xHCI platform hooks for the Renesas wrapper. It resets the shared USB3 dual-role controller block during xHCI initialization and enables host interrupt sources when xHCI starts.

## Important APIs, Types, And Functions
The exported hook functions are `xhci_rzv2m_init_quirk(struct usb_hcd *hcd)` and `xhci_rzv2m_start(struct usb_hcd *hcd)`. Register definitions include `RZV2M_USB3_INTEN`, `RZV2M_USB3_INT_XHC_ENA`, `RZV2M_USB3_INT_HSE_ENA`, and `RZV2M_USB3_INT_ENA_VAL`.

## Control Flow
`xhci_rzv2m_init_quirk()` is called by the Renesas platform match data before generic xHCI setup and invokes `rzv2m_usb3drd_reset(dev->parent, true)` on the parent dual-role device. `xhci_rzv2m_start()` runs during HCD start and, if registers are mapped, ORs xHCI and host system error interrupt enables into the wrapper interrupt-enable register.

## State And Persistence
State is entirely hardware-side: the parent DRD reset line/state and the interrupt enable register. No private RZ/V2M software state is allocated.

## Dependencies And Integration Points
Depends on `linux/usb/rzv2m_usb3drd.h`, generic xHCI types, and `xhci-plat.h`. It is selected by `xhci-rcar.c` match data for `renesas,rzv2m-xhci`.

## Risks And Test Signals
Risks include parent-device assumptions, reset ordering with the DRD block, and missing interrupts if the enable register is not retained. Test signals include RZ/V2M host probe, parent reset side effects on role switching, USB enumeration after reset, interrupt delivery, and remove/reprobe cycles.
