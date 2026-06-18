# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc.c

### Purpose
`intel_vdsc.c` implements Intel display-stream-compression source programming. It validates DSC availability, derives slice layout and PPS/rate-control parameters, writes PPS and RC registers for one or more VDSC engines, enables compressed or uncompressed joiner paths, emits DP/DSI PPS packets, reads hardware state back into `intel_crtc_state`, and contributes CDCLK/prefill constraints.

### Important APIs, Types, And Functions
Public entry points include `intel_dsc_source_support()`, `intel_dsc_get_slice_config()`, `intel_dsc_compute_params()`, `intel_dsc_enable_on_crtc()`, `intel_dsc_enabled_on_link()`, `intel_dsc_power_domain()`, `intel_dsc_get_num_vdsc_instances()`, `intel_dsc_dsi_pps_write()`, `intel_dsc_dp_pps_write()`, `intel_dsc_su_et_parameters_configure()`, `intel_uncompressed_joiner_enable()`, `intel_dsc_enable()`, `intel_dsc_disable()`, `intel_dsc_get_config()`, `intel_vdsc_state_dump()`, and `intel_vdsc_min_cdclk()`. Internal helpers compute RC tables, PPS register addresses, and DSS control register selection.

### Control Flow
Atomic check code first marks compression enabled and calls `intel_dsc_compute_params()`, which sets picture/slice dimensions, validates slice constraints, derives color format flags, chooses DSC 1.1/1.2 rate-control setup or local interpolation for Xe_LPD+, and computes mux/scale fields. Commit programming calls `intel_dsc_pps_configure()` to write PPS 0-10, 16, and MTL+ PPS 17/18, then writes RC threshold/range arrays to the proper pipe/transcoder engine registers. `intel_dsc_enable()` sets DSS bits for VDSC0/1/2, small joiner, bigjoiner, or ultrajoiner; disable clears DSS controls. Readback obtains the right power domain, reads DSS state, infers streams per pipe, verifies replicated PPS values, and reconstructs `drm_dsc_config`.

### State, Persistence, And Dependencies
Runtime state is held in `intel_crtc_state->dsc` and persisted to display engine MMIO registers for the active pipe/transcoder. Link-side PPS is persisted in DP SDP or DSI commands. Dependencies include DRM DSC helpers, fixed-point helpers, QP lookup tables, DP/DSI encoder helpers, power-domain helpers, `intel_de` MMIO accessors, and register definitions from `intel_vdsc_regs.h`.

### Integration Points
DP, eDP, DSI, MST, PSR selective update, bigjoiner/ultrajoiner, CDCLK calculation, state dump, and modeset readback all consume this module. `intel_bios.c` seeds slice capabilities from VBT, DP code writes PPS infoframes, DSI code sends MIPI compression mode, and PSR uses SU parameter programming.

### Risks
Slice layout is constrained by hardware engine count, joined-pipe topology, and format-specific DSC spec limits; mistakes can produce invalid PPS or underrun. PPS replication must target all active VDSC engines, including BMG DSC2. Native 4:2:0 doubles bpp internally and must be undone on readback. Power-domain selection differs for ICL eDP/DSI and Gen12 pipe A. Joiner and DSC enable sequencing is sensitive because DSS bits define pipe combining.

### Test Signals
High-value tests are modeset bring-up with single, dual, triple-engine and joined-pipe DSC; RGB, YCbCr444, and native 420; DP PPS SDP capture; DSI PPS command validation; suspend/resume readback; CDCLK minimum checks; PSR SU updates; and negative checks for invalid slice dimensions or unsupported pipe/transcoder combinations.
