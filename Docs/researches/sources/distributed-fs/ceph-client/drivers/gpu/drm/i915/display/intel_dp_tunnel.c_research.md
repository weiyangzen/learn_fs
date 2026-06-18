# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.c

## Purpose
Integrates DRM DisplayPort tunnel support with i915 DP connectors and atomic modesets. It detects DP tunnels, manages bandwidth allocation mode, accounts per-stream tunnel bandwidth, coordinates inherited bandwidth on already-active pipes, and allocates or reduces bandwidth during atomic commits.

## Important APIs, types, and functions
- Tunnel lifecycle: `intel_dp_tunnel_detect()`, `intel_dp_tunnel_disconnect()`, `intel_dp_tunnel_destroy()`, `intel_dp_tunnel_suspend()`, `intel_dp_tunnel_resume()`, `intel_dp_tunnel_bw_alloc_is_enabled()`.
- Atomic state helpers: `intel_dp_tunnel_atomic_cleanup_inherited_state()`, `intel_dp_tunnel_atomic_add_state_for_crtc()`, `intel_dp_tunnel_atomic_check_state()`, `intel_dp_tunnel_atomic_compute_stream_bw()`, `intel_dp_tunnel_atomic_clear_stream_bw()`, `intel_dp_tunnel_atomic_check_link()`, `intel_dp_tunnel_atomic_alloc_bw()`.
- Manager lifecycle: `intel_dp_tunnel_mgr_init()` and `intel_dp_tunnel_mgr_cleanup()`.
- Private state: `struct intel_dp_tunnel_inherited_state` stores per-pipe `drm_dp_tunnel_ref` entries for bandwidth inherited outside a normal atomic state.

## Control flow
Detection skips eDP. If a tunnel already exists, the code updates its state and reports whether effective link bandwidth changed; on update error it destroys and recreates the tunnel. New tunnel detection uses the display-wide tunnel manager, enables bandwidth allocation mode when supported, allocates bandwidth for any already-active pipes, updates sink caps, and returns `1` when userspace should be notified of mode-list-relevant bandwidth changes.

Suspend disables bandwidth allocation mode and marks the tunnel suspended. Resume may read DPRX caps only to satisfy the Thunderbolt connection manager without overwriting cached caps, re-enables bandwidth allocation, allocates bandwidth for the resumed pipe, and logs/drop-rejects on error. MST resume allocation is noted as TODO.

Atomic compute records each stream's required rate in the DRM tunnel state and takes a tunnel ref in the CRTC state. Clearing stream bandwidth writes zero for the pipe and releases the ref. Connector atomic checks add group state for old/new CRTCs and inherited tunnel state when a tunnel was detected after a stream was already active. Link checks call DRM tunnel bandwidth validation and, on ENOSPC, reduce i915 bpp limits and return `-EAGAIN` for recompute. Commit allocation first decreases bandwidth for modeset streams whose required bandwidth dropped, then increases bandwidth for new requirements and queues a modeset retry if allocation fails on a connected sink.

## State and persistence
Long-lived state includes `display->dp_tunnel_mgr`, `intel_dp->tunnel`, `intel_dp->tunnel_suspended`, and per-CRTC `dp_tunnel_ref`. Atomic-only state includes DRM tunnel state, stream required bandwidth per pipe, and `state->inherited_dp_tunnels` refs. Sink/tunnel bandwidth allocation state persists in the external tunnel manager/device until disabled or reallocated.

## Dependencies and integration points
Depends on DRM `drm_dp_tunnel` helpers, i915 atomic state, DP link training capability reads, MST active-pipe helpers, link bandwidth reduction, connector detection, suspend/resume, and display commit paths. Call sites include DP detection, SST/MST compute config, connector atomic checks, display atomic cleanup, CRTC add-state, link bandwidth validation, and commit bandwidth allocation.

## Risks
Bandwidth accounting must stay balanced across detection on active links, normal atomic modesets, failures, and cleanup. Missing inherited tunnel cleanup leaks refs or leaves bandwidth allocated. Resume currently allocates only a single SST pipe and explicitly lacks MST support. Returning `1` from detect affects userspace notification behavior, so false positives can cause unnecessary reprobes and false negatives can hide mode changes. Allocation failure after atomic check is handled by retry work, which depends on accurate connected-sink detection.

## Test signals
Signals include DPTUN debug logs for detection, state update, bandwidth changes, initial per-stream allocations, inherited tunnel state, required stream bandwidth, allocation failures, suspend/resume, and manager creation. Tests should cover tunnel hotplug, bandwidth allocation unsupported, active-stream detection, atomic bpp reduction on ENOSPC, suspend/resume, disconnect cleanup, SST and MST interactions, and mode-list updates after tunnel bandwidth changes.
