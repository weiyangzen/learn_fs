# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-plane.c

## Purpose
Implements DCSS DRM plane objects and the atomic plane programming path. It validates formats, modifiers, rotation, cropping, source size, and scaling limits, then programs DPR addresses/format/rotation, scaler setup, DTG position/alpha, and channel enable state.

## Important APIs, types, and functions
- Format lists are `dcss_common_formats`, `dcss_video_format_modifiers`, and `dcss_graphics_format_modifiers`.
- Plane lifecycle uses `dcss_plane_init()`, `dcss_plane_destroy()`, and `dcss_plane_format_mod_supported()`.
- Atomic hooks are `dcss_plane_atomic_check()`, `dcss_plane_atomic_update()`, and `dcss_plane_atomic_disable()`.
- Helper logic includes `dcss_plane_can_rotate()`, `dcss_plane_is_source_size_allowed()`, `dcss_plane_atomic_set_base()`, and `dcss_plane_needs_setup()`.

## Control flow
Plane initialization chooses Vivante tiled/super-tiled modifiers only for the primary plane, registers the universal plane, adds immutable zpos, scaling-filter, and rotation properties, and maps `zpos` to the DCSS channel number.

Atomic check rejects too-small sources, invalid scaling ratios from `dcss_scaler_get_min_max_ratios()`, unsupported rotation/modifier combinations, non-linear cropped scanout, and invalid modifiers. Atomic update fast-paths pure base-address flips when the old framebuffer exists, no modeset is needed, and geometry/format/modifier/rotation/filter did not change. Full setup computes clipped source/destination sizes, normalizes overlay linear modifiers, programs DPR format/resolution/rotation/address, selects scaler filter, configures scaling with rotation-aware source dimensions, sets DTG position and alpha, and enables DPR/scaler/DTG channels unless channel 0 is fully transparent. Disable clears DPR, scaler, DTG position, and DTG channel enable for that hardware channel.

## State and persistence
Plane state is mostly DRM atomic state. The file persists only `dcss_plane->ch_num`; hardware state is persisted in DPR/scaler/DTG blocks and in DCSS context-loader queued writes. Base address programming uses DMA addresses from the current GEM DMA framebuffer and handles packed RGB, packed YUV, and NV12/NV21 secondary plane addresses.

## Dependencies and integration points
Depends on DRM atomic helpers, GEM DMA framebuffer helpers, DRM blend/scaling/rotation properties, and DCSS DPR/scaler/DTG APIs. It integrates with `dcss_kms.h` object definitions and assumes `plane->dev->dev_private` is the live `struct dcss_dev`.

## Risks
`dcss_plane_can_rotate()` checks `rotation & supported_rotation`, which accepts a request if any requested bit overlaps a supported bit; unexpected compound rotation/reflection combinations need coverage. Cropping is disallowed only for non-linear buffers, so linear address calculations must stay correct for subsampled formats. The primary plane's alpha-zero path disables channel 0 and clears its rectangle, which can interact with global alpha and z-order assumptions. Error unwinding in `dcss_plane_init()` returns after property creation failures without explicitly cleaning the initialized plane.

## Test signals
Validation should include primary tiled and super-tiled RGB, overlay linear RGB, invalid overlay tiled modifiers, NV12/NV21 and packed YUV source-size limits, rotation/reflection combinations, scaling limits per channel, fast page flips that only update base addresses, alpha-zero primary disable, and cropped linear versus cropped tiled framebuffers.
