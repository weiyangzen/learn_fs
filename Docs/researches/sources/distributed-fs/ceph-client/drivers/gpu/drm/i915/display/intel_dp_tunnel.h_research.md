# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.h

## Purpose
Declares the i915 DP tunnel integration API and provides no-op inline fallbacks when DP tunnel support is not built for the active driver configuration.

## Important APIs, types, and functions
- Feature gate: enabled when `CONFIG_DRM_I915_DP_TUNNEL` with `I915` or `CONFIG_DRM_XE_DP_TUNNEL` without `I915` is set.
- Declares tunnel detect/disconnect/destroy/suspend/resume, bandwidth-allocation query, inherited state cleanup, stream bandwidth compute/clear, CRTC and connector atomic state checks, atomic link check, bandwidth allocation, and manager lifecycle.
- Fallbacks return neutral success for atomic operations, false for bandwidth allocation enabled, `-EOPNOTSUPP` for detect, and no-op for cleanup/lifecycle functions.

## Control flow
The header's conditional compilation chooses either real declarations or inline stubs. The stubs let the rest of i915/Xe display code call tunnel hooks unconditionally without scattering feature checks.

## State and persistence
No state is defined in the header. Real implementation state lives in `intel_dp->tunnel`, display tunnel manager fields, atomic inherited tunnel refs, and CRTC tunnel refs. Stub builds store no tunnel state.

## Dependencies and integration points
Uses `linux/errno.h` and `linux/types.h`, plus forward declarations for DRM connector state, modeset acquire context, i915 atomic/CRTC/display/DP structures, encoders, and link bandwidth limits. Integrated by DP detect, DP/MST compute, atomic check/cleanup, commit allocation, and display manager init/cleanup.

## Risks
The fallback for `intel_dp_tunnel_atomic_alloc_bw()` is typed as `int` while the real function is `void`; callers that ignore the return value compile in practice, but signature consistency is worth watching. Feature-gate mistakes can silently disable tunnel behavior and leave only no-op atomic accounting. Real callers must tolerate `-EOPNOTSUPP` from detect.

## Test signals
Builds with tunnel support enabled should link against `intel_dp_tunnel.c`; disabled builds should compile through the stubs and behave as if no tunnel is present. Runtime tunnel tests should confirm detection returns `-EOPNOTSUPP` only in stubbed builds and that atomic hooks remain harmless when unsupported.
