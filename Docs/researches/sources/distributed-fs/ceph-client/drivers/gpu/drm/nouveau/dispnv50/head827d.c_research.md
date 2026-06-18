<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c

### Purpose
`head827d.c` adapts the 507D head table for 827D-era hardware, mainly by adding explicit CTXDMA programming for cursor, core, and LUT resources and using updated method names.

### Key APIs And Functions
Static helpers implement `head827d_curs_clr()`, `head827d_curs_set()`, `head827d_core_set()`, `head827d_olut_clr()`, and `head827d_olut_set()`. The exported `head827d` table reuses 507D view/mode/core-calc/layout/format/base/overlay/dither/procamp logic while replacing the resource-binding callbacks.

### Control Flow And State
Cursor set writes control, offset, and cursor context DMA; clear disables and clears the context. Core set writes offset, size, storage, params, context DMA, and viewport point. OLUT set enables the LUT and binds `HEAD_SET_CONTEXT_DMA_LUT`; clear disables and clears the context. Runtime state remains in `nv50_head_atom`.

### Dependencies And Integration
It depends on `cl827d`, `push507c`, `head.h`, and `core.h`. It is selected by generation-specific core tables for display classes that need 827D resource methods.

### Risks And Test Signals
Handle programming is the key difference from 507D; stale or missing context DMA handles can produce blank scanout, cursor, or LUT output. Tests should cover gamma updates, cursor image changes, framebuffer format changes, and disable/re-enable on 827D-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c -->
