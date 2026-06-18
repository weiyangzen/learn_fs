# sources/distributed-fs/ceph-client/net/mac80211/tests/chan-mode.c

Purpose: KUnit parameterized tests for `ieee80211_determine_chan_mode()`, verifying how mac80211 selects or downgrades connection mode and bandwidth from AP IEs, hardware strictness, userspace membership-selector handling, and HT/VHT/HE/EHT capability requirements.

Important APIs/types: `struct determine_chan_mode_case` captures case parameters and expected outcomes. `test_determine_chan_mode()` builds synthetic BSS IEs for supported rates, HT/VHT capabilities and operation, HE capabilities/operation, and EHT capabilities/operation, then calls `ieee80211_determine_chan_mode()`. It uses `T_SDATA(test)` from `util.h`, KUnit parameter generation via `KUNIT_ARRAY_PARAM_DESC`, and suite registration as `mac80211-mlme-chan-mode`.

Control flow: each case seeds `struct ieee80211_conn_settings`, optional hardware flags (`IEEE80211_HW_STRICT`, `IEEE80211_HW_DISALLOW_PUNCTURING`), capability masks, userspace selectors, and a fake `cfg80211_bss`. The parser runs under RCU, returned elements are freed if valid, and assertions compare either expected `-EINVAL` or resulting `conn.mode` and `conn.bw_limit`.

State and persistence behavior: all state is per-test and allocated through KUnit. It mutates test sdata masks and local hardware flags but does not persist beyond test lifetime. The fake BSS IE blob is copied into KUnit-managed memory.

Dependencies and integration points: depends on `net/cfg80211.h`, KUnit, local test utility fixtures, exported mac80211 channel-mode internals, and constants for membership selectors and HT/VHT/HE/EHT operation encodings.

Risks and edge cases covered: unsupported basic membership selectors, userspace override of unknown selectors, strict HT/VHT capability masking, AP basic MCS requirements exceeding client streams, all-zero VHT/HE basic-rate workaround behavior, EHT MCS-7 NSS limitations, EHT-required failure, and bandwidth downgrade when puncturing is disallowed.

Test signals: passing suite confirms deterministic downgrade/error behavior for representative EHT/HE/VHT/HT cases. It does not cover every operating class/channel layout or malformed IE length, so parser fuzzing and MLME integration tests remain useful.
