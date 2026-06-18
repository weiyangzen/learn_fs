# sources/distributed-fs/ceph-client/net/mac80211/spectmgmt.c

## Purpose
`spectmgmt.c` implements mac80211 spectrum-management helpers for channel switch announcement parsing and measurement request refusal. It converts channel-switch IEs into validated cfg80211 channel requests, checks advertised bandwidth against station connection capabilities and bandwidth limits, handles 6 GHz HE/EHT operating encodings, captures mesh CSA parameters, and sends a measurement report refusing unsupported measurement requests.

## Important APIs, Types, and Functions
The primary exported/internal APIs are `ieee80211_parse_ch_switch_ie()` and `ieee80211_process_measurement_req()`. Internal helpers are `wbcs_elem_to_chandef()`, `validate_chandef_by_ht_vht_oper()`, `validate_chandef_by_6ghz_he_eht_oper()`, and `ieee80211_send_refuse_measurement_request()`.

Important data structures include `struct ieee802_11_elems`, `struct ieee80211_csa_ie`, `struct cfg80211_chan_def`, `struct ieee80211_conn_settings`, `struct ieee80211_wide_bw_chansw_ie`, `struct ieee80211_bandwidth_indication`, `struct ieee80211_ext_chansw_ie`, `struct ieee80211_sec_chan_offs_ie`, `struct ieee80211_he_6ghz_oper`, `struct ieee80211_eht_operation_info`, and `struct ieee80211_msrment_ie`.

## Control Flow, State, and Persistence
`ieee80211_parse_ch_switch_ie()` begins by clearing the output `csa_ie`, selecting channel switch, extended channel switch, secondary-channel-offset, wide-bandwidth-channel-switch, and EHT bandwidth-indication elements from parsed IEs. It disables HT/VHT bandwidth elements when the current connection mode or bandwidth limit cannot use them. Extended channel switch IEs supply operating class, channel, count, and mode when understood; otherwise ordinary CSA supplies the channel/count/mode. Mesh channel switch parameters add TTL, mode flags, precedence value, and optional reason code.

The parser converts the new channel number and band to a frequency, rejects unsupported or disabled channels, derives an initial operating chandef from secondary channel offset or non-HT/5/10 MHz state, and stores that as both operating and AP channel request. It then tries richer bandwidth encodings in priority order: EHT bandwidth indication, VHT wide bandwidth channel switch, operating class chandef, or the initial CSA chandef. For 6 GHz it validates by synthesizing HE 6 GHz and optional EHT operation elements; for other bands it validates by synthesizing HT and VHT operation elements. Invalid capability-derived chandefs are ignored by nulling `chan`.

When a valid new chandef remains, the function records the AP-advertised chandef, downgrades it until it fits `conn->bw_limit`, verifies compatibility with the initial CSA chandef, and stores it as `csa_ie->chanreq.oper`. It also parses maximum channel switch time from its three-byte little-endian field. Return values distinguish no understood CSA data (`1`), valid parsed data (`0`), and fatal unsupported/inconsistent channel data (`-EINVAL`).

`wbcs_elem_to_chandef()` handles VHT WBCS encodings, including deprecated 160/80+80 forms and the modern 80 MHz encoding where `ccfs1` disambiguates 160 versus 80+80. `validate_chandef_by_ht_vht_oper()` reconstructs HT/VHT operation elements from a candidate chandef and lets core mac80211 validate against VHT capability. `validate_chandef_by_6ghz_he_eht_oper()` reconstructs HE 6 GHz and EHT operation state, including 320 MHz, 160 MHz, 80+80, 80, 40, and 20 MHz encodings, then validates with `ieee80211_chandef_he_6ghz_oper()`.

Measurement request handling is intentionally minimal. `ieee80211_process_measurement_req()` always sends a refusal report through `ieee80211_send_refuse_measurement_request()`. The refusal helper allocates an action management frame, fills addresses, spectrum-management category, measurement report action, dialog token, measurement report IE, request token/type, and refused mode bit, then transmits it with `ieee80211_tx_skb()`.

Persistent side effects are limited to the caller-provided `struct ieee80211_csa_ie` output and transmitted refusal skbs. The file does not maintain its own long-lived state.

## Dependencies and Integration Points
The file depends on cfg80211 channel/frequency/chandef helpers, mac80211 connection mode and bandwidth-limit definitions, parsed-element output from the IE parser, local wiphy channel tables, and TX skb helpers. `rx.c` calls `ieee80211_process_measurement_req()` for 5 GHz station measurement requests and queues channel-switch actions for station, IBSS, and mesh processing after basic validation. MLME/IBSS/mesh code consumes `ieee80211_parse_ch_switch_ie()` results to perform channel switch decisions.

## Risks and Test Signals
Risks include accepting inconsistent CSA/WBCS/BWI information, mishandling operating class to band conversion, incorrect bandwidth downgrades versus disconnection decisions, 6 GHz HE/EHT synthetic operation mismatches, 320/160/80+80 center-frequency errors, disabled-channel handling, and silent behavior differences for unprotected action frames where logging is suppressed. Measurement handling is spec-incomplete by design and only refuses requests.

Tests should cover CSA-only, ECSA, mesh CSA parameters, invalid operating classes, disabled/unsupported channels, secondary channel offsets, 5/10 MHz preservation, WBCS 40/80/160/80+80 encodings, EHT bandwidth indication with puncturing, 6 GHz HE/EHT validation including 320 MHz, bandwidth-limit downgrade loops, incompatible chandef rejection, max channel switch time parsing, unprotected action logging behavior, and measurement request refusal frame contents/allocation failure.
