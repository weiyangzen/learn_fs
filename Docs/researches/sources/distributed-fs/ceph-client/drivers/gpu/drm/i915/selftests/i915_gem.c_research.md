# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_gem.c

Purpose: Live GEM selftests for suspend, hibernate, stolen-memory loss simulation, context switching after resume, and GEM wound/wait locking behavior.

Important APIs/functions: `i915_gem_live_selftests()`, `igt_gem_suspend()`, `igt_gem_hibernate()`, `igt_gem_ww_ctx()`, `switch_to_context()`, and PM helper shims.

Control flow: Suspend/hibernate tests create a mock file and live context, submit requests on all context engines, run GEM suspend/freeze paths under runtime PM where needed, simulate hibernate by overwriting stolen memory through GGTT aperture, resume GGTT/GEM/PAT state, and submit again. WW test creates two internal objects and locks them repeatedly using a GEM ww context, handling `-EDEADLK` by backing off and retrying.

State/persistence: No lasting state after tests. Temporarily mutates stolen memory contents, GGTT suspend/resume state, GEM object locks, and context/request state.

Dependencies/integration: GEM PM, GGTT, stolen memory, runtime PM, PAT setup, mock DRM files, live contexts, internal GEM objects, and `igt_flush_test` patterns.

Risks: Stolen-memory trashing is intentionally destructive in a controlled test slot and only works when GGTT aperture exists. PM sequencing must mimic real S3/S4 enough to catch restoration bugs without full platform sleep. WW locking test relies on correct deadlock handling.

Test signals: Context switch failures after resume, stolen restore issues, GEM PM failures, and ww lock/backoff errors. Wedged GT skips the live suite.
