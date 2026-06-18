# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.c

Purpose: Shared DRM bridge core for MMIO-based Analogix DisplayPort/eDP controllers used by platform drivers such as Exynos and Rockchip. It handles AUX registration, HPD, link training, panel sequencing, video setup, PSR, CRC, runtime PM, and bridge binding.

Important APIs/types/functions: Exported APIs are `analogix_dp_probe`, `analogix_dp_suspend`, `analogix_dp_resume`, `analogix_dp_bind`, `analogix_dp_unbind`, `analogix_dp_start_crc`, `analogix_dp_stop_crc`, `analogix_dp_aux_to_plat_data`, and `analogix_dp_get_aux`. Internal major flows include `analogix_dp_full_link_train`, `analogix_dp_fast_link_train`, `analogix_dp_commit`, `analogix_dp_enable_psr`, `analogix_dp_disable_psr`, `analogix_dp_bridge_atomic_enable`, and `analogix_dpaux_transfer`.

Control flow: Probe allocates `struct analogix_dp_device`, parses platform data, gets optional PHY, clock, MMIO, HPD GPIO/IRQ, initializes AUX, and enables runtime PM. Resume powers clocks/platform/PHY and initializes hardware registers. Bind registers AUX and attaches the DRM bridge. Atomic enable prepares the panel, exits PSR if needed, sets mode-derived video info, detects HPD, trains the link, enables scrambling, configures video, enables the panel, detects fast training and PSR. Disable handles PSR transitions specially, otherwise disables panel/IRQ, powers analog blocks down, and drops runtime PM.

State and persistence: In-memory state includes connector, bridge, AUX, clock/IRQ/MMIO/PHY, video_info, link_train, DPMS mode, HPD force flag, fast-training and PSR flags, and platform data. There is no persistent storage. Link training state machines update `dp->link_train` during each enable.

Dependencies and integration: Depends on DRM bridge/connector/panel/EDID helpers, DP AUX/DPCD helpers, component-style platform drivers, runtime PM, clocks, PHY API, GPIO IRQs, and `analogix_dp_reg.c` register helpers. Platform callbacks in `analogix_dp_plat_data` provide SoC-specific power, attach, and mode hooks.

Risks: `pm_runtime_get_sync` return values are not always checked. Connectorless attach is rejected unless `skip_connector` is set through platform data behavior. Fast training has optional verification disabled by a static false. PSR state is tied to atomic self-refresh and can interact subtly with panel power and link retraining.

Test signals: Link training against sinks with different rates/lanes, HPD GPIO and MMIO interrupt paths, forced HPD eDP panels, EDID mode population, runtime suspend/resume, PSR enter/exit through self-refresh, CRC start/stop, and PHY configure failures are important signals.
