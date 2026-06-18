# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Kconfig

Purpose: this Kconfig file declares the MT76x0 driver build options. `MT76x0_COMMON` is an internal tristate selected by bus-specific variants and selects `MT76x02_LIB`. `MT76x0U` exposes USB dongle support and selects `MT76x02_USB`; `MT76x0E` exposes PCIe support for MT7610/MT7630 devices.

Important symbols: `MT76x0U` depends on `MAC80211` and `USB`, while `MT76x0E` depends on `MAC80211` and `PCI`. Both select `MT76x0_COMMON`; neither directly selects firmware or platform-specific regulatory features. Help text documents 802.11ac 1x1 433 Mbps devices and module build behavior.

Control flow and integration: Kconfig selection determines which objects the Makefile links. Selecting USB or PCIe pulls in the shared init/main/eeprom/phy code through `MT76x0_COMMON` plus bus-specific transport and firmware loaders.

State and persistence behavior: no runtime state is stored here. The persistent effect is build-time configuration in kernel `.config`, which controls module availability and dependency closure.

Dependencies: the file integrates with the parent mt76 Kconfig tree and relies on mac80211 plus either USB or PCI kernel subsystems. The common code depends on the mt76x02 library selected here.

Risks: missing dependency or select statements can produce link failures or drivers without required bus helpers. Because common code is selected only through USB/PCI variants, new bus support would need an additional symbol and Makefile object mapping.

Test signals: `make oldconfig`, `make menuconfig`, and kernel builds with `CONFIG_MT76x0U=m`, `CONFIG_MT76x0E=m`, both enabled, and each disabled should verify dependency and object selection.
