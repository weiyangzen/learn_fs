# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_plane.c

## Purpose
Implements SH Mobile DRM plane objects for the Renesas shmobile LCDC driver. It creates DRM primary and overlay planes, validates atomic plane state, computes DMA scanout addresses for RGB and semi-planar YUV framebuffers, and programs LCDC primary/overlay registers through the register helpers in `shmob_drm_regs.h`.

## Important APIs, Types, And Functions
The private `struct shmob_drm_plane` embeds `struct drm_plane` plus a hardware plane index. `struct shmob_drm_plane_state` extends `drm_plane_state` with resolved `shmob_drm_format_info` and up to two DMA base addresses. `shmob_drm_plane_create()` is the exported constructor. Atomic hooks are `shmob_drm_plane_atomic_check()`, `shmob_drm_plane_atomic_update()`, `shmob_drm_plane_atomic_disable()`, plus custom reset/duplicate/destroy state functions.

## Control Flow
Plane creation allocates a universal plane with supported formats and attaches helper funcs. Atomic check clears invisible/disabled state, fetches the CRTC state, rejects scaling through `drm_atomic_helper_check_plane_state()`, resolves the SH Mobile format descriptor, and precomputes DMA bases. Atomic update programs either primary registers (`LDDFR`, `LDMLSR`, `LDDDSR`, `LDSA*R`, `LDRCNTR`) or overlay registers (`LDBn*`) depending on plane type. Overlay disable clears `LDBnBSIFR` and triggers bank update bits.

## State And Persistence
Persistent driver state is the plane object, its index, and the custom plane state allocated during reset. Hardware state is written directly to memory-mapped LCDC registers at commit time. DMA addresses are recomputed per atomic state and not persisted outside `shmob_drm_plane_state`.

## Dependencies And Integration Points
Depends on DRM atomic helpers, DMA framebuffer helpers, GEM DMA objects, `shmob_drm_format_info()`, and LCDC register helpers. Primary planes expose `get_scanout_buffer = drm_fb_dma_get_scanout_buffer`, integrating with DRM scanout buffer queries.

## Risks
YUV colorimetry is hardcoded to REC709. Scaling is forbidden. DMA address calculation assumes the fb plane layout and YUV subsampling rules match the local format table. Overlay alpha uses `state->alpha >> 8`; blend semantics depend on LCDC register interpretation.

## Test Signals
Useful signals include atomic plane format rejection, no-scaling rejection, primary RGB/YUV scanout, overlay enable/disable register traces, plane alpha behavior, and framebuffer offsets/pitches for cropped planes.
