# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/Kconfig

## Purpose

`tegra/Kconfig` declares the NVIDIA Tegra DRM driver and its debug/staging options.

## Important APIs, Types, and Definitions

- `DRM_TEGRA`: tristate for the Tegra DRM driver, dependent on Tegra architecture or compile testing, common clock, DRM, and OF.
- Selected subsystems include DRM display helpers, bridge connector, DP AUX bus, KMS helper, MIPI DSI, panel support, Host1x, interconnect, IOMMU IOVA, and optional fbdev DMA helpers.
- Optional audio/CEC selections are tied to Tegra SPDIF or CEC notifier configs.
- `DRM_TEGRA_DEBUG`: enables debug support.
- `DRM_TEGRA_STAGING`: exposes the HOST1X interface to userspace when `STAGING` is enabled.

## Control Flow and State

Kconfig controls whether the composite `tegra-drm` object is built and which optional paths compile. The nested options only appear when `DRM_TEGRA` is enabled.

## Dependencies and Integration Points

It integrates with Host1x, DRM display helper libraries, bridge/panel/MIPI/DP helpers, interconnect/IOMMU infrastructure, fbdev emulation, sound, and CEC subsystems.

## Risks and Edge Cases

- The driver selects many subsystems, so dependency changes can have broad build impacts.
- Staging userspace HOST1X exposure is explicitly optional and should remain gated.
- Debug config changes compile flags in the Makefile.

## Test Signals

Build tests should cover built-in/module Tegra DRM, compile-test builds on non-Tegra architectures, debug enabled/disabled, staging enabled/disabled, fbdev emulation, and optional audio/CEC dependencies.
