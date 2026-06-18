## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_drm_drv.h

### Purpose

`mtk_drm_drv.h` declares the shared driver-private data structures and platform driver externs used by the MediaTek DRM master and component drivers. It is the cross-file contract for CRTC paths, MMSYS SoC data, private DRM state, and sub-driver registration.

### Important APIs, types, and functions

Important constants are `MAX_CONNECTOR`, `DDP_COMPONENT_DRM_OVL_ADAPTOR`, and `DDP_COMPONENT_DRM_ID_MAX`. `enum mtk_crtc_path` defines `CRTC_MAIN`, `CRTC_EXT`, and `CRTC_THIRD`. `struct mtk_drm_route` describes connector route options. `struct mtk_mmsys_driver_data` describes per-SoC paths, route tables, shadow-register flag, MMSYS identity/count, and size limits. `struct mtk_drm_private` stores per-device DRM, component, mutex, MMSYS, suspend, mailbox, and multi-private coordination state.

### Control flow

The header has no runtime control flow. It enables `mtk_drm_drv.c` to register all component platform drivers and lets component code include common definitions without circular declarations.

### State and persistence behavior

The header owns no state, but defines the layout of persistent per-MMSYS state in `struct mtk_drm_private` and immutable/mostly immutable path data in `struct mtk_mmsys_driver_data`. These structures persist for the platform-device lifetime and are used throughout component binding and KMS operation.

### Dependencies

It includes `<linux/io.h>` and `mtk_ddp_comp.h`, forward-declares DRM/device/regmap types, and declares extern platform drivers for AAL, CCORR, COLOR, GAMMA, MERGE, OVL adaptor, OVL, RDMA, DPI, DSI, ETHDR, MDP RDMA, and padding.

### Integration points

`mtk_drm_drv.c` is the primary consumer. Component drivers rely on the extern declarations for the unified driver registration array. Path and private structs are used by DPI bind, CRTC creation, DDP component initialization, graph path building, and multi-MMSYS coordination.

### Risks

Changing `DDP_COMPONENT_DRM_OVL_ADAPTOR` or `DDP_COMPONENT_DRM_ID_MAX` affects array sizing and pseudo-component indexing across the driver. Adding fields to `mtk_mmsys_driver_data` or `mtk_drm_private` requires updating copy/allocation behavior in graph-built paths. Extern platform-driver declarations must match actual definitions or module link fails.

### Test signals

Build coverage across enabled MediaTek DRM components is the main signal. Runtime signals include successful component registration, OVL adaptor path construction using the pseudo ID, and multi-MMSYS state sharing through `all_drm_private`.
