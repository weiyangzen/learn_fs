## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.c

### Purpose

`mtk_crtc.c` implements MediaTek DRM CRTC objects over DDP component pipelines. It creates planes from component capabilities, powers/clocks and connects DDP paths, coordinates mutex/MMSYS routing, applies modes and plane updates, supports CMDQ-assisted register programming, handles vblank/page-flip completion, and exposes color management through gamma/CTM components.

### Important APIs, types, and functions

Main state is `struct mtk_crtc` and `struct mtk_crtc_state`. Public functions include `mtk_crtc_create()`, `mtk_crtc_plane_check()`, `mtk_crtc_plane_disable()`, `mtk_crtc_async_update()`, `mtk_crtc_dma_dev_get()`, and `mtk_ddp_comp_for_plane()` inside the file. DRM hooks cover reset/duplicate/destroy state, mode validation/fixup/set, atomic begin/flush/enable/disable, vblank enable/disable, and CRTC destroy.

### Control flow

Creation validates that every path component exists, allocates the CRTC and DDP component array, gets a display mutex, registers vblank callbacks, counts component planes, creates DRM planes, initializes the CRTC, enables color management if gamma/CTM components are present, and optionally creates a CMDQ mailbox packet. Atomic enable powers the first component, updates connector-dependent route tail, initializes hardware by resuming runtime PM, preparing the mutex, enabling component clocks, connecting components through component hooks or MMSYS fallback, adding them to the mutex, enabling the mutex, configuring/starting all components, and programming initial disabled plane state. Flush marks dirty plane/config state, programs directly or builds CMDQ commands, and defers completion to vblank/CMDQ callbacks. Atomic disable disables all planes, waits for CMDQ/vblank, shuts off vblank, stops components, removes/disconnects routes, disables clocks/mutex/runtime PM, and powers off.

### State and persistence behavior

Software state includes pending config dimensions, pending plane flags, event pointer, enabled state, CMDQ packet/vblank timeout counters, locks, component path, connector routes, and DMA device. Hardware state persists in DDP component registers, MMSYS routes, display mutex membership, clocks, and power domains until disable or suspend.

### Dependencies

It depends on DRM atomic/vblank helpers, MediaTek MMSYS/mutex/CMDQ APIs, runtime PM, mailbox, DMA sync, and DDP component wrappers from `mtk_ddp_comp.h`.

### Integration points

`mtk_drm_drv.c` calls `mtk_crtc_create()` for SoC-defined paths. Plane code calls plane check/disable/async update. DDP component drivers provide callbacks for config, layer programming, vblank, color management, connection, and DMA device selection.

### Risks

The commit path has several concurrency points: `hw_lock`, `config_lock`, CMDQ callback, vblank IRQ, and pending event ownership. CMDQ timeout is based on three vblanks and can leave pending state if callbacks fail. Connector route switching mutates the final DDP component based on encoder masks. Disable removes components in two loops, so duplicate remove fallback behavior must remain harmless. Plane-to-component mapping assumes first two components provide layers.

### Test signals

Signals include atomic modeset/page-flip IGT, vblank events, async plane updates, CMDQ and CPU-register paths, suspend/resume, connector route changes, gamma/CTM application, multi-plane composition, runtime PM balance, and error-free CRTC disable while planes are active.
