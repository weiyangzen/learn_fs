<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c

### Purpose
`head.c` implements the common DRM CRTC/head layer for NV50 display. It translates DRM atomic CRTC state into `nv50_head_atom`, validates color/scaler/dither/procamp/CRC state, flushes head programming through generation-specific callbacks, creates head planes, and handles vblank/CRC events.

### Key APIs And Functions
Public helpers are `nv50_head_create()`, `nv50_head_flush_set()`, `nv50_head_flush_set_wndw()`, and `nv50_head_flush_clr()`. Atomic helpers compute procamp, dither, viewport/scaler, LUT validity, hardware mode timing, and set/clr masks. DRM CRTC functions duplicate/destroy/reset state, expose vblank callbacks, and register CRC debugfs. `nv50_head_vblank_handler()` bridges NVIF vblank events to DRM and CRC handling.

### Control Flow And State
During atomic check, the file validates LUT sizes, handles output scaling/underscan/aspect/center modes, calculates hardware raster timing with interlace adjustments, derives set/clr masks by comparing old and new head atoms, and requests `disp->mutex` locking when head state changes. During commit, `disp.c` calls flush helpers that dispatch to the selected `nv50_head_func`. Creation selects old or CRC-capable CRTC funcs by display class, creates base/overlay/window/cursor planes, enables color management, allocates OLUT memory when needed, constructs an NVIF head object, and registers vblank events.

### Dependencies And Integration
The file depends on DRM atomic/vblank/color helpers, Nouveau connector/CRTC/display code, NVIF head/event APIs, and local base/core/curs/ovly/crc/lut modules. It is the central integration point between DRM CRTC state and generation files such as `head507d.c`, `head907d.c`, and `headc37d.c`.

### Risks And Test Signals
The set/clr mask logic controls hardware sequencing, so subtle comparisons can cause missed updates or unnecessary modesets. Risks include LUT stealing by indexed-color windows, cursor/core ordering constraints, scaler math edge cases, runtime-PM/vblank pairing, and CRC state transitions. Tests should cover modeset and fastset paths, gamma/degamma sizes, underscan/aspect scaling, cursor-only updates, base/overlay visibility changes, vblank events, and debugfs CRC hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c -->
