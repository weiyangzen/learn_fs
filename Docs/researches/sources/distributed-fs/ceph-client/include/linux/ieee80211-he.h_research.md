# sources/distributed-fs/ceph-client/include/linux/ieee80211-he.h

## Purpose
Defines IEEE 802.11ax HE structures, MAC/PHY capability bits, TWT, MCS/NSS, HE operation, spatial reuse, MU EDCA, 6 GHz operation/capability, transmit power envelope, and inline size validators.

## Important APIs, Types, And Functions
Key types are `ieee80211_twt_params`, `ieee80211_twt_setup`, `ieee80211_he_cap_elem`, `ieee80211_he_mcs_nss_supp`, `ieee80211_he_operation`, `ieee80211_he_spr`, `ieee80211_mu_edca_param_set`, `ieee80211_he_6ghz_oper`, `ieee80211_tx_pwr_env`, and `ieee80211_he_6ghz_capa`. Helpers compute HE MCS/NSS and PPE sizes, validate HE capability and TPE elements, compute HE operation and spatial reuse element sizes, and locate the 6 GHz operation field.

## Control Flow
Parsers inspect fixed fields, use channel-width and presence bits to add optional lengths, and only then expose optional structures. HE operation size is derived from VHT operation info, co-hosted BSS, and 6 GHz operation bits. TPE validation branches by category and interpretation, with different count rules for EIRP and PSD formats.

## State And Persistence
No state is owned here. It represents on-wire management-frame capabilities that are cached by wireless stack station/BSS state elsewhere after parsing.

## Dependencies And Integration Points
Depends on Linux types, Ethernet constants, bit operations, unaligned/LE helpers, and related HT/VHT constants referenced by 6 GHz capability definitions. Integrates with cfg80211/mac80211 association, scan parsing, regulatory power handling, rate control, TWT negotiation, and 6 GHz operation.

## Risks
Variable-length elements can be truncated or malformed. TPE extension counts, PPE sizing, and 6 GHz optional offsets need exact validation before access. Some capability bits have AP vs non-AP semantics, so callers must interpret in context.

## Test Signals
HE capability fuzzing, MCS/NSS size tests for 80/160/80+80, PPE boundary tests, HE operation optional-field tests, TPE validation for EIRP/PSD and extension fields, 6 GHz operation extraction, and Wi-Fi 6 association/regulatory interop tests.
