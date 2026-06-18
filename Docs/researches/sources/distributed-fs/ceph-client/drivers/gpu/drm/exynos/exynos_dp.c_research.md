## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_dp.c

### Purpose
`exynos_dp.c` provides Samsung Exynos-specific glue around the shared Analogix DisplayPort bridge driver. It creates the DRM encoder, discovers panels or downstream bridges, bridges Exynos CRTC clock control into Analogix power callbacks, and participates in the component framework.

### Important APIs, Types, And Functions
`struct exynos_dp_device` stores the encoder, connector, optional downstream bridge, DRM/device pointers, fallback videomode, Analogix device, and platform data. Important functions are `exynos_dp_crtc_clock_enable()`, `exynos_dp_poweron()`, `exynos_dp_poweroff()`, `exynos_dp_get_modes()`, `exynos_dp_bridge_attach()`, `exynos_dp_dt_parse_panel()`, bind/unbind, probe/remove, and runtime suspend/resume.

### Control Flow
Probe allocates state and temporarily stores it as platform drvdata, supports legacy `panel` phandle lookup, otherwise uses `drm_of_find_panel_or_bridge()`, fills Analogix platform callbacks, records whether connector creation should be skipped for a downstream bridge, calls `analogix_dp_probe()`, and adds the component. Bind parses a fallback videomode when no panel or bridge exists, initializes a simple TMDS encoder, attaches helper funcs, sets possible Exynos LCD CRTCs, stores the encoder in platform data, and calls `analogix_dp_bind()`. Runtime PM delegates suspend/resume to Analogix.

### State, Persistence, And Dependencies
State persists in the encoder, connector pointer, bridge/panel references, fallback videomode, Analogix private object, and platform data callbacks. Dependencies include DRM bridge/panel/OF helpers, Exynos CRTC clock helpers, Analogix DP core, runtime PM, and component APIs.

### Integration Points
The Kconfig symbol `DRM_EXYNOS_DP` selects Analogix DP and panel helpers; the Makefile links this file into `exynosdrm`. The exported `dp_driver` platform driver matches `samsung,exynos5-dp`.

### Risks
Power callbacks fail with `-EPERM` when the encoder has no CRTC. Legacy panel and graph bridge discovery must not conflict. If `analogix_dp_bind()` fails, the encoder is destroyed; ownership must stay aligned with DRM helper expectations. Fallback videomode parsing only applies when there is no panel or bridge.

### Test Signals
Tests should cover legacy panel phandle, graph panel, graph bridge with skipped connector, fallback videomode, CRTC clock enable/disable during DP power transitions, bind failure cleanup, runtime suspend/resume, and possible-CRTC assignment.
