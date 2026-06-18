# sources/distributed-fs/ceph-client/drivers/usb/atm/Makefile

## Purpose
`drivers/usb/atm/Makefile` maps the USB ATM Kconfig symbols to the shared core module and mini-driver modules.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_CXACRU) += cxacru.o`
- `obj-$(CONFIG_USB_SPEEDTOUCH) += speedtch.o`
- `obj-$(CONFIG_USB_UEAGLEATM) += ueagle-atm.o`
- `obj-$(CONFIG_USB_ATM) += usbatm.o`
- `obj-$(CONFIG_USB_XUSBATM) += xusbatm.o`

## Control Flow
Kbuild includes object files according to the tristate values selected in Kconfig. The mini-drivers are independent modules that depend on symbols exported by `usbatm.o`, so module dependency generation should load `usbatm` first.

## State And Persistence Behavior
This file affects build graph state only. Runtime state is entirely in the generated modules.

## Dependencies And Integration Points
The object names align with `drivers/usb/atm/Kconfig` module descriptions and with C module names. It integrates with the top-level USB Makefile, which descends into `atm/` for USB ATM-related configurations.

## Risks And Edge Cases
If a mini-driver symbol is selected while `USB_ATM` is absent or misconfigured, linking would fail because the mini-driver calls shared `usbatm` exports. Current Kconfig nesting prevents that. Renaming `ueagle-atm.o` or other hyphenated module names requires matching source and firmware documentation updates.

## Test Signals
Build each symbol as module and verify `modules.order` includes the expected `.ko` files. Run `modinfo` to confirm dependencies on `usbatm` for mini-drivers.
