# sources/distributed-fs/ceph-client/drivers/usb/Makefile

## Purpose
`drivers/usb/Makefile` maps USB Kconfig symbols to subdirectory builds. It is the top-level kbuild dispatcher for USB common/core code, host controllers, dual-mode controllers, class/storage/image/serial/misc drivers, USB ATM, gadgets, USBIP, Type-C, and role-switch support.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_COMMON) += common/` and `obj-$(CONFIG_USB) += core/` build core infrastructure.
- Multiple HCD symbols append `host/`, allowing the host subdirectory to be entered for many controller choices.
- `obj-$(CONFIG_USB_C67X00_HCD) += c67x00/` dispatches the Cypress controller files in this work item.
- `obj-$(CONFIG_USB_ATM) += atm/` and `obj-$(CONFIG_USB_SPEEDTOUCH) += atm/` enter the ATM subdirectory.
- `obj-$(CONFIG_USB) += storage/` and `obj-$(CONFIG_USB_STORAGE) += storage/` keep storage subdirectory traversal available for core storage glue.

## Control Flow
Kbuild evaluates each `obj-*` line against the final configuration. Built-in `y` descends into a subdirectory for built-in objects; `m` descends for modules. The same subdirectory can appear from multiple config symbols, and kbuild coalesces traversal. This file does not compile C directly; child Makefiles define exact objects.

## State And Persistence Behavior
It creates build graph state only. There is no runtime behavior, but enabled symbols determine which modules and built-in objects are present.

## Dependencies And Integration Points
The Makefile must stay aligned with `drivers/usb/Kconfig` and child Makefiles. It integrates with `drivers/usb/atm/Makefile` for `usbatm`, `speedtch`, `cxacru`, `ueagle-atm`, and `xusbatm`, and with `drivers/usb/c67x00/Makefile` for the Cypress host controller aggregate object.

## Risks And Edge Cases
Duplicate subdirectory entries are intentional but can obscure why a directory is entered. If a Kconfig symbol is renamed without updating this file, selected code silently stops building. Entering `atm/` on `CONFIG_USB_SPEEDTOUCH` as well as `CONFIG_USB_ATM` protects SpeedTouch selection, but child dependencies still matter.

## Test Signals
Run targeted builds with `CONFIG_USB_C67X00_HCD=m`, `CONFIG_USB_ATM=m`, and individual ATM mini-drivers. Use `make V=1` to confirm subdirectory traversal and resulting module names. Compare generated `modules.order` with expected USB modules.
