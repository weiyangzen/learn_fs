# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Kconfig

## Purpose
This Kconfig file declares Cadence media platform options for the MIPI CSI-2 RX and TX controller bridge drivers.

## Important APIs, Types, and Functions
It defines `VIDEO_CADENCE_CSI2RX` and `VIDEO_CADENCE_CSI2TX` tristate symbols. Both depend on `VIDEO_DEV` and select `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, and `V4L2_FWNODE`. RX additionally selects `GENERIC_PHY` and `GENERIC_PHY_MIPI_DPHY`.

## Control Flow
Enabled symbols cause the sibling Makefile to build `cdns-csi2rx.o` or `cdns-csi2tx.o`. The selected APIs match the drivers' role as V4L2 bridge subdevices, not standalone video nodes.

## State and Persistence
Only kernel configuration state persists. Runtime subdev, clock, reset, lane, stream, and D-PHY state live in the C drivers.

## Dependencies and Integration Points
The file integrates Cadence bridge drivers with media-controller graphs, fwnode endpoint parsing, V4L2 subdev device nodes, and generic PHY support for CSI2RX external D-PHY configuration.

## Risks and Edge Cases
If generic PHY support is not selected for RX, external D-PHY configuration will not build. If subdev/media-controller selections are removed, the drivers' pad/link operations are unavailable.

## Test Signals
Run allmodconfig and targeted builds with each symbol as module. Confirm `cdns-csi2rx.ko` and `cdns-csi2tx.ko` build and expose V4L2 subdevice APIs.
