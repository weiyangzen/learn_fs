# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pfit.h

Purpose: declares panel fitter compute, validation, programming, disable, and readout APIs.

Important APIs: `intel_pfit_compute_config()`, `intel_pfit_mode_valid()`, ILK/PCH enable-disable-readout, and i9xx/GMCH enable-disable-readout.

Control flow/state: no state; functions operate on `intel_crtc_state`, connector state, display, and display modes to store or apply pfit decisions.

Dependencies/integration: used by LVDS/eDP/CRTC modeset computation and enable/disable/readout paths.

Risks/test signals: signatures must stay aligned with CRTC state fields and scaler validation. Build coverage and scaling-mode tests catch regressions.
