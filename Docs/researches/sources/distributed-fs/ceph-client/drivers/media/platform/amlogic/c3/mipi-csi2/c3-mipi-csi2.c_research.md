
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-csi2/c3-mipi-csi2.c

## Purpose

`c3-mipi-csi2.c` implements the Amlogic C3 MIPI CSI-2 receiver bridge. It configures analog PHY, DPHY timing/lane routing, and CSI-2 host lane count, exposes a two-pad V4L2 subdevice, parses fwnode MIPI bus settings, and propagates streaming to an upstream image sensor.

## Important APIs, Types, And Functions

Register routing macros split the hardware into APHY, DPHY, and HOST submodules. `struct c3_csi_device` stores device pointer, three MMIO bases, clocks, subdev, pads, notifier, upstream pad, parsed `v4l2_mbus_config_mipi_csi2`, and match-data clock info. `c3_mipi_csi_formats[]` lists RAW10 and RAW12 Bayer bus codes.

Hardware helpers are `c3_mipi_csi_write()`, `c3_mipi_csi_cfg_aphy()`, `c3_mipi_csi_cfg_dphy()`, `c3_mipi_csi_cfg_host()`, and `c3_mipi_csi_start_stream()`. V4L2 operations include stream enable/disable, bus-code enumeration, format set/get, and initial state. Platform helpers initialize/deinitialize the subdev, register async notifier, map named resources `aphy`, `dphy`, `host`, get clocks `vapb` and `phy0`, and handle runtime PM.

## Control Flow

Probe maps APHY/DPHY/HOST resources, gets clocks, enables runtime PM, initializes a bridge subdevice with sink/source pads, parses endpoint 0 as `V4L2_MBUS_CSI2_DPHY`, stores bus lane configuration, registers an async notifier for the remote sensor endpoint, and registers the subdev. Bound notification creates an immutable enabled link from the sensor to the CSI-2 sink.

Format negotiation accepts RAW10/RAW12 Bayer formats on the sink pad, clamps dimensions to 160x120 through 2888x2240, forces RAW colorspace metadata, and mirrors the sink format to the source pad.

Stream enable resolves the unique upstream pad, resumes runtime PM, calls `c3_mipi_csi_start_stream()`, then enables the upstream sensor stream. Start obtains link frequency from the upstream pad, computes lane rate as twice link frequency, rejects rates above 1.5 Gbps, programs APHY constants, computes DPHY high-speed settle from lane rate, sets lane mux order, enables all digital lanes and the clock lane, resets host output, and writes `num_data_lanes - 1`.

## State And Persistence

State persists in the allocated `struct c3_csi_device`: resource bases, clock descriptors, parsed bus lane count, subdev state, notifier, and current upstream pad. Hardware programming is volatile and repeated at stream start. There is no disk persistence.

## Dependencies And Integration Points

The receiver depends on device-tree graph endpoints with MIPI CSI-2 DPHY bus data, upstream sensor link-frequency reporting, media-controller links, V4L2 subdev APIs, and runtime PM. It integrates upstream of `c3-mipi-adapter.c` in the C3 camera media graph.

## Risks

`pm_runtime_resume_and_get()` and `c3_mipi_csi_start_stream()` return values are not fully checked in stream enable; the call to start stream ignores its return, so an invalid/missing link frequency may still be followed by upstream stream enable. DPHY programming enables all four data lanes regardless of parsed `num_data_lanes`, while host lane count reflects the parsed value. Lane mux is fixed to identity order and does not use endpoint lane mapping. Timing constants are mostly fixed except HS settle, so unusual sensors may need tuning.

## Test Signals

Device-tree tests should cover one-, two-, and four-lane endpoints with link-frequency controls. Subdev tests should verify RAW format enumeration, clamping, and sink/source mirroring. Hardware stream tests should verify lane-rate rejection, correct host lane count, stable sensor-to-adapter streaming, and no runtime-PM register access failures. Static tests should flag the ignored return from `c3_mipi_csi_start_stream()` as a candidate fix.
