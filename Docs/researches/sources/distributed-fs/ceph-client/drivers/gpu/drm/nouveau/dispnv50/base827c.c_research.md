<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c

## Purpose
This file adapts the base channel image programming for NV827C-class display hardware while reusing most NV507C base-plane behavior.

## Important APIs, Types, and Functions
It defines `base827c_image_set`, the `base827c` `nv50_wndw_func` table, and `base827c_new`.

## Control Flow
Image set emits NV827C methods for present control, context DMA ISO array, optional FP16 gain/offset processing, surface offsets, size, storage, and params. The function table reuses NV507C acquire/release, notifier, semaphore, LUT, image clear, and update helpers. Constructor delegates to `base507c_new_` with NV507C formats and NV827C image methods.

## State and Persistence Behavior
It programs persistent base channel image state in NV827C hardware and otherwise shares state behavior with `base507c.c`.

## Dependencies and Integration Points
It depends on `cl827c` method definitions, NVIF push helpers, and the common base helper ABI in `base.h`.

## Risks
NV827C context DMA and surface method layout differs from NV507C; using the wrong function table would corrupt channel methods. The same format table is assumed valid for the class. Pitch/block encoding must be class-compatible.

## Test Signals
Primary plane display on G82/GT200/GT214 classes, FP16 processing path, pitch and block layouts, notifier/semaphore behavior inherited from NV507C, and class selection through `nv50_base_new` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c -->
