# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/analogix_dp-rockchip.c

## Purpose
Provides Rockchip-specific glue for the Analogix DisplayPort/eDP core. It handles GRF muxing, clocks, resets, panel/AUX discovery, runtime PM, encoder setup, and SoC-specific chip data for RK3288, RK3399, and RK3588 eDP/DP blocks.

## Important APIs, Types, And Functions
Key structs are `rockchip_grf_reg_field`, `rockchip_dp_chip_data`, and `rockchip_dp_device`. Core callbacks include `rockchip_dp_poweron()`, `rockchip_dp_powerdown()`, `rockchip_dp_get_modes()`, encoder helpers, `rockchip_dp_bind()`, `rockchip_dp_link_panel()`, `rockchip_dp_probe()`, and PM callbacks.

## Control Flow
Probe matches SoC data by compatible and MMIO resource start, obtains GRF, clocks, and resets, then calls `analogix_dp_probe()`. AUX bus population eventually calls `rockchip_dp_link_panel()` and registers the component. Bind creates the DRM encoder, sets endpoint IDs, and delegates to `analogix_dp_bind()`. Atomic enable chooses the active VOP endpoint and writes LCDC selection to GRF; disable waits for vertical active end when entering self refresh.

## State And Persistence
The device stores clock/reset/regmap handles, selected chip data, Analogix core handle, and DRM mode. GRF writes persist SoC mux and eDP mode state. Runtime PM delegates suspend/resume to the Analogix core.

## Dependencies And Integration Points
Depends on Analogix DP bridge APIs, DP AUX bus population, DRM OF graph helpers, Rockchip encoder endpoint metadata, reset/clock/regmap frameworks, and optional panel/bridge nodes.

## Risks
The RK3588 chip-data selection relies on MMIO base addresses. Some enable paths return without disabling `grfclk` if endpoint lookup fails. Color formats are forced from YUV to RGB due to VOP limitations, which may surprise sinks.

## Test Signals
Probe on each compatible, panel and driver-free DP mode, AUX bus population with and without panel endpoints, runtime suspend/resume, self-refresh transitions, and GRF mux correctness for big/little VOP endpoints.
