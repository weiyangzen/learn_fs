<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c

### Purpose
`headc37d.c` implements Volta/Turing-style C37D head programming for static window-channel display hardware. It handles output resource, procamp, dither, cursor, output LUT, raster timing, viewport, and static window ownership.

### Key APIs And Functions
Important callbacks are `headc37d_view()`, `headc37d_curs_format()`, `headc37d_curs_set()`, `headc37d_curs_clr()`, `headc37d_dither()`, and `headc37d_static_wndw_map()`. Static helpers implement `headc37d_or()`, `headc37d_procamp()`, `headc37d_olut_*()`, `headc37d_olut()`, and `headc37d_mode()`. The `headc37d` table omits old core/base/overlay callbacks because newer window channels own scanout more directly.

### Control Flow And State
Static window mapping assigns two windows per head. Mode programming writes raster timing, raw sequence methods for interlace/blank2 fields, pixel clocks, and head usage bounds. OLUT accepts 256 or 1024 entries with unity range and interpolation, using `head907d_olut_load()`. Cursor programming writes control, composition, context DMA, and offset.

### Dependencies And Integration
It depends on `clc37d`, `pushc37b`, `atom.h`, `head.h`, and shared 907D helpers. `disp.c` calls `static_wndw_map` during atomic check when initial window assignment is required.

### Risks And Test Signals
Depth mapping contains a known hack translating older depth encodings. Raw `PUSH_NVSQ` methods and static two-window ownership are fragile. Tests should cover every head/window pair, 256/1024 LUTs, 256 cursor support, interlaced modes, DP depth variants, and initial modeset after firmware-provided state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c -->
