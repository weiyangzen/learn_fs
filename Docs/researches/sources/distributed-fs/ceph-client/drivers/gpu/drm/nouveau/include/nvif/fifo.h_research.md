# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/fifo.h

## Purpose
Declares FIFO runlist selection helpers.

## Important APIs, Types, And Functions
Exports `nvif_fifo_runlist()` and inline `nvif_fifo_runlist_ce()` which selects CE-capable runlists, excluding GRCE-only runlists when possible.

## Control Flow
`nvif_fifo_runlist_ce()` reads GR and CE runlist masks, removes GR overlap if independent CE runlists exist, and falls back to GR when only GRCE is available.

## State And Persistence
No state is stored; it queries cached device runlist information.

## Dependencies And Integration Points
Depends on `nvif/device.h` and `NV_DEVICE_HOST_RUNLIST_ENGINES_*` masks; integrated with channel/runlist selection for copy engines.

## Risks
Incorrect mask logic can route CE work to GR-only or unavailable runlists.

## Test Signals
Copy-engine channel allocation, multi-runlist hardware behavior, and runlist mask debug output validate it.
