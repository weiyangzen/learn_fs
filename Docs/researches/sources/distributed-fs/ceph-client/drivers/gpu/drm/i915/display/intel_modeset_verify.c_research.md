# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_verify.c

Purpose: high-level display state verification after modeset/fastset activity. It cross-checks atomic software state, legacy connector/encoder links, hardware readout, DPLL state, PHY state, FDI dotclock assumptions, and watermark state.

Important functions: `intel_modeset_verify_crtc()` runs verification when a CRTC needs modeset or fastset. `intel_modeset_verify_disabled()` checks disabled encoders/connectors and DPLLs. Helpers include `verify_crtc_state()`, `verify_encoder_state()`, `verify_connector_state()`, `intel_connector_verify_state()`, and `intel_pipe_config_sanity_check()`.

Control flow: CRTC verification first verifies watermark state, then connector state for connectors targeting that CRTC, allocates a temporary CRTC state, reads hardware pipe config, compares active bits, checks encoder hardware state and pipe ownership, reads encoder config into the temporary state, runs FDI sanity, compares pipe config, dumps mismatched states, then verifies DPLL/MPLLB state. Disabled verification scans all encoders and connectors with old/new connector states and confirms no detached encoder is still enabled.

State and persistence: it should not persistently program hardware except through helper verification side effects; it allocates and destroys temporary CRTC state. It emits WARN-style diagnostics via `INTEL_DISPLAY_STATE_WARN()` and debug logs.

Dependencies/integration: depends on atomic state helpers, CRTC state allocation/readout/compare/dump, connector/encoder hooks, FDI link frequency, DPLL/MPLLB verification, and watermark verification.

Risks/test signals: false positives are possible where hardware readout is incomplete or platform exceptions exist, while false negatives hide state corruption. Exercise modeset, fastset, disabled encoder, PCH FDI, MST/non-MST, and PHY-specific paths with debug state checks enabled; look for `pipe state doesn't match`, encoder pipe mismatch, connector active/crtc mismatch, and DPLL verification warnings.
