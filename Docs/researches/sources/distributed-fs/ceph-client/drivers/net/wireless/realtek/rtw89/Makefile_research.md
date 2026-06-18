## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Makefile

Purpose: builds rtw89 core, chip, bus, and debug modules according to Kconfig symbols.

Important targets: `rtw89_core.o` includes core, mac80211, MAC/PHY, firmware, CAM, EFUSE, regulatory/SAR, coexistence, power-save, channel, SER, ACPI, and util objects; PM adds `wow.o`. Chip modules aggregate chip logic, tables, RFK, and RFK tables for 8851B/8852A/8852B/8852BT/8852C/8922A. Interface modules include per-device PCI/USB glue objects and transport modules `rtw89_pci.o` (`pci.o`, `pci_be.o`) and `rtw89_usb.o` (`usb.o`).

Control flow and state: no runtime flow; it maps Kconfig booleans/tristates to object composition. The ordering ensures common support is available before chip/interface modules at link time.

Dependencies and integration: coupled tightly to `Kconfig` symbol names and source-file names. Debug object inclusion depends on `CONFIG_RTW89_DEBUG`.

Risks and test signals: missing object entries cause unresolved symbols; stale entries cause build failures. Test by building each Kconfig combination, especially PM on/off, debug on/off, USB-only, PCI-only, and Wi-Fi 7 8922A.
