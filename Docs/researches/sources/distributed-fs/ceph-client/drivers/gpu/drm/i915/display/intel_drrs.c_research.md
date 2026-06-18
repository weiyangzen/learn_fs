<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c

## Purpose
This file implements Display Refresh Rate Switching for internal panels. DRRS saves power by switching from high to low refresh after frontbuffer activity becomes idle, then returning to high refresh on rendering, flips, or manual debugfs control.

## Important APIs, Types, and Functions
Public APIs are `intel_drrs_type_str()`, `intel_cpu_transcoder_has_drrs()`, `intel_drrs_is_active()`, `intel_drrs_activate()`, `intel_drrs_deactivate()`, `intel_drrs_invalidate()`, `intel_drrs_flush()`, `intel_drrs_crtc_init()`, `intel_drrs_crtc_debugfs_add()`, and `intel_drrs_connector_debugfs_add()`.

Key internal helpers are `intel_drrs_set_refresh_rate_pipeconf()`, `intel_drrs_set_refresh_rate_m_n()`, `intel_drrs_set_state()`, `intel_drrs_schedule_work()`, `intel_drrs_frontbuffer_bits()`, `intel_drrs_downclock_work()`, and `intel_drrs_frontbuffer_update()`.

## Control Flow
Activation checks `has_drrs`, active hardware state, and joiner secondary status, then stores the CPU transcoder, DP M/N pairs, relevant frontbuffer bits, clears busy bits, and schedules a one-second delayed downclock. Invalidation/flush calls intersect frontbuffer bits with each active CRTC. Any activity forces high refresh; flush clears busy bits and schedules low-refresh work only when all tracked frontbuffers are idle. Deactivation forces high refresh, clears active state, and cancels delayed work.

## State and Persistence Behavior
Per-CRTC DRRS state is protected by `crtc->drrs.mutex` and includes `cpu_transcoder`, current refresh-rate state, M/N values, tracked frontbuffer masks, busy frontbuffer masks, and delayed work. `cpu_transcoder == INVALID_TRANSCODER` marks inactive DRRS. State is runtime-only and is rebuilt on modesets/activation.

## Dependencies and Integration Points
The implementation depends on frontbuffer tracking, DP M/N programming, transcoder PIPECONF bits, panel VBT/EDID DRRS type, CRTC atomic state, joiner-pipe masks, display workqueues, and debugfs. It integrates with `intel_panel_drrs_type()` for connector reporting.

## Risks
DRRS is sensitive to frontbuffer bit accounting: missing an invalidate can leave the panel at low refresh during visible activity, while missing a flush can prevent power savings. Joiner configurations require tracking all joined pipe frontbuffers from the primary. Switching via PIPECONF versus M/N depends on transcoder capabilities. Debugfs manual activation waits for commit `hw_done`, but races around modeset state still require careful locking.

## Test Signals
Signals include debugfs `i915_drrs_status` transitions, frontbuffer invalidate/flush tests showing high/low refresh changes, internal panel EDID/VBT modes with multiple refresh rates, joiner-pipe DRRS behavior, suspend/resume and modeset deactivation returning to high refresh, and no delayed work after CRTC teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c -->
