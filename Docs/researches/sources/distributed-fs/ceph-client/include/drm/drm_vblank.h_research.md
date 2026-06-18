# sources/distributed-fs/ceph-client/include/drm/drm_vblank.h

## Purpose
`drm_vblank.h` declares DRM vertical blanking tracking, event delivery, timestamping, interrupt reference counting, vblank timers, and delayed vblank work infrastructure per CRTC.

## Important APIs, types, and functions
Key types are `struct drm_pending_vblank_event`, `struct drm_vblank_crtc_config`, `struct drm_vblank_crtc_timer`, and `struct drm_vblank_crtc`. Runtime fields track wait queues, disable timer, seqlock-protected count/time, refcount, wraparound data, max counter, modeset state, pipe, timing constants, cached hardware mode, config, enabled state, kthread worker, pending vblank work, and high-resolution timer. APIs include `drm_vblank_init`, `drm_dev_has_vblank`, `drm_crtc_vblank_count`, `drm_crtc_vblank_count_and_time`, event send/arm/set helpers, `drm_handle_vblank`, `drm_crtc_handle_vblank`, get/put/wait/off/on/reset/restore helpers, timestamping constants, waitqueue access, max counter setup, timer start/cancel/timeout, and helper timestamp functions.

## Control flow
Drivers initialize vblank tracking for CRTCs, enable vblank interrupts when users/events need them, call handle-vblank from IRQs, and release references after waits/events. Counts and timestamps are updated under seqlock with ordering guarantees. Off/on paths preserve counts across modesets. Timer paths can emulate or predict vblank timing where appropriate.

## State and persistence
All state is runtime per-CRTC tracking. Counters and timestamps persist while the DRM device is active but reset across driver unload. Refcounts govern whether hardware vblank interrupts remain enabled.

## Dependencies and integration points
It depends on seqlocks, hrtimers, IDR/poll/kthreads, DRM files/events, display modes, CRTC funcs, and vblank work. It integrates with page flips, atomic commits, legacy wait-vblank IOCTLs, event delivery, timestamp helpers, and hot modesets.

## Risks and test signals
Risks include refcount leaks disabling or keeping IRQs on, counter wraparound errors, timestamp inaccuracies, event sequence races, modeset off/on count loss, missing barriers around count/time, and timer interval drift. Test signals include vblank IRQ handling, page-flip event sequences, wait-vblank IOCTLs, counter wraparound, modeset disable/enable, timer-backed vblank, timestamp max-error validation, and vblank reference leak tests.
