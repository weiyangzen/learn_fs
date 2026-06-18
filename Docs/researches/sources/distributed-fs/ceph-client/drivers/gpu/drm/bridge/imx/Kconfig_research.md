# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Kconfig

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Kconfig

## Purpose

This Kconfig file declares build-time options for i.MX DRM bridge drivers under `ARCH_MXC` or `COMPILE_TEST`.

## Important APIs, Types, And Functions

It defines symbols for the shared LDB helper, legacy i.MX bridge, i.MX8MP DW HDMI bridge, HDMI PAI/PVI helpers, i.MX8QM/QXP LDB and pixel-link blocks, PXL2DPI, and i.MX93 MIPI DSI. Dependencies include OF, COMMON_CLK, DRM_IMX, IMX_SCU, and selected/implied DRM/PHY/regmap helpers.

## Control Flow

There is no runtime flow. Kconfig choices control which objects the Makefile builds and which supporting frameworks are selected. `DRM_IMX8MP_DW_HDMI_BRIDGE` implies its PAI/PVI and HDMI PHY helpers rather than selecting all unconditionally.

## State And Persistence Behavior

The only state is kernel configuration. It persists in the built kernel config and determines which drivers and symbols exist.

## Dependencies And Integration Points

This file integrates the i.MX bridge subdirectory with the kernel config system and ensures module dependencies are available for each driver.

## Risks And Test Signals

Risks include missing `select` dependencies that cause link failures, overly broad `imply` choices that omit required runtime pieces in minimal configs, and helper visibility when consumers are modular. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and representative i.MX defconfig builds.
