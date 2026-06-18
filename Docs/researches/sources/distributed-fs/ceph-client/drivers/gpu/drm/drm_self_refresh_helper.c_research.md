# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_self_refresh_helper.c

Purpose: implements atomic helper support for panel self refresh, scheduling entry into self refresh after inactivity and adjusting atomic state to exit self refresh transparently.

Important APIs/types/functions: `struct drm_self_refresh_data` stores the target CRTC, delayed entry work, average mutex, and EWMA entry/exit times. `drm_self_refresh_helper_entry_work()` commits a self-refresh-active state. `drm_self_refresh_helper_update_avg_times()` updates transition timing. `drm_self_refresh_helper_alter_state()` modifies atomic state for self-refresh exit and queues future entry. `drm_self_refresh_helper_init()` and `drm_self_refresh_helper_cleanup()` manage per-CRTC helper lifetime.

Control flow: alter_state detects async or no-modeset updates that would touch a CRTC currently in self refresh and forces a normal modeset-capable update so SR can exit. For active CRTCs with helper data, it schedules entry work after twice the sum of recent entry and exit averages. Entry work allocates an atomic state, handles modeset deadlock retries, verifies the CRTC is enabled and all affected connectors are `self_refresh_aware`, sets `active=false` and `self_refresh_active=true`, then commits.

State and persistence behavior: helper data hangs off `crtc->self_refresh_data`, with delayed work on `system_percpu_wq` and EWMA timings seeded to 200 ms. Atomic commits persist self-refresh state in CRTC state, hidden from userspace.

Dependencies and integration points: integrates atomic state allocation/commit, modeset locking, connector self-refresh awareness, CRTC state flags, and driver atomic_check/commit_tail expectations.

Risks: entry work races with normal atomic commits and depends on deadlock backoff correctness. Drivers must fail atomic_check if hardware cannot enter SR despite awareness. Cleanup must cancel delayed work before freeing helper data. Forcing async updates into full modesets can surprise paths assuming no modeset work.

Test signals: init/cleanup and double-init rejection, delayed entry after inactivity, no entry when connectors are not aware, SR exit on plane/CRTC updates, EWMA transition updates, deadlock retry coverage, and suspend/unload cancellation tests.
