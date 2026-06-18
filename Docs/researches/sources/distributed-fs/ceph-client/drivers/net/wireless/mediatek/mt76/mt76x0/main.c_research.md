# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/main.c

Purpose: this file provides shared mac80211 configuration callbacks for MT76x0 devices: channel switching, SAR power updates, and general config changes.

Important functions: `mt76x0_set_channel` is the driver-op set-channel path used by bus drivers. `mt76x0_set_sar_specs` updates SAR constraints and reapplies txpower when running. `mt76x0_config` handles mac80211 `IEEE80211_CONF_CHANGE_CHANNEL`, `IEEE80211_CONF_CHANGE_POWER`, and `IEEE80211_CONF_CHANGE_MONITOR`.

Control flow: channel switching disables pre-TBTT, disables the DFS tasklet on MMIO devices, calls `mt76x0_phy_set_channel`, resets channel counters/EDCCA, reinitializes DFS params for MMIO, reenables the tasklet and pre-TBTT, and returns success. Power config updates channel data before locking, then applies SAR and calls `mt76x0_phy_set_txpower` only when the PHY is running. Monitor mode toggles the promiscuous bit in `dev->mt76.rxfilter` and writes `MT_RX_FILTR_CFG`.

State and persistence behavior: it mutates `mphy->chandef` through `mt76_update_channel`, `dev->txpower_conf`, current PHY txpower through PHY helpers, DFS/pre-TBTT tasklet state, EDCCA/channel counters, and the RX filter cache. No persistent storage is changed.

Dependencies and integration: it depends on mac80211 configuration callbacks, mt76 core channel/SAR helpers, mt76x02 DFS/EDCCA/MAC helpers, and `phy.c` for channel/txpower programming. `pci.c` wires these functions into `ieee80211_ops`/driver ops; USB code likely does the same.

Risks: channel changes interact with DFS tasklets and calibration work, so ordering matters. The monitor-mode condition is counterintuitive: non-monitor sets `PROMISC`, monitor clears it, so changes require careful validation against hardware semantics. SAR updates require a valid chandef and mutex protection.

Test signals: change channel width/band under traffic, scan/DFS on PCIe, update regulatory/SAR/power level, and toggle monitor mode while checking RX filter behavior and packet capture expectations.
