<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h

## Purpose
This header declares NV50 base channel constructors and shared base-plane helper functions.

## Important APIs, Types, and Functions
It declares `base507c_new`, `base507c_new_`, `base507c_format`, base acquire/release, semaphore and LUT helpers, generation constructors `base827c_new`, `base907c_new`, `base917c_new`, exported function table `base907c`, and public factory `nv50_base_new`.

## Control Flow
There is no standalone flow. The declarations let newer class files reuse the NV507C constructor and helper methods while substituting class-specific image/LUT/CSC emitters and format lists.

## State and Persistence Behavior
No state is stored in the header. The declared functions operate on `struct nv50_wndw`, `struct nv50_wndw_atom`, and `struct nv50_head_atom` atomic/display state.

## Dependencies and Integration Points
It includes `wndw.h` and is consumed by `base.c` and all generation-specific base channel files.

## Risks
Function signatures must stay synchronized with `struct nv50_wndw_func` expectations. Exporting `base907c` for reuse by `base917c` couples newer formats to GF110-era methods.

## Test Signals
Build coverage across all base class files and runtime primary-plane programming on each supported display class validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h -->
