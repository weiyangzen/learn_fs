# sources/distributed-fs/ceph-client/include/drm/drm_crtc_helper.h

Purpose: Declares the legacy DRM modesetting helper entry points used by drivers that rely on shared CRTC/encoder/connector helper code instead of hand-implementing all KMS transitions.

Important APIs, types, and functions: Exposes `drm_helper_disable_unused_functions()`, `drm_crtc_helper_set_config()`, `drm_crtc_helper_set_mode()`, `drm_crtc_helper_atomic_check()`, `drm_helper_crtc_in_use()`, `drm_helper_encoder_in_use()`, `drm_helper_connector_dpms()`, `drm_helper_resume_force_mode()`, and `drm_helper_force_disable_all()`. It forward-declares the KMS objects used by these helpers.

Control flow: Drivers route legacy `set_config` and DPMS paths into these helpers. The helpers evaluate whether CRTCs and encoders are in use, apply modes or disable unused functions, and provide resume/force-disable paths that restore or shut down display pipelines after suspend or error handling. Atomic-capable users can call the atomic check helper to validate a CRTC contribution in a shared path.

State and persistence: No state is stored in the header. Runtime effects occur in CRTC/encoder/connector state and hardware programmed by helper implementations.

Dependencies and integration points: Integrates with CRTC, encoder, connector, framebuffer, display mode, atomic state, and modeset acquire contexts. It exists for helper-based KMS drivers and legacy compatibility paths, often alongside `drm_crtc_funcs.set_config`.

Risks and test signals: Risks include mixing helper and driver-private modeset sequencing inconsistently, missing modeset acquire contexts, leaving unused encoders enabled, and resume paths restoring stale modes. Test legacy SETCRTC, connector DPMS, suspend/resume, forced global disable, and helper paths in drivers that also expose atomic APIs.
