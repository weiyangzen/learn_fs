# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.c

## Purpose
Implements GuC Power Conservation support outside the GuC RC-specific file: SLPC startup/reset, frequency bounds and user limits, power profiles, platform workarounds, C-state/status reads, residency counters, and teardown frequency handling.

## Important APIs, Types, And Functions
Exports init/start/stop/print, generic SLPC param set/unset, frequency getters/setters, RP0/RPa/RPe/RPn getters, current/actual frequency reads, power profile get/set, RC6/MC6 residency, early RP value init, unslice raise, stashed frequency restore, and flush-frequency limit apply/remove. Important internal helpers include `wait_for_pc_state`, `pc_action_reset`, `pc_action_query_task_state`, `pc_set_min_freq`, `pc_set_max_freq`, `pc_adjust_freq_bounds`, `pc_init_freqs`, `pc_set_mert_freq_cap`, and `pc_modify_defaults`.

## Control Flow
Init skips when `skip_guc_pc` is set; otherwise it initializes `freq_lock`, allocates a pinned mapped SLPC shared-data BO, sets the default power profile, and registers hardware teardown. Early init reads fused RP bounds under forcewake. Start takes forcewake, handles skip mode by requesting maximum frequency manually, clears shared data, writes the shared-data size, sends SLPC reset, waits for `SLPC_GLOBAL_STATE_RUNNING` with a short then extended timeout, modifies platform defaults, initializes and clamps frequency bounds, restores user requests, applies MERT caps, enables compute strategy, and writes the cached power profile. Stop marks frequencies not ready. Getters/setters lock `freq_lock`, query GuC task state when needed, and reject operations while reset/stop leaves `freq_ready` false.

## State And Persistence
Persistent state includes the shared-data BO, fused `rp0_freq`/`rpn_freq`, user-requested min/max, stashed min/max for unload or workarounds, `flush_freq_limit`, `freq_ready`, `freq_lock`, and `power_profile`. User-requested limits survive resets through `pc_adjust_requested_freq`; stashed values are restored by `xe_guc_pc_restore_stashed_freq`.

## Dependencies And Integration Points
Depends on SLPC GuC action ABI, GuC CT, Xe BO/map/MMIO/forcewake/pcode/PM helpers, GT throttle and idle support, generated WA tables, SR-IOV mode checks, and platform registers for TGL/PVC/MTL-class frequency data. It interacts with `xe_guc_rc.c` because GuC RC mode is controlled through SLPC messages.

## Risks And Test Signals
The state machine is timing-sensitive: startup failure disables dynamic frequency and GT sleep states. Frequency setters must respect `freq_ready`, RP bounds, user limits, and platform workarounds. The flush cap workaround serializes user max-frequency updates with `wait_var_event_timeout`, and failures can leave caps active until removal. Test signals include SLPC running state, sysfs/debugfs min/max round trips, reset recovery preserving user limits, power-profile changes, WA-specific flush frequency behavior, and teardown without wedged-device CT errors.
