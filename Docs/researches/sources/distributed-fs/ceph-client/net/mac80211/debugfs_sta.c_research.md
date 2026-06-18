# sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.c

## Purpose

`debugfs_sta.c` creates station and per-link-station debugfs diagnostics. It exposes station flags, AID, PS buffering, last sequence numbers, AQM/AQL/airtime state, aggregation session controls, driver-buffered TIDs, driver-owned station debugfs, and HT/VHT/HE/EHT capability decoders.

## Important APIs, Types, And Functions

The lifecycle APIs are `ieee80211_sta_debugfs_add()`, `ieee80211_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_add()`, `ieee80211_link_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_drv_add()`, and `ieee80211_link_sta_debugfs_drv_remove()`. Station file handlers include `sta_flags_read()`, `sta_num_ps_buf_frames_read()`, `sta_last_seq_ctrl_read()`, `sta_aqm_read()`, `sta_airtime_read()`/`sta_airtime_write()`, `sta_aql_read()`/`sta_aql_write()`, and `sta_agg_status_read()`/`sta_agg_status_write()`.

Per-link-station handlers include `link_sta_addr_read()`, `link_sta_ht_capa_read()`, `link_sta_vht_capa_read()`, `link_sta_he_capa_read()`, and `link_sta_eht_capa_read()`. Macros generate file operations and simple counters for station and link-station fields.

## Control Flow

`ieee80211_sta_debugfs_add()` creates a station directory named by MAC address under the interface `stations` directory, tolerating failure due to a documented remove/add race for the same address. It adds station-level files, optional AQL controls if the wiphy advertises the AQL extended feature, `driver_buffered_tids`, and driver station debugfs via `drv_sta_add_debugfs()`.

`ieee80211_link_sta_debugfs_add()` places link-specific files directly in the station directory for non-MLO stations, or under `link-<id>` for valid-links MLO stations. It adds address for MLO links, capability decoders, and RX duplicate/fragment counters. Driver link-station debugfs is added separately, and removal recreates the directory without driver data for MLO link-station entries.

Aggregation control uses `wiphy_locked_debugfs_read/write()`. Reads print RX/TX BA session state per TID. Writes parse `tx start [timeout=N] <tid>`, `tx stop <tid>`, or `rx stop <tid>` style commands and call BA session start/stop helpers.

## State And Persistence

Station directories are runtime debugfs dentries stored in `sta->debugfs_dir` and `link_sta->debugfs_dir`. Reads expose live station flags, queues, AQL/airtime counters, aggregation state, and capability structures populated during association. Writes can reset airtime accounting, change per-station AQL limits, and start/stop aggregation sessions. No data is persisted beyond object lifetime.

Locking is per data type: fq stats use `local->fq.lock`, airtime and AQL limits use `active_txq_lock[ac]` for reads/resets, aggregation state uses the wiphy lock, and debugfs directory lifecycle follows station/link lifecycle serialization.

## Dependencies And Integration Points

This file depends on debugfs, `ieee80211_i.h`, `sta_info.h`, `driver-ops.h`, and capability helper macros from IEEE 802.11 headers. It is integrated with netdev debugfs station directories, driver debugfs hooks, BA aggregation management, AQL scheduling, rate/AQM queue structures, and HE/EHT capability parsing in files such as `eht.c`.

## Risks

The capability formatters are large and mirror evolving standards bit layouts; new capability bits can be missed or decoded incorrectly. The station add path documents a race where a new station with the same address may appear before the old debugfs directory is removed. `ieee80211_link_sta_debugfs_remove()` sets `sta->debugfs_dir = NULL` when removing the non-MLO default link directory alias, which requires lifecycle ordering to avoid losing the station directory unexpectedly. Writable aggregation and AQL controls can perturb live traffic and should remain debug-only.

## Test Signals

Tests should cover station add/remove races with repeated same-MAC association, MLO and non-MLO station link directories, driver debugfs add/remove recreation, AQL feature-present/absent paths, airtime reset behavior, aggregation command parsing and error cases, and sample HT/VHT/HE/EHT capability dumps for known capability fixtures. Lockdep/KASAN runs are useful while removing stations during debugfs reads.
