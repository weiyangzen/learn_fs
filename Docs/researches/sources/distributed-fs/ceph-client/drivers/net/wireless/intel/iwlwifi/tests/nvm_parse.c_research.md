# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/tests/nvm_parse.c

## Purpose
This KUnit suite validates regulatory rule flag derivation for selected iwlwifi NVM channel flags, especially 6 GHz VLP client/AP behavior.

## Important APIs, Types, and Functions
- `struct nvm_flag_case` defines parameterized cases with expected set and clear regulatory flags.
- `nvm_flag_cases[]` covers restricted VLP, allowed VLP client/AP, and client-only VLP behavior.
- `test_nvm_flags()` calls `iwl_nvm_get_regdom_bw_flags()` and asserts required flags are present and forbidden flags are absent.
- `KUNIT_ARRAY_PARAM_DESC()` and `KUNIT_CASE_PARAM()` register the parameterized inputs.

## Control Flow
Each parameter case initializes an empty `iwl_reg_capa`, invokes the NVM parser helper with the case's `nvm_flags`, then checks bit inclusion/exclusion using explicit failure messages. The suite name is `iwlwifi-nvm_flags`.

## State and Persistence Behavior
The suite is stateless. It constructs local data and reads constants from the iwlwifi/NL80211 regulatory APIs.

## Dependencies and Integration Points
It includes `<iwl-nvm-parse.h>`, imports `EXPORTED_FOR_KUNIT_TESTING`, and depends on regulatory flag definitions such as `NL80211_RRF_NO_6GHZ_VLP_CLIENT` and `NL80211_RRF_ALLOW_6GHZ_VLP_AP`.

## Risks and Edge Cases
The cases are focused rather than exhaustive. They protect a specific mapping of NVM VLP bits to cfg80211 regulatory flags but do not cover all channel flags, bandwidth flags, or capability combinations.

## Test Signals
Passing KUnit output confirms the NVM parser preserves the expected 6 GHz VLP policy for the covered cases.
