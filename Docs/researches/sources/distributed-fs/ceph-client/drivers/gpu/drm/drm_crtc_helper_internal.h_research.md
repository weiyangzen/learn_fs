# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_crtc_helper_internal.h

Purpose: Private header for the DRM KMS helper module. It exposes only internal helper-layer prototypes shared between legacy CRTC helpers and probe helpers; these interfaces are not exported to drivers.

Important APIs/types/functions: Declares opaque structs and `drm_crtc_mode_valid`, `drm_encoder_mode_valid`, `drm_connector_mode_valid`, and `drm_connector_get_single_encoder`. The mode-validation functions are implemented in probe-helper code, while `drm_connector_get_single_encoder` is implemented in `drm_crtc_helper.c`.

Control flow: There is no runtime control flow in the header. It defines the compile-time coupling that lets helper code validate a mode against CRTC, encoder, and connector callbacks and lets probe/configuration code fetch the sole possible encoder when a connector does not need a `best_encoder` policy.

State and persistence behavior: No state is stored here. The declarations operate on caller-owned DRM connector, encoder, CRTC, display mode, and modeset acquire context objects.

Dependencies and integration points: Integrates the legacy/helper KMS module with `drm_probe_helper.c` and `drm_crtc_helper.c`. It forward-declares only the types required by these internal prototypes, keeping the include boundary small.

Risks: Because this is an internal header, signature drift must be kept synchronized across helper C files. `drm_connector_get_single_encoder` is only correct for connectors with one possible encoder and warns when that assumption is violated.

Test signals: Build coverage is the main signal. Functional coverage comes from mode-probe validation tests and legacy set_config paths that use connector mode validation and single-encoder fallback.
