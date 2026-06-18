# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.c

## Purpose

`armada_fb.c` implements Armada framebuffer object creation and maps DRM FourCC formats to Armada LCD hardware format/config bits.

## Important APIs, Types, And Functions

The exported functions are `armada_framebuffer_create()` and `armada_fb_create()`. `armada_fb_funcs` delegates destroy and handle creation to GEM framebuffer helpers. `armada_framebuffer_create()` fills `struct armada_framebuffer` with hardware `fmt` and `mod` values and initializes the DRM framebuffer. `armada_fb_create()` is the mode-config framebuffer creation callback.

## Control Flow

Framebuffer creation maps `mode->pixel_format` through a switch covering RGB, BGR, ARGB/ABGR, packed and planar YUV, and C8 formats. It allocates an Armada framebuffer wrapper, stores the GEM object in `fb.obj[0]`, fills DRM framebuffer fields, initializes the framebuffer, and takes a GEM reference for framebuffer lifetime. The user-facing create callback logs the request, requires all planes to use the same handle for multi-plane formats, looks up the GEM object, maps imported objects if needed, rejects objects without a scanout device address, delegates wrapper creation, and drops the lookup reference.

## State And Persistence Behavior

`struct armada_framebuffer` persists as a DRM framebuffer and stores hardware format/modifier config used by plane programming. It owns a reference on the underlying GEM object. No hardware registers are written here; state is consumed later by plane/CRTC code.

## Dependencies And Integration Points

The file depends on DRM framebuffer/GEM helper APIs, Armada GEM lookup/import mapping, Armada hardware format bits, and `struct armada_framebuffer` from `armada_fb.h`. It is registered via `armada_drm_mode_config_funcs` in `armada_drv.c`.

## Risks And Edge Cases

The implementation only handles single-handle multi-plane framebuffers, which restricts planar YUV layouts. Imported buffers must map to one contiguous DMA segment through `armada_gem_map_import()`. A framebuffer requires `obj->mapped` so it can be scanned out. Format mapping must remain synchronized with plane register programming and userspace expectations.

## Test Signals

Validation includes framebuffer creation for every supported FourCC, rejection of unsupported formats, multi-handle multi-plane rejection, imported contiguous dmabuf success and scattered import rejection, GEM reference lifetime tests, and scanout tests verifying channel order and YUV swap bits.
