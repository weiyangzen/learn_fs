## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_crtc.h

### Purpose

`mtk_crtc.h` declares the MediaTek CRTC interface used by the DRM core driver and plane code.

### Important APIs, types, and functions

It defines color-management bounds `MTK_MAX_BPC` and `MTK_MIN_BPC`. It declares `mtk_crtc_commit()`, `mtk_crtc_create()`, `mtk_crtc_plane_check()`, `mtk_crtc_plane_disable()`, `mtk_crtc_async_update()`, and `mtk_crtc_dma_dev_get()`.

### Control flow

There is no runtime flow in the header. Callers create CRTCs from SoC DDP paths, validate/configure planes through CRTC helpers, and query the DMA device for buffer mapping.

### State and persistence behavior

The header owns no state. State is held in private `struct mtk_crtc` instances in `mtk_crtc.c`.

### Dependencies

It includes DRM CRTC types and MediaTek DDP, DRM-private, and plane headers so signatures can reference route and plane-state types.

### Integration points

The declarations connect `mtk_drm_drv.c`, `mtk_plane.c`, DDP component code, and DMA mapping paths.

### Risks

`mtk_crtc_commit()` is declared here but not in the researched `mtk_crtc.c` content, so users must rely on the full tree for its definition or dead declaration status. Header coupling to several MediaTek internals means changes in route or plane-state types propagate widely.

### Test signals

Build coverage across the MediaTek DRM driver and plane update tests validate the header contract.
