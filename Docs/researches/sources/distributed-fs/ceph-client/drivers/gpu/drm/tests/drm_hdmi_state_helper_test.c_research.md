# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_hdmi_state_helper_test.c

## Purpose
KUnit coverage for the DRM HDMI connector state helpers. The file builds a mock atomic DRM pipeline with one primary plane, one CRTC, one TMDS encoder, and one HDMI connector, then verifies HDMI atomic check, reset defaults, mode validation, and InfoFrame programming behavior across DVI, HDMI, RGB, YUV, deep-color, HDR, and constrained-TMDS scenarios.

## Important APIs, Types, And Functions
The central fixture is `struct drm_atomic_helper_connector_hdmi_priv`, embedding `struct drm_device`, `drm_encoder`, `drm_connector`, current EDID storage, and an `hdmi_update_failures` counter. `__connector_hdmi_init()` allocates the KUnit device/DRM device, creates a primary plane and CRTC through `drm_kunit_helpers`, initializes an HDMI connector with `drmm_connector_hdmi_init()`, attaches the encoder, resets mode config, and optionally loads EDID. `dummy_connector_get_modes()` turns the current raw EDID into `display_info` and connector modes through `drm_edid_connector_update()` and `drm_edid_connector_add_modes()`. `test_encoder_atomic_enable()` exercises `drm_atomic_helper_connector_hdmi_update_infoframes()`.

## Control Flow
Most tests initialize the fixture with driver-supported output formats and a max BPC, find a preferred or CEA VIC mode, enable the connector with `drm_kunit_helper_enable_crtc_connector()`, then allocate an atomic state and run `drm_atomic_check_only()` or `drm_atomic_commit()`. Repeated `retry_*` labels handle `-EDEADLK` by clearing/backing off the modeset context. Check-suite cases validate broadcast RGB mode-change propagation and quantization, BPC and format selection, TMDS rate fallback, YUV420-only failures, DVI fallback, and connector disable. Reset-suite cases validate initial HDMI state values before atomic check fills computed fields. Mode-valid tests exercise default acceptance, hook-based rejection, total rejection, and EDID max-TMDS filtering. InfoFrame tests commit modesets with accept/reject HDMI callbacks and check whether failure counts change.

## State And Persistence
State is all in-memory KUnit/DRM state: connector EDID bytes, parsed `display_info`, mode lists, connector atomic HDMI fields (`broadcast_rgb`, `output_bpc`, `output_format`, `tmds_char_rate`, `is_limited_range`, InfoFrame state), CRTC `mode_changed`, and the fixture failure counter. No persistent storage is used. KUnit actions clean up DRM devices, atomic states, and display modes.

## Dependencies And Integration Points
This file integrates DRM atomic helpers, EDID parsing, HDMI state helpers, HDMI InfoFrame helpers, connector properties, mode validation, and the shared `drm_kunit_helpers` fixture layer. Test inputs come from `drm_kunit_edid.h`. It is sensitive to DRM mode constants, CEA VIC matching, HDMI Forum/CTA EDID interpretation, and `drmm_connector_hdmi_init()` property setup.

## Risks And Maintenance Notes
The largest risk is semantic drift in HDMI helper policy: output-format preference, RGB quantization rules, deep-color fallback order, max-TMDS filtering, or HDR property gating changes will require expected values to be updated. Many tests manually mutate atomic state and connector callback pointers, so they intentionally bypass normal driver layering. The `-EDEADLK` retry loops are necessary but verbose; missing a clear/backoff path could create flakes. EDID fixture changes can alter preferred mode ordering, `is_hdmi`, max TMDS, HDR property exposure, and 4:2:0-only decisions.

## Test Signals
Passing signals include expected BPC/format/TMDS rates, correct limited/full RGB decisions for auto/full/limited modes, `mode_changed` only when HDMI state changes require it, rejected modes disappearing from `connector->modes`, failed YUV420-only commits when the driver lacks YUV420, reset defaults of zero computed HDMI fields, and InfoFrame update failure counters changing only for programmed failing frames.
