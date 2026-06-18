# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Makefile

Purpose: Object composition for MT7925 kernel modules.

Important APIs/types/functions: `mt7925-common.o` is built for `CONFIG_MT7925_COMMON`; `mt7925e.o` for PCIe; `mt7925u.o` for USB. Common objects are `mac.o`, `mcu.o`, `regd.o`, `main.o`, `init.o`, and `debugfs.o`; `testmode.o` is conditional on `CONFIG_NL80211_TESTMODE`; PCIe objects are `pci.o`, `pci_mac.o`, `pci_mcu.o`; USB object is `usb.o`.

Control flow: Kbuild combines common and bus-specific objects according to Kconfig symbols. The bus modules link against exported common symbols such as MAC/MCU helpers and mac80211 ops.

State/persistence: no runtime state. It controls built module contents.

Dependencies/integration: must match Kconfig symbols and exported functions across MT7925 common, PCIe, and USB source files.

Risks: missing a common object creates link failures; adding new exported bus helpers requires object list updates. Testmode code is excluded unless nl80211 testmode is enabled, so references must stay macro-guarded.

Test signals: compile with `CONFIG_MT7925E=m`, `CONFIG_MT7925U=m`, both enabled, and `CONFIG_NL80211_TESTMODE` toggled.
