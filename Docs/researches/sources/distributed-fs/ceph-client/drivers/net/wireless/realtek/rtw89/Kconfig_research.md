## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Kconfig

Purpose: Kconfig menu for Realtek rtw89 Wi-Fi 6/6E/7 driver support. It defines the top-level `RTW89` menu, core/transport/chip internal symbols, user-selectable adapter modules, and debug options.

Important symbols: `RTW89` depends on `MAC80211`; `RTW89_CORE` selects `WANT_DEV_COREDUMP`; `RTW89_PCI` and `RTW89_USB` are transport internals. Chip internals include `RTW89_8851B`, `8852A`, `8852B_COMMON`, `8852B`, `8852BT`, `8852C`, and `8922A`. User-visible modules cover PCI and USB variants: 8851BE/BU, 8852AE/AU/BE/BU/BTE/CE/CU, and 8922AE. Debug options are `RTW89_DEBUGMSG` and `RTW89_DEBUGFS`.

Control flow and state: build-time dependency selection only. Choosing a device symbol selects core, transport, and chip support so the Makefile can link the corresponding objects.

Dependencies and integration: integrates with Linux kernel Kconfig, mac80211, PCI/USB subsystems, cfg80211 debugfs, and Makefile object lists.

Risks and test signals: dependency mistakes produce missing symbols or modules without required transport/core code. Test with `allmodconfig`, individual device configs, PCI-only/USB-only builds, and debugfs-disabled builds.
