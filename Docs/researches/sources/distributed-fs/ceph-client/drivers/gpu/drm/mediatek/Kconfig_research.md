## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/Kconfig

### Purpose

`mediatek/Kconfig` defines the MediaTek DRM/KMS driver family and optional DisplayPort and HDMI subdrivers.

### Important APIs, types, and functions

The file defines `DRM_MEDIATEK`, `DRM_MEDIATEK_DP`, `DRM_MEDIATEK_HDMI_COMMON`, `DRM_MEDIATEK_HDMI`, and `DRM_MEDIATEK_HDMI_V2`. The base driver depends on DRM, MediaTek architecture or compile-test, common clocks, ARM SMCCC or compile-test, OF, and MTK MMSYS; it selects DRM client, GEM DMA, KMS, display helpers, bridge connector, MIPI DSI, panel, and videomode helpers.

### Control flow

There is no runtime control flow. Kconfig choices drive which objects in `mediatek/Makefile` are compiled and which helper subsystems are guaranteed available.

### State and persistence behavior

Configuration symbols persist in the kernel config and determine module availability. No driver runtime state is stored here.

### Dependencies

The dependencies mirror driver use of DT-described MMSYS/DDP components, clocks, SMCCC, MIPI DSI, DRM bridge/panel/display helpers, HDMI codec/display helpers, and DP AUX/helper infrastructure.

### Integration points

`CONFIG_DRM_MEDIATEK` builds the core `mediatek-drm` aggregate; HDMI and DP symbols add their output-specific modules. HDMI v1 selects the common HDMI library and CEC/DDC pieces, while HDMI v2 selects a separate v2 implementation.

### Risks

Optional symbols must align with Makefile objects and exported namespaces. Compile-test coverage may not catch missing runtime dependencies such as DT graph or power domains.

### Test signals

Signals include build matrix coverage for base-only, HDMI v1, HDMI v2, DP, built-in and module configurations, plus boot/probe on supported MediaTek SoCs.
