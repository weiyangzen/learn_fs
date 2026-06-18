# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.c

## Purpose

`intel_alpm.c` implements DisplayPort/eDP Adaptive Link Power Management support, including AUX wake, AUX-less wake, Lunar Lake ALPM timing calculations, Panel Replay ALPM programming, Link Off Between Frames (LOBF) policy, sink DPCD enablement, debugfs controls, hardware disable, and ALPM error handling.

## Important APIs, Types, And Functions

Public entry points include `intel_alpm_init()`, `intel_alpm_aux_wake_supported()`, `intel_alpm_aux_less_wake_supported()`, `intel_alpm_is_alpm_aux_less()`, `intel_alpm_compute_params()`, `intel_alpm_lobf_compute_config()`, `intel_alpm_lobf_compute_config_late()`, `intel_alpm_lobf_min_guardband()`, `intel_alpm_configure()`, `intel_alpm_port_configure()`, `intel_alpm_enable_sink()`, `intel_alpm_lobf_enable()`, `intel_alpm_lobf_disable()`, `intel_alpm_lobf_debugfs_add()`, `intel_alpm_disable()`, and `intel_alpm_get_error()`. Internal timing helpers calculate silence period symbols, LFPS cycles, AUX-less wake time, fast wake lines, IO wake lines, and LOBF feasibility.

## Control Flow

Initialization creates `intel_dp->alpm.lock`. During atomic configuration, `intel_alpm_lobf_compute_config()` filters for eDP, Display version 20+, adaptive-sync SDP support, no PSR, fixed VRR timing, supported ALPM DPCD capabilities, and successful timing computation before setting `crtc_state->has_lobf`. A late LOBF check then verifies Window 1 and guardband/wake timing after other state fields such as VRR guardband and context latency are known. `intel_alpm_compute_params()` converts eDP spec timing, AUX precharge/preamble, PHY wake, fast wake, and LNL AUX-less timing into scanline counts stored in `crtc_state->alpm_state`.

Enable/configure flow writes sink DPCD `DP_RECEIVER_ALPM_CONFIG`, then writes transcoder `ALPM_CTL` and optional `PR_ALPM_CTL`, and writes port-level ALPM/LFPS registers for AUX-less mode. LOBF enable iterates encoders in the CRTC state and applies the eDP DP path. Disable clears ALPM/LOBF bits in the stored transcoder. Error handling reads `DP_RECEIVER_ALPM_STATUS`, logs lock timeout, clears the sink error bit by writing it back, and returns whether an error was observed.

## State And Persistence Behavior

Persistent software state lives in `intel_dp->alpm`: lock, selected transcoder, debug disable flag, and sink error state from surrounding code. Per-commit ALPM state lives in `crtc_state->alpm_state` and `crtc_state->has_lobf`. Hardware state persists in transcoder `ALPM_CTL`, `PR_ALPM_CTL`, port `PORT_ALPM_CTL`, `PORT_ALPM_LFPS_CTL`, and sink DPCD ALPM configuration/status registers until disabled or reprogrammed.

## Dependencies And Integration Points

The file integrates DP/eDP state, PSR and Panel Replay decisions, DP AUX helpers, VRR fixed-rate policy, CRTC timing conversion, display register access, DP DPCD constants, and connector debugfs. It is used by DP modeset and panel power flows rather than by standalone connector code.

## Risks And Edge Cases

ALPM timing is highly generation-specific. The LNL AUX-less path has several unit conversions from link rate, symbols, microseconds, nanoseconds, and scanlines; overflow or rounding mistakes can either disable ALPM unnecessarily or cause wake timing violations. A FIXME notes that LOBF guardband currently uses the max of IO and AUX-less wake lines because the exact applicable wake mode is not readily available. Debugfs can force LOBF off. `intel_alpm_disable()` relies on the last stored transcoder. DPCD read failures are treated as errors, and sink lock-timeout status is cleared by writing the read value back.

## Test Signals

Validation should cover eDP panels with AUX wake and AUX-less wake capabilities, Display version 20+ hardware, Panel Replay with ALPM, LOBF with fixed VRR timing, debugfs disable and info files, PSR exclusion, sink error injection, suspend/resume and modeset disable clearing registers, safest-params behavior, and DPCD traces confirming sink configuration.
