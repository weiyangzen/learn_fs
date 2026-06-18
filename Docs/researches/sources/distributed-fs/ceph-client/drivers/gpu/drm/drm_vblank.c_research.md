# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vblank.c

## Purpose
Implements the DRM core vblank subsystem: per-CRTC vblank interrupt/timer accounting, timestamp interpolation, reference-counted enable/disable, userspace vblank wait and sequence ioctls, event delivery, and integration with vblank work. It is the central code drivers rely on after `drm_vblank_init()` and `drm_crtc_handle_vblank()`.

## Important APIs, Types, and Functions
Exports include `drm_vblank_init`, `drm_dev_has_vblank`, `drm_crtc_vblank_get/put`, `drm_crtc_vblank_on/off/reset/restore`, count/time accessors, event helpers, wait/sequence ioctls, vblank timer start/cancel/timeout helpers, and timestamp helpers. State is held in `struct drm_vblank_crtc` entries under `dev->vblank`, including atomic `count`, hardware `last`, `time`, `seqlock`, waitqueue, `refcount`, `enabled`, `inmodeset`, config, mode timing, hrtimer, and pending work list. Module parameters `vblankoffdelay` and `timestamp_precision_usec` tune IRQ disable delay and timestamp precision.

## Control Flow
Initialization allocates per-CRTC vblank state, initializes locks/timers/seqlocks/workers, and registers managed cleanup. `drm_vblank_get()` increments the refcount under `vbl_lock`; the 0-to-1 transition enables hardware vblank through CRTC funcs and reconciles missed counts via `drm_update_vblank_count()`. `drm_vblank_put()` schedules immediate, delayed, or no disable depending on `offdelay_ms` and `disable_immediate`. Interrupt handlers call `drm_handle_vblank()`, which locks `event_lock` and `vblank_time_lock`, updates count/time, wakes waiters, delivers queued events, runs vblank work, and possibly disables instant-off IRQs. Userspace waits convert relative/absolute requests to 64-bit sequences, optionally queue events, or block on the vblank waitqueue. Timer-backed vblank calls use an hrtimer to synthesize `drm_crtc_handle_vblank()`.

## State and Persistence
Counters are in-memory software counters that survive IRQ disable intervals by estimating missed vblanks using hardware counters or timestamps. Count/time snapshots are protected by a seqlock; enable/disable state and modeset gating are protected by `vbl_lock` and `vblank_time_lock`. Events persist on `dev->vblank_event_list` until delivered or prematurely flushed on CRTC disable. No on-disk persistence exists.

## Dependencies and Integration Points
Depends on DRM CRTC funcs (`enable_vblank`, `disable_vblank`, `get_vblank_counter`, `get_vblank_timestamp`), helper funcs (`get_scanout_position`, timer timeout handlers), atomic/modeset state, DRM leases, DRM event infrastructure, hrtimers, timers, waitqueues, and `drm_vblank_work.c`. Drivers must call `drm_crtc_handle_vblank()` from IRQs or use vblank timers.

## Risks
The risky areas are reference balancing between queued events/work and vblank IRQ refs, races around modeset disable/enable, hardware counter wrap/reset handling, timestamp precision failures, and hrtimer cancellation deadlocks. Incorrect driver hooks can create stale counts, duplicate events, or missed page-flip completion. `disable_immediate` requires race-free timestamping.

## Test Signals
Useful signals include vblank wait ioctl behavior, sequence ioctl event ordering, page-flip event timestamps, suspend/resume and modeset counter continuity, timer-backed virtual vblank operation, debug `DRM_UT_VBL` traces, lockdep, WARNs for invalid pipe/refcount state, and stress tests with rapid enable/disable plus queued events.
