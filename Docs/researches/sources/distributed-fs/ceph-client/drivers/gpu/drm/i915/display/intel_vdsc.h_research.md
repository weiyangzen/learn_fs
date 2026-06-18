# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.h

### Purpose
`intel_vdsc.h` declares the display-stream-compression interface used by display modeset, DP/DSI encoders, PSR, state dump, and clock/prefill code. It hides the PPS/register implementation in `intel_vdsc.c` while exposing the state transitions needed by the wider i915 display stack.

### Important APIs, Types, And Functions
The header forward-declares `intel_crtc_state`, `intel_display`, `intel_encoder`, `intel_dsb`, `intel_dsc_slice_config`, and related types. It exports capability helpers, slice configuration helpers, enable/disable hooks, PPS writers for DSI and DP, PSR selective-update parameter programming, state dump, min-CDCLK and prefill calculations, and `intel_dsc_get_pixel_rate_with_dsc_bubbles()`.

### Control Flow
Callers use this header during three phases: atomic check computes slice/PPS parameters, commit enables DSC or uncompressed joiners and sends link PPS, and modeset readback reconstructs active DSC configuration. Clock and guardband code call the exported min-CDCLK and prefill helpers after compression state has been chosen.

### State, Persistence, And Dependencies
The header owns no state. Its API operates on caller-owned `intel_crtc_state` and hardware state programmed by the implementation. It depends only on `linux/types.h` plus forward declarations, keeping compile-time coupling low.

### Integration Points
Primary users are `intel_dp`, `intel_dp_mst`, `intel_dsi`, `intel_psr`, `intel_crtc_state_dump`, clock calculation, and modeset setup/readout. The interface is the boundary between encoder policy and low-level VDSC register programming.

### Risks
The API assumes callers have already populated `crtc_state->dsc` consistently before enabling. Calling link PPS writers without `compression_enable` is harmless but means no PPS is emitted. Slice count and VDSC instance helpers depend on `slice_config` having been computed or read back first.

### Test Signals
Compile coverage across DP, MST, DSI, PSR, and display dump paths is important. Runtime signals include successful DSC mode enable/disable, PPS packet emission, readback state matching the atomic state, and min-CDCLK changes when DSC is active.
