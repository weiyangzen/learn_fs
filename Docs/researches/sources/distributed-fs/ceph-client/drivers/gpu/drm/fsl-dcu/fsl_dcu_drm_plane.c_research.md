<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c

## Purpose

This file implements FSL DCU primary-plane allocation, atomic plane validation, layer descriptor programming, and layer reset. It maps DRM framebuffer formats and plane state to DCU hardware layer descriptors.

## Important APIs, Types, And Functions

Important functions are `fsl_dcu_drm_plane_index()`, `fsl_dcu_drm_plane_atomic_check()`, `fsl_dcu_drm_plane_atomic_disable()`, `fsl_dcu_drm_plane_atomic_update()`, `fsl_dcu_drm_init_planes()`, and `fsl_dcu_drm_primary_create_plane()`. It defines DRM plane helper/functions and `fsl_dcu_drm_plane_formats` for RGB565, RGB888, XRGB/ARGB8888, XRGB/ARGB4444, XRGB/ARGB1555, and YUV422.

## Control Flow

Plane creation allocates a `struct drm_plane`, initializes it as a primary universal plane with possible CRTCs filled later, and adds helper callbacks. Atomic check accepts only the supported formats. Atomic update exits if no framebuffer, maps the DRM plane index to a DCU layer by reversing `total_layer - index - 1`, gets the DMA GEM object, converts the fourcc to a DCU BPP code and alpha mode, then writes descriptor registers for size, position, base DMA address, enable/BPP/alpha, chroma key min/max, tile, foreground/background, and LS1021A-specific skip values. Disable clears `DCU_LAYER_EN` in descriptor register 4. Plane initialization zeros every descriptor register for every hardware layer.

## State And Persistence

Layer descriptor registers are persistent hardware state. Atomic updates overwrite all descriptor fields used by this driver; disable only clears the enable bit, leaving most layer state intact. GEM DMA addresses are consumed directly by hardware. The layer index mapping means DRM plane ordering is inverted relative to DCU layer numbering.

## Dependencies And Integration Points

The file uses DRM atomic and plane helpers, DRM fourcc/framebuffer metadata, GEM DMA helpers, regmap, SoC layer counts from `fsl_dcu_drm_drv.h`, and `fsl_dcu_drm_crtc_create()` indirectly through primary plane creation.

## Risks And Test Signals

Risks include unchecked clipping/scaling constraints beyond format validation, using `plane->state->fb` while fetching `new_state`, DMA address width assumptions, format/alpha mismatches for XRGB versus ARGB variants, and layer register count differences. Test signals are atomic commits for all formats, plane disable/reenable, suspend/resume layer reset, out-of-range plane index logging, LS1021A register-10 programming, and framebuffer panning/position changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_plane.c -->
