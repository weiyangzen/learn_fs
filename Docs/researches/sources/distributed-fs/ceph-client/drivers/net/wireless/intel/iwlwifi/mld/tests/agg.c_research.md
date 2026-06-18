# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/agg.c

Purpose: Provides KUnit coverage for RX reorder-buffer behavior around BAID validity, multicast/non-QoS bypass, old/duplicate sequence handling, sequence-number wrap, holes, buffered release order, and A-MSDU subframe release.

Important APIs and functions: Defines parameterized `reorder_buffer_cases`, `test_reorder_buffer()`, fake static stubs for `iwl_mld_pass_packet_to_mac80211()` and `iwl_mld_fw_sta_id_mask()`, and helpers that build MPDU descriptors, SKBs, BAID state, and reorder buffer contents.

Control flow: Each test case creates an MLD station/VIF, prepares one incoming SKB and descriptor, installs BAID data into `mld->fw_id_to_ba`, invokes `iwl_mld_reorder()` under RCU, then asserts the reorder result, stored count, head sequence number, and exact release order captured by the fake pass-to-mac80211 stub.

State and persistence: Uses test-global `g_released_skbs` and `g_num_released_skbs` to capture releases for a single case. Allocated BAID, SKB, VIF, STA, and MLD state is KUnit-managed and discarded after each case.

Dependencies and integration points: Depends on KUnit, static stubs, KUnit SKB helpers, `utils.c` test setup, production `agg.h`, `rx.h`, and `sta.h`. It validates production reorder semantics without firmware.

Risks: The fake FW STA mask assumes only MLD link pointers set up by utils, not all production validation. Cases use a single queue and BA window size of 64, so multi-queue and nonstandard BA sizes need separate tests.

Test signals: Existing cases are strong signals for in-order, out-of-order, wrap, duplicate, old SN, invalid BAID, multicast, non-QoS, and A-MSDU behavior. Missing signals include timeout release, multiple queues, BA teardown races, and memory pressure.
