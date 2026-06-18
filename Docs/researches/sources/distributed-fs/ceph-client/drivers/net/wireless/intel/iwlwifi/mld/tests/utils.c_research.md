# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/utils.c

Purpose: Provides shared KUnit construction helpers for synthetic MLD, VIF, link, station, channel context, notification packet, EMLSR association, and information-element objects.

Important APIs and functions: `iwlmld_kunit_test_init()` allocates and initializes a minimal `iwl_mld`. Helpers add VIFs, links, chanctxs, STAs, MLO associations, non-MLO associations, EMLSR dual-link associations, packets, elements, and PHY lookup by link.

Control flow: Test init allocates trans/cfg/fw/hw/wiphy, initializes wiphy mutex, calls `iwl_construct_mld()`, seeds firmware capability counts, allocates NVM data and a scan command buffer, and marks firmware running. Association helpers create VIF/link mappings, allocate FW IDs, assign channel contexts under wiphy lock, create authorized AP STAs, and set association state.

State and persistence: All objects are KUnit-allocated and scoped to a test. The helpers populate RCU pointer maps in VIF, STA, MLD, and link structures, plus firmware ID maps used by production functions.

Dependencies and integration points: Depends on KUnit, test-bug helpers, firmware scan/MAC definitions, MLD construction, interface/link/PHY/station allocation helpers, and shared channel definitions in `utils.h`.

Risks: The environment is intentionally partial: no real hw private area, TXQs are TODO, supported interface types are limited, and firmware/radio capabilities are simplified. Tests using these helpers must not assume full opmode-start parity.

Test signals: Provides reusable setup for RX, aggregation, link, and link-selection suites. Helper assertions catch invalid chandefs, missing link/channel pointers, and allocation failures.
