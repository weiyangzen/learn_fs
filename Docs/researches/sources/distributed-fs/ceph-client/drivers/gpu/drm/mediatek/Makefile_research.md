## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Makefile

### Purpose

`mediatek/Makefile` defines the MediaTek DRM object graph for the core display pipeline and optional HDMI/DP modules.

### Important APIs, types, and functions

The `mediatek-drm-y` aggregate includes CRTC, DDP component registry, display blocks such as AAL/CCORR/COLOR/GAMMA/MERGE/OVL/RDMA/ETHDR/PADDING, DRM core, DSI, DPI, MDP RDMA, and plane support. Optional objects are selected by `CONFIG_DRM_MEDIATEK_HDMI_COMMON`, `CONFIG_DRM_MEDIATEK_HDMI`, `CONFIG_DRM_MEDIATEK_HDMI_V2`, and `CONFIG_DRM_MEDIATEK_DP`.

### Control flow

There is no runtime flow. Kbuild links the selected objects into either the core `mediatek-drm` module or separate output modules.

### State and persistence behavior

The file only affects build state. Runtime state is owned by the individual drivers.

### Dependencies

It depends on Kconfig selecting helper subsystems and on cross-object symbols declared mainly in `mtk_disp_drv.h`, `mtk_crtc.h`, and `mtk_ddp_comp.h`.

### Integration points

The aggregate ensures display component implementations are linked with the DDP registry and CRTC code. HDMI v1 includes CEC, HDMI, and DDC; HDMI v2 includes v2 HDMI/DDC; DP builds `mtk_dp.o`.

### Risks

Missing an object from `mediatek-drm-y` can break DDP function tables. Moving a helper between optional and core modules requires symbol export and namespace review.

### Test signals

Build tests across MediaTek display configurations verify linkage. Runtime probe tests should confirm all DT-selected components have corresponding platform drivers or aggregate functions.
