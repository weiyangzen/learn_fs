# sources/distributed-fs/ceph-client/net/mac80211/tests/elems.c

Purpose: KUnit coverage for mac80211 element parsing, specifically defragmentation of nested EHT Multi-Link Element data and per-STA profile fragments.

Important APIs/functions: `mle_defrag()` constructs an skb containing an EHT basic MLE with a complete per-STA profile and many SSID elements, fragments both the STA profile and outer MLE using `ieee80211_fragment_element()`, then calls `ieee802_11_parse_elems_full()`. The suite is registered as `mac80211-element-parsing`.

Control flow: the test allocates and pads an skb, writes the MLE and nested profile fields manually, fragments inner and outer elements, fills `ieee80211_elems_parse_params`, parses, asserts a non-NULL result, and checks that `ml_basic`, `ml_basic_len`, `prof`, and `sta_prof_len` match expected reconstructed lengths. It frees parsed output and skb.

State and persistence behavior: all state is local to the KUnit test. The parser result is heap allocated and explicitly freed; the skb is freed at the end.

Dependencies and integration points: depends on KUnit, `../ieee80211_i.h`, exported-for-KUnit parser helpers, skb APIs, unaligned little-endian writes, and EHT MLE constants. This test supports MLME scan/association parsing paths that consume fragmented MLEs.

Risks and edge cases: validates that fragmentation does not lose nested profile data or return NULL unexpectedly. It does not exhaustively cover malformed fragments, multiple profiles, all link IDs, or memory-pressure failures beyond allocation asserts.

Test signals: passing test indicates basic nested MLE defragmentation remains intact after parser changes.
