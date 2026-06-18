# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_tunnel.h

Purpose: helper interface for DisplayPort tunneling over USB4-style transport, including tunnel detection, bandwidth allocation, IRQ handling, reference tracking, atomic stream bandwidth state, and manager lifecycle.

Important APIs/types/functions: `struct drm_dp_tunnel_ref`, opaque tunnel/manager/state types, get/put/ref wrappers, detect/destroy, enable/disable bandwidth allocation, allocate/get/update bandwidth, set I/O error, IRQ handling, max DPRX rate/lane count, available bandwidth, name lookup, atomic state getters, stream bandwidth setters, group stream queries, bandwidth checks, required bandwidth, and manager create/destroy. Disabled builds return `-EOPNOTSUPP` or safe sentinel stubs.

Control flow: drivers create a tunnel manager, detect tunnels through AUX, enable bandwidth allocation, handle tunnel IRQs, assign per-stream bandwidth in atomic state, validate aggregate bandwidth, and commit allocation requests.

State and persistence: tunnel lifetime is reference-tracked with optional ref trackers. Runtime state lives in opaque tunnel objects and DPCD tunnel registers; allocations are runtime transport state.

Dependencies and integration points: DRM devices, DP AUX, DRM atomic state, error pointers, ref tracking, DP tunneling DPCD constants, USB4 bandwidth allocation, and display atomic validation.

Risks and test signals: leaked refs, unsupported stubs hiding missing Kconfig, stale I/O-error state, bandwidth unit mismatches, and stream-mask mismatch are risks. Test enabled/disabled builds, detect/destroy, IRQ events, allocation success/failure, multi-stream checks, teardown with live refs, and max rate/lane reporting.
