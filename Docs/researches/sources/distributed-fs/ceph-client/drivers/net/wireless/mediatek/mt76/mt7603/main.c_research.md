# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/main.c

## Purpose
MT7603 mac80211 operations, module entry/exit, interface lifecycle, channel/power/filter/BSS configuration, station/key/AMPDU/rate handling, power-save frame release, and TX entrypoint.

## Important APIs, Types, And Functions
- `mt7603_start()` and `mt7603_stop()` control running state, counters, MAC start/stop, and periodic MAC work.
- `mt7603_add_interface()` and `mt7603_remove_interface()` allocate/free interface indices, program MAC/BSSID registers, create per-vif reserved WCIDs, and manage beacon timers.
- `mt7603_set_channel()` stops beaconing/MAC, updates bandwidth, sends MCU channel command, loads RSSI offsets, writes channel frequency index, restarts MAC/work, resets survey/CCA/EDCCA, and restores beaconing.
- `mt7603_config()`, `mt7603_configure_filter()`, `mt7603_bss_info_changed()`, and `mt7603_set_sar_specs()` handle mac80211 config changes.
- Station operations `mt7603_sta_add()`, `mt7603_sta_event()`, `mt7603_sta_remove()`, and `mt7603_sta_ps()` manage WTBL allocation, caps, polling, PS, and queued frames.
- `mt7603_release_buffered_frames()` releases per-station PS queue entries and falls back to common mt76 buffering.
- `mt7603_set_key()` supports TKIP/CCMP hardware keys with software fallback for unsupported/per-STA GTK cases.
- `mt7603_conf_tx()`, `mt7603_ampdu_action()`, `mt7603_sta_rate_tbl_update()`, `mt7603_set_coverage_class()`, and `mt7603_tx()` implement QoS, BA, rate, timing, and TX routing.
- `mt7603_ops` is the mac80211 callback table; module init registers platform and PCI drivers.

## Control Flow
mac80211 calls `start`, then interface/station/key/config callbacks as network state changes. TX selects the WCID from control STA, VIF, or global reserved WCID and calls common `mt76_tx()`. Channel changes route through shared `mt76_update_channel()` to this file's set-channel implementation. Module init registers the SoC platform driver first, then PCI if enabled; exit unregisters in reverse.

## State And Persistence
State includes `dev->mt76.vif_mask`, per-vif indices/WCIDs, MAC/BSSID hardware registers, `dev->rxfilter`, slottime, coverage class, station WTBL/PS/rate state, beacon timer state, SAR frequency powers, `mphy.state`, survey time, and delayed MAC work. No durable state is written.

## Dependencies And Integration Points
Integrates mac80211 with lower-level `mac.c`, `mcu.c`, `beacon.c`, common mt76 station/TX/RX helpers, PCI and platform frontends, cfg80211 SAR/regulatory APIs, and Kconfig-selected module registration.

## Risks
VIF index allocation uses `__ffs64(~vif_mask)` and must stay bounded by `MT7603_MAX_INTERFACES`. BSS/beacon changes disable tasklets around timer updates; missing serialization can race pre-TBTT. Channel changes must restore MAC/beacon state even on failures. Hardware key limitations require correct `-EOPNOTSUPP` fallback. Empty `flush()` means mac80211 flush requests rely on common queue draining elsewhere.

## Test Signals
Test station, AP, P2P, adhoc/mesh where enabled, multi-BSSID AP up to limits, start/stop, channel/power/SAR updates, monitor filters, key fallback, AMPDU start/stop, rate updates, PS release, and module load/unload for PCI and platform paths. Watch for leaked vif_mask bits and stale WCIDs after interface removal.
