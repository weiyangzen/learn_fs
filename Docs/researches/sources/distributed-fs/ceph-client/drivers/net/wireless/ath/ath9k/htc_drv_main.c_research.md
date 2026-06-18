# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_main.c

## Purpose

`htc_drv_main.c` implements the mac80211 operation surface for ath9k HTC devices. It translates mac80211 start/stop, channel, interface, station, power-save, key, filter, scan, TSF, AMPDU, and rate-control requests into shared ath9k hardware operations plus WMI commands to the USB firmware target.

## Important APIs, Types, and Functions

The exported operation table is `struct ieee80211_ops ath9k_htc_ops`. Its callbacks include `ath9k_htc_tx()`, `ath9k_htc_start()`, `ath9k_htc_stop()`, `ath9k_htc_add_interface()`, `ath9k_htc_remove_interface()`, `ath9k_htc_config()`, `ath9k_htc_configure_filter()`, `ath9k_htc_sta_add()`, `ath9k_htc_sta_remove()`, `ath9k_htc_conf_tx()`, `ath9k_htc_set_key()`, TSF accessors, AMPDU handling, scan hooks, coverage class, bitrate mask, stats, antenna reporting, and channel-switch beacon tracking.

Power management centers on `ath9k_htc_setpower()`, `ath9k_htc_ps_wakeup()`, `ath9k_htc_ps_restore()`, and `ath9k_ps_work()`. These protect `ath9k_hw_setpower()` with `htc_pm_lock` and reference-count awake requests through `ps_usecount`.

Reset and channel transitions are handled by `ath9k_htc_reset()` and `ath9k_htc_set_channel()`. Both stop ANI, stop queues, delete the TX cleanup timer, drain host and target TX, disable firmware interrupts, stop receiving, drain WMI events, reset the hardware core, restart receive, set firmware PHY mode, re-enable interrupts, restart HTC, reconfigure VIF beacon/ANI state, wake queues, and restore power-save state.

Interface and station management uses WMI target objects: `ath9k_htc_add_interface()`/`remove_interface()` create/remove VAPs, `ath9k_htc_add_station()`/`remove_station()` create/remove target station entries, and special monitor helpers create an exclusive monitor VIF plus a station entry for injection. Rate information is marshalled through `ath9k_htc_setup_rate()`, `ath9k_htc_send_rate_cmd()`, `ath9k_htc_init_rate()`, and `ath9k_htc_update_rate()`. AMPDU state is coordinated by `ath9k_htc_tx_aggr_oper()`.

## Control Flow

`ath9k_htc_start()` wakes the chip, flushes receive state, maps mac80211's configured channel to an `ath9k_channel`, resets hardware, sets target mode via WMI, initializes firmware receive, updates target capabilities, clears `ATH_OP_INVALID`, starts HTC/HIF traffic, wakes mac80211 queues, arms the TX cleanup timer, and starts BT coexistence.

`ath9k_htc_stop()` performs the reverse while carefully leaving the main mutex before cancelling work that could need driver locks. It wakes power, disables interrupts, drains target TX, stops receive, kills RX tasklet, drains TX/WMI state, cancels work, stops ANI and BT coexistence, removes monitor mode if present, disables PHY and hardware, enters full sleep, and marks `ATH_OP_INVALID`.

Interface creation chooses a firmware opmode for station, IBSS, AP, or mesh; allocates VIF and station slots through bitmaps; sends `WMI_VAP_CREATE_CMDID` and `WMI_NODE_CREATE_CMDID`; updates BSSID masks; updates opmode; assigns beacon slots for beaconing modes; and starts ANI for AP operation. Removal sends `WMI_VAP_REMOVE_CMDID`, removes the VIF station, frees slots, updates opmode/BSSID mask, and stops ANI if no active users remain.

`ath9k_htc_config()` reacts to mac80211 change bits. Idle exit forces a reset, monitor changes add/remove a firmware monitor VIF, channel changes call `ath9k_htc_set_channel()`, PS changes enter/leave network sleep, and power changes update the hardware TX power limit.

## State and Persistence Behavior

The file maintains `priv->ps_usecount`, `ps_idle`, `ps_enabled`, `nvifs`, `nstations`, `vif_slot`, `sta_slot`, per-type VIF counters, `vif_sta_pos`, `mon_vif_idx`, `num_sta_assoc_vif`, `cur_beacon_conf`, `rearm_ani`, `reconfig_beacon`, `csa_vif`, `rxfilter`, and `curtxpow`. Station private state stores firmware station indices, rate update work, and TID aggregation state. Common hardware state includes `curbssid`, `curaid`, `op_flags`, TSF adjustment, slottime, and opmode.

## Dependencies and Integration Points

This file is the main integration point with mac80211 and cfg80211. It also calls WMI command helpers, HTC start/stop/drain APIs, ath9k common helpers for channels, TX power, RX filters, keys, and RSSI, beacon code, BT coexistence code, debug/stat helpers, and the shared hardware core in `hw.c`.

## Risks

Lock ordering is a primary risk: the file mixes `priv->mutex`, `htc_pm_lock`, `beacon_lock`, TX locks, RCU, work cancellation, tasklets, timers, and mac80211 callbacks. Power-save reference imbalance can leave the chip awake or asleep at the wrong time. VIF and station slot bitmaps must stay synchronized with firmware objects. Channel reset paths must drain WMI/TX/RX before hardware reset to avoid stale completions. Monitor mode is special and limited to one firmware interface. Several WMI command macros reuse a local `ret`; changes around those macros can accidentally skip error handling.

## Test Signals

Exercise mac80211 start/stop, add/remove station/AP/mesh/IBSS/monitor interfaces, concurrent two-interface combinations, association/disassociation, channel change and off-channel scan, software scan start/complete, power-save transitions, suspend-like stop/start, key install/removal for supported ciphers, AMPDU start/stop/operational transitions, bitrate mask updates, beacon enable/disable, TSF get/set/reset, and hot unplug during active callbacks.
