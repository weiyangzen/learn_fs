# sources/distributed-fs/ceph-client/include/linux/rtsx_common.h

## Purpose
`rtsx_common.h` holds shared constants and slot metadata for Realtek RTSX card-reader PCI child drivers.

## Important APIs, types, and functions
The header defines driver-name constants, `RTSX_REG_PAIR()`, spread-spectrum clock depth constants, card indexes `RTSX_SD_CARD` and `RTSX_MS_CARD`, clock-conversion direction constants, and `struct rtsx_slot` containing a platform device and card-event callback.

## Control flow, state, and persistence
Parent card-reader code creates platform child devices for card slots and stores each slot's event callback. Card-detect or interrupt handling invokes the callback to notify the SD/MMC or MemoryStick child. State persists in the parent `rtsx_slot` array while the PCI reader is registered.

## Dependencies and integration points
It integrates the RTSX PCI core with platform child drivers, and its constants are shared with `rtsx_pci.h`. It depends only on a forward `struct platform_device`.

## Risks and test signals
Risks include mismatched card indexes between parent and child drivers, wrong packed register/value pairs, and stale callbacks during remove. Test signals include PCI reader probe creating slots, SD/MS card insert/remove notifications, clock conversion paths, and module unload cleanup.
