# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.c

Purpose: Initializes common mac80211 channel/rate tables and HT capability data for ath9k devices.

Important APIs/functions: `ath9k_cmn_init_channels_rates()` allocates and installs 2 GHz/5 GHz supported band channel/rate tables. `ath9k_cmn_setup_ht_cap()` fills `struct ieee80211_sta_ht_cap` from hardware capabilities and chainmasks. `ath9k_cmn_reload_chainmask()` refreshes HT capabilities after chainmask changes.

Control flow: Static channel tables define calibrated 2 GHz channels 1..14 and selected 5 GHz UNII/middle band channels, with `hw_value` used as the private channel array index. Legacy rate table includes CCK and OFDM rates plus half/quarter support flags. Init copies tables into devm-allocated memory only for bands advertised by `ah->caps.hw_caps`. HT setup enables 20/40, SMPS, SGI40, DSSS/CCK40, optional LDPC/SGI20/STBC, chooses max streams by silicon revision, counts active TX/RX chains, sets TX MCS mismatch bits, and fills RX MCS masks.

State/persistence: Populates `common->sbands[]` channel/rate/HT capability fields. Allocations are devm-managed against `ah->dev`.

Dependencies/integration: Used during hardware registration with mac80211. Depends on revision predicates, capability bits, `ath9k_cmn_count_streams()`, and cfg80211/mac80211 band/rate structures.

Risks: `hw_value` must remain aligned with `ATH9K_NUM_CHANNELS` and `ah->channels[]`; a build-time assertion checks total count. Revision-to-stream mapping is hardware-specific. Partial allocation failure can leave one band initialized before returning `-ENOMEM`.

Test signals: Device registration for 2 GHz only, 5 GHz only, dual-band, HT-capable and legacy chips, chainmask reload after antenna changes, and mac80211 visible rates/MCS masks.
