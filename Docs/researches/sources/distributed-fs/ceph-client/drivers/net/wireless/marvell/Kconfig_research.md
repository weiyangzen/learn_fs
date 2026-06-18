## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Kconfig

Purpose: this vendor Kconfig menu gates Marvell wireless driver choices. `WLAN_VENDOR_MARVELL` is a boolean menu selector defaulting to yes; when enabled it sources Libertas, Libertas thin firmware, and mwifiex Kconfig files and defines the `MWL8K` PCI/PCIe mac80211 driver option.

Important symbols: `WLAN_VENDOR_MARVELL` controls menu visibility only. `MWL8K` is tristate, depends on `MAC80211 && PCI`, and builds the `mwl8k` module for Marvell TOPDOG 88W8xxx PCI/PCIe devices.

Control flow and integration: Kconfig flow is declarative. If the vendor selector is disabled, downstream Marvell driver options are hidden. If enabled, child Kconfig files contribute bus-specific and family-specific symbols. The matching `Makefile` consumes these symbols to include subdirectories or objects.

State and persistence: selections persist in the kernel `.config`, not in runtime driver state.

Dependencies and risks: incorrect dependencies can expose unbuildable drivers or hide valid hardware support. The top-level selector intentionally does not affect compiled code by itself. Test signals are Kconfig menu visibility, `allmodconfig`/`randconfig` coverage, and verifying selected symbols produce expected objects.
