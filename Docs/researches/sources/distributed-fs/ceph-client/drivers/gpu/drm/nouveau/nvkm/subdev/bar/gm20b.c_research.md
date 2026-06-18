# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm20b.c

## Purpose
Implements GM20B BAR support as a GM107/GF100-derived BAR1-only, uncached-iomap variant.

## Important APIs, types, and functions
`gm20b_bar_new()` calls `gf100_bar_new_()` with a function table containing BAR1 init/wait/VMM and G84 flush, then sets `iomap_uncached`.

## Control flow, state, and persistence
BAR1 VMM setup and teardown are inherited from GF100. No BAR2 hooks are provided. The uncached mapping flag persists for CPU BAR access semantics.

## Dependencies and integration points
Depends on `gm107_bar_bar1_wait()`, GF100 helpers, and G84 flush. Used on Tegra GM20B devices.

## Risks and test signals
No BAR2 means callers must tolerate `nvkm_bar_bar2_vmm()` returning NULL. Signals include successful BAR1 mapping and correct uncached iomap behavior.
