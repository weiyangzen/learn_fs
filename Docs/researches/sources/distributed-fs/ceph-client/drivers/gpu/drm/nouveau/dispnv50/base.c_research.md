<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c

## Purpose
This file selects and creates the per-head NV50 base display channel, which backs primary planes on pre-window-display hardware generations.

## Important APIs, Types, and Functions
`nv50_base_new` is the public factory. It contains a class table mapping supported display base DMA channel classes to `base507c_new`, `base827c_new`, `base907c_new`, or `base917c_new`.

## Control Flow
The factory asks `nvif_mclass` to select the best supported class from the display object. If no class matches, it logs an error and returns the negative code. Otherwise, it dispatches to the selected generation constructor with the DRM device, head index, object class, and output window pointer.

## State and Persistence Behavior
This file does not store state itself. The selected constructor allocates and initializes `struct nv50_wndw` and its DMA channel.

## Dependencies and Integration Points
It depends on `nv50_disp(drm->dev)->disp->object`, NVIF class matching, and generation-specific base constructors declared in `base.h`.

## Risks
Class ordering determines preference; a wrong order can choose an older implementation on newer hardware. Unsupported classes fail primary plane creation. Constructor function-table compatibility must match the chosen class.

## Test Signals
Runtime initialization on NV50, G82/GT200/GT214, GF110, GK104/GK110, and newer supported GPUs; forced class-match failure; and primary plane creation per head are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c -->
