## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.c

Purpose: implements GuC Single Loop Power Control (SLPC) support for dynamic GT frequency management, including initialization, reset/start, min/max/boost frequency controls, efficient-frequency policy, media ratio mode, power profiles, task-state queries, PM interrupt setup, and debug printing.

Important APIs, types, and functions:
- Support/selection: `__detect_slpc_supported()`, `__guc_slpc_selected()`, and `intel_guc_slpc_init_early()`.
- Shared memory helpers: `slpc_mem_set_param()`, enable/disable helpers, `slpc_shared_data_reset()`, and `slpc_get_state()`.
- GuC action wrappers: `guc_action_slpc_set_param[_nb]()`, `guc_action_slpc_query()`, and `guc_action_slpc_reset()`.
- Lifecycle: `intel_guc_slpc_init()`, `intel_guc_slpc_enable()`, and `intel_guc_slpc_fini()`.
- Frequency APIs: `intel_guc_slpc_set_max_freq()`, `intel_guc_slpc_get_max_freq()`, `intel_guc_slpc_set_min_freq()`, `intel_guc_slpc_get_min_freq()`, `intel_guc_slpc_set_boost_freq()`, `intel_guc_slpc_boost()`, and `intel_guc_slpc_dec_waiters()`.
- Policy APIs: `intel_guc_slpc_set_ignore_eff_freq()`, `intel_guc_slpc_set_strategy()`, `intel_guc_slpc_set_media_ratio_mode()`, and `intel_guc_slpc_set_power_profile()`.
- Diagnostics: `intel_guc_slpc_print_info()` prints SLPC task status, decoded min/max frequencies, and waitboost counters.

Control flow:
- Early init marks SLPC supported only for Gen12+ GuC submission and selected when GuC submission is selected.
- Full init allocates a GuC-mapped shared data page, initializes softlimit/cache fields, mutex, boost work, waiter count, media ratio mode, and base power profile.
- Enable zeros and seeds shared data overrides, sends a reset event, waits for running state, queries task state, enables PM interrupt delivery to GuC, reads RP values from RPS caps, handles server RPMax-min case, sets max to fused RP0, restores cached efficient-frequency/media/strategy/power-profile/softlimit state, and returns errors on failed critical steps.
- Frequency setters validate against platform limits and current softlimits, use runtime PM, send SLPC parameter actions, and update cached softlimits on success. Min updates are locked because waitboost can temporarily force min frequency.
- Waitboost increments waiters, schedules boost work, raises min to boost/RP0 while waiters exist, and restores min softlimit when the last waiter retires.

State and persistence:
- `intel_guc_slpc` persists the shared VMA pointer/address, support/selection flags, platform RP/min frequencies, softlimits, efficient-frequency ignore flag, boost frequency, media ratio mode, power profile, lock, work item, waiter count, and boost count.
- GuC shared memory stores SLPC global/task state and override parameters; host flushes/queries it around firmware actions.

Dependencies and integration points:
- Depends on GuC CT send helpers, runtime PM, RPS frequency capability conversion, GT PM interrupt mask register, SLPC firmware ABI constants, media ratio support predicate, and DRM printer.
- Integrates with sysfs/debugfs frequency controls and request waitboost paths.

Risks:
- Frequency validation must keep min/max/boost within platform limits and softlimits; wrong ordering can reject valid sysfs requests or send invalid firmware parameters.
- Nonblocking boost actions can fail without making request retirement fail; diagnostics are notices.
- Shared data is read after cache flushes; missing cache maintenance can report stale state.
- Enable sequence has several best-effort cached parameter restores whose failures may be ignored or only logged in some calls.

Test signals:
- Boot with GuC submission on Gen12+ and confirm SLPC reaches running state.
- Sysfs min/max/boost tests for boundary values, invalid values, and persistence across reset/re-enable.
- Waitboost tests for waiter increment/decrement and min-frequency restore.
- Debugfs `guc_slpc_info` should reflect task state and decoded frequencies.
- Platform tests for media ratio support, server RPMax-min handling, and power saving/base profiles.
