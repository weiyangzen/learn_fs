# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/main.c

Purpose: mac80211 operations for MT7925. It exposes HE/EHT/MLO capabilities and implements interface, station, key, scan, ROC, AP, PM, channel context, SAR, antenna, CSA, rfkill, and link-management operations.

Important APIs/types/functions: exported `mt7925_ops` is the central mac80211 ops table. Key helpers include `mt7925_init_he_caps()`, `mt7925_init_eht_caps()`, `mt7925_init_mlo_caps()`, `__mt7925_start()`, `mt7925_add_interface()`, `mt7925_mac_sta_add/remove/event()`, `mt7925_set_key()`, scan and sched-scan wrappers, `mt7925_change_vif_links()`, `mt7925_change_sta_links()`, channel-context ops, and CSA work.

Control flow: start programs regulatory channel domain and RTS threshold, resets counters, marks running, starts watchdog, and maybe rfkill polling. Interface add allocates BSS/WCID indexes and firmware device info. Station add allocates WCIDs per link, publishes RCU pointers, wakes PM, updates BSS before station records, and handles MLO primary/secondary ordering. Association updates BSS/STA records and MLO link selection. Removal tears down ROC, pending TX, firmware STA/BSS records, poll lists, WCIDs, and MLO state.

State/persistence: manages `vif_mask`, `omac_mask`, `valid_links`, `deflink_id`, per-link `mt792x_bss_conf`, per-link WCIDs, `mlo_pm_state`, queue parameters, PM flags, scan/ROC bits, channel context pointers, SAR power limits, CQM settings, CSA timers/work, IPv6 NS offload queue, and wiphy capabilities/flags. Firmware mirrors most BSS/STA/key/channel/PM state through MCU commands.

Dependencies/integration: integrates mac80211/cfg80211 callbacks, mt76 common helpers, MT7925 MCU and MAC helpers, regulatory code, EHT/HE capability encoding, MLO link APIs, IPv6 neighbor discovery, PM/WoW, SAR, rfkill, and channel switch mechanisms.

Risks: MLO link add/remove has complex partial failure handling; host-only unwind intentionally avoids firmware cleanup after MCU timeouts, relying on reset recovery. Several operations assume valid per-link context and can warn/fail if mac80211 ordering changes. Monitor mode disables PM/deep sleep and changes sniffer firmware state. Channel switch is unsupported for MLD and limited to associated STA contexts.

Test signals: add/remove AP, STA, P2P and monitor interfaces; associate/disassociate legacy and MLD stations; add/remove links; key install/remove across ciphers and MLO links; hardware/scheduled scans; ROC/join flows; AP start/stop and beacon offload; runtime PM and monitor transitions; SAR updates; channel context assignment/change/CSA; rfkill polling.
