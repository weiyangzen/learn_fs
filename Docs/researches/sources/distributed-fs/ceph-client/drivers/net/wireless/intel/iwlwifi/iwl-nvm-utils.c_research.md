# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.c

Purpose: Provides reusable helpers for initializing supported-band channel slices and HT capabilities from parsed NVM data.

Important APIs and functions: `iwl_init_sband_channels()` selects the contiguous channel range for a band inside `data->channels`. `iwl_init_ht_hw_capab()` fills `struct ieee80211_sta_ht_cap` from SKU capabilities, module parameters, RF configuration, band, and TX/RX chain masks.

Control flow: Channel initialization advances through the parsed channel array until the requested band starts, assigns the `sband->channels` pointer, counts contiguous channels in that band, and stores `n_channels`. HT initialization disables HT if SKU/module/config disallow it, reduces RX chains for SISO diversity or MIMO-disabled SKUs, sets STBC/LDPC/A-MSDU/AMPDU/MCS flags, computes highest RX rate, and records TX MCS stream differences.

State and persistence: Mutates caller-owned `iwl_nvm_data` band structures and cfg80211/mac80211 capability structs. No persistent storage exists.

Dependencies and integration points: Uses `iwl_modparams`, `iwl-trans`, `iwl_nvm_data`, mac80211 HT constants, antenna-count helpers, and RF config HT parameters. Exported for NVM parser and opmode setup.

Risks: `iwl_init_sband_channels()` assumes channels are sorted/grouped by band and can advance one element beyond the last matched channel while counting. HT rate/MCS masks must match chain count and standards expectations. Module parameters can suppress capabilities after SKU parsing.

Test signals: Band slicing for 2.4/5/6 GHz channel arrays, HT disabled cases, 1x1/2x2/3x3 MCS masks, SISO diversity, MIMO-disabled SKU, STBC/LDPC flags, and A-MSDU size influence on HT cap.
