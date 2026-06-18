# sources/distributed-fs/ceph-client/net/mac80211/tests/s1g_tim.c

Purpose: KUnit tests for S1G TIM Partial Virtual Bitmap decoding via `ieee80211_s1g_check_tim()`, covering block bitmap, single AID, open-ended block, and inverse forms based on IEEE 802.11 annex examples.

Important APIs/functions: helpers `BC()`, `tim_begin()`, `tim_end()`, `pvb_add_block_bitmap()`, `pvb_add_single_aid()`, `pvb_add_olb()`, `fill_bitmap()`, `fill_bitmap_inverse()`, and `check_all_aids()` build TIM IEs and compare expected AID membership. `dump_tim_bits()` emits diagnostic bit-level logs. Suite name is `mac80211-s1g-tim`.

Control flow: each test constructs an in-stack TIM IE buffer, appends one S1G PVB encoding mode, builds an expected bitmap for AIDs 1 through `MAX_AID`, optionally dumps encoding details, and checks every AID with `ieee80211_s1g_check_tim()`. Six cases cover normal and inverse variants for block, single, and OLB encodings.

State and persistence behavior: state is entirely per-test stack data plus KUnit log output. No global mac80211 state is mutated.

Dependencies and integration points: depends on Linux IEEE 802.11 definitions, KUnit, `kunit/test-bug.h`, bitmap helpers, S1G TIM encoding constants, and the production S1G TIM decoder.

Risks and edge cases: verifies positive and inverse membership semantics across the supported encoding modes, but notes that ADE mode is optional and not supported by mac80211. Coverage is bounded to `MAX_AID` 128 and synthetic single-block style examples, so larger AID ranges and malformed/truncated TIMs remain separate concerns.

Test signals: passing suite gives targeted confidence that S1G TIM decoding matches the constructed annex-style examples and inverse semantics.
