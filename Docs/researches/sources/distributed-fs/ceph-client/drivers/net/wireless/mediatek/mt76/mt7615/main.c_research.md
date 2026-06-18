# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/main.c

Purpose: mac80211 operations implementation for MT7615-family devices, covering radio start/stop, interface and station lifecycle, channel changes, keys, filters, BSS updates, TX, AMPDU, scan/ROC, suspend/resume, antenna, SAR, and TSF operations.

Important APIs/functions: defines and exports `const struct ieee80211_ops mt7615_ops`, plus exported helpers `mt7615_set_channel()`, `mt7615_mac_sta_add()`, `mt7615_mac_sta_remove()`, and `mt7615_tx_worker()`. Internal functions implement add/remove interface, set key, config, WMM conf, filter config, BSS changes, STA rate updates, AMPDU actions, TSF get/set/offset, antenna and coverage class, hardware/scheduled scan, remain-on-channel, decap offload, and PM hooks.

Control flow: start waits for MCU init, powers on required band(s), enables MAC, pushes channel domain/rate power for offload firmware, sets RX path, marks PHY running, schedules MAC work, and resets counters. Stop cancels work/timers, clears running state, cancels scans, disables MAC/PM for bands no longer running. Interface add allocates VIF and OMAC indices, updates DBDC mapping, assigns reserved WTBL entries, and sends dev info to firmware; remove tears down BSS/STA/dev info and masks. Station add/remove allocate/free WTBL WCIDs and firmware records. TX either sends immediately with PM reference or queues skb for wake. Scan/ROC mostly delegate to firmware offload and complete asynchronously from MCU events.

State and persistence: updates `vif_mask`, `omac_mask`, per-PHY `omac_mask`, `monitor_vif`, WCID tables, key indices/cipher state, rx filters, `n_beacon_vif`, scan event queues, ROC state/grant/timer, PM pending SKBs, mac80211 running/suspend/scan bits, station rate cache, and hardware TSF. No durable persistence beyond firmware/hardware state.

Dependencies and integration: integrates with mac80211 callbacks, cfg80211 scan/SAR/ROC/WoWLAN state, mt76 station/tx/status helpers, connac MCU helper library, `mac.c` WTBL/MAC routines, `mcu.c` firmware commands, and init-provided capability/offload decisions.

Risks: OMAC/VIF/WCID allocation has limited table space and must unwind correctly on firmware errors. Key programming falls back for unsupported ciphers and has special MMIE/BIP handling. Runtime PM queuing in TX can reorder wake behavior if not drained correctly. Offload firmware controls availability of scan/ROC/rekey/beacon-filter paths. Suspend/resume must coordinate multiple PHYs.

Test signals: mac80211 interface add/remove across AP/STA/monitor/P2P roles; station association and teardown; hardware encryption for supported ciphers and software fallback for unsupported cases; channel switches with DFS and calibration; AMPDU setup; hardware scan/sched-scan completion; ROC grant/timeout; suspend/resume with WoWLAN when supported; SAR txpower changes.
