# sources/distributed-fs/ceph-client/net/mac80211/eht.c

## Purpose

`eht.c` handles selected IEEE 802.11be EHT behavior in mac80211. It parses EHT capability IEs into per-link station capability state and processes protected EHT EML Operating Mode Notification action frames for MLD peers, forwarding accepted changes to the driver and replying with a notification response.

## Important APIs, Types, And Functions

The exported functions are `ieee80211_eht_cap_ie_to_sta_eht_cap()` and `ieee80211_rx_eml_op_mode_notif()`. The local helper `ieee80211_send_eml_op_mode_notif()` builds the response action frame. The code uses `struct ieee80211_sta_eht_cap`, `struct ieee80211_eht_cap_elem`, `struct ieee80211_eml_params`, `struct link_sta_info`, `struct sta_info`, and driver wrapper `drv_set_eml_op_mode()`.

## Control Flow

Capability parsing starts by zeroing `link_sta->pub->eht_cap`, rejecting absent EHT IEs or unsupported local iftype capability, computing the variable MCS/NSS size from the peer HE/EHT capabilities, optionally computing PPE threshold length from the EHT PPE header, validating all lengths against `eht_cap_len`, copying fixed capability fields, copying only the advertised MCS/NSS bytes into a zeroed destination structure, copying PPE thresholds if present, and setting `has_eht`. It then recalculates `cur_max_bandwidth` and station bandwidth. On 2.4 GHz only, it maps EHT max MPDU length bits into aggregate max AMSDU length and calls `ieee80211_sta_recalc_aggregates()`.

`ieee80211_rx_eml_op_mode_notif()` first requires an MLD vif, rejects mutually invalid eMLSR/eMLMR control combinations, requires local iftype extended capabilities and a valid RX link, and looks up the transmitting station in the BSS. For eMLSR it verifies local support, accounts for link bitmap and optional parameter update length, validates padding/transition delay values, and updates the station EML capability delay bits. For eMLMR it verifies support, validates MCS map count and total optional length, checks every RX/TX MCS map entry is within range, and copies the map into `eml_params`. If either mode is active it reads the link bitmap and ensures it is a subset of active links. It then calls `drv_set_eml_op_mode()` and sends a response only on driver success.

## State And Persistence

The file mutates runtime station/link state: EHT capability structures, `link_sta->cur_max_bandwidth`, `link_sta->pub->bandwidth`, `link_sta->pub->agg.max_amsdu_len`, `sta->sta.eml_cap` delay fields, and driver EML operation mode state. No persistence exists. Received frame contents are validated against skb length before optional fields are consumed.

## Dependencies And Integration Points

It depends on mac80211 internal station/link structures, cfg80211 iftype extended capabilities, EHT/HE size helpers (`ieee80211_eht_mcs_nss_size`, `ieee80211_eht_ppe_size`), bandwidth helpers (`ieee80211_sta_cap_rx_bw`, `ieee80211_sta_cur_vht_bw`), aggregate recalculation, protected EHT action frame definitions, TX path `ieee80211_tx_skb()`, and driver callback `set_eml_op_mode` through `driver-ops.h`.

## Risks

Length accounting is security-critical because EHT capabilities and EML notifications contain variable optional fields. The code carefully validates lengths before reads, but future field additions could break offsets. EML notification handling updates `sta->sta.eml_cap` before the driver callback; if the driver rejects the mode change, delay fields may already be changed. The response copies optional bytes from the request after masking unsupported control bits, so opt_len calculation must match the request format exactly. Capability parsing depends on the associated HE capability IE for MCS/NSS sizing.

## Test Signals

Tests should parse EHT capability IEs with absent local support, truncated fixed fields, truncated MCS/NSS, PPE present with too-short headers, oversized PPE, 2.4 GHz MPDU length variants, and 6 GHz/5 GHz MPDU cases. EML notification tests should cover non-MLD rejection, invalid mode combinations, invalid link status, missing station, unsupported local eMLSR/eMLMR, malformed optional lengths, out-of-range delay/MCS values, inactive link bitmaps, driver callback failure, and successful response frame generation.
