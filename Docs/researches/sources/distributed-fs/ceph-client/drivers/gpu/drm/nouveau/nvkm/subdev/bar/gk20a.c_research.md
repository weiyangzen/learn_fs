# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gk20a.c

## Purpose
Implements GK20A BAR support as a GF100-derived BAR1-only, uncached-iomap variant.

## Important APIs, types, and functions
`gk20a_bar_new()` calls `gf100_bar_new_()` with a function table that omits BAR2 hooks and sets `(*pbar)->iomap_uncached = true` on success.

## Control flow, state, and persistence
Oneinit creates only BAR1 state through shared GF100 helpers. The uncached iomap flag persists on the BAR object for mapping behavior.

## Dependencies and integration points
Depends on GF100 BAR helpers and G84 flush. Used on Tegra GK20A-class devices.

## Risks and test signals
BAR2 is intentionally absent. Signals include successful BAR1 VMM creation and correct uncached CPU mapping behavior.
