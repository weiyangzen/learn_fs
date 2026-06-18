# sources/distributed-fs/ceph-client/net/mac80211/tests/util.c

## Purpose
This file provides reusable KUnit fixture construction for mac80211 tests. It builds a minimal but capability-rich `ieee80211_sub_if_data`, `wiphy`, and supported-band environment so unit tests can exercise internal mac80211 code without a real driver or registered wireless device.

## Important APIs, types, and functions
- `channels_2ghz` and `channels_5ghz` are static channel tables with nl80211 bands, center frequencies, and hardware values.
- `bitrates` provides legacy 2.4/5 GHz rates, including short-preamble flags where relevant.
- `sband_capa_5ghz` defines HE and EHT interface-type capabilities for station and P2P-client modes. It models a small hwsim-like capability set with up to four spatial streams.
- `t_sdata_init()` is the KUnit resource initializer. It allocates `struct t_sdata`, `struct ieee80211_sub_if_data`, and `struct wiphy`, wires the local/sdata/wiphy relationships, and allocates per-band channels/rates.
- `t_sdata_exit()` frees allocated channel/rate arrays plus the fake `sdata`, `wiphy`, and wrapper object.

## Control flow
Initialization allocates the wrapper first, then `sdata`, then `wiphy`, setting the KUnit resource name to `sdata`. It assigns a station-mode default interface, initializes the default link back-pointer and link ID, attaches 2 GHz and 5 GHz supported-band structs to `wiphy->bands`, and loops from `NL80211_BAND_2GHZ` through `NL80211_BAND_5GHZ`. For each band, it assigns band identity, duplicates the shared bitrate table, duplicates the correct channel table, and fills HT capabilities. The 5 GHz path additionally sets VHT capabilities and MCS maps. After the loop, `ieee80211_set_sband_iftype_data()` attaches HE/EHT station/P2P capability data to the 5 GHz band.

## State and persistence
All state is per KUnit resource and freed by `t_sdata_exit()`. The fixture stores pointers into its own `struct t_sdata` for bands while dynamically allocating channel and bitrate arrays. There is no persistence beyond the test resource lifetime. The helper leaves `t_sdata->ctx` available for tests that need to associate caller-specific context, but `t_sdata_init()` itself does not consume the `ctx` argument.

## Dependencies and integration points
The fixture depends on internal mac80211 structures from `ieee80211_i.h` via `util.h`, public wireless structures from `<net/mac80211.h>`, cfg80211/nl80211 capability constants, KUnit resource APIs, and kernel allocation helpers such as `kzalloc_obj()` and `kmemdup()`. It is consumed through the `T_SDATA(test)` macro in `util.h`; one visible user in this tree is `tests/chan-mode.c`.

## Risks and edge cases
Allocation failures after earlier allocations rely on KUnit assertions to abort; the exit hook is the cleanup path for successfully created resources. The code duplicates `bitrates` before the switch and again in each supported case, which makes the first duplicate unreachable for 2 GHz/5 GHz and is a small fixture leak if not optimized away by test abort semantics. The fixture currently only models 2 GHz and 5 GHz bands, so tests needing 6 GHz, S1G, or richer per-interface capabilities must extend it. Since it uses partial internal structs, tests can accidentally depend on fields left zeroed here but initialized differently in real mac80211 devices.

## Test signals
A test that obtains `T_SDATA(test)` and reaches its assertions verifies that basic fake mac80211 object wiring, band tables, and HE/EHT capability setup are sufficient for the unit under test. Failures during resource allocation or cleanup point to fixture setup errors rather than production wireless behavior.
