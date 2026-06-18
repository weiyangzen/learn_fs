
# sources/distributed-fs/ceph-client/drivers/media/usb/siano/Makefile

## Purpose
This Makefile builds the Siano USB transport and adds include paths needed for shared Siano headers.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_SMS_USB_DRV) += smsusb.o` and adds `-I $(srctree)/drivers/media/common/siano`. It also appends `$(extra-cflags-y)` and `$(extra-cflags-m)` to `ccflags-y`.

## Control Flow
Kbuild compiles `smsusb.c` when the Siano USB Kconfig symbol is enabled. The include path lets `smsusb.c` include `smscoreapi.h`, `sms-cards.h`, and related common headers.

## State and Persistence
No runtime state exists here; this is build graph and compiler-flag state.

## Dependencies and Integration Points
The Makefile depends on Kbuild's object selection and the common Siano source tree.

## Risks and Edge Cases
The extra CFLAGS pass-through can affect warnings or ABI assumptions if set by parent makefiles. Moving common Siano headers requires updating this include path.

## Test Signals
Build Siano USB support and confirm `smsusb.c` resolves common Siano includes without local relative include hacks.
