## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.c

Purpose: registers GuC debugfs files for status, registered contexts, SLPC status, scheduler-disable tuning, and GuC log debugfs integration.

Important APIs, types, and functions:
- `guc_info_show()` prints firmware load status, log info, and, when GuC submission is used, CT state, submission info, and ADS policy info.
- `guc_registered_contexts_show()` prints GuC-registered context information when GuC submission is active.
- `guc_slpc_info_show()` prints SLPC state via `intel_guc_slpc_print_info()`.
- `guc_sched_disable_delay_ms_get/set()` exposes and clamps scheduler disable delay to 60 seconds.
- `guc_sched_disable_gucid_threshold_get/set()` exposes scheduler-disable GuC-id threshold and clamps to `intel_guc_sched_disable_gucid_threshold_max()`.
- `intel_guc_debugfs_register()` registers the file table and delegates GuC log files to `intel_guc_log_debugfs_register()`.

Control flow:
- Registration is skipped if GuC is unsupported. Reads route through `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE` helpers. SLPC file visibility is guarded by an eval callback that checks `intel_guc_slpc_is_used()`.

State and persistence:
- Debugfs files mutate runtime `guc->submission_state.sched_disable_delay_ms` and `sched_disable_gucid_threshold`. Other files are read-only status projections.

Dependencies and integration points:
- Depends on GT debugfs helpers, GuC ADS, CT, SLPC, submission, log debugfs, and DRM printer/seq_file integration.

Risks:
- Debugfs setters can change scheduling behavior at runtime; clamping prevents extreme delay/threshold values but does not validate workload-specific impact.
- Status reads may return `-ENODEV` when GuC submission or SLPC is not used.

Test signals:
- Mount debugfs and verify file presence based on GuC/SLPC enablement.
- Read `guc_info`, `guc_registered_contexts`, and `guc_slpc_info` under supported/unsupported configurations.
- Write boundary values to scheduler tuning files and confirm clamping.
