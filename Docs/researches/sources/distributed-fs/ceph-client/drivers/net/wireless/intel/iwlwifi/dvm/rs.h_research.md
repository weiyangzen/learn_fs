# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.h

## Purpose
`rs.h` is the shared definition header for the DVM rate-scaling implementation. It declares the internal rate indexes, PLCP and IEEE encodings, rate masks, rate-control thresholds, mode-search action constants, traffic-load constants, table classification helpers, and the per-station state structures consumed by `rs.c` and related station code.

The header forms the contract between mac80211 station private data, firmware link-quality commands, and the DVM rate-control policy.

## Important APIs, Types, And Macros
- `struct iwl_rate_info` describes each rate's firmware PLCP encodings, IEEE value, and adjacent-rate relationships. `iwl_rates[]` is declared here and defined in `rs.c`.
- `IWL_RATE_*_INDEX`, `IWL_RATE_*_INDEX_TABLE`, and first/last OFDM/CCK enums define the internal indexing space.
- `IWL_RATE_*_MASK` macros build bitmasks for supported-rate filtering.
- Legacy and HT PLCP enums map internal rates to firmware API values for legacy, SISO, MIMO2, and MIMO3 rates.
- IEEE rate enums provide the mac80211-visible half-Mbps values.
- Threshold macros such as `IWL_RATE_HIGH_TH`, `IWL_RATE_INCREASE_TH`, and `IWL_RATE_DECREASE_TH` use a `128 * percent` success-ratio scale.
- `IWL_LEGACY_*` and `IWL_NONE_LEGACY_*` constants define how long the algorithm stays in a selected modulation table.
- `IWL_*_SWITCH_*` constants enumerate possible search actions from legacy, SISO, MIMO2, and MIMO3 modes.
- `enum iwl_table_type` plus helpers `is_legacy()`, `is_siso()`, `is_mimo2()`, `is_mimo3()`, `is_mimo()`, `is_Ht()`, and `is_a_band()` classify LQ tables.
- `struct iwl_rate_scale_data` stores per-rate sliding-window statistics.
- `struct iwl_scale_tbl_info` stores one active or search table's modulation type, antenna mask, SGI/HT40/duplicate flags, action cursor, expected throughput table, current rate, and per-rate windows.
- `struct iwl_traffic_load` stores a per-TID circular traffic-load history used to decide when to start TX aggregation.
- `struct iwl_lq_sta` is the central per-station rate-control state, including two `iwl_scale_tbl_info` tables, the current firmware `iwl_link_quality_cmd`, supported-rate masks, counters, aggregation flags, last selected rates, and a backpointer to `struct iwl_priv`.
- `first_antenna()` returns `ANT_A`, `ANT_B`, or `ANT_C` from a mask in priority order.
- Public functions are `iwl_rs_rate_init()`, `iwlagn_rate_control_register()`, and `iwlagn_rate_control_unregister()`.

## Control Flow
This header does not execute control flow, but it defines the state machine vocabulary. `LQ_SIZE` fixes two mode tables: active and search. `active_tbl`, `search_better_tbl`, `stay_in_tbl`, action counters, table count limits, and success/failure limits in `struct iwl_lq_sta` are the flags and counters that `rs.c` mutates when moving between rate adjustment and modulation-mode search.

Rate masks begin with peer/mac80211 capabilities (`supp_rates`, `active_*_rate`) and are intersected with mode-specific table masks during scaling. Action constants define the order in which `rs.c` tries antenna changes, SISO/MIMO transitions, and guard interval changes. Traffic-load constants define the time bucket size and maximum history used before requesting aggregation.

## State And Persistence Behavior
All persistent rate-control state described here is per station and lives in mac80211 station private storage through `struct iwl_station_priv`. It survives across many packets and callbacks until station teardown or reinitialization. The `iwl_link_quality_cmd lq` inside `struct iwl_lq_sta` is both a cached software representation and the template sent to firmware.

No state in this header is global except the declared `iwl_rates[]` table. The macros and enums are compile-time contracts with firmware encodings and cannot be changed without updating conversion logic and firmware command expectations.

## Dependencies And Integration Points
The header includes mac80211 definitions, `iwl-config.h`, and firmware command structures from `commands.h`. It references `struct iwl_priv`, `struct ieee80211_sta`, `struct iwl_link_quality_cmd`, `IWL_MAX_TID_COUNT`, antenna masks, and rate flag encodings declared elsewhere in the DVM driver.

`sta.c` uses `iwl_rates[]` and `first_antenna()` when constructing default link-quality commands for local and broadcast stations. `rs.c` owns most consumers of the structures. RXON/HT configuration and station HT capabilities feed fields in `struct iwl_lq_sta` and `struct iwl_scale_tbl_info`.

## Risks And Edge Cases
- The internal rate ordering mixes CCK, OFDM, and a pseudo 60 Mbps index. Conversion code must respect gaps and band-specific offsets.
- Success ratio thresholds are scaled by 128, not plain percentages. Misinterpreting them changes rate-control aggressiveness.
- `is_g_and()` appears to be a typo-like helper name for `LQ_G`; callers should avoid propagating the naming mistake into new APIs.
- `TIME_WRAP_AROUND()` handles a wrapping millisecond counter by arithmetic expression; callers must pass comparable rounded times.
- `first_antenna()` returns `ANT_C` when neither A nor B is set, so callers should validate masks before treating its return as guaranteed supported.
- `struct iwl_lq_sta` mixes algorithm-only state, firmware command state, debugfs state, and driver backpointers. Lifetime and locking must be handled by station code and mac80211 callbacks.
- Action constants are mode-specific but some loops in `rs.c` compare against similarly valued constants from another mode; changes to these values need broad review.

## Test Signals
Build coverage should include debugfs enabled and disabled because `dbg_fixed_rate` changes `struct iwl_lq_sta`. Runtime validation should confirm rate mask derivation for 2.4 GHz CCK/OFDM, 5 GHz OFDM-only, and HT MCS masks for one, two, and three streams. Tests that inspect debugfs `rate_scale_table` and `rate_stats_table` can validate that structure fields are populated and evolve as expected. Any change to constants should be checked with throughput, aggregation, and Bluetooth coexistence tests because those thresholds directly steer rate-control state.
