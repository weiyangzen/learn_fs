<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c

### Purpose
`head507d.c` implements the NV507D base head programming table for early NV50 display hardware. It writes raster timing, viewport scaler, core/base/overlay usage, cursor, output LUT, dither, and procamp methods.

### Key APIs And Functions
Exported helpers include `head507d_view()`, `head507d_mode()`, `head507d_olut()`, `head507d_core_calc()`, `head507d_core_clr()`, `head507d_curs_layout()`, `head507d_curs_format()`, `head507d_base()`, `head507d_ovly()`, `head507d_dither()`, and `head507d_procamp()`. Static helpers implement cursor set/clr, core set, and OLUT set/clr/load. The `head507d` table wires all callbacks.

### Control Flow And State
`head507d_core_calc()` derives a dummy or real core surface from base/overlay/cursor visibility and writes pitch-linear A8R8G8B8 defaults. Cursor programming accepts ARGB8888 and 32/64 layouts. OLUT supports 256-entry LUTs and appends a duplicate final entry for interpolation. Mode programming converts `nv50_head_mode` timing into `HEAD_SET_*` methods.

### Dependencies And Integration
It depends on `cl507d`, `push507c`, `head.h`, and `core.h`. Common `head.c` computes atom state and calls this table for old display classes.

### Risks And Test Signals
The core dummy-surface workaround, cursor/core ordering note, and 256-entry-only OLUT are important constraints. Tests should cover old NV50 modesets with base-only, overlay-only, cursor-only, gamma LUT, dither/procamp changes, and 32/64 cursor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c -->
