# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_alpm.h

## Purpose

`intel_alpm.h` declares the DisplayPort/eDP ALPM interface used by DP, PSR, Panel Replay, VRR, modeset, and debugfs code. It exposes capability checks, parameter computation, hardware programming, LOBF lifecycle, and error handling while keeping timing formulas in `intel_alpm.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_dp`, `struct intel_crtc_state`, `struct drm_connector_state`, `struct intel_connector`, `struct intel_atomic_state`, and `struct intel_crtc`. It declares capability helpers `intel_alpm_aux_wake_supported()`, `intel_alpm_aux_less_wake_supported()`, and `intel_alpm_is_alpm_aux_less()`, setup and computation functions `intel_alpm_init()`, `intel_alpm_compute_params()`, `intel_alpm_lobf_compute_config()`, `intel_alpm_lobf_compute_config_late()`, and `intel_alpm_lobf_min_guardband()`, programming functions `intel_alpm_configure()`, `intel_alpm_port_configure()`, `intel_alpm_enable_sink()`, `intel_alpm_lobf_enable()`, `intel_alpm_lobf_disable()`, and lifecycle/debug helpers `intel_alpm_lobf_debugfs_add()`, `intel_alpm_disable()`, and `intel_alpm_get_error()`.

## Control Flow

The header has no direct control flow. It allows the DP modeset path to compute ALPM/LOBF eligibility during atomic check, program sink and source registers during enable, clear state during disable, and expose connector debugfs files at registration time.

## State And Persistence Behavior

No state is stored in the header. The implementation updates `intel_dp->alpm`, `intel_crtc_state->alpm_state`, source ALPM registers, and sink DPCD state. Call order is important because late LOBF computation depends on values established by earlier atomic computations.

## Dependencies And Integration Points

The header depends on `<linux/types.h>` for `bool` and forward declarations for Intel display types. It integrates ALPM with DP/eDP code while avoiding direct register or DPCD helper exposure.

## Risks And Edge Cases

The API mixes early compute, late compute, enable, disable, and debug responsibilities, so call sites must preserve ordering. `intel_alpm_is_alpm_aux_less()` depends on both PSR needs and LOBF state, making stale `crtc_state` data a risk. Future non-eDP or non-LNL support would need careful API expansion because current implementation filters heavily by output type and display version.

## Test Signals

Build coverage, DP modeset call-order tests, debugfs registration on eDP only, ALPM sink error handling, and LOBF enable/disable sequencing are the relevant signals.
