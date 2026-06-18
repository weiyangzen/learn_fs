# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.h

Purpose: this header publishes the Exynos CRTC helper API used by Exynos display controllers and output bridges. It is intentionally small and delegates type definitions to `exynos_drm_drv.h`.

Important APIs and types: it declares `exynos_drm_crtc_create()`, `exynos_drm_crtc_get_by_type()`, `exynos_drm_set_possible_crtcs()`, `exynos_drm_crtc_te_handler()`, and `exynos_crtc_handle_event()`. The core type is `struct exynos_drm_crtc`, defined in `exynos_drm_drv.h`, with `enum exynos_drm_output_type` identifying LCD, HDMI, and VIDI paths.

Control flow and integration: CRTC providers call `exynos_drm_crtc_create()` after creating their primary plane. Encoder/bridge glue calls `exynos_drm_set_possible_crtcs()` or `exynos_drm_crtc_get_by_type()` during bind. TE-capable DSI paths call `exynos_drm_crtc_te_handler()` to push panel synchronization back into the CRTC implementation.

State and persistence: the header stores no state. It exposes functions that manipulate DRM mode objects and Exynos wrapper state.

Dependencies: it includes `exynos_drm_drv.h`, making this header part of the internal Exynos DRM contract rather than a standalone public UAPI.

Risks: because the header exposes CRTC lookup by output type, call sites must handle `ERR_PTR(-ENODEV)` and avoid assuming that an LCD CRTC exists before all components bind. The TE helper requires a valid `struct drm_crtc *`.

Test signals: compile coverage with and without specific output drivers, DSI/DPI/MIC bind ordering, and command-mode panel page flips are the main signals.
