# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.h

Purpose: shared inline helpers and utility prototypes for rtw89.

Important APIs/types: packet-number masks for CCMP/TKIP-style PN fields, `rtw89_iterate_vifs_bh()`, `rtw89_for_each_rtwvif()`, duplicate-vif guard `rtw89_rtwvif_in_list()`, signed division helpers with round-down/closest semantics, `ether_addr_copy_mask()`, `ccmp_hdr2pn()`, and prototypes for dB conversion and ellipsis helpers.

Control flow: iteration macros wrap mac80211 active-interface iteration and the driver's `rtwvifs_list`. The signed division helper normalizes negative remainders so results are mathematical floor division. `ccmp_hdr2pn()` extracts six PN bytes from an 802.11 CCMP header into a 64-bit PN.

State and persistence: no owned state; helpers inspect `rtwdev` lists and caller-provided buffers.

Dependencies/integration: includes `core.h`, depends on mac80211 iteration APIs, Ethernet address helpers, and Linux bitfield helpers. Used by SAR/TAS, WoWLAN key handling, SER/vif list safety, and diagnostics.

Risks: `rtw89_for_each_rtwvif()` requires the wiphy mutex; misuse can race list mutation. PN byte ordering is security-sensitive. Masked Ethernet copy treats each bit as a byte selector.

Test signals: lockdep for vif iteration, PN extraction vectors, negative division edge cases, and WoWLAN pattern/key tests.
