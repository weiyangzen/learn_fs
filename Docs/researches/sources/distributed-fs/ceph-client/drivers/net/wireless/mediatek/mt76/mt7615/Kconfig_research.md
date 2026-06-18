# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Kconfig

Purpose: kernel configuration menu for MT7615/MT7622/MT7663 driver variants and their common support objects.

Important symbols: `MT7615_COMMON` selects `WANT_DEV_COREDUMP` and `MT76_CONNAC_LIB`; `MT7615E` enables PCIe MT7615/MT7663 support and depends on MAC80211 and PCI; `MT7622_WMAC` enables integrated MT7622 WMAC support when `MT7615E` and MediaTek architecture or compile-test are available and selects REGMAP; `MT7663_USB_SDIO_COMMON` feeds shared USB/SDIO code; `MT7663U` selects `MT76_USB`; `MT7663S` selects `MT76_SDIO`.

Control flow: Kconfig selections determine which objects the Makefile builds. Enabling any transport selects the common mt7615 implementation; transport-specific symbols add PCI, SoC, USB, or SDIO entry points and bus libraries.

State and persistence: no runtime state. Build-time choices affect module availability, firmware declarations compiled into modules, and whether coredump/regmap/USB/SDIO dependencies are present.

Dependencies and integration: integrates the driver with kernel `drivers/net/wireless/mediatek/mt76` build configuration. The help text documents hardware capabilities and module build expectations for users.

Risks: `MT7622_WMAC` depends on `MT7615E`, so SoC support is tied to the PCIe driver symbol and common PCIe object grouping. Missing `MAC80211`, `PCI`, `USB`, or `MMC` dependencies prevent the expected transport from building. `default y` for MT7622 under its dependencies can increase build coverage and binary surface.

Test signals: `make menuconfig` visibility, randconfig/allmodconfig coverage, correct module object generation for each selected transport, and modinfo showing expected firmware and aliases from corresponding source files.
