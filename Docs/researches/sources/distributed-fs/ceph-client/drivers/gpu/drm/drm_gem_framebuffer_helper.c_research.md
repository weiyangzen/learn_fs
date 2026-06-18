# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_framebuffer_helper.c

## Purpose
`drm_gem_framebuffer_helper.c` provides framebuffer helpers for drivers that use plain `struct drm_framebuffer` backed directly by GEM objects. It validates framebuffer BO sizes, initializes framebuffer objects, manages GEM references, exposes BO handle creation for GETFB, maps/unmaps framebuffer BOs for CPU access, synchronizes imported dma-bufs for CPU access, and validates AFBC layout size requirements.

## Important APIs, Types, And Functions
Core exports are `drm_gem_fb_get_obj()`, `drm_gem_fb_destroy()`, `drm_gem_fb_create_handle()`, `drm_gem_fb_init_with_funcs()`, `drm_gem_fb_create_with_funcs()`, `drm_gem_fb_create()`, `drm_gem_fb_create_with_dirty()`, `drm_gem_fb_vmap()`, `drm_gem_fb_vunmap()`, `drm_gem_fb_begin_cpu_access()`, `drm_gem_fb_end_cpu_access()`, and `drm_gem_fb_afbc_init()`. It also defines standard framebuffer funcs with optional dirty callback via `drm_atomic_helper_dirtyfb`.

## Control Flow
Framebuffer creation first checks atomic-driver format/modifier support, then looks up each GEM handle from the creating DRM file. For each format plane it computes plane-adjusted width and height, calculates the minimum byte size from pitch, min pitch, and offset, and rejects undersized GEM objects. Successful validation stores object references in `fb->obj[]` and calls `drm_framebuffer_init()`. Destruction drops each GEM reference, cleans up the framebuffer, and frees the struct. Vmap maps every backing object through `drm_gem_vmap()` and unwinds already mapped planes on failure; optional data pointers are derived by adding each plane offset. CPU access begin/end only calls dma-buf CPU access hooks for imported GEM objects. AFBC initialization decodes block size and tiled-header modifier bits, computes aligned dimensions, header size, body size, and rejects too-small backing objects.

## State And Persistence Behavior
The framebuffer holds one GEM reference per backing plane for its lifetime. `fb->obj[]`, pitches, offsets, modifiers, and format metadata form the persistent state consumed by atomic helpers and drivers. Vmap state is caller-owned through arrays of `struct iosys_map` and must be explicitly released. Dirty framebuffer support persists through the selected framebuffer funcs.

## Dependencies And Integration Points
This helper integrates with DRM format metadata, mode config `fb_create`, GEM handle lookup, GEM vmap/vunmap, dma-buf CPU access synchronization, atomic damage helper dirty handling, and AFBC modifier definitions. It is commonly paired with `drm_gem_atomic_helper.c` shadow-plane helpers and simple display drivers.

## Risks
Generic size validation may be insufficient for hardware-specific pitch, alignment, tiling, compression, or modifier constraints; drivers must validate those before or around these helpers. Integer overflow in size calculations would be high impact, so callers rely on prior mode validation and small typed fields. CPU access calls only cover imported BOs; native cache management remains object/driver-specific. AFBC bpp handling includes format-specific special cases and a TODO to replace it once format block info is complete.

## Test Signals
ADDFB2/GETFB tests should cover multi-plane formats, offsets, undersized BO rejection, unsupported format/modifier rejection, dirtyfb paths, vmap unwind on partial failure, imported dma-buf begin/end CPU access, and AFBC modifiers including invalid block sizes, tiled headers, and too-small buffers. IGT framebuffer and kms tests are the most relevant runtime signal.
