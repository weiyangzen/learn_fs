# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Makefile

## Purpose
This Makefile maps MT7921 Kconfig symbols to the shared common module and the PCIe, SDIO, and USB transport modules.

## Important APIs, Types, And Functions
`mt7921-common-y` builds `mac.o`, `mcu.o`, `main.o`, `init.o`, and `debugfs.o`. `mt7921-common-$(CONFIG_NL80211_TESTMODE)` adds `testmode.o`. `mt7921e-y` builds `pci.o`, `pci_mac.o`, and `pci_mcu.o`; `mt7921s-y` builds `sdio.o`, `sdio_mac.o`, and `sdio_mcu.o`; `mt7921u-y` builds `usb.o`.

## Control Flow
Object inclusion follows Kconfig: `CONFIG_MT7921_COMMON` creates `mt7921-common.o`, while each bus symbol creates its own transport object. The bus modules call into exported symbols from the common module for mac80211 ops, RX/TX processing, MCU command helpers, reset work, and device registration.

## State And Persistence
The file stores build composition only. Its runtime effect is module boundaries and exported symbol dependencies.

## Dependencies And Integration Points
It depends on Kbuild syntax, Kconfig symbols from `Kconfig`, and neighboring source files. It also defines whether testmode code participates in common-module builds.

## Risks
Incorrect object membership can cause unresolved symbols or duplicate module definitions. The common module must include all transport-independent exports used by PCI, SDIO, and USB. Optional testmode code must remain guarded by `CONFIG_NL80211_TESTMODE`.

## Test Signals
Build all transport combinations and run `modpost` for unresolved-symbol checks. Testmode builds should expose cfg80211 testmode callbacks, while non-testmode builds should omit `testmode.o` cleanly.
