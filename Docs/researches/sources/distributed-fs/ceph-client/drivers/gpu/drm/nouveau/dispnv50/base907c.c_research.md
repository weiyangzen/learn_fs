<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c

## Purpose
This file implements GF110-era base channel image programming plus input LUT and color-space-conversion support for base planes.

## Important APIs, Types, and Functions
It defines `base907c_image_set`, LUT set/clear, `base907c_ilut`, `base907c_csc`, CSC set/clear, exported function table `base907c`, and `base907c_new`.

## Control Flow
Image set emits NV907C present control with timestamp disabled, context DMA, offsets, size, storage, and params. LUT set programs base LUT enable/mode/offset and routes output LUT to core LUT, while clear disables base/output LUTs and clears DMA LUT context. `base907c_ilut` selects interpolation mode by LUT size and sets the loader. CSC conversion maps DRM CTM S31.32 coefficients into 19-bit S3.16 two's-complement hardware fields, clamps out-of-range values, and stores a 3x4 matrix with zero offsets. CSC set emits ownership and matrix methods.

## State and Persistence Behavior
The file populates `nv50_wndw_atom` LUT and CSC fields during atomic check paths and programs persistent base channel LUT/CSC/image state during commit. It reuses notifier, semaphore, acquire/release, image clear, and update state from NV507C.

## Dependencies and Integration Points
It depends on `cl907c`, `head907d_olut_load`, DRM CTM format, NVIF push helpers, and shared base/window atomic state.

## Risks
Color conversion precision and clamping must match DRM expectations. LUT size assumptions choose between 257 and 1024 modes. CSC owner clear returns ownership to core; missing clear could leave stale plane CSC. Image method layout must match class-specific offsets.

## Test Signals
Atomic color-management tests for CTM and input LUT, C8 and true-color primary plane commits, LUT clear/set transitions, CSC identity and saturated coefficients, GF110 primary display, and class selection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c -->
