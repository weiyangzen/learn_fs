<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h

### Purpose
`handles.h` centralizes Nouveau-chosen display object handles for sync buffers, VRAM contexts, window contexts, and CRC notifier contexts.

### Key APIs And Macros
It defines `NV50_DISP_HANDLE_SYNCBUF`, `NV50_DISP_HANDLE_VRAM`, `NV50_DISP_HANDLE_WNDW_CTX(kind)`, and `NV50_DISP_HANDLE_CRC_CTX(head, i)`.

### Control Flow And State
The header has no runtime logic. The constants become persistent object identifiers passed to NVIF object constructors. On Blackwell paths without CTXDMAs, fake handles preserve nonzero-handle enable checks in existing code.

### Dependencies And Integration
`disp.c` uses sync/VRAM handles for DMA channel context objects, window code uses window context handles, and `crc.c` uses CRC context handles for per-head notifier DMA objects.

### Risks And Test Signals
Uniqueness is the key invariant. Handle collision would bind methods to the wrong object. Tests should cover simultaneous window and CRC context creation, multi-head CRC setup, and Blackwell paths that rely on fake handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h -->
