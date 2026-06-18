
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimmc37b.c

## Purpose
Implements the C37B-style window immediate channel backend. It programs fast output-position changes and interlocks them with the main window channel.

## Important APIs, types, and functions
- `wimmc37b_point()` writes `NVC37B_SET_POINT_OUT(0)` from `asyw->point`.
- `wimmc37b_update()` emits `NVC37B_UPDATE` with optional interlock against the main window.
- `wimmc37b_init_()` creates the immediate DMA channel and installs the function table.
- `wimmc37b_init()` is the exported concrete initializer.
- `static const struct nv50_wimm_func wimmc37b` supplies `.point` and `.update`.

## Control flow
Initialization creates a display DMA channel for the same window id, without a sync offset, then records the immediate interlock bit and function table. At flush time, `nv50_wndw_flush_set()` writes a point update when only the output position changes or when point state is dirty, then kicks the immediate channel update.

## State and persistence
The backend persists `wndw->wimm` and `wndw->immd`. Hardware point-out state persists in the immediate channel until updated. Interlock flags coordinate visibility of WIMM and main window changes.

## Dependencies and integration points
Depends on `wimm.h`, `atom.h`, `wndw.h`, `nvif/if0014.h`, `nvif/pushc37b.h`, and `clc37b.h`. It integrates with the atomic plane position path and display interlock bookkeeping.

## Risks
Interlock mismatches can make position updates race with image updates. `PUSH_KICK()` failures propagate through update, so callers must handle atomic commit errors. Channel allocation failure blocks window creation.

## Test signals
Move-only atomic commits should update plane position without full image reprogramming. Interlock tests should verify no tearing or stale coordinates when image and point change together.
