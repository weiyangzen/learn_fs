# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.h

## Purpose
`pp_psm.h` exposes the legacy Power State Manager lifecycle and state-selection API to hwmgr orchestration code. It is the narrow public contract for initializing, selecting, adjusting, and freeing PSM state.

## Important APIs
The header declares `psm_init_power_state_table()`, `psm_fini_power_state_table()`, `psm_set_boot_states()`, `psm_set_performance_states()`, `psm_set_user_performance_state()`, and `psm_adjust_power_state_dynamic()`. The user-state function returns a `struct pp_power_state **` selected from the internal table. The dynamic adjust function accepts `skip_display_settings` and an optional explicit `new_ps` override.

## Control flow and state
There is no executable code in the header. It includes `hwmgr.h`, so it intentionally exposes hwmgr-owned state types and enums. The declared functions mutate `struct pp_hwmgr` fields and, through the `.c` implementation, may program hardware/SMC state.

## Dependencies and integration points
Primary callers are in `hwmgr.c`, which sequences PSM initialization during hardware manager setup and calls boot/performance/user state transitions around start, suspend, resume, and profile changes. ASIC-specific hwmgr callbacks fill the table that this API manages.

## Risks and test signals
The interface communicates support absence through successful calls with `hwmgr->ps == NULL`, so callers should not assume every `0` return means a state was selected or applied. Build coverage should catch type/prototype drift with `hwmgr.c`; runtime tests should validate that user state pointers are not retained after `psm_fini_power_state_table()`.
