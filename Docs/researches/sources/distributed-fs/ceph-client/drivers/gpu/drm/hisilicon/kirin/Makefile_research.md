# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/Makefile

Purpose: builds the Kirin DRM objects for the selected Kconfig option.

Important APIs/types: `kirin-drm-y` contains `kirin_drm_drv.o` and `kirin_drm_ade.o`; `obj-$(CONFIG_DRM_HISI_KIRIN)` links `kirin-drm.o` plus `dw_drm_dsi.o`.

Control flow: when `DRM_HISI_KIRIN` is enabled, the master DRM/ADE code and DSI host/encoder code are compiled into the module/built-in target.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: tied to the Kconfig symbol and Linux kbuild conventions. It keeps the DSI driver as a separate object alongside the aggregate Kirin DRM object.

Risks: adding ADE or DSI dependencies requires updating this list. Incorrect object order or missing object would break component binding at runtime.

Test signals: kernel build with `CONFIG_DRM_HISI_KIRIN=y/m`, module contents inspection, and symbol presence for `kirin_drm_platform_driver` and `dsi_driver`.
