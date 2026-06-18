# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.h

### Purpose
`intel_vrr.h` declares the VRR interface shared by connector capability checks, atomic modeset computation, transcoder programming, DSB update paths, PSR integration, vblank timing code, and state readback.

### Important APIs, Types, And Functions
The header exports capability/range helpers, atomic modeset change detection, configuration/guardband computation, hardware timing programming, enable/disable hooks, DSB push send/check, DC-balance helpers, fixed-RR detection/programming, readback, safe-window timing, and DCB vblank-start query helpers.

### Control Flow
Callers use these APIs in order: check connector/mode capability, compute VRR state during atomic check, compute guardband after other timing/prefill inputs are known, program transcoder timing, enable VRR/DCB during commit, send pushes for latency-sensitive updates, and read back state during modeset setup or verification.

### State, Persistence, And Dependencies
The header owns no state. It operates on `intel_crtc_state`, `intel_connector`, `intel_atomic_state`, `intel_dsb`, and `intel_display` objects whose state is persisted by `intel_vrr.c` into transcoder and DMC registers. Dependency footprint is intentionally small: `linux/types.h` plus forward declarations.

### Integration Points
Users include DP/MST, vblank, DSB, color, PSR, display state dump, and modeset readout. The safe-window and DCB helpers are especially tied to DSB/vblank scheduling.

### Risks
APIs such as `intel_vrr_vmin_vblank_start()` assume `crtc_state->vrr.guardband` has already been computed. Push helpers must be used only where delayed vblank ordering is respected. DCB helpers require hardware support and a valid live VRR configuration.

### Test Signals
Build coverage across all display modules, VRR atomic transitions setting mode-changed, vblank helper correctness, DSB push polling, PSR frame-change programming, and readback matching programmed fixed-RR/VRR state are useful.
