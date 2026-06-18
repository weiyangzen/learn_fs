<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile

## Purpose
This Makefile builds the pureLiFi plfxlc driver object from its implementation files.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_PLFXLC) := plfxlc.o` and composes `plfxlc-objs` from `chip.o`, `firmware.o`, `usb.o`, and `mac.o`.

## Control Flow
Kbuild links the four implementation objects into one built-in or module object according to `CONFIG_PLFXLC`.

## State And Persistence
No runtime state exists; the file defines build-time object composition.

## Dependencies And Integration Points
This integrates with the parent pureLiFi Makefile and the Kconfig symbol. It reflects the driver layering: chip control, firmware staging, USB transport, and mac80211 integration.

## Risks
Adding a new source file without updating `plfxlc-objs` will omit code. Object order is simple and should not matter except for module init/exit symbols in `usb.o`.

## Test Signals
Build with `CONFIG_PLFXLC=m` and verify all four object files are compiled and linked into `plfxlc.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/Makefile -->
