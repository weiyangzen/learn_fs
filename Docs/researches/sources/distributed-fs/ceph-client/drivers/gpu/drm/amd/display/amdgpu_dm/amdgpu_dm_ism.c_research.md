# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.c

## Purpose
`amdgpu_dm_ism.c` implements per-CRTC idle state management. It coordinates OS vblank/cursor activity, DC hardware idle optimizations, and panel static-screen optimizations such as PSR1 and Replay low-Hz behavior through a finite-state machine, hysteresis timers, and recent idle-duration history.

## Important APIs, types, and functions
Public APIs are `amdgpu_dm_ism_init()`, `amdgpu_dm_ism_fini()`, `amdgpu_dm_ism_commit_event()`, `amdgpu_dm_ism_disable()`, and `amdgpu_dm_ism_enable()`. Core helpers include `dm_ism_next_state()`, `dm_ism_trigger_event()`, `dm_ism_dispatch_power_state()`, delay/history helpers, `dm_ism_commit_idle_optimization_state()`, and delayed-work callbacks.

## Control flow
Callers deliver idle, exit, cursor, and timer events while holding `dm->dc_lock`. `amdgpu_dm_ism_commit_event()` advances the FSM and processes immediate follow-up events until no more are needed. Enter-idle goes through hysteresis, records timestamps, computes frame-based delay from recent short-idle history, and schedules work or enters optimized idle. Optimized idle may allow DC idle optimizations and then progress to panel SSO. Exit-idle or cursor activity cancels timers, records idle duration, and restores full-power/vblank behavior.

## State and persistence behavior
State lives in `struct amdgpu_dm_ism` embedded in each `amdgpu_crtc`: config, current/previous states, circular idle history, last idle timestamp, and two delayed works. It mutates DC-wide idle optimization state and panel self-refresh controls. There is no persistence.

## Dependencies and integration points
It depends on DRM vblank semantics, AMD DC stream timing, `amdgpu_crtc`, `dm_crtc_state`, `dc_lock`, delayed workqueues, tracepoints, `dm->active_vblank_irq_count`, and PSR/Replay panel controls.

## Risks and edge cases
The FSM assumes `dc_lock` is held. Frame-time calculations require valid stream timing and nonzero pixel clock. History records must be initialized and timestamp-ordered. Disable paths must cancel work before DC teardown. Config values are frame counts, and zero values disable filters or delays.

## Test signals
Cover valid and invalid FSM transitions, vblank enable/disable, cursor updates during hysteresis/idle, delayed idle and SSO timers, CRTC-disabled immediate idle, short-idle filtering, disable/enable workqueue behavior, trace output, and expected toggling of DC idle optimizations and PSR/Replay.
