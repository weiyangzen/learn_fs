# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm.h

Purpose: shared Hyper-V DRM private header. It defines device-private state and prototypes for modeset and VMBus protocol operations.

Important APIs/types: `struct hyperv_drm_device` embeds DRM device, plane, CRTC, encoder, connector, mode limits, preferred mode, depth, VRAM resource/mapping/base/size, VMBus wait completion, negotiated protocol version, MMIO size, dirt flag, fixed init/receive buffers, and `hv_device`. `to_hv()` converts DRM device to private state. Protocol function prototypes cover VRAM location, situation update, pointer hide, dirty rect, and VSP connect.

Control flow: `hyperv_drm_drv.c` allocates this structure and initializes protocol/VRAM/modeset; modeset and protocol files share it through `hv_get_drvdata()` and `to_hv()`.

State and persistence: contains all runtime state for the synthetic video device. No disk persistence.

Dependencies and integration points: requires DRM object types through including C files and Hyper-V types for `struct hv_device`. Integrates VMBus protocol state with DRM KMS objects.

Risks: fixed 16 KiB buffers must cover all in-band messages. Completion and shared init buffer require single outstanding synchronous protocol transaction. `dirt_needed` gates dirty-rect notifications.

Test signals: VSP negotiation, resolution query, VRAM map, atomic updates, suspend/resume, dirty notification, and remove/unplug paths.
