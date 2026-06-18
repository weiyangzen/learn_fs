# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Makefile

## Purpose
This Makefile builds the Extron DA HD 4K Plus CEC module.

## Important APIs, Types, and Functions
It composes `extron-da-hd-4k-plus-cec.o` from `extron-da-hd-4k-plus.o` and `cec-splitter.o`, and maps it to `CONFIG_USB_EXTRON_DA_HD_4K_PLUS_CEC`.

## Control Flow
Kbuild links the device/protocol driver and shared splitter policy helper into one module.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
This build composition allows `extron-da-hd-4k-plus.c` to call the local splitter policy functions without exporting them globally.

## Risks and Test Signals
Build tests should confirm both objects are included; omitting `cec-splitter.o` would leave unresolved splitter helper symbols.
