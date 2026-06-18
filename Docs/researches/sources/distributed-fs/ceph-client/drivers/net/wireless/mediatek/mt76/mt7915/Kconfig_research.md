# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Kconfig

Purpose: Build-time configuration for MT7915-family drivers. It exposes PCIe MT7915E support and optional MT798x SoC WMAC support.

Important symbols: `MT7915E` is tristate, depends on `MAC80211` and `PCI`, selects `MT76_CONNAC_LIB`, `WANT_DEV_COREDUMP`, and `RELAY`. `MT798X_WMAC` is bool, depends on `MT7915E` and `ARCH_MEDIATEK || COMPILE_TEST`, and selects `REGMAP`.

Control flow: there is no runtime control flow; Kconfig controls which objects can be built and which supporting kernel subsystems are pulled in.

State and persistence: persistent state is kernel configuration. Enabling `MT7915E=m` builds a module; enabling `MT798X_WMAC` compiles SoC support into that driver build.

Dependencies and integration: ties the driver to mac80211, PCI, relay-based firmware logging, devcoredump request support, Connac common library, MediaTek SoC architecture support, and regmap for SoC access.

Risks: selecting `WANT_DEV_COREDUMP` is not the same as enabling `CONFIG_DEV_COREDUMP`; coredump code remains conditional in the Makefile/header. `MT798X_WMAC` cannot be selected independently of PCIe support, which may surprise SoC-only configurations.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST` on non-MediaTek arches, builds with and without `CONFIG_DEV_COREDUMP`, and module dependency inspection for relay/mac80211/mt76_connac.
