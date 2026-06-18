# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs-fw.c

## Purpose
`rs-fw.c` implements the firmware-offloaded transmit rate-control path for the Intel `iwlwifi` MVM driver. Instead of running the full driver-side rate-scaling state machine, it translates mac80211 station/link capabilities into firmware `TLC_MNG_CONFIG_CMD` payloads, handles firmware TLC update notifications, and maintains the small persistent per-link RS state needed by debug/status paths.

## Important APIs, Types, and Functions
- `iwl_mvm_rs_fw_rate_init()` is the central entry point. It builds `struct iwl_tlc_config_cmd_v4`, derives the firmware station ID from `mvmsta->link[link_id]`, resets non-persistent `lq_sta->rs_fw` state, programs supported rates, updates mac80211 aggregate limits, and sends the command asynchronously.
- `rs_fw_set_supp_rates()` selects the firmware mode in priority order: EHT, HE, VHT, HT, then non-HT. It populates `non_ht_rates` and the `ht_rates[NSS][BW]` matrix.
- `rs_fw_eht_set_enabled_rates()`, `rs_fw_he_set_enabled_rates()`, and `rs_fw_vht_set_enabled_rates()` intersect peer RX capabilities with local TX capabilities and station NSS/SMPS limits.
- `rs_fw_get_config_flags()` derives LDPC, STBC, HE DCM NSS1, and EHT extra-LTF related flags from local configuration, station capabilities, and sband capabilities.
- `iwl_mvm_tlc_update_notif()` consumes firmware TLC notifications, updates `last_rate_n_flags`, and applies firmware-selected AMSDU policy to `mvmsta`, `link_sta->agg`, and per-TID max AMSDU sizes.
- `rs_fw_get_max_amsdu_len()` maps HT/VHT/HE 6 GHz/EHT capabilities to the max MPDU length used for AMSDU enablement.
- `iwl_mvm_rs_add_sta_link()` and `iwl_mvm_rs_add_sta()` initialize persistent `struct iwl_lq_sta_rs_fw` fields.

## Control Flow
The rate-init path starts from `iwl_mvm_rs_fw_rate_init()`, which collects band capabilities through mac80211 helpers, computes channel width from `link_sta->bandwidth`, computes feature flags, and records `sta_id` under RCU. It clears the volatile part of `struct iwl_lq_sta_rs_fw` up to `pers`, then calls `rs_fw_set_supp_rates()` to choose the best supported PHY mode. The command is sent as v4 when supported, translated to v3/v2 layout for older firmware, or rejected with `-EINVAL` for unsupported future command versions.

The notification path is asynchronous. `iwl_mvm_tlc_update_notif()` enters RCU, maps firmware station ID to mac80211 station and link station, validates that the link still exists, and then handles only the fields indicated by notification flags. Rate notifications update cached rate display state. AMSDU notifications are range-checked against current link limits and ignored if debugfs has overridden `orig_amsdu_len`; otherwise they update enabled TIDs, max length, per-TID aggregate lengths, and trigger `ieee80211_sta_recalc_aggregates()`.

## State and Persistence
The firmware-offload state is intentionally small. `last_rate_n_flags` is volatile and reset on rate init. The nested `pers` fields in `struct iwl_lq_sta_rs_fw` persist across rate reinitialization and store station ID, chain RSSI history, last RSSI, driver back-pointer, and debug fixed-rate data. AMSDU decisions persist in `struct iwl_mvm_sta` (`amsdu_enabled`, `max_amsdu_len`) and in `struct ieee80211_link_sta::agg`. `orig_amsdu_len` protects debug overrides from being silently overwritten by firmware updates.

## Dependencies and Integration Points
This file depends on mac80211 station/link capability structures, MVM station/link wrappers, firmware command version lookup, endian conversion helpers, RCU station maps, and firmware API constants from `fw-api.h`. It is selected by `iwl_mvm_rs_rate_init()` in `rs.c` when `iwl_mvm_has_tlc_offload(mvm)` is true. It also shares debug frame-stat reset and AMSDU sizing behavior with the driver-side RS path.

## Risks
- Capability intersection is dense and version-sensitive. EHT 20 MHz-only handling, 160/320 MHz indices, NSS maps, and SMPS pruning can silently under-advertise or over-advertise rates if any mac80211 structure semantics change.
- Command-version translation must remain aligned with firmware ABI layouts; the v3/v2 fallback deliberately truncates fields.
- `iwl_mvm_tlc_update_notif()` receives updates during station removal, so RCU validation is critical. Missed null/ERR checks could dereference stale station/link state.
- AMSDU size handling intentionally disables AMSDU by setting per-TID length to `1`; future mac80211 changes could make that convention fragile.
- `rs_fw_tx_protection()` is a stub, so RTS/CTS protection requests are not effective under TLC offload.

## Test Signals
- Association with EHT, HE, VHT, HT, and legacy peers should emit expected `TLC CONFIG CMD` debug logs for mode, width, chains, flags, non-HT rates, and `ht_rates`.
- Firmware TLC notifications should update debug last-rate output and `link_sta->agg.max_rc_amsdu_len` without WARNs.
- 20 MHz VHT should not advertise MCS9; static SMPS should clear NSS2 rates.
- 6 GHz HE max MPDU and 2.4 GHz EHT max MPDU cases should produce expected AMSDU lengths.
- Station removal during TLC notification should log the invalid RCU pointer path and not crash.
