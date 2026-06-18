# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_color_mgmt.c

## Purpose
`drm_color_mgmt.c` implements DRM color-management helpers for CRTC degamma/CTM/gamma properties, legacy gamma ioctls, plane color encoding/range properties, LUT validation, and common gamma/palette programming helpers.

## Important APIs, Types, And Functions
Important APIs include `drm_color_ctm_s31_32_to_qm_n()`, `drm_crtc_enable_color_mgmt()`, `drm_mode_crtc_set_gamma_size()`, `drm_mode_gamma_set_ioctl()`, `drm_mode_gamma_get_ioctl()`, `drm_plane_create_color_properties()`, `drm_color_lut_check()`, `drm_color_lut32_check()`, gamma load/fill helpers for 888/565/555, and palette helpers for C8/RGB332.

## Control Flow
Drivers attach CRTC color properties through `drm_crtc_enable_color_mgmt()`. Legacy gamma setup allocates three contiguous `u16` tables and initializes a linear ramp. Gamma set ioctl validates support and size, copies user tables into `gamma_store`, and either calls the legacy `gamma_set` hook or creates a LUT blob and atomic state mapping to `GAMMA_LUT` or `DEGAMMA_LUT` while clearing CTM. Gamma get ioctl copies the store back to userspace. Plane property creation validates bitmasks, creates enum properties, attaches defaults, and initializes existing plane state.

## State And Persistence
State includes attached DRM properties, `crtc->gamma_size`, `crtc->gamma_store`, CRTC color blob pointers in atomic state, and plane state color encoding/range defaults. Property blobs are DRM-refcounted. No disk persistence exists.

## Dependencies And Integration Points
It integrates with DRM properties/blobs, atomic state/commit, modeset locks, user copy, CRTC/plane initialization, KUnit-visible helpers, framebuffer format color paths, and driver hardware LUT callbacks.

## Risks And Edge Cases
Legacy-to-atomic gamma must balance blob refs and locks correctly. User copy can fail with `-EFAULT`. CTM conversion warns rather than rejects unsupported precision. Plane color property creation can leave partial state on second-property failure. `fill_gamma_555()` appears to use `r >> 4` in blue expansion, which should be checked against expected `b >> 4`.

## Test Signals
Use KUnit/IGT coverage for CTM conversion, encoding/range names, LUT validation, gamma set/get faults, blob refcounts, plane property defaults, and golden output values for gamma/palette fill/load helpers.
