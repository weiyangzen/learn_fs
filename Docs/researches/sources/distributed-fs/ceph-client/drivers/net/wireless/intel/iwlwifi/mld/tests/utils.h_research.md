# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.h

Purpose: Declares shared MLD KUnit helper APIs and static channel/channel-definition fixtures.

Important APIs and types: Declares `struct iwl_mld_kunit_link`, allocation assertion macros, VIF/link/chanctx/STA/association helpers, packet creation helper, EMLSR association helper, element generation helper, and PHY lookup helper. Defines reusable 2.4/5/6 GHz channels and a `CHANDEF_LIST` spanning 20 through 320 MHz widths.

Control flow and integration: Test sources include this header to build consistent synthetic mac80211/MLD topologies. `CHANDEF_LIST` also feeds a KUnit chandef-validity suite in `utils.c`.

State and persistence: Header-level static channel and chandef fixtures are compile-time test data.

Dependencies: Requires mac80211 and KUnit test-bug infrastructure; implementation lives in `utils.c`.

Risks: Static channel fixtures use `hw_value` equal to frequency, which is fine for tested policy but not a full hardware-channel model. Helper macros assert allocation success and abort tests, so they are not suitable for negative allocation-path tests.

Test signals: Build and KUnit usage across all MLD suites; invalid chandef definitions are caught by `iwlmld_valid_test_chandefs`.
