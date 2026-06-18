# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr.c

### Purpose
`intel_vrr.c` implements Intel Variable Refresh Rate, fixed-refresh use of the VRR timing generator, dormant CMRR support, VRR guardband computation, DSB push sequencing, PSR frame-change integration, DC-balance firmware programming, and hardware state readback.

### Important APIs, Types, And Functions
Public APIs include capability/range checks, `intel_vrr_compute_config()`, `intel_vrr_compute_guardband()`, timing accessors, fixed-RR programming, transcoder timing enable/disable, VRR enable/disable, push send/check helpers, DC-balance reset/increment helpers, readback, safe-window helpers, and DCB live/final vblank-start helpers. Internal helpers compute vmin/vmax, guardband limits, optimized prefill-based guardband, hardware-adjusted vmin/vmax/flipline, and DCB parameter sets.

### Control Flow
Atomic check first verifies connector and mode eligibility: DP/eDP only, no MST, Ignore MSA DPCD support, monitor range > 10 Hz, no interlace, and VBT VRR bit for eDP. It computes `vmin` from current vtotal and `vmax` from minimum monitor refresh, enables true VRR only when userspace requested it and range permits, otherwise programs fixed refresh through the same timing registers. Guardband computation uses prefill worst-case latency plus PSR/SDP/ALPM minima, capped by hardware and vblank limits. Commit writes transcoder timing registers after `TRANS_DDI_FUNC_CTL`, arms push support, writes AS SDP timing, enables DCB when configured, and enables/disables the VRR timing generator depending on platform generation.

### State, Persistence, And Dependencies
State lives in `intel_crtc_state->vrr`, `->cmrr`, mode flags, live `intel_crtc->dc_balance.flip_count`, and MMIO registers such as `TRANS_VRR_CTL`, `TRANS_VRR_VMIN/VMAX/FLIPLINE`, `TRANS_PUSH`, DCB registers, and CMRR M/N registers. Dependencies include DP DPCD helpers, PSR, ALPM, DMC/PIPEDMC, DSB, vblank timing, watermark latency, prefill, and `intel_vrr_regs.h`.

### Integration Points
The module is called from DP/MST modeset compute and enable paths, vblank timestamp/window logic, DSB waits, color commits, PSR frame change handling, state dumps, and DMC DC-balance event configuration. `skl_prefill` and watermark data feed optimized guardband selection.

### Risks
VRR timing is extremely sequencing-sensitive: programming before the transcoder is ready can hang ICL, push-send must clear before delayed vblank assumptions are used, and Gen12/13 chicken bits have platform-specific meanings. Guardband must not exceed vblank space or hardware field width. Always-use-VRR-TG platforms overwrite adjusted vblank timing, so readback must reconstruct mode values carefully. DC-balance is limited to PIPE A/B and depends on firmware/DMC behavior. CMRR is compiled but intentionally disabled by an unconditional false path.

### Test Signals
Signals include DP/eDP VRR enablement, fixed-RR fallback, vblank timestamp correctness at min/max refresh, DSB/color update push completion, PSR coexistence, DC-balance register programming on supported pipes, suspend/resume readback, and negative tests for MST/interlace/unsupported DPCD/monitor-range cases.
