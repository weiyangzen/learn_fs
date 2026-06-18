# sources/distributed-fs/ceph-client/net/mac80211/tests/tpe.c

## Purpose
This file is a KUnit suite for mac80211 transmit power envelope (TPE) helper behavior. It validates the 6 GHz channel-subchannel offset logic and PSD reordering logic that are implemented in `mlme.c` and exported only for KUnit with `EXPORT_SYMBOL_IF_MAC80211_KUNIT`.

## Important APIs, types, and functions
- `struct subchan_test_case` describes one channel definition, a target partial subchannel count, and the expected offset returned by `ieee80211_calc_chandef_subchan_offset()`.
- `struct psd_reorder_test_case` describes AP and actually-used channel definitions plus an input/output `struct ieee80211_parsed_tpe_psd`.
- `subchan_offset()` asserts that the provided chandef is valid and compares the computed offset with the expected result.
- `psd_reorder()` copies the input PSD, calls `ieee80211_rearrange_tpe_psd()`, and compares the whole parsed PSD structure with `KUNIT_EXPECT_MEMEQ()`.
- `tpe_test_cases` registers two parameterized test families, and `kunit_test_suite(tpe)` exposes the suite as `mac80211-tpe`.

## Control flow
The suite defines static 6 GHz channels for control frequencies 5955, 6115, and 6255 MHz. Parameter generation comes from `KUNIT_ARRAY_PARAM_DESC()` for both case arrays. Each test first validates the constructed `cfg80211_chan_def`; this catches test-fixture errors before testing mac80211 helper logic. The offset cases cover equal-width channels, 320 MHz subdivision, 80+80 MHz primary/secondary ordering, and narrowing to 20/40/160 MHz. The PSD cases cover unchanged 320 MHz data, N=0 default behavior, and 320 MHz AP cases where HE subchannels and used EHT subchannels are lower, upper, or split.

## State and persistence
The tests use only static channel fixtures and stack-local copies of input structs. They do not allocate resources, mutate global state, or persist any state after a KUnit invocation. The PSD test intentionally copies `params->psd` before mutation because `ieee80211_rearrange_tpe_psd()` operates in place.

## Dependencies and integration points
The file includes `../ieee80211_i.h` for internal mac80211 declarations and imports the `EXPORTED_FOR_KUNIT_TESTING` namespace so it can link against KUnit-only exported helpers. It depends on cfg80211 channel validation and nl80211 channel-width constants. The covered production path is `ieee80211_rearrange_tpe()` in `mlme.c`, which rearranges parsed TPE values before station association/channel-use decisions consume them.

## Risks and edge cases
The test data encodes expected channel arithmetic directly; future changes to `ieee80211_chandef_downgrade()` or 320 MHz/80+80 semantics can require fixture updates. `KUNIT_EXPECT_MEMEQ()` compares the entire PSD structure, so padding or unrelated field changes in `struct ieee80211_parsed_tpe_psd` could make the test fragile if the structure layout changes. The tests focus on selected 6 GHz cases and do not exhaustively cover invalid chandefs, puncturing interactions, or every possible primary-channel offset.

## Test signals
Passing `mac80211-tpe` gives a direct signal that TPE PSD rearrangement still handles 320 MHz and 80+80 MHz offset calculations used by association logic. Failures identify either invalid fixture chandefs, wrong subchannel offset calculation, or in-place PSD mutation that no longer matches expected count/N/power ordering.
