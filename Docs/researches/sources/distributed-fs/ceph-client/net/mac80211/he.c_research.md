<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/he.c -->
# sources/distributed-fs/ceph-client/net/mac80211/he.c

## Purpose
Handles High Efficiency (802.11ax/HE) station capability parsing, HE operation and spatial reuse propagation into BSS configuration, 6 GHz capability updates, and exported OMI bandwidth transition helpers for drivers.

## Important APIs, Types, and Functions
`_ieee80211_he_cap_ie_to_sta_he_cap()` parses peer HE capabilities against a caller-supplied local capability set; `ieee80211_he_cap_ie_to_sta_he_cap()` selects local capabilities for the VIF type and band. `ieee80211_he_op_ie_to_bss_conf()` and `ieee80211_he_spr_ie_to_bss_conf()` copy HE operation and spatial reuse parameters into `vif->bss_conf`. `ieee80211_update_from_he_6ghz_capa()` applies 6 GHz SMPS and MPDU/AMSDU limits to a link station. `ieee80211_prepare_rx_omi_bw()` and `ieee80211_finalize_rx_omi_bw()` are exported GPL APIs used by drivers to stage and finalize peer RX bandwidth changes advertised through OMI.

## Control Flow
HE capability parsing first clears the public station HE capability and exits if the peer IE or local HE support is absent. It validates the variable HE IE length by computing MCS/NSS and PPE sizes, copies the fixed capability element, copies the present MCS/NSS fields, conditionally copies PPE thresholds, marks `has_he`, updates bandwidth, and applies 6 GHz capability if present on 6 GHz. It intersects peer RX/TX MCS maps with local TX/RX support for 80 MHz, then handles 160 MHz and 80+80 MHz only if both sides support each width; otherwise it disables the peer MCS maps and clears unsupported width bits.

HE operation conversion zeroes the BSS HE operation before copying params and NSS set. Spatial reuse conversion zeroes OBSS-PD state, copies control, then walks optional fields according to presence bits. OMI prepare/finalize enforce paired staging: narrowing bandwidth updates TX-facing bandwidth and rate control first, widening updates RX/channel-context first, and finalize applies the complementary side plus channel-context or rate-control recalculation.

## State and Persistence
Persistent state is held in `link_sta->pub->he_cap`, `link_sta->pub->he_6ghz_capa`, `link_sta->pub->bandwidth`, `link_sta->cur_max_bandwidth`, aggregate `max_amsdu_len`, OMI staging fields (`rx_omi_bw_staging`, `rx_omi_bw_tx`, `rx_omi_bw_rx`), and `vif->bss_conf` HE operation/spatial reuse structs. The file itself has no global mutable state.

## Dependencies and Integration Points
Depends on `ieee80211_i.h`, rate-control helpers, cfg80211/nl80211 HE definitions, station aggregate recalculation, channel-context recalculation, tracepoints, and RCU/wiphy dereference helpers. Integrates with managed, mesh, and cfg80211 station update paths that call HE capability parsing; with BSS configuration notification paths that consume `vif->bss_conf.he_oper` and `he_obss_pd`; and with drivers through exported OMI bandwidth APIs.

## Risks
Variable-length HE IE parsing relies on helper size calculations and one indexed byte used for PPE size; malformed lengths must be rejected before copying optional data. MCS intersection direction is asymmetric and easy to regress by swapping own RX/TX against peer TX/RX. OMI helpers require strict prepare/finalize pairing and warn if staging fields diverge; missed finalize can leave rate control or channel context temporarily inconsistent. The 6 GHz SMPS switch has no explicit default assignment outside enumerated values, relying on known field encodings.

## Test Signals
Good tests cover HE IE lengths with and without PPE thresholds, local support absent, 160 and 80+80 capability intersection, 6 GHz max MPDU/SMPS mapping, HE operation reset when IE is absent, SPR optional field combinations, and OMI narrowing/widening sequences that verify rate-control updates and channel-context recalculation order. Runtime signals include changed station bandwidth, `IEEE80211_RC_BW_CHANGED` callbacks, trace API events, and aggregate max AMSDU recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/he.c -->
