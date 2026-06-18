# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.h

## Purpose
Declares the i915 DisplayPort MST interface used by DP initialization, atomic modeset code, link-bandwidth checks, tunnel integration, and stream mode computation.

## Important APIs, types, and functions
- Exposes MST encoder manager lifecycle, source-support query, active stream count, master/slave transcoder helpers, topology state addition, atomic link check, topology modeset need detection, probe preparation, DPCD state verification, and MTP/TU config computation.
- Forward declares i915 atomic, CRTC, digital port, DP, connector state, and link bandwidth structures.

## Control flow
No runtime control flow is implemented in the header. Callers use the declarations to enter MST setup, compute, and atomic validation paths implemented in `intel_dp_mst.c`.

## State and persistence
No state is stored here. The implementation operates on `intel_dp->mst`, DRM MST topology state, connector MST fields, and CRTC atomic state.

## Dependencies and integration points
The header is included by DP core, tunnel code, compliance test code, and display atomic/link bandwidth paths. It defines the local contract between generic DP code and MST-specific behavior.

## Risks
Because MST participates in atomic check and encoder lifecycle, API misuse can cause missing topology state, wrong bandwidth recomputation, or incorrect master transcoder logic. The exported `intel_dp_mtp_tu_compute_config()` is shared with SST-like MTP calculations, so callers must pass coherent bpp and DSC limits.

## Test signals
Build coverage catches signature drift. Runtime validation is through MST connector enumeration, atomic modeset success, bandwidth fallback, and master/slave transcoder behavior in the implementation.
