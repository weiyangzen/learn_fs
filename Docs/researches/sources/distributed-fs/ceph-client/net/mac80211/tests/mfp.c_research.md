# sources/distributed-fs/ceph-client/net/mac80211/tests/mfp.c

Purpose: parameterized KUnit tests for management frame protection acceptance/drop decisions in `ieee80211_drop_unencrypted_mgmt()`.

Important APIs/types: `struct mfp_test_case` describes whether a peer station exists, whether MFP/association/decryption/unicast is present, frame subtype/category/action, and expected `ieee80211_rx_result`. `accept_mfp()` builds a synthetic management skb and invokes the RX helper. Suite name is `mac80211-mfp`.

Control flow: each test zeroes a static `sta_info`, optionally sets `WLAN_STA_MFP` and raw `WLAN_STA_ASSOC`, allocates an skb, marks RX decrypted/protected state when requested, adjusts destination address for unicast/multicast, appends action or reason payload, then asserts the drop/continue result.

State and persistence behavior: no persistent state beyond the static station reused after `memset`. It uses station flags from `sta_info.h` but does not insert the station into global tables.

Dependencies and integration points: depends on KUnit, KUnit skb helpers, `../ieee80211_i.h`, `../sta_info.h`, RX status control block flags, WLAN category/action constants, and exported-for-KUnit RX management filtering.

Risks and edge cases covered: public action acceptance for unknown/non-MFP peers, dropping unicast public action when MFP should use protected dual, protected-dual rejection without decrypted MFP, deauth/disassoc allowed before keys are set, and robust non-public action behavior before/after association. One case labelled disassoc uses `IEEE80211_STYPE_DEAUTH`, so it may not independently cover the disassociation subtype.

Test signals: passing suite confirms core MFP filtering matrix. Additional integration tests should cover real key installation, multicast robust management frames, and full RX path sequencing.
