# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_plane.c

## Purpose
Implements MediaTek DRM plane state management, atomic validation/update/disable, cursor async update support, framebuffer DMA address derivation, AFBC address calculations, and plane property initialization.

## Important APIs, types, and functions
- `mtk_plane_init()` creates a universal plane with formats/modifiers, immutable zpos, optional rotation, alpha, and blend-mode properties.
- Custom plane funcs handle reset, duplicate/destroy state, modifier support, and atomic update helpers.
- `mtk_plane_update_new_state()` translates DRM plane state and framebuffer metadata into `mtk_plane_pending_state`.
- Async helpers `mtk_plane_atomic_async_check()` and `mtk_plane_atomic_async_update()` are for cursor updates.

## Control flow
Reset allocates or clears `struct mtk_plane_state`, initializes DRM state, and defaults pending format/modifier. Atomic check calls MediaTek CRTC plane validation and DRM helper no-scaling checks. Atomic update returns for no CRTC/fb, disables invisible planes, otherwise computes pending state from framebuffer DMA object, source crop, destination rectangle, rotation, modifier, format, pitch, and color encoding, then marks pending dirty. Disable marks pending disabled and calls CRTC plane disable for the old CRTC. Async update copies positional state into the live state, recomputes pending state, swaps framebuffer references, marks `async_dirty`, and calls `mtk_crtc_async_update()`.

## State and persistence
Persistent plane state is `struct mtk_plane_state`, whose `pending` sub-struct is the handoff to CRTC/component programming. It stores enable/config flags, DMA addresses, AFBC header address/pitch, pitch, format, modifier, position, dimensions, rotation, dirty flags, and color encoding. Hardware persistence happens later when CRTC code consumes pending state.

## Dependencies and integration points
Depends on DRM atomic, GEM DMA, framebuffer format/modifier metadata, blend/rotation helpers, MediaTek CRTC hooks, and AFBC layout constants from `mtk_plane.h`. It integrates with all MediaTek display components that consume `mtk_plane_state`.

## Risks
Only `DRM_FORMAT_MOD_LINEAR` is reported as supported by `mtk_plane_format_mod_supported()`, while AFBC calculations exist and `mtk_plane_init()` can pass modifier lists when `supports_afbc` is true; modifier policy should be checked with callers. Address arithmetic uses `int offset` before adding to `dma_addr_t`, which is guarded by comments but still sensitive to large dimensions. Async update is restricted to the CRTC cursor and existing framebuffer.

## Test signals
Signals include atomic check failures, cursor async movement, primary/overlay scanout, disable paths, zpos immutability, alpha/blend property behavior, rotation property creation, AFBC-capable caller behavior, and correct DMA offsets for cropped framebuffers.
