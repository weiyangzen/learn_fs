# sources/distributed-fs/ceph-client/net/wireless/tests/scan.c

## Purpose
`tests/scan.c` provides KUnit coverage for cfg80211 scan-related helpers: multi-BSSID IE generation, malformed IE handling, BSS inform/lookup behavior, MLO STA-profile BSS synthesis, and 6 GHz colocated AP parsing from Reduced Neighbor Report elements.

## Important APIs, Types, And Functions
The file defines `struct test_elem`, parameter tables for `gen_new_ie`, `inform_bss_ml_sta`, and `cfg80211_parse_colocated_ap`, and tests `test_gen_new_ie()`, `test_gen_new_ie_malformed()`, `test_inform_bss_ssid_only()`, `test_inform_bss_ml_sta()`, and `test_cfg80211_parse_colocated_ap()`. It registers suites `cfg80211-ie-generation`, `cfg80211-inform-bss`, and `cfg80211-scan-6ghz`. Production APIs under test include `cfg80211_gen_new_ie()`, `cfg80211_inform_bss_data()`, `cfg80211_get_bss()`, `__cfg80211_get_bss()`, `cfg80211_put_bss()`, `cfg80211_parse_colocated_ap()`, and `cfg80211_free_coloc_ap_list()`.

## Control Flow
IE-generation tests build parent, child, and expected SKBs from table entries, run `cfg80211_gen_new_ie()` with ample, exact, and insufficient output sizes, and compare output lengths/data. The malformed test checks that truncated elements are ignored rather than overread. The SSID-only inform test creates a KUnit wiphy, installs an `inform_bss` callback, submits a BSS, validates returned metadata and IE contents, then verifies lookup by SSID and BSSID. The MLO test constructs a probe response containing SSID, optional operating class, RNR, fragmented Basic Multi-Link element, fragmented STA profile, and vendor elements; it then expects both reporting and link BSS entries and validates link metadata, generated IE length, NSTR restrictions, and BSS lookup visibility. The colocated-AP tests build RNR elements and verify valid/invalid parsing outcomes.

## State And Persistence
All state is per-test and allocated through KUnit helpers. `T_WIPHY()` creates a disposable wiphy with a 2.4 GHz band. Test callbacks count inform-BSS notifications through `struct inform_bss`. BSS cache entries created by production code are released with `cfg80211_put_bss()`.

## Dependencies And Integration Points
The suite depends on KUnit SKB helpers, cfg80211 core internals, the local `util.h` wiphy fixture, mac80211 IE fragmentation helper `ieee80211_fragment_element()`, KUnit-exported cfg80211 symbols, and 802.11 constants for RNR/MLE/MBSSID fields.

## Risks And Edge Cases
The tests target untrusted-management-frame parsing risks: fragmented elements, invalid extension elements, non-inheritance rules, MLE common/profile length validation, duplicate link handling, RNR channel derivation, unsupported NSTR nonprimary links, invalid BSSID and disabled MLD links, and precise IE buffer sizing. Because expected generated IE lengths are explicit, benign production changes in generated metadata may require coordinated test updates.

## Test Signals
Passing suites show that IE inheritance preserves or overrides elements correctly, malformed IEs do not corrupt output, BSS inform callbacks receive the expected `ies` pointer and driver data, BSS lookup works by SSID/BSSID, MLO STA-profile parsing creates a link BSS with expected channel/TSF/capability/use restrictions, and RNR colocated AP parsing accepts only valid 6 GHz TBTT records.
