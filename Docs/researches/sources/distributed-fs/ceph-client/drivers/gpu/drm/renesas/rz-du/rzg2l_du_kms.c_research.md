# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.c

## Purpose

`rzg2l_du_kms.c` builds the RZ/G2L KMS topology and format/framebuffer policy. It defines supported framebuffer formats, validates framebuffer creation, initializes mode config, discovers VSPs and output encoders from DT, creates the CRTC, and assigns encoder routing masks.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_format_info()`, `rzg2l_du_dumb_create()`, and `rzg2l_du_modeset_init()`. Important internals are `rzg2l_du_fb_create()`, `rzg2l_du_encoders_init_one()`, `rzg2l_du_encoders_init()`, and `rzg2l_du_vsps_init()`.

## Control Flow

Modeset init creates mode config, sets size limits to 1920x1920, initializes vblank for available CRTCs, parses `renesas,vsps` to bind CRTC indices to VSP devices/pipes, initializes VSP planes, creates the CRTC, scans DT endpoints for outputs, maps endpoint ports to SoC routes, initializes encoders, errors if none are usable, assigns `possible_crtcs` and clone masks, resets mode config, and starts connector polling. Framebuffer creation rejects unsupported formats and pitches above the VSP 65535-byte limit. Dumb buffer creation aligns pitch to `16 * cpp`.

## State and Persistence Behavior

Supported format metadata is static. Runtime KMS state is stored in `rzg2l_du_device`, DRM mode_config, VSP objects, CRTC, planes, encoders, and connectors. DT node references acquired during VSP parsing are released in all exit paths.

## Dependencies and Integration Points

It depends on DRM atomic/GEM framebuffer/vblank helpers, OF graph/platform APIs, VSP1, local CRTC/encoder/VSP types, and V4L2 pixel format constants.

## Risks and Edge Cases

- `rzg2l_du_vsps_init()` computes `cells = ret / rcdu->num_crtcs - 1` without first checking `ret < 0`, so malformed/missing `renesas,vsps` can produce misleading results.
- The driver is currently sized for one CRTC/VSP; multi-CRTC hardware requires revisiting loops and arrays.
- Only the first pitch is validated; multi-plane pitch relationships are delegated to helpers/VSP behavior.
- Encoder probe deferral aborts the whole modeset init, while other encoder failures are skipped.

## Test Signals

Test all supported formats, invalid pitches, DT endpoint route matching, missing/disabled remote endpoints, absent encoders, VSP phandle parsing errors, and boot to fbdev on each supported SoC.
