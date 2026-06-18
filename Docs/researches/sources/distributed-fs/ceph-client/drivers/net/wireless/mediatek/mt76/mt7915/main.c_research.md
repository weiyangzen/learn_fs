# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/main.c

## Purpose

`main.c` is the mac80211-facing control plane for the MT7915 family driver. It implements `const struct ieee80211_ops mt7915_ops`, translates mac80211 lifecycle and configuration callbacks into mt76 state changes and MCU commands, and coordinates per-phy, per-vif, and per-station runtime state. It is not the low-level DMA or firmware transport layer; instead, it sits above `mcu.c`, `mac.c`, mt76 common helpers, and MMIO bus operations.

The file owns user-visible wireless behavior such as device start/stop, interface allocation, BSS updates, AP start/stop, channel changes, key installation, rate-control updates, AMPDU aggregation, TSF operations, antenna selection, SAR power updates, ethtool statistics, TWT teardown requests, background radar, and WED forwarding path export.

## Important APIs, Types, and Functions

- `mt7915_ops` is the main exported mac80211 operation table. It wires local callbacks into mac80211 and delegates generic behavior to mt76 helpers for TX queues, scans, survey, station state transitions, txpower query, buffered frames, testmode, and WED TC setup.
- `mt7915_run()`, `mt7915_start()`, and `mt7915_stop()` control radio bring-up and shutdown for primary and secondary PHYs. They toggle MCU power management, MAC enable state, noise floor collection, thermal protection, RTS threshold, SKU power enforcement, RX path/channel setup, and watchdog work.
- `mt7915_add_interface()` and `mt7915_remove_interface()` allocate and release vif indices, OMAC slots, WMM index, WCIDs, BSS state, dev-info state, and the internal per-vif WCID used for non-station traffic.
- `mt7915_set_channel()` performs per-channel firmware and MAC reconfiguration: optional DPD calibration, MCU channel switch, MAC timing update, DFS radar detector initialization, CCA reset, MIB reset, noise reset, and watchdog scheduling.
- `mt7915_set_key()` validates cipher support, handles BIP key-index selection, updates per-vif cipher state, programs WCID key state through mt76, and sends MCU key records.
- `mt7915_bss_info_changed()`, `mt7915_start_ap()`, `mt7915_stop_ap()`, `mt7915_channel_switch_beacon()`, and `mt7915_update_bss_color()` coordinate BSS firmware records, virtual STA records, beacons, protection, slot timing, QoS/EDCA, OBSS PD, in-band discovery, and color-change state.
- `mt7915_mac_sta_add()`, `mt7915_mac_sta_event()`, and `mt7915_mac_sta_remove()` manage station WCIDs, firmware STA records, rate-control records, TWT cleanup, duplicate AP station pruning, and polling/rate-control lists.
- `mt7915_ampdu_action()` maps mac80211 AMPDU actions into mt76 RX aggregation state and MCU BA add/remove commands.
- `mt7915_get_tsf()`, `mt7915_set_tsf()`, and `mt7915_offset_tsf()` manipulate LPON TSF registers with chip-specific control registers.
- `mt7915_sta_statistics()`, `mt7915_get_et_strings()`, `mt7915_get_et_sset_count()`, and `mt7915_get_et_stats()` expose station and device counters, including WED offload counters and page-pool stats.
- `mt7915_set_radar_background()` controls background RDD state and `dev->rdd2_phy` ownership.
- `mt7915_net_fill_forward_path()` is compiled with WED support and exports hardware forwarding metadata to the networking stack.

## Control Flow

Startup begins in mac80211 `.start`, which flushes pending initialization work, locks `dev->mt76.mutex`, and calls `mt7915_run()`. `mt7915_run()` first detects whether any PHY is already running. If this is the first active PHY, it disables MCU power-save for the primary band, enables the MAC and RX header translation, and enables noise-floor collection. If the requested PHY is the extension PHY, it repeats the power/MAC/noise setup for that band. It then configures thermal throttling, thermal protection, RTS threshold, SKU power enforcement, and RX path channel information before marking the PHY running and queueing watchdog work.

Stop is the inverse at PHY granularity. `mt7915_stop()` cancels watchdog work, resets testmode, clears the running bit, disables the extension PHY if stopping it, and disables the primary PHY only if no PHY remains running. This shared-device check avoids powering down the shared hardware while a second band is still active.

Interface addition is allocation-heavy. `mt7915_add_interface()` resets testmode, records monitor vifs, picks a free `mvif->mt76.idx` from `dev->mt76.vif_mask`, picks an OMAC slot from `phy->omac_mask` based on interface type, chooses a WMM set, sends `mt7915_mcu_add_dev_info()`, marks masks, allocates a WTBL/WCID entry, initializes the per-vif `mt7915_sta`, clears admission counters, assigns the vif txq WCID, adjusts offload flags, initializes bitrate masks and capabilities, then creates BSS and STA records in firmware. Removal deletes firmware BSS/STA/dev-info records, clears masks, drops RCU WCID pointer, removes poll list entries, and calls `mt76_wcid_cleanup()`.

Station flow is split between mt76 station callbacks and mac80211 state events. `mt7915_mac_sta_add()` allocates a station WCID and sends a newly created disconnected STA record. On associate, `mt7915_mac_sta_event()` sends a connect STA record, tweaks WTBL DW30, installs rate control, and enables the WCID. On authorize, it disconnects matching STAs from other AP vifs before marking the current station port secure. On disassociate, it tears down all TWT flows under the mt76 mutex, sends a disconnect STA record, and disables the WCID.

BSS changes are handled under the mt76 mutex. BSSID changes, association changes, and non-AP beacon enable transitions decide whether to add or remove BSS and virtual STA firmware records. The same callback also updates protection mode, slot timing, EDCA/tx command mode, OBSS spatial reuse, BSS color, beacon templates, FILS discovery, and unsolicited broadcast probe responses.

## State and Persistence Behavior

State is in memory and hardware/firmware, not persisted to disk by this file. Durable calibration and EEPROM handling live elsewhere. Important state mutations include:

- `dev->mt76.vif_mask` and `phy->omac_mask` track allocated software vif indices and hardware OMAC slots.
- `dev->mt76.wcid_mask` and `dev->mt76.wcid[]` track allocated firmware/hardware station table entries; RCU protects readers of WCID pointers.
- `mvif->bitrate_mask`, `mvif->queue_params`, and `mvif->cap` cache mac80211 policy that later MCU commands use for rate control, EDCA, and beamforming.
- `msta->wcid` carries per-station firmware index, tx flags, aggregation state, header-translation flags, statistics, and key index state.
- `msta->twt.flow[]` and `dev->twt` state are cleaned up when stations disassociate.
- `phy->rxfilter`, `dev->monitor_mask`, `phy->slottime`, `phy->coverage_class`, `phy->noise`, `phy->throttle_state`, and channel-state/MIB structures represent live radio state.
- `dev->rdd2_phy` and `dev->rdd2_chandef` record which PHY owns background radar detection.

The file consistently uses `dev->mt76.mutex` for firmware and hardware configuration sequences, spinlocks for station poll/rate-control lists, and RCU for WCID pointer publication. Some MCU calls during teardown occur outside the mutex before later mask cleanup, so ordering depends on the higher mac80211/mt76 lifecycle.

## Dependencies and Integration Points

`main.c` depends on mac80211 and cfg80211 for callback contracts, vifs, stations, BSS configuration, channel definitions, SAR, radar, TWT, and statistics. It depends on mt76 common helpers for WCID allocation, TX, testmode, survey, scan, key setup, rate helpers, WED netdev hooks, and work scheduling. It depends heavily on `mcu.c` for firmware commands and on `mac.c` for WTBL updates, timing, counters, TXWI generation, and TWT teardown. It also touches MMIO registers via `mt76_rr/wr/rmw` macros backed by `mmio.c`.

WED integration is conditional on `CONFIG_NET_MEDIATEK_SOC_WED`; station statistics and forwarding path behavior change when WED is active. Debugfs station hooks are conditional on `CONFIG_MAC80211_DEBUGFS`. Testmode resets and antenna overrides are conditional on `CONFIG_NL80211_TESTMODE`.

## Risks and Edge Cases

- Interface allocation has several coupled resources. A failure after dev-info creation or mask updates can leave partial firmware or mask state if not carefully unwound; this path should be reviewed when changing allocation order.
- `get_free_idx()` uses `ffs()` on a generated mask and returns a 1-based index that callers subtract. Boundary changes to OMAC constants can break slot selection.
- `mt7915_set_key()` falls back for unsupported ciphers and per-STA RX GTK limitations; changing cipher handling risks hardware/software encryption mismatch.
- BSS change handling intentionally delays removals until the end of the callback; reordering can race beacon, BSS, and STA firmware records.
- Rate-control fixed-mask logic accepts only specific mask shapes. Multi-rate or mixed-preamble masks can silently fall back to firmware rate control.
- TSF register accesses are chip-specific and assume the mt76 mutex is held by the internal helper.
- Background radar state rejects concurrent ownership with `-EBUSY`; caller behavior must tolerate this.
- WED station statistics are partly queried from WA firmware and partly accumulated locally; counter freshness and overflow behavior differ from non-WED paths.

## Test Signals

Useful validation signals include successful interface create/remove cycles across AP, STA, monitor, mesh, and dual-band modes; `iw` association and AP bring-up; key install for CCMP/GCMP/TKIP/BIP; channel switch and DFS radar events; `iw station dump` TX/RX bitrate and ACK signal fields; ethtool stat count matching `MT7915_SSTATS_LEN + page_pool_ethtool_stats_get_count()`; AMPDU start/stop under traffic; TWT setup/teardown; SAR power updates; monitor filter behavior; WED forwarding path activation; and suspend/reconfig complete paths waking queues and restarting watchdog work.
