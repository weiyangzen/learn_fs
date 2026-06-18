# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_drv.h

Purpose: this is the main internal contract for the Exynos DRM driver family. It defines shared plane, CRTC, clock, per-file, and device-private structures plus conditional helper stubs and external platform-driver declarations.

Important types: `enum exynos_drm_output_type` identifies NONE, LCD, HDMI, and VIDI outputs. `struct exynos_drm_plane_state` extends DRM plane state with clipped source/CRTC rectangles and 16.16 scaling ratios. `struct exynos_drm_plane` and `struct exynos_drm_plane_config` describe hardware windows and their formats/capabilities. `struct exynos_drm_crtc_ops` is the hardware callback table consumed by `exynos_drm_crtc.c`. `struct exynos_drm_crtc` wraps `drm_crtc` and stores output type, ops, implementation context, optional pipe clock, and I80 mode flag. `struct drm_exynos_file_private` stores G2D in-use command lists, event list, and userptr list. `struct exynos_drm_private` stores global device integration state.

Control flow and integration: display engines populate plane configs and CRTC ops, call shared plane and CRTC creation helpers, then export callbacks through this contract. The top-level driver stores `exynos_drm_private` in `drm->dev_private`, and helpers such as `to_dma_dev()` and `is_drm_iommu_supported()` use that pointer.

State and persistence: all state is runtime kernel memory. `pending`, `lock`, and `wait` exist for atomic commit synchronization across CRTCs. `mapping` and `dma_dev` are the DMA/IOMMU shared state.

Dependencies: this header depends on Linux module and DRM CRTC/device/plane headers. It conditionally declares DPI and FIMC helpers based on Kconfig, providing no-op or `-ENODEV` behavior when disabled.

Risks: the header relies on `drm->dev_private` being initialized before helpers are used. Capability flags must stay in sync with plane implementation support. Stub behavior can hide disabled features if call sites do not distinguish `NULL` encoder from deferred probe.

Test signals: compile all Kconfig combinations, CRTC/plane initialization for all display engines, IOMMU-supported and non-IOMMU GEM paths, G2D open/close file-private lifecycle, and DPI/FIMC disabled builds.
