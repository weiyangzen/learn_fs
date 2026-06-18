
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/wimm.c

## Purpose
Selects and initializes the display window immediate channel used to move a window's output point independently from the main window DMA channel.

## Important APIs, types, and functions
- `nv50_wimm_init()` selects among GB202, GA102, TU102, and GV100 `DISP_WINDOW_IMM_CHANNEL_DMA` classes.
- The local `wimms[]` table maps all supported immediate channel classes to `wimmc37b_init()`.

## Control flow
At the end of `nv50_wndw_new()`, the display code calls `nv50_wimm_init()`. It asks `nvif_mclass()` which immediate class the display object supports, reports an error if none match, and invokes the selected initializer.

## State and persistence
No persistent state is stored in this file. The selected initializer creates `wndw->wimm`, fills `wndw->immd`, and configures immediate interlock state.

## Dependencies and integration points
Depends on `wimm.h` and `nvif/class.h`. It is tightly integrated with `wndw.c` window creation and `nv50_wndw_flush_set()`, which calls `wndw->immd->point()` and `update()` when plane position changes.

## Risks
Failure to allocate a WIMM channel makes window creation fail even if the main window channel exists. The class table assumes all listed hardware generations can use the C37B-style implementation.

## Test signals
Plane creation on GV100, TU102, GA102, and GB202 classes should allocate immediate channels. Moving a visible plane without changing its image should exercise WIMM point updates.
