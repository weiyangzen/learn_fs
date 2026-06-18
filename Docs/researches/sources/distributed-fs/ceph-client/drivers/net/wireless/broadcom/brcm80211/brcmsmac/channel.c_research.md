# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/channel.c

Purpose: implements brcmsmac channel/regulatory management, transmit-power limit construction, country/regdomain initialization, chanspec validation, and cfg80211 regulatory notifier behavior.

Important APIs and functions: `brcms_c_channel_mgr_attach()` creates `struct brcms_cm_info`, derives country/default regdomain from SROM alpha2, and applies initial country settings. `brcms_c_channel_set_chanspec()` computes regulatory power limits, applies local constraints, adjusts gmode for no-OFDM channels, and calls `brcms_b_set_chanspec()`. `brcms_c_channel_reg_limits()` fills `struct txpwr_limits` across CCK, OFDM, MCS, 20/40 MHz, SISO/CDD/STBC/MIMO tables. `brcms_c_valid_chanspec_db()` validates chanspec shape/band. `brcms_c_regd_init()` masks unsupported PHY channels, installs notifier, applies custom regulatory domain, and relaxes beaconing flags where allowed.

Control flow: attach chooses `X2` default when SROM country is invalid or not in the small local table. Setting a channel reads cfg80211 current channel flags and local constraints, clamps every power table entry, and programs hardware. Regulatory notifier reapplies radar/no-IR rules, checks if any channel remains legal, toggles radio country-disable bit, and adjusts Japan channel 14 widefilter behavior.

State and persistence: `brcms_cm_info` stores current world regdomain pointer and driver references. cfg80211 channel flags and hardware tx power/channel state persist until later regulatory/channel changes or reset.

Dependencies and integration: depends on cfg80211/mac80211 regulatory APIs, PHY channel capability queries, brcms main/STF/gmode/hardware programming, SSB SPROM alpha2, and power constants from `channel.h`.

Risks and test signals: regulatory correctness is high risk. The local country table is minimal, power table indexing must match 2.4/5 GHz channel groups, and zero-as-unspecified fallback behavior must not create illegal power. Test valid/invalid alpha2 values, DFS/no-IR behavior, country IE notifier paths, all-disabled-channel radio disable, channel 14 Japan handling, and 20/40 MHz power limits.
