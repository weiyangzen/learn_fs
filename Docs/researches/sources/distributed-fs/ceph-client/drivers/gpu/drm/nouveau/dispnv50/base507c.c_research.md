<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c

## Purpose
This file implements the NV507C base channel methods and shared helper logic reused by later base channel classes.

## Important APIs, Types, and Functions
Important functions include `base507c_update`, image set/clear, LUT set/clear, notifier reset/set/clear/wait, semaphore set/clear, `base507c_acquire`, `base507c_release`, `base507c_new_`, and `base507c_new`. It exports `base507c_format` and defines the `base507c` `nv50_wndw_func` table.

## Control Flow
Acquire validates primary plane state with no scaling, updates head base metadata from framebuffer format and source coordinates, and marks color management changed when 8bpp behavior crosses LUT ownership rules. Image set emits present control, DMA ISO context, FP16 processing conversion, offset, size, storage, and format methods. Update emits the core interlock and kicks the push buffer. Constructor creates a DRM primary window, then allocates a display DMA channel with notifier/semaphore offsets and interlock data.

## State and Persistence Behavior
The functions mutate atomic head base fields, window notifier/semaphore handles, DMA push channel state, and hardware base channel methods. The active image, context DMA, LUT mode, notifier, and semaphore settings persist in the display channel until changed or cleared.

## Dependencies and Integration Points
It depends on NVIF push macros, class `cl507c`, `nv50_wndw_new_`, `nv50_dmac_create`, BO notifier access macros, DRM framebuffer formats, and `nv50_disp` sync BO layout.

## Risks
Offsets are shifted by hardware-specific granularity (`>> 8`), so alignment is critical. Storage pitch/block fields share method encoding and must match layout. Notifier waits have a 2-second timeout. FP16 processing special-case must match class format IDs. Constructor error paths leave partial `nv50_wndw` allocation to outer cleanup.

## Test Signals
Primary plane commits for every listed format, pitch and block-linear layouts, notifier/semaphore synchronization, page flips with interlock, LUT ownership changes for C8, FP16 framebuffer display, and channel allocation failure injection are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c -->
