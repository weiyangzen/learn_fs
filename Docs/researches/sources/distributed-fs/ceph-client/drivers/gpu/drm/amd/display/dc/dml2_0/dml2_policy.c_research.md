<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c

Purpose: builds DML2.0 policy defaults and synthesizes a sorted SoC state table from PMFW-derived clocks and DCFCLK STAs. It translates sparse clock entries into complete DCFCLK/FCLK/UCLK tuples that DML mode support can evaluate.

Important APIs/types/functions: exported functions are `dml2_policy_build_synthetic_soc_states()` and `build_unoptimized_policy_settings()`. Internal helpers include `get_optimal_ntuple()`, `calculate_net_bw_in_mbytes_sec()`, `insert_entry_into_table_sorted()`, and `remove_entry_from_table_at_index()`.

Control flow: synthetic state construction scans input states for max display, PHY, fabric, DCFCLK, SOC, and UCLK limits, seeds an entry from state 0, inserts all DCFCLK STAs, UCLK DPMs, and FCLK DPMs or max FCLK into a bandwidth-sorted table, removes unsupported entries, rounds UCLK/FCLK to available DPMs, clamps minimum FCLK/DCFCLK, and removes neighboring duplicates. `build_unoptimized_policy_settings()` initializes all planes to as-needed MPC/ODM, required immediate flip, and permissive p-state/stutter policy, then adjusts DCN35/DCN36/DCN351 policy flags.

State and persistence behavior: state is written only to caller-provided `soc_states_st`, scratch entry, and `dml_mode_eval_policy_st`. There is no static mutable state.

Dependencies and integration points: consumes `display_mode_core_structs.h` structures and constants such as `__DML_MAX_STATE_ARRAY_SIZE__`. It is called from `dml2_translation_helper.c` for native SoC-state construction and from `dml2_wrapper_fpu.c` before each mode-support evaluation.

Risks and test signals: the code assumes at least one input state and enough output-table capacity; insert operations do not enforce a hard bounds check. `num_fclk_dpms - 1` is used in the coarse-FCLK path, so missing FCLK entries would underflow. Floating bandwidth comparisons and integer truncation can change state ordering. Test signals include synthetic table generation with 1, 2, and many FCLK/UCLK entries, duplicate removal, override tables, max-clock rejection, and DCN35/DCN36 policy deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c -->
