# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crtc.h

## Purpose
Declares the i915 CRTC interface used by display initialization, atomic commit, vblank management, event delivery, and bandwidth calculations.

## Important APIs and integration
The header exposes scanline/time conversion helpers, vblank event helpers, max counter/query/on/off/wait functions, CRTC initialization and state allocation/reset, pipe update start/end, worker flush, CRTC lookup helpers, active/enable change detection, and bandwidth helpers. It also defines `VBLANK_EVASION_TIME_US`, widened when lock proving is enabled.

## State, dependencies, risks, and tests
The header owns no state but exposes functions that mutate CRTC state, vblank refs, event pointers, worker state, and pipe update timing. Risks are incorrect call ordering around `intel_pipe_update_start/end()` and vblank work flushing. Build coverage plus atomic/vblank/flip tests exercise the API contract.
