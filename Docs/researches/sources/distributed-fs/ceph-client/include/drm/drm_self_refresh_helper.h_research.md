# sources/distributed-fs/ceph-client/include/drm/drm_self_refresh_helper.h

## Purpose
`drm_self_refresh_helper.h` declares helpers for panel self-refresh / display self-refresh support in atomic KMS drivers.

## Important APIs, types, and functions
APIs are `drm_self_refresh_helper_alter_state`, `drm_self_refresh_helper_update_avg_times`, `drm_self_refresh_helper_init`, and `drm_self_refresh_helper_cleanup`. They operate on `struct drm_atomic_state` and `struct drm_crtc`.

## Control flow
Drivers initialize helper state for a CRTC, then atomic commit paths call `alter_state` to adjust commits for self-refresh transitions and `update_avg_times` with commit duration and the new self-refresh mask. Cleanup removes helper state on CRTC teardown.

## State and persistence
The header owns no direct fields, but the implementation maintains runtime helper state associated with the CRTC, including timing averages used to decide self-refresh behavior. No persistent storage is involved.

## Dependencies and integration points
It integrates with atomic state management, CRTC power sequencing, panels that support self-refresh, and commit timing heuristics.

## Risks and test signals
Risks include entering self-refresh while updates are pending, stale timing averages, missing cleanup, incorrect mask handling across multiple CRTCs, and power-saving transitions that break visible updates. Test signals include PSR/self-refresh entry and exit, atomic commits with and without damage, multi-CRTC commits, suspend/resume, commit-time accounting, and helper cleanup during driver unload.
