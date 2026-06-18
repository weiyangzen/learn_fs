# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.c

Purpose: Supplies shared ath9k and ath9k_htc helpers for RX acceptance/post-processing, RX rate/RSSI translation, TX crypto key type selection, channel conversion, stream counting, TX power updates, and hardware key cache initialization.

Important APIs/functions: Exported APIs include `ath9k_cmn_rx_accept()`, `ath9k_cmn_rx_skb_postprocess()`, `ath9k_cmn_process_rate()`, `ath9k_cmn_process_rssi()`, `ath9k_cmn_get_hw_crypto_keytype()`, `ath9k_cmn_get_channel()`, `ath9k_cmn_count_streams()`, `ath9k_cmn_update_txpow()`, and `ath9k_cmn_init_crypto()`.

Control flow: RX acceptance filters descriptor errors while allowing decrypt/MIC/keymiss cases that mac80211 can process, normalizes keymiss handling for CCMP only, flags failed FCS/decrypt/MIC conditions, and handles TKIP MIC stripping/error reporting. Postprocess removes hardware padding, marks decrypted frames by descriptor key index or IV key ID, and forces software decrypt for management frames when configured. Rate processing maps HT and legacy hardware rates to mac80211 RX status. RSSI processing skips aggregate subframes without signal, reports per-chain signal, and low-pass filters beacon RSSI for ANI. Channel conversion maps cfg80211 width/band to internal `channelFlags`.

State/persistence: Mutates RX status flags, skb data pointer/length, `common->last_rssi`, `ah->stats.avgbrssi`, `ah->channels[]`, regulatory max power, and key cache contents. Crypto state uses `common->keymap`, `tkip_keymap`, `ccmp_keymap`, `keymax`, and `crypt_caps`.

Dependencies/integration: Depends on mac80211 RX/TX status formats, ath hardware descriptors, channel width helpers, regulatory TX power helpers, and hardware key reset.

Risks: Padding removal uses header length and skb length checks; mistakes corrupt frames. Keymiss/decrypt logic is security-sensitive. RSSI chain indexing compresses active chains and must match chainmask. Channel `hw_value` must match internal array indexes. TX power readback can differ from requested due to regulatory clamping.

Test signals: RX error matrix for CRC/decrypt/MIC/keymiss, TKIP MIC stripped vs reported, management software crypto, HT/legacy/short-preamble rates, half/quarter bandwidth, per-chain RSSI, channel width flags, TX power clamping, and key cache reset at init.
