# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/skl_prefill.h

### Purpose
`skl_prefill.h` declares the fixed-point prefill context and APIs used to estimate display pipeline prefill latency, guardband needs, and minimum CDCLK.

### Important APIs, Types, And Functions
`struct skl_prefill_ctx` stores `.16` scanline prefill components (`fixed`, `wm0`, `scaler_1st`, `scaler_2nd`, `dsc`, `full`) and `.16` adjustment factors (`cdclk`, `scaler_1st`, `scaler_2nd`). The public APIs initialize normal or worst-case contexts, check vblank sufficiency, compute minimum guardband, and compute minimum CDCLK.

### Control Flow
Callers initialize a context from an `intel_crtc_state`, then pass it with a latency value to guardband/vblank checks or to the CDCLK helper. Worst-case initialization is used when scaler assignment or latency may not yet be finalized.

### State, Persistence, And Dependencies
The context is transient stack/caller state; it is not persisted. The header depends only on Linux types and an `intel_crtc_state` forward declaration.

### Integration Points
Used by VRR guardband computation and CDCLK/watermark paths that need a shared prefill estimate. Its structure is filled by `skl_prefill.c` using VDSC, scaler, watermark, and CDCLK modules.

### Risks
Fields are fixed-point scanlines and factors, not raw integers; external callers should treat the struct as produced by the init functions. Adding new pipeline stages requires updating both normal and worst-case initialization.

### Test Signals
Compile coverage for VRR/CDCLK users and runtime checks showing guardband/min-CDCLK changes when watermarks, scalers, DSC, or CDCLK constraints change are useful.
