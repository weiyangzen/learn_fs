# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/rx.c

Purpose: Provides KUnit coverage for RX duplicate detection in `iwl_mld_is_dup()`.

Important APIs and functions: Defines parameterized `is_dup_cases`, helpers to initialize duplicate-data state and RX packet descriptors, and `test_is_dup()` which asserts duplicate decisions and RX status flags.

Control flow: Each case creates a station, seeds one queue of `iwl_mld_rxq_dup_data`, builds an 802.11 header and MPDU descriptor, calls `iwl_mld_is_dup()`, and checks whether the frame is dropped as duplicate plus whether `RX_FLAG_DUP_VALIDATED` or `RX_FLAG_ALLOW_SAME_PN` is set.

State and persistence: Per-test duplicate data stores last sequence and A-MSDU subframe index for a selected TID. State is KUnit-managed and not persistent.

Dependencies and integration points: Depends on production RX duplicate logic, station private data, iwl-trans structures, and utility setup. It models one RX queue.

Risks: Only single-queue duplicate state is exercised. Fragmented frames and hardware-provided duplicate status outside the modeled descriptor fields are not covered here.

Test signals: Existing cases cover control/null/multicast bypass, QoS and non-QoS sequence matching, retry-bit duplicate drops, invalid TID, and A-MSDU same-PN allowance by subframe ordering.
