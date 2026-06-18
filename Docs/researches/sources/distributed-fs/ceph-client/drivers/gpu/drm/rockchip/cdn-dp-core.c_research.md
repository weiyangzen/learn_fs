# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.c

## Purpose
Implements the Rockchip RK3399 Cadence DisplayPort bridge driver. It manages firmware loading, Type-C/extcon port selection, PHY power, link training, EDID/DPCD access, video and audio bridge operations, HPD notification, suspend/resume, and component binding to Rockchip DRM.

## Important APIs, Types, And Functions
Uses `struct cdn_dp_device`, `struct cdn_dp_port`, and `struct cdn_dp_data`. Major functions include `cdn_dp_enable()`, `cdn_dp_disable()`, `cdn_dp_bridge_atomic_enable()`, `cdn_dp_bridge_atomic_disable()`, `cdn_dp_pd_event_work()`, `cdn_dp_bind()`, `cdn_dp_probe()`, audio callbacks, and firmware helpers. It delegates register/mailbox operations to `cdn-dp-reg.c`.

## Control Flow
Probe discovers extcon/PHY pairs and registers a component. Bind parses DT resources, initializes encoder/bridge/connector, registers extcon notifiers, enables runtime PM, and schedules event work. Event work requests firmware, checks connected ports, powers PHY, reads sink DPCD, enables the controller, and notifies bridge HPD. Atomic enable selects VOP in GRF, enables DP, validates or trains the link, idles video, configures video, then marks video valid.

## State And Persistence
State is protected by `dp->lock` and includes `connected`, `active`, `suspended`, firmware state, active port, lane/rate results, DPCD cache, audio/video info, and per-port `phy_enabled`. Firmware is cached until unbind; hardware state is reset on enable/disable and suspend.

## Dependencies And Integration Points
Integrates with DRM bridge connector, Rockchip encoder atomic state, extcon Type-C properties, PHY framework, syscon GRF, clocks/resets, runtime PM, firmware loader, and HDMI codec bridge audio callbacks.

## Risks
Firmware load can block/retry for up to 64 seconds. Hotplug state is asynchronous and depends on extcon plus DPCD reads. Error paths in link enable must keep PHY, HPD mux, clocks, and firmware active state balanced. Mode validation assumes 80% DP efficiency and uses cached DPCD.

## Test Signals
Firmware missing/delayed load, Type-C orientation and lane-count changes, dock-without-sink cases, retraining after link-status failure, audio I2S/SPDIF prepare/mute/shutdown, suspend/resume with active display, and HPD userspace notification.
