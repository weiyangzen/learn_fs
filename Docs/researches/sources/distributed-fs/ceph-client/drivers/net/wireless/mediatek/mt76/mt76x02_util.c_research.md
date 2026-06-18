<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c

Purpose: shared mt76x02 mac80211 utility layer. It initializes hw capabilities, interface combinations, LEDs, filters, station/VIF lifecycle, aggregation, keys, EDCA, coverage/RTS, scanning completion, PS handling, BSS changes, and address lists.

Important APIs/types/functions: `mt76x02_init_device()`, `mt76x02_configure_filter()`, `mt76x02_sta_add/remove()`, `mt76x02_add/remove_interface()`, `mt76x02_ampdu_action()`, `mt76x02_set_key()`, `mt76x02_conf_tx()`, `mt76x02_set_coverage_class()`, `mt76x02_bss_info_changed()`, and `mt76x02_config_mac_addr_list()`.

Control flow: init configures queues, rate limits, interface combinations, LED callbacks, DFS notifier for MMIO, drv_priv sizes, chain masks, antenna masks, and hardware flags. Interface add assigns BSSID indexes with STA offset handling. Key setup rejects unsupported ciphers/topologies, maps keys to WCIDs/shared key tables, and requests software fallback when needed. BSS changes program BSSID/protection/beacon interval/enable/preamble/slot time.

State and persistence: updates wiphy/mac80211 capability state, vif/wcid masks, WCID table, hardware key tables, RX filter, EDCA/protection registers, slottime/coverage, scan/calibration state, LED config, and MAC address list.

Dependencies/integration: mac80211 callbacks, mt76 core WCID/TXQ/key helpers, shared MAC/DFS/beacon code, LEDs, and USB/MMIO feature differences.

Risks: multi-VIF index conflicts, key-offload fallback correctness, USB AP GTK limitation, AMPDU state transitions, and filter flag inversion. Test signals include AP/STA/P2P/mesh combinations, WEP/TKIP/CCMP, AMPDU start/stop, EDCA changes, scanning recovery, TIM/beacon changes, and SAR/antenna capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c -->
