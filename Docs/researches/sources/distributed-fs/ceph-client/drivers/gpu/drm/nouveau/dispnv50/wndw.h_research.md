
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndw.h

## Purpose
Declares the common Nouveau NV50+ display window structures, callback interfaces, helper APIs, and generation-specific constructors.

## Important APIs, types, and functions
- `struct nv50_wndw_ctxdma` stores a context DMA object in a per-window list.
- `struct nv50_wndw` embeds the DRM plane plus display DMA channels, interlock state, LUT storage, notification/semaphore offsets, and callback pointers.
- `struct nv50_wndw_func` describes class-specific acquire/release, prepare, semaphore, notifier, LUT, CSC, image, scale, blend, and update operations.
- `struct nv50_wimm_func` describes immediate-channel point and update operations.
- Declares shared helpers such as `nv50_wndw_new_()`, `nv50_wndw_flush_set()`, `nv50_wndw_flush_clr()`, `nv50_wndw_ntfy_enable()`, and `nv50_wndw_wait_armed()`.
- Declares generation constructors and callbacks for C37E, C57E, C67E, CA7E, and generic `nv50_wndw_new()`.
- Inline `nvif_chan_wait()` adapts WIMM channel space checks to the NVIF push path.

## Control flow
The header has only the `nvif_chan_wait()` inline branch: it returns success when `curs507a_space(wndw)` reports room and `-ETIMEDOUT` otherwise. Runtime control flow is provided by implementations through the callback tables.

## State and persistence
The header defines the layout of persistent window state and the callback contract for hardware state programming. Atomic per-commit state is referenced through `struct nv50_wndw_atom` from `atom.h`.

## Dependencies and integration points
Includes `disp.h`, `atom.h`, and `lut.h`; exports `const struct drm_plane_funcs nv50_wndw`; and bridges common window code, cursor/immediate helpers, and class-specific files.

## Risks
The callback table is broad, so missing callbacks must be matched by checks in common code. Structure layout changes affect every generation backend. The WIMM wait helper is specialized around cursor space logic and should not be generalized without auditing push semantics.

## Test signals
Compile coverage across all window backends is the first signal. Runtime signals are successful plane creation, callback dispatch, WIMM point updates, and no null callback dereferences in atomic commits.
