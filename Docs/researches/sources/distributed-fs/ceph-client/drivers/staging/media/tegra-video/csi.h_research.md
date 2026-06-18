# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.h

## Purpose
Declares the Tegra CSI data model, constants, SoC operation table, and cross-module helpers.

## Important APIs, Types, And Functions
Constants describe CSI bricks, lane counts, ganged ports, and pad count. `struct tegra_csi_channel` owns the V4L2 subdev, pads, DT node, gang/lane mapping, TPG mode, active mbus format, blanking/framerate, MIPI handle, and pixel rate. `struct tpg_framerate` maps TPG resolution/format to blanking and framerate. `struct tegra_csi_ops` provides SoC callbacks for start, stop, and error recovery. `struct tegra_csi_soc` carries ops, MIPI ops, channel count, clocks, and TPG table. `struct tegra_csi` is the device-level host1x client with iomem, clocks, regulator, ops, lock, and channel list. Exports include `tegra_csi_error_recover()` and `tegra_csi_calc_settle_time()`.

## Control Flow
The header enables generic `csi.c` to operate through SoC callbacks supplied by `tegra20.c`/`tegra210.c` while VI locates CSI subdevices and calls stream operations.

## State And Persistence
All state is runtime kernel memory. Format and TPG settings persist for the life of a channel or until changed by pad ops/control flow.

## Dependencies And Integration Points
Depends on media entity, V4L2 async/subdev, host1x, clocks, regulators, and Tegra MIPI calibration types. Used by VI, CSI, and SoC backend files.

## Risks And Test Signals
Struct layout and constants define assumptions for all backends. Risks include port array bounds for ganged channels and optional callback handling. Test signals are compile coverage for all enabled SoC symbols and runtime stream coverage with TPG and external sensors.
