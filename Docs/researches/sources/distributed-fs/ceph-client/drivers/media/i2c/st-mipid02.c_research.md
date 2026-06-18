# sources/distributed-fs/ceph-client/drivers/media/i2c/st-mipid02.c

## Purpose
`st-mipid02.c` is a V4L2 subdevice driver for the ST MIPID02 CSI-2 to parallel video bridge. It discovers the upstream CSI-2 sensor through async notifier plumbing, validates firmware endpoints, translates sink serial media-bus formats to source parallel formats, configures MIPI lane timing/polarity/data type and parallel bus width, and manages runtime power around streaming.

## Important APIs, Types, and Functions
- `struct mipid02_dev` stores I2C/regmap, supplies, subdev, media pads, xclk, reset GPIO, parsed RX/TX endpoints, async notifier state, bound source subdev, and a register-image cache.
- Format helpers `bpp_from_code()`, `data_type_from_code()`, `get_fmt_code()`, and `serial_to_parallel_code()` map V4L2 bus codes to MIPI CSI-2 data types, bit depth, and parallel output codes.
- `mipid02_set_power_on()` and `mipid02_set_power_off()` manage xclk, regulators, reset GPIO, and runtime PM callbacks.
- `mipid02_configure_from_rx()`, `_from_rx_speed()`, `_from_tx()`, and `_from_code()` build register values from endpoint and format state.
- Stream ops `mipid02_enable_streams()` and `mipid02_disable_streams()` power the device, program registers with CCI helpers, and delegate stream on/off to the upstream subdev.
- `mipid02_parse_rx_ep()`, `mipid02_parse_tx_ep()`, and async notifier callbacks establish firmware graph integration.

## Control Flow and State
Probe allocates state, validates xclk rate in the 6-27 MHz range, obtains reset GPIO and supplies, creates a 16-bit CCI regmap, initializes three media pads, finalizes subdev state, powers the chip for detection, parses TX and RX endpoints, registers an async notifier for the remote sensor, enables autosuspended runtime PM, and registers the subdev.

Active format state lives in the V4L2 subdev state object. Enabling streams clears the cached register image, derives lane enables/swap/polarity and UI timing from remote link frequency, derives parallel bus flags and width from TX endpoint, sets manual data type except for JPEG, writes all bridge registers, and then enables the upstream stream. Disabling streams stops upstream first, disables all lanes, and releases runtime PM.

## Dependencies and Integration Points
The driver uses V4L2 fwnode endpoint parsing, async subdev notifiers, media-controller pads/links, CCI regmap helpers, runtime PM, regulators, clocks, GPIO descriptors, and MIPI CSI-2 data type constants. Device tree compatible is `st,st-mipid02`.

## Risks and Edge Cases
- Only sink pad 0 is supported; sink 1 returns `-EINVAL`.
- Clock lane must be lane 0 and at most two data lanes are supported.
- `mipid02_configure_from_rx_speed()` requires the upstream entity pad and link-frequency controls to be available; missing controls fail stream-on.
- Error cleanup in stream-on disables lanes and releases runtime PM, but upstream stream is only enabled after register writes, so no upstream disable is needed in that path.
- JPEG bypasses manual data type, relying on hardware auto-detection.
- Probe powers the device before endpoint parsing and must unwind notifier, PM, power, and media entity state correctly on failures.

## Test Signals
Test endpoint parsing for valid and invalid lane counts, clock-lane remapping rejection, lane swap/polarity register values, all supported media-bus code enumeration and source-code conversion, link-frequency failure when the upstream sensor lacks controls, stream-on/off register writes, runtime PM autosuspend, async media link creation, and remove cleanup after a bound sensor.
