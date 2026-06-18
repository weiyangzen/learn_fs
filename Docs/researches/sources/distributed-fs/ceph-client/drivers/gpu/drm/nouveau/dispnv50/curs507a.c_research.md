<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c

### Purpose
`curs507a.c` implements the base NV50 cursor plane and immediate-channel behavior. It validates DRM cursor plane state, writes hotspot/update methods, and constructs the hardware cursor channel.

### Key APIs And Functions
`curs507a_space()` waits for immediate-channel FIFO space. `curs507a_update()` and `curs507a_point()` implement `nv50_wimm_func`. `curs507a_acquire()` validates no scaling, square cursor size, no framebuffer offsets, packed pitch, head-specific layout, and format. `curs507a_prepare()` tracks cursor BO handle/offset in head state and requests a core lock when the backing image changes. `curs507a_new_()` constructs the cursor plane/object; `curs507a_new()` supplies NV50 interlock data.

### Control Flow And State
Atomic acquire writes visibility and image metadata into `nv50_head_atom`. Prepare compares the current cursor handle/offset against the new state and sets `asyh->set.curs` as needed. Channel construction maps the NVIF object and stores the immediate function table in `wndw->immd`.

### Dependencies And Integration
The file depends on DRM atomic plane checks, fourcc formats, NVIF timers/channels, `cl507a`, `head.h`, and `core.h`. It integrates with head-specific cursor layout/format callbacks and with `head_flush_set_wndw()`.

### Risks And Test Signals
Cursor restrictions are strict and user-visible. Tests should cover 32/64-size cursors on old hardware, invalid pitch/offset/format, cursor BO changes without position changes, legacy cursor updates, and FIFO timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c -->
