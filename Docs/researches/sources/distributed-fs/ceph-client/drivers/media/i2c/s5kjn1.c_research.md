# sources/distributed-fs/ceph-client/drivers/media/i2c/s5kjn1.c

## Purpose
`s5kjn1.c` implements a V4L2 subdev driver for the Samsung S5KJN1 raw Bayer sensor. It uses V4L2 CCI register helpers, validates a 4-lane CSI-2 endpoint and 24 MHz MCLK, exposes 4080x3072 and 8160x6144 modes, manages optional regulators with runtime PM, and supports exposure, gain, blanking, test pattern, and flip-dependent Bayer order controls.

## Important APIs, Types, and Functions
State is `struct s5kjn1`, with device/regmap/clock/reset, optional `afvdd`, `vdda`, `vddd`, and `vddio` regulators, one source-pad subdev, control handler, cached controls, and current `struct s5kjn1_mode`. Modes store width, height, HTS, VTS, default exposure, mode-specific exposure margin, and a register list. Register tables include `init_array_setting`, `s5kjn1_4080x3072_30fps_mode`, and `s5kjn1_8160x6144_10fps_mode`.

Important functions mirror the S5K3M5 pattern: `s5kjn1_set_ctrl()`, `s5kjn1_init_controls()`, `s5kjn1_enable_streams()`, `s5kjn1_disable_streams()`, format/enumeration/selection/init-state helpers, `s5kjn1_identify_sensor()`, `s5kjn1_check_hwcfg()`, `s5kjn1_power_on()`, `s5kjn1_power_off()`, `s5kjn1_probe()`, and `s5kjn1_remove()`.

## Control Flow
Probe creates a 16-bit CCI regmap, validates 24 MHz clock, parses the endpoint for CSI-2 DPHY with exactly four lanes and supported 700 MHz link frequency, obtains reset GPIO, optionally obtains four regulators, powers the device to read chip ID `0x38e1`, initializes controls, finalizes the media entity and subdev state, enables runtime PM, registers the sensor subdev, and arms autosuspend.

Stream-on resumes runtime PM, writes page/version/reset staging registers, waits, applies common init and selected mode tables, applies cached controls, and writes `S5KJN1_REG_CTRL_MODE` to start streaming. Stream-off writes zero and autosuspends. Control writes while active program analogue gain, exposure, VTS, orientation, and test pattern registers; when suspended they only update cached control values. Format setting picks the nearest supported mode and updates control ranges.

## State and Persistence
The file has no firmware or filesystem state. Runtime state consists of current mode, controls, regulator/clock/reset state, runtime PM state, and volatile sensor registers. Optional regulators allow boards to omit named supplies, with power sequencing adapting to the available set.

## Dependencies and Integration Points
Dependencies include Linux CCI/regmap over I2C, V4L2 controls/subdev/fwnode APIs, runtime PM, clock, GPIO, optional regulators, OF compatible `samsung,s5kjn1`, and media graph registration as a sensor source subdev.

## Risks and Edge Cases
The register tables are large and opaque, so mode timing changes require hardware validation. `get_selection()` reports height as `mode->width`, which appears to be a crop rectangle typo. Link-frequency validation requires the endpoint to advertise exactly a supported frequency. Optional regulators make the driver flexible but can mask incomplete board descriptions until power sequencing fails electrically. Flip controls update an orientation register when active, so Bayer-code changes and streaming orientation must remain synchronized.

## Test Signals
Signals include successful optional-regulator handling, chip ID match, endpoint lane/link-frequency validation, stream-on after common and mode register sequences, 4080x3072 and 8160x6144 mode switching, correct exposure range updates from per-mode margins, active orientation writes on H/V flip, Bayer-code enumeration changes, runtime PM autosuspend, and clean removal from active or suspended states.
