
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.c

## Purpose
Implements the common NV50+ DRM plane/window core for Nouveau display. It handles DRM plane lifecycle, atomic checking, framebuffer pinning, context DMA creation, LUT/CSC/blend/image state derivation, panic scanout mapping, format modifier validation, and generation-specific window class selection.

## Important APIs, types, and functions
- Context DMA helpers: `nv50_wndw_ctxdma_new()` and `nv50_wndw_ctxdma_del()`.
- Flush helpers: `nv50_wndw_flush_set()`, `nv50_wndw_flush_clr()`, `nv50_wndw_ntfy_enable()`, and `nv50_wndw_wait_armed()`.
- Atomic helpers: `nv50_wndw_atomic_check()`, `nv50_wndw_atomic_check_acquire()`, `nv50_wndw_atomic_check_lut()`, release/acquire RGB/YUV format mapping helpers.
- FB lifecycle: `nv50_wndw_prepare_fb()` pins BOs and sets image handles/offsets; `nv50_wndw_cleanup_fb()` unpins.
- DRM panic helpers: `nv50_wndw_get_scanout_buffer()`, `nv50_set_pixel()`, and `nv50_set_pixel_swizzle()`.
- Plane lifecycle: `nv50_wndw_reset()`, duplicate/destroy-state, `nv50_wndw_destroy()`, and `const struct drm_plane_funcs nv50_wndw`.
- Creation APIs: `nv50_wndw_new_()` and `nv50_wndw_new()`.

## Control flow
Plane creation picks the newest supported window class from GB202, GA102, TU102, and GV100, calls the generation-specific constructor, then initializes WIMM. The generic constructor allocates the DRM plane, installs helper funcs, creates LUT storage for windows with ILUT support, and exposes zpos/alpha/blend properties when hardware blending is available.

During atomic check, the code fetches new and old CRTC/head atoms, decides visibility, recalculates LUT/CSC when needed, and either acquires or releases hardware window state. Acquire maps DRM formats to display formats, derives pitch or block-linear storage parameters, chooses non-tearing versus immediate present mode from async flip state, computes scaling/blending/point dirty state, and delegates class-specific validation. Release clears handles and asks the backend to release resources. Modesets and disables mark old notifier, semaphore, LUT, CSC, and image state for clearing.

During prepare, the framebuffer BO is pinned to VRAM, a matching context DMA is created or reused for pre-Blackwell hardware, a fake enable handle is used for Blackwell's physical-address path, GEM plane preparation runs, and the scanout offset is recorded. Flush code then calls class-specific clear/set callbacks and updates display interlocks. Point-only changes are routed through the WIMM immediate channel.

## State and persistence
Persistent state lives in `struct nv50_wndw`: function pointers, window id, interlock data, context DMA object list, DRM plane, LUT allocation, main/WIMM DMA channels, notifier offsets, semaphore offsets, and cached data. Atomic state persists in `struct nv50_wndw_atom` fields copied by duplicate-state. Hardware state persists in display window methods until explicit clear or reprogram. Framebuffer BO pinning persists from prepare to cleanup.

## Dependencies and integration points
Depends on DRM atomic, blend, framebuffer, GEM plane helper, panic, and TTM mapping APIs; Nouveau BO/GEM/framebuffer helpers; NVIF DMA object creation; display interlocks; `tile.h`; generation backends `wndwc37e`, `wndwc57e`, `wndwc67e`, and `wndwca7e`; and WIMM initialization. It is the central integration point between DRM plane state and Nouveau display hardware channels.

## Risks
This file is high risk. Incorrect atomic dirty tracking can leave stale LUT/CSC/image state. Context DMA handle reuse is keyed by framebuffer kind, so layout extraction must be accurate. BO pin/unpin error paths must stay balanced; note that failures after `drm_gem_plane_helper_prepare_fb()` or backend `prepare()` rely on DRM cleanup behavior. Format modifier validation differs by chipset and can accidentally expose unsupported block-linear layouts. Panic scanout only supports single-plane uncompressed buffers and limited tiled 32-bit formats. The assignment inside `if (asyw->set.point = false, asyw->set.mask)` is intentional comma-expression clearing but easy to misread.

## Test signals
Useful signals include DRM atomic logs (`NV_ATOMIC`), successful plane creation per generation, primary/overlay/cursor flips, async flips, C8 legacy gamma behavior, degamma/CTM updates, zpos/alpha/blend modes, tiled and linear scanout, panic text rendering, modifier acceptance tests, BO pin leak checks, and WIMM move-only commits.
