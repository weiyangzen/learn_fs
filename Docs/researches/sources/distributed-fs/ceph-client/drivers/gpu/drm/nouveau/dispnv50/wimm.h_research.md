
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.h

## Purpose
Declares the window immediate-channel initialization APIs used by `wndw.c`.

## Important APIs, types, and functions
- `nv50_wimm_init(struct nouveau_drm *drm, struct nv50_wndw *)`.
- `wimmc37b_init(struct nouveau_drm *, s32, struct nv50_wndw *)`.
- Includes `wndw.h` so callers see `struct nv50_wndw`.

## Control flow
No runtime control flow exists. It exposes the class selector and the concrete C37B initializer.

## State and persistence
No state is defined here. Implementations mutate `struct nv50_wndw` by creating the WIMM DMA channel and assigning the `nv50_wimm_func` table.

## Dependencies and integration points
This header is the narrow bridge between generic window creation and immediate-channel backends.

## Risks
Because it includes `wndw.h`, include-order or circular dependency changes require care. Signature drift would fail at build time.

## Test signals
Compile coverage is the primary signal. Runtime coverage comes from successful `nv50_wimm_init()` during window creation.
