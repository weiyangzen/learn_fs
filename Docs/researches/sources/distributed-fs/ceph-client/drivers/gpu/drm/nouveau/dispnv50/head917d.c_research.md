<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c

### Purpose
`head917d.c` adapts the 907D head implementation for 917D-era hardware with updated dither/base/cursor methods and support for larger cursor layouts.

### Key APIs And Functions
`head917d_dither()` writes `NV917D HEAD_SET_DITHER_CONTROL`. `head917d_base()` programs base usage bounds and advertises 1025-entry base LUT usage. `head917d_curs_set()` writes cursor control, offset, and context DMA. `head917d_curs_layout()` accepts 32, 64, 128, and 256-pixel cursor widths. The exported `head917d` table otherwise reuses 907D view/mode/OLUT/core/overlay/procamp/output-resource callbacks.

### Control Flow And State
The wrapper preserves 907D timing and color behavior but adjusts method encodings for the newer class. Cursor layout is derived from framebuffer width rather than the parsed image width.

### Dependencies And Integration
It depends on `cl917d`, `push507c`, generic push helpers, and shared head/core declarations. It is selected for display classes that sit between 907D and C37D behavior.

### Risks And Test Signals
Cursor size support is broader and must match mode-config cursor limits. Tests should exercise 128/256 cursor images, base LUT usage with gamma, dither property changes, and modeset reuse of inherited 907D callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c -->
