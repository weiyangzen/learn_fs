# sources/distributed-fs/ceph-client/drivers/media/i2c/og01a1b.c

## Purpose
This driver supports the OmniVision OG01A1B 1280x1024 global-shutter sensor over two-lane CSI-2. It exposes a modern V4L2 sensor subdev with one source pad, stream enable/disable pad operations, runtime PM, CCI register-list mode programming, 8-bit or 10-bit monochrome output, exposure/gain/blanking/test-pattern controls, and OF/ACPI matching.

## Important APIs, Types, and Functions
Mode data is represented by `struct og01a1b_mode`, `struct og01a1b_reg_list`, and `struct og01a1b_link_freq_config`. `struct og01a1b` stores device resources, CCI regmap, clock/reset/regulators, V4L2 subdev/media pad/control handler, key controls, current mode, and selected media bus code. Important helpers include `to_pixel_rate()`, `to_pixels_per_line()`, `og01a1b_test_pattern()`, `og01a1b_set_ctrl()`, `og01a1b_init_controls()`, `og01a1b_enable_streams()`, `og01a1b_disable_streams()`, `og01a1b_set_format()`, `og01a1b_check_hwcfg()`, `og01a1b_power_on()`, `og01a1b_power_off()`, and `og01a1b_probe()`.

## Control Flow
Probe initializes the I2C subdev and 16-bit CCI regmap, obtains and validates a 19.2MHz external clock, checks firmware endpoint requirements, obtains optional reset GPIO and optional AVDD/DOVDD/DVDD regulators, powers the device, verifies the 24-bit chip ID, initializes default mode/code and controls, finalizes subdev state, registers the sensor subdev, enables runtime PM, and idles the device. Stream enable resumes runtime PM, writes link-frequency PLL registers, writes the mode register table, programs output bit depth, applies all controls, and writes mode-select streaming. Stream disable writes standby and drops the runtime PM autosuspend reference.

## State and Persistence
Current mode and output code are cached in `cur_mode` and `code`; controls cache link frequency, pixel rate, blanking, exposure, gain, and test pattern values. VBLANK changes dynamically adjust exposure maximum. Controls are only written when runtime PM says the device is already active; otherwise V4L2 caches values for setup on stream start. Register state is volatile and is replayed on every stream enable.

## Dependencies and Integration Points
The driver depends on V4L2 CCI helpers, V4L2 fwnode endpoint parsing, subdev active-state/finalize APIs, `v4l2_subdev_s_stream_helper`, runtime PM, clocks, GPIOs, regulators, OF compatible `ovti,og01a1b`, and ACPI ID `OVTI01AC`. Firmware must describe a CSI-2 D-PHY endpoint with exactly two data lanes and link frequency 500 MHz.

## Risks and Edge Cases
Only one sensor mode is supported, so format negotiation is nearest-size but effectively fixed at 1280x1024. `og01a1b_set_format()` does not validate `fmt->format.code` against the enumerated codes before using it; unrecognized codes fall into the 8-bit bpp path while the returned format preserves the caller's code. Optional regulators mean power sequencing may rely on board defaults. `pm_runtime_put()` in control writes does not use autosuspend, unlike stream error/disable paths. Hardware configuration validation requires every driver-supported link frequency to appear in firmware, not just the selected one.

## Test Signals
Test OF and ACPI probe, wrong xclk frequency, missing endpoint, wrong CSI-2 lane count, missing/incorrect link frequencies, optional regulator and reset-GPIO combinations, chip-ID mismatch, 8-bit versus 10-bit output format programming, vblank-driven exposure-range updates, stream-on/off loops with runtime PM, test-pattern menu values, and invalid requested media bus codes.
