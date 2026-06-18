# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/Kconfig

## Purpose
Defines build-time configuration for the Rockchip DRM driver and its optional display pipeline/output subdrivers.

## Important APIs, Types, And Functions
The top-level `DRM_ROCKCHIP` tristate depends on DRM, OF, Rockchip architecture or compile test, and selects common DRM helpers. Child bool options enable VOP, VOP2, Analogix DP, Cadence DP, Synopsys DW DP, DW HDMI, DW HDMI QP, DW MIPI DSI, DW MIPI DSI2, Innosilicon HDMI, LVDS, RGB, and RK3066 HDMI.

## Control Flow
Kconfig selection controls which platform drivers are compiled into the single `rockchipdrm` object and which helper libraries are selected. Conditional selects pull bridge, panel, DP, HDMI, MIPI, audio codec, and PHY support.

## State And Persistence
No runtime state. Configuration persists in the kernel build `.config` and directly changes object composition and probe-time subdriver registration.

## Dependencies And Integration Points
Integrates with DRM, bridge/helper libraries, extcon for Cadence DP, generic PHY for DSI, and SoC pinctrl requirements for LVDS/RGB. The selected symbols are consumed by `Makefile` and `rockchip_drm_drv.c`.

## Risks
Because many subdrivers are bool under a tristate parent, dependency mismatches can create missing symbol or unusable runtime combinations. Conditional `select` statements hide some dependencies, so adding a new bridge needs both Kconfig and Makefile updates.

## Test Signals
Build matrix coverage for built-in, module, COMPILE_TEST, and partial-output configurations is the main signal. Runtime probe coverage should confirm only enabled subdrivers are registered.
