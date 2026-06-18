# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.c

## Purpose
`pp_psm.c` implements the legacy Power State Manager glue for `struct pp_hwmgr`. It builds an in-memory table of BIOS/PPTable power states, tracks requested/current/boot/UVD states, selects boot/performance/user states by classification labels, and applies dynamic power-state changes through the common PHM hooks.

## Important APIs and functions
Exported functions are `psm_init_power_state_table()`, `psm_fini_power_state_table()`, `psm_set_boot_states()`, `psm_set_performance_states()`, `psm_set_user_performance_state()`, and `psm_adjust_power_state_dynamic()`. Local helpers search by UI label or classification flag, copy selected states to `hwmgr->request_ps`, and run the actual hardware transition through `power_state_management()`.

## Control flow
Initialization is callback-driven. If `get_num_of_pp_table_entries` or `get_power_state_size` is missing, initialization returns success with no PSM table. If table count or state size is invalid, it warns, zeros `num_ps`/`ps_size`, and returns success so newer ASICs without this PSM can continue. Otherwise it allocates a contiguous state arena where each record is `sizeof(struct pp_power_state) + ASIC-private-size`, fills entries via `get_pp_table_entry()`, assigns one-based IDs, and records boot/UVD pointers.

Dynamic adjustment gates display/state handling behind `hwmgr->not_vf`. With PSM state, it applies state adjustment rules, compares current/requested hardware states, and calls `phm_set_power_state()` when hardware differs or display configuration requires SMC update. Without a PSM table, it still runs `phm_apply_clock_adjust_rules()` so DAL clock limits can be honored on ASICs such as Vega12/Vega20. It then applies forced DPM levels and updates workload power profile mode outside manual DPM mode.

## State and persistence behavior
The module owns heap-backed `hwmgr->ps`, `request_ps`, and `current_ps`; `boot_ps` and `uvd_ps` are pointers into the `ps` arena. Requested and current states are full copies. `psm_set_states()` mutates only `request_ps`. `power_state_management()` mutates hardware via PHM hooks and then copies `request_ps` to `current_ps`. The DPM/workload section mutates `hwmgr->dpm_level` and may update firmware-visible power profile state.

## Dependencies and integration points
This file depends on `hwmgr->hwmgr_func` callbacks, PHM helpers (`phm_apply_state_adjust_rules`, `phm_check_states_equal`, `phm_set_power_state`, display notification helpers, DPM/profile helpers), kernel allocation, and classification/label enums. `hwmgr.c` calls these functions during hwmgr init, start, suspend/resume, performance-level changes, and user profile changes.

## Risks and test signals
Missing PSM support is reported as success with `hwmgr->ps == NULL`, so callers must not treat every `0` return as an applied state. Direct misuse can be unsafe because `power_state_management()` expects initialized `current_ps`. Battery/Balanced user labels fall back to Performance. Workload masks with multiple bits collapse to the highest set bit. Tests should cover allocation cleanup, missing callbacks, classification lookup, user-label fallback, forced/manual DPM behavior, and no-PSM ASIC clock-adjust handling.
