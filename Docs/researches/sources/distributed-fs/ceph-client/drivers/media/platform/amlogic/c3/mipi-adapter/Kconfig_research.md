
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig

## Purpose

This Kconfig file introduces `CONFIG_VIDEO_C3_MIPI_ADAPTER`, the build option for the Amlogic C3 MIPI adapter V4L2 subdevice driver. The adapter receives data from the C3 MIPI CSI-2 receiver, organizes RAW MIPI data, and sends it onward to the ISP pipeline.

## Important APIs, Types, And Functions

The file defines a single tristate symbol, `VIDEO_C3_MIPI_ADAPTER`, with user-visible prompt `"Amlogic C3 MIPI adapter"`. It has no C APIs or runtime functions, but its selects and dependencies directly control which media framework APIs are available to `c3-mipi-adap.c`.

## Control Flow

Kconfig evaluation permits the symbol when building for `ARCH_MESON` or under `COMPILE_TEST`, when `VIDEO_DEV` and `OF` are available. If selected as built-in or module, it also selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`.

## State And Persistence

There is no runtime state. The configuration state persists in the kernel build configuration and determines whether the Makefile emits `c3-mipi-adap.o`.

## Dependencies And Integration Points

The option integrates the adapter into the media platform driver build. `OF` is required because the driver relies on device-tree resources and fwnode graph endpoints. The selected V4L2/media symbols match the driver's use of subdev pads, async notifier, and fwnode link creation.

## Risks

The symbol does not explicitly depend on the C3 MIPI CSI-2 or ISP drivers, so users can build it alone; this is valid for modular media graphs but may produce incomplete runtime pipelines if device-tree and companion drivers are absent. It selects media-controller support unconditionally when enabled, increasing build footprint.

## Test Signals

Run `make olddefconfig` and compile with `CONFIG_VIDEO_C3_MIPI_ADAPTER=m` and `=y` under both Meson and `COMPILE_TEST` environments. Confirm the generated module is named from the Makefile object and that enabling this symbol pulls in the required V4L2 subdev/fwnode/media-controller infrastructure.
