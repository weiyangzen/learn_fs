
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/mipi-adapter/c3-mipi-adap.c

## Purpose

`c3-mipi-adap.c` implements the Amlogic C3 MIPI adapter V4L2 subdevice. It bridges the upstream MIPI CSI-2 receiver to the ISP by configuring adapter top, frontend, DDR reader, pixel, and alignment blocks for direct RAW Bayer delivery.

## Important APIs, Types, And Functions

The file defines register address composition macros for three adapter submodules: TOP, frontend, and reader. `struct c3_adap_device` stores device pointer, three MMIO bases, clocks, subdev, pads, async notifier, current upstream pad, and match-data clock info. `struct c3_adap_pix_format` maps RAW10/RAW12 media-bus codes to MIPI CSI-2 data types.

Hardware helpers include `c3_mipi_adap_update_bits()`, `c3_mipi_adap_cfg_top()`, `c3_mipi_adap_cfg_frontend()`, `c3_mipi_adap_cfg_rd0()`, `c3_mipi_adap_cfg_pixel0()`, and `c3_mipi_adap_cfg_alig()`. V4L2 operations are `c3_mipi_adap_enable_streams()`, `c3_mipi_adap_disable_streams()`, `c3_mipi_adap_enum_mbus_code()`, `c3_mipi_adap_set_fmt()`, and `c3_mipi_adap_init_state()`.

Probe/remove helpers initialize subdev/media pads, async notifier, named resources `top`, `fd`, `rd`, runtime PM, and clocks `vapb` and `isp0`.

## Control Flow

Probe maps all three hardware regions, obtains clocks, enables runtime PM, initializes the bridge subdevice, registers an async notifier for remote endpoint port 0 endpoint 0, and registers the subdev. Bound notifier callbacks create immutable enabled links from the upstream remote subdev to the adapter sink.

Format negotiation accepts RAW10 and RAW12 Bayer sink formats, clamps dimensions to 160x120 through 2888x2240, forces RAW colorspace metadata, and mirrors the sink format to the source pad. Source-pad enumeration exposes only the current source format.

Stream enable finds the unique upstream source pad, resumes runtime PM, gets the sink format, programs top reset/decompress bypass, frontend window and VC0 RAW packet handling, DDR_RD0 direct mode, PIXEL0 data type/start, and alignment blanking/path/start. It then enables the upstream source stream. Disable disables upstream stream if present, clears `src_pad`, and drops runtime PM.

## State And Persistence

Persistent state is per-device memory: MMIO bases, clocks, subdev state, notifier state, and `src_pad`. Format state is held in V4L2 subdev state. Hardware state is volatile and configured at stream enable. There is no file-backed state.

## Dependencies And Integration Points

The adapter depends on platform resources named `top`, `fd`, and `rd`, device-tree compatible `amlogic,c3-mipi-adapter`, V4L2 async fwnode graph links, media-controller validation, MIPI CSI-2 data-type definitions, and runtime PM. In the media graph it sits between the C3 CSI-2 receiver and C3 ISP core.

## Risks

`c3_mipi_adap_cfg_pixel0()` assumes `c3_mipi_adap_find_format(fmt->code)` succeeds; this depends on format state being validated. `pm_runtime_resume_and_get()` return value is ignored, so stream enable may program registers without clocks if runtime resume fails. Stream enable calls the local hardware configuration before enabling upstream; upstream failure drops PM but does not explicitly reset/stop already-started adapter blocks. The adapter forces VC0 and RAW packets only, with no support for multiple virtual channels or YUV despite some register definitions.

## Test Signals

Use media graph tests to verify immutable upstream links and two-pad bridge registration. Subdev format tests should validate RAW10/RAW12 enumeration, default SRGGB10 1920x1080 state, clamping, and sink-to-source mirroring. Hardware tests should stream from a sensor through CSI-2 and adapter into ISP, checking that RAW data type matches the selected bus code and that alignment blanking satisfies ISP requirements.
