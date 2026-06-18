
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wndwc67e.c

## Purpose
Implements the GA102/C67E window backend. It is a small variant of the C57E backend with adjusted image storage programming.

## Important APIs, types, and functions
- `wndwc67e_image_set()` writes NVC57E-compatible methods but omits the `MEMORY_LAYOUT` field from `SET_STORAGE`.
- `static const struct nv50_wndw_func wndwc67e` reuses C37E semaphore/notifier/blend/update and C57E ILUT/CSC callbacks.
- `wndwc67e_new()` delegates to `wndwc37e_new_()`.

## Control flow
Common window code computes the same `nv50_wndw_atom` image, LUT, CSC, blend, and point state. This backend emits the GA102-compatible image method sequence, then shared callbacks handle the rest.

## State and persistence
No private state exists beyond the common window object. Hardware surface, LUT, CSC, blend, notifier, and semaphore state persist in the display channel after emitted.

## Dependencies and integration points
Uses `wndw.h`, `atom.h`, `nvif/pushc37b.h`, and `clc57e.h`. It is selected for `GA102_DISP_WINDOW_CHANNEL_DMA`.

## Risks
Because the implementation uses C57E class macros, it assumes GA102's method layout is compatible except for storage fields. Advertising inherited format/modifier behavior must remain aligned with GA102 layout restrictions enforced in `wndw.c`.

## Test signals
GA102 primary/overlay flips in linear and block-linear layouts, ILUT/CSC updates, and move-only WIMM commits are the important checks.
