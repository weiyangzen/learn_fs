# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/Kbuild

## Purpose
Lists PMU subdevice objects linked into NVKM, covering common PMU code, memory scripts, and generation-specific PMU backends.

## Important APIs, Types, And Functions
Declaratively adds `base.o`, `memx.o`, `gt215.o`, `gf100.o`, `gf119.o`, `gk104.o`, `gk110.o`, `gk208.o`, `gk20a.o`, `gm107.o`, `gm200.o`, `gm20b.o`, `gp102.o`, and `gp10b.o`.

## Control Flow
No runtime control flow exists.

## State And Persistence
No runtime state. Build membership persists via `nvkm-y`.

## Dependencies And Integration Points
Integrates with nouveau Kbuild and generation constructor tables that expect these PMU objects.

## Risks And Test Signals
Risk is missing PMU object linkage or stale object names after refactors. Test allmodconfig-style builds and unresolved PMU constructor/helper symbols.
