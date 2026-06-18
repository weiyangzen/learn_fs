
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig

## Purpose

This Kconfig file defines `CONFIG_VIDEO_C3_MIPI_CSI2`, the build option for the Amlogic C3 MIPI CSI-2 receiver subdevice driver. The receiver ingests MIPI CSI-2 data from an image sensor and forwards media-bus data into the C3 camera pipeline.

## Important APIs, Types, And Functions

The file defines one tristate symbol, `VIDEO_C3_MIPI_CSI2`, with prompt `"Amlogic C3 MIPI CSI-2 receiver"`. It exposes no runtime APIs but selects framework capabilities required by `c3-mipi-csi2.c`.

## Control Flow

Kconfig allows the option on Meson platforms or under compile testing, requiring `VIDEO_DEV` and `OF`. Enabling it selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`.

## State And Persistence

There is no runtime state. The selected build state persists in `.config` and controls whether the Makefile builds `c3-mipi-csi2.o`.

## Dependencies And Integration Points

`OF` is necessary because the driver parses device-tree fwnode endpoints and MIPI CSI-2 bus configuration. The selected media symbols match its use of V4L2 subdevs, async notifier, and media graph links.

## Risks

The symbol does not enforce presence of the adapter or ISP symbols, allowing partial builds. That is useful for modular graphs and compile testing but can surprise integrators expecting a full camera stack from one option.

## Test Signals

Compile with `CONFIG_VIDEO_C3_MIPI_CSI2=m` and `=y`, both on Meson and under `COMPILE_TEST`. Confirm enabling the symbol selects the needed V4L2/media infrastructure and produces the expected object/module.
