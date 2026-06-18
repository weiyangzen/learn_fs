# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/Makefile

Purpose: builds the Unisoc DRM driver as one composite object.

Important APIs/types/functions: `sprd-drm-y` combines `sprd_drm.o`, `sprd_dpu.o`, `sprd_dsi.o`, and `megacores_pll.o`; `obj-$(CONFIG_DRM_SPRD)` emits `sprd-drm.o`.

Control flow: all subcomponents are linked into the same module/built-in unit, allowing `sprd_drm.c` to register platform drivers exported by DPU and DSI sources.

State and persistence: no runtime state.

Dependencies and integration: must remain aligned with extern declarations in `sprd_drm.h` and DSI PLL functions declared in `sprd_dsi.h`.

Risks: omitting any object breaks link-time references between DSI and PLL or master and subdrivers.

Test signals: module link and modpost with `CONFIG_DRM_SPRD=m` and built-in.
