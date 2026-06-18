# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Kconfig

## Purpose
This Kconfig file declares build-time options for the MT7921 driver family: a shared common module and bus-specific PCIe, SDIO, and USB front ends.

## Important APIs, Types, And Functions
`config MT7921_COMMON` is a tristate selected by concrete transports and selects `MT792x_LIB` plus `WANT_DEV_COREDUMP`. `config MT7921E` enables PCIe support and depends on `MAC80211` and `PCI`. `config MT7921S` enables SDIO support, selects `MT76_SDIO`, and depends on `MAC80211` and `MMC`. `config MT7921U` enables USB support, selects `MT792x_USB`, and depends on `MAC80211` and `USB`.

## Control Flow
Kconfig selection determines which objects in the Makefile are built. Choosing any bus-specific symbol pulls in `MT7921_COMMON`, which builds shared mac80211, MCU, init, MAC, and debugfs logic. Transport options then compile the matching probe/reset/MCU bus implementation.

## State And Persistence
There is no runtime state. The persistent effect is kernel configuration state and module availability.

## Dependencies And Integration Points
This file integrates with the parent mt76 Kconfig tree, mac80211, bus subsystem options, coredump support, and the Makefile in this directory.

## Risks
Missing `select` or `depends on` entries can create link failures or expose unusable menu options. The common symbol is hidden, so all transport options must select it. Optional testmode compilation is controlled elsewhere through `CONFIG_NL80211_TESTMODE` in the Makefile.

## Test Signals
Build matrix signals include `MT7921E=m/y`, `MT7921S=m/y`, `MT7921U=m/y`, combinations of transports, and builds with and without `NL80211_TESTMODE`. `modinfo` should show each bus module and the shared common module as expected.
