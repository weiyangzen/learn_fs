<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c

### Purpose
`ovly507e.c` implements the base NV50 overlay DMA plane. It validates overlay plane state, programs image and scaling methods, and constructs the overlay DMA channel with notifier/semaphore offsets.

### Key APIs And Functions
`ovly507e_scale_set()` writes source point, input size, and output width. `ovly507e_image_set()` writes present control, ISO context, composition mode, surface offset/size/storage/params. `ovly507e_acquire()` validates no scaling via DRM helpers and stores bytes-per-pixel in head overlay state. `ovly507e_release()` clears overlay cpp. `ovly507e_new_()` constructs the DRM overlay plane and DMA channel; `ovly507e_new()` supplies NV50 formats and interlock data.

### Control Flow And State
Acquire/release update `asyh->ovly.cpp`, which common head code turns into usage-bound updates. Image and scale programming write into the overlay DMA push buffer; update and notifier callbacks are inherited from base channel helpers. The constructed window stores `ntfy`, `sema`, and initial notifier data offsets.

### Dependencies And Integration
It depends on DRM atomic/fourcc helpers, `cl507e`, `if0014`, `push507c`, `atom.h`, `ovly.h`, and `nv50_dmac_create()`. `ovly.c` selects it for NV50 overlay class support.

### Risks And Test Signals
Surface storage programming includes pitch/block fields and a duplicated `PITCH` macro use for blocks, so format/layout tests matter. Tests should cover supported YUYV/UYVY/XRGB formats, overlay enable/disable, notifier completion, no-scaling validation, and semaphore offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c -->
