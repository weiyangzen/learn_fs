<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c

### Purpose
`lut.c` manages per-head output LUT backing memory and loading. It allocates double-buffered VRAM LUT storage and populates either userspace-provided gamma data or a generated identity ramp.

### Key APIs And Functions
`nv50_lut_init()` allocates and maps two `kmsLut` VRAM buffers sized for 257 or 1025 entries depending on display class. `nv50_lut_load()` selects a buffer, obtains blob data or creates a 1024-entry identity LUT, calls the generation-specific `load()` writer, and returns the GPU address. `nv50_lut_fini()` destroys both memory objects.

### Control Flow And State
LUT state persists in `struct nv50_lut.mem[2]`; common head atomic code toggles buffers to avoid overwriting an active LUT. Identity generation uses `kvmalloc_objs()` and fills a linear 16-bit ramp before invoking the hardware-specific loader.

### Dependencies And Integration
The file depends on DRM color management helpers, NVIF memory mapping, and `disp.h`. `head.c` allocates LUT memory during CRTC creation and loads it from `nv50_head_flush_set_wndw()`.

### Risks And Test Signals
Allocation failure, incorrect size selection, or identity-ramp generation problems affect gamma output. Tests should cover 257-entry old hardware, 1025-entry newer hardware, NULL gamma blob identity behavior, double-buffer flips, and cleanup on head creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c -->
