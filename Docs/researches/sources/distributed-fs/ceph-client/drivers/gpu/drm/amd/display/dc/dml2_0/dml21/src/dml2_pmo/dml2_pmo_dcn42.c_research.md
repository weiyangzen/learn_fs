# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_pmo/dml2_pmo_dcn42.c

## Purpose
Defines a DCN42 PMO policy implementation that uses vblank-only p-state strategies for one to four displays. It initializes DCN4-style PMO strategy lists while disabling FAMS-specific parameter ranges and provides a strict DCN42 p-state support test.

## Important APIs, types, and functions
- Static `dcn42_strategy_list_1_display` through `_4_display` each contain one strategy: all active streams use `dml2_pstate_method_vblank`, inactive slots use `dml2_pstate_method_na`, and `allow_state_increase` is true.
- `pmo_dcn42_initialize()` stores PMO instance pointers/limits/options, zeros FAMS refresh-rate limits, selects override strategy lists or built-in DCN42 lists, and expands them with `pmo_dcn4_fams2_expand_base_pstate_strategies()`.
- `pmo_dcn42_test_for_pstate_support()` accepts all-streams-blanked configs, rejects missing candidates, then requires every active stream candidate to be vblank method with enough reserved time and no positive vactive p-state margin.

## Control flow and integration
The code is structurally compatible with the DCN4 FAMS2 PMO scratch/init data. Initialization iterates display counts 1..4, selects a base list from options or static defaults, chooses the corresponding expanded output array, asserts base list size, and calls the FAMS2 strategy expander. The test function reads `scratch.pmo_dcn4.cur_pstate_candidate`, `pstate_strategy_candidates`, and stream plane masks to validate current strategy state.

## State and persistence behavior
Writes into `dml2_pmo_instance`: SoC/IP/options pointers, combine limits, MCG table size, FAMS parameter defaults, and expanded DCN4 strategy-list storage in `init_data.pmo_dcn4`. Test reads PMO scratch but does not mutate it.

## Dependencies
Includes DCN42 PMO header, float math, debug logging, and `dml2_pmo_dcn4_fams2.h`. It depends on FAMS2 helper functions `pmo_dcn4_fams2_expand_base_pstate_strategies()`, `dcn4_get_minimum_reserved_time_us_for_planes()`, and `dcn4_get_vactive_pstate_margin()`.

## Risks and edge cases
In the researched factory, `dml2_project_dcn42` is routed to `pmo_dcn4_fams2_initialize()` and related FAMS2 callbacks, not to `pmo_dcn42_initialize()` or `pmo_dcn42_test_for_pstate_support()`. That makes this file potentially unused unless another factory or build path wires it. If enabled, its policy intentionally rejects non-vblank methods and any positive vactive p-state margin, so it is stricter than FAMS-capable policies. Override strategy lists can change behavior but still pass through the same expander.

## Test signals
Tests should first verify whether the build/factory actually wires these functions. Direct unit tests should cover one to four streams, override and default strategies, all-streams-blanked bypass, invalid `cur_pstate_candidate`, insufficient reserved time, positive vactive margin, and non-vblank candidate rejection.
