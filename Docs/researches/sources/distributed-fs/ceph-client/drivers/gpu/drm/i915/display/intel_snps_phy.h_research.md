# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy.h

## Purpose
`intel_snps_phy.h` declares the i915 Synopsys PHY and MPLLB functions used across display initialization, modeset, PSR, and state verification code.

## Important APIs, Types, And Functions
- Forward declarations: `enum phy`, `struct intel_atomic_state`, `struct intel_crtc`, `struct intel_crtc_state`, `struct intel_display`, `struct intel_encoder`, and `struct intel_mpllb_state`.
- PHY helpers: `intel_snps_phy_wait_for_calibration()`, `intel_snps_phy_update_psr_power_state()`, and `intel_snps_phy_set_signal_levels()`.
- MPLLB lifecycle: `intel_mpllb_calc_state()`, `intel_mpllb_enable()`, `intel_mpllb_disable()`, and `intel_mpllb_readout_hw_state()`.
- Clock/state helpers: `intel_mpllb_calc_port_clock()` and `intel_mpllb_state_verify()`.

## Control Flow
The header has no runtime control flow. It groups related SNPS PHY operations so platform and encoder code can call into the implementation without depending on table internals.

## State And Persistence
The header owns no state. The declared functions operate on display-global state, encoder/CRTC atomic state, hardware registers, and caller-provided MPLLB state structures.

## Dependencies And Integration Points
It depends on Linux integer types and i915 display type declarations. It is included by SNPS PHY implementation and by modeset/encoder code that needs PHY calibration, signal-level programming, MPLLB programming, or verification.

## Risks And Edge Cases
Callers must respect modeset ordering: calculate state before enable, do not readout into uninitialized storage assumptions, and call verification only when an active new encoder exists. The header does not encode platform constraints; incorrect calls on non-SNPS encoders must be guarded by callers or implementation checks.

## Test Signals
Compile-time coverage catches signature mismatches. Runtime coverage comes from SNPS PHY modeset tests, PSR power-state tests, and MPLLB state verification paths declared here.
