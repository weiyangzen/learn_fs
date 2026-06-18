<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c

Purpose: MT76x2 common initialization helpers. It handles SAR power updates, WLAN reset/power state, default MAC register programming, and per-channel max power initialization.

Important APIs/types/functions: `mt76x2_set_sar_specs()`, `mt76x2_reset_wlan()`, `mt76_write_mac_initvals()`, and `mt76x2_init_txpower()`.

Control flow: SAR update validates chandef, initializes SAR data, converts configured power to per-chain units on 2x2 devices, and reprograms TX power if running. WLAN reset toggles function clock/reset bits. MAC init writes a large reference register table plus default protection configs. TX power init iterates each supported channel, reads EEPROM target/rate power, computes `orig_mpwr`, converts to combined 2x2 output, and clamps to regulatory max.

State and persistence: updates `txpower_conf`, SAR state, WLAN control registers, MAC/protection/TX power defaults, and channel `orig_mpwr`/`max_power` fields.

Dependencies/integration: cfg80211 SAR helpers, mt76 register pair writes, shared EEPROM/power helpers, mt76x2 PHY TX power, and channel registration.

Risks: per-chain vs combined power conversion, invalid chandef path, reference register magic values, and regulatory max interaction. Test signals include SAR updates while running/stopped, channel power listings, 2G/5G band registration, WLAN reset after suspend, and TX power debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c -->
