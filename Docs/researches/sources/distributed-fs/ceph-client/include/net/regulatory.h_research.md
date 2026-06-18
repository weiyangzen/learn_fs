# sources/distributed-fs/ceph-client/include/net/regulatory.h

Purpose: defines cfg80211 regulatory request/domain data structures, device regulatory flags, frequency/power/WMM rules, and rule-construction macros.

Important APIs and types: `enum environment_cap` classifies country-IE environment. `struct regulatory_request` records initiator, wiphy index, user hint type, alpha2, DFS region, intersection/processed flags, country-IE environment, list node, and RCU head. `enum ieee80211_regulatory_flags` defines custom/strict/beacon/country-IE/relax/self-managed behavior. `struct ieee80211_reg_rule` composes frequency range, power rule, WMM rule, flags, DFS CAC, PSD, and WMM presence. `struct ieee80211_regdomain` stores alpha2, DFS region, rule count, flexible rule array, and RCU head. `REG_RULE*` macros convert MHz/dBi/dBm inputs.

Control flow: regulatory core queues requests, intersects domains when needed, applies per-wiphy flags, and exposes channel power/DFS/no-IR constraints to wireless drivers.

State and persistence: regulatory requests and regdomains are runtime RCU-managed state; system/user hints may be reapplied but are not persisted here.

Dependencies and integration points: depends on IEEE80211/nl80211 UAPI, cfg80211 wireless core, RCU, DFS handling, country IEs, and driver wiphy registration.

Risks and test signals: risks include incompatible flag combinations, alpha2 special-code semantics, RCU freeing mistakes, WMM rule omission, unit conversion errors, and self-managed device conflicts. Test user/driver/core/country-IE hints, custom/strict/self-managed flags, DFS regions/CAC, WMM regulatory limits, beacon hints, and regulatory domain intersection.
