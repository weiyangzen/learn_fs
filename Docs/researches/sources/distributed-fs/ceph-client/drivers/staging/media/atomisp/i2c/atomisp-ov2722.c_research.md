# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/i2c/atomisp-ov2722.c

## Purpose
This file implements the V4L2 I2C subdevice driver for the OmniVision OV2722/OV2720 raw Bayer camera sensor used by AtomISP platforms. It owns sensor register access, probe/remove, platform power sequencing, CSI setup, mode selection, stream control, exposure programming, and a small volatile-control surface.

## Important APIs, Types, And Functions
- `ov2722_read_reg()`, `ov2722_write_reg()`, and `ov2722_i2c_write()` implement 16-bit register addressing over I2C with 8/16/32-bit reads and 8/16-bit writes. Register values are marshalled big-endian, matching sensor bus order.
- `ov2722_write_reg_array()` batches consecutive `struct ov2722_reg` entries into one transfer and flushes on gaps, delays, termination, or buffer pressure. It depends on `OV2722_TOK_TERM`, `OV2722_TOK_DELAY`, and `OV2722_MAX_WRITE_BUF_SIZE` from `ov2722.h`.
- `__ov2722_set_exposure()`, `ov2722_s_exposure()`, and `ov2722_ioctl()` expose AtomISP private exposure programming through `ATOMISP_IOC_S_EXPOSURE`. Coarse integration is shifted to sensor register format, VTS is extended when exposure plus margin exceeds the current frame length, analog gain is written to `OV2722_AGC_ADJ_H`, and digital gains are written to R/G/B manual white-balance gain registers.
- `ov2722_g_volatile_ctrl()` backs `V4L2_CID_EXPOSURE_ABSOLUTE` and read-only `V4L2_CID_LINK_FREQ`.
- `power_ctrl()`, `gpio_ctrl()`, `power_up()`, `power_down()`, and `ov2722_s_power()` implement the module sequencing contract through `struct camera_sensor_platform_data`.
- `ov2722_set_fmt()`, `ov2722_get_fmt()`, `ov2722_enum_mbus_code()`, `ov2722_enum_frame_size()`, and `ov2722_get_frame_interval()` provide the pad-format and frame-size V4L2 subdev operations.
- `ov2722_detect()` reads chip ID registers and accepts both `OV2722_ID` and `OV2720_ID`.
- `ov2722_probe()` allocates `struct ov2722_device`, obtains G-Min platform data, configures/detects the sensor, initializes controls/media entity state, and registers with AtomISP via `atomisp_register_i2c_module()`.

## Control Flow
Probe initializes a default preview resolution, registers the V4L2 subdev shell, obtains G-Min platform data for RAW10/GRBG, runs `ov2722_s_config()`, initializes controls, sets source-pad/media-entity metadata, and registers the I2C module with AtomISP. `ov2722_s_config()` power-cycles the sensor, enables CSI routing, detects the chip, and powers back down after probe-time validation.

Runtime power-on calls `power_up()` and then `ov2722_init()`, which resets the active global mode table to preview. `set_fmt()` chooses the nearest preview resolution, updates `dev->res`, `pixels_per_line`, and `lines_per_frame`, resets the sensor, and writes the selected register table. If startup fails, it retries the whole power-down/power-up/startup sequence up to `OV2722_POWER_UP_RETRY_NUM`. Streaming itself is a single write to `OV2722_SW_STREAM`.

Exposure control is serialized by `input_lock`; `ov2722_s_exposure()` validates analog gain is nonzero, then writes timing, exposure, analog gain, and digital gain registers. Querying exposure reads the three exposure bytes and assembles the sensor value for EXIF/control reporting.

## State And Persistence
Persistent driver state lives in `struct ov2722_device`: the active resolution pointer, cached line timing, platform callbacks, media pad, frame format, control handler, and link-frequency control. The file also mutates file-scope globals from `ov2722.h` (`ov2722_res` and `N_RES`) during init. Sensor programming is persisted in device registers until power-down/reset. There is no disk persistence.

## Dependencies And Integration Points
The driver depends on V4L2 subdev/media controller APIs, Linux I2C transfer APIs, ACPI matching for `INT33FB`, AtomISP private UAPI (`ATOMISP_IOC_S_EXPOSURE`, `struct atomisp_exposure`), G-Min platform helpers, and `camera_sensor_platform_data` callbacks for rails, GPIOs, clocks, and CSI configuration. It integrates with AtomISP by calling `atomisp_register_i2c_module()` after media entity setup and `atomisp_gmin_remove_subdev()` on remove/failure paths.

## Risks
- I2C read errors in `ov2722_detect()` are not checked before using ID bytes, which can turn bus failures into misleading ID failures.
- `ov2722_get_fmt()` reports `MEDIA_BUS_FMT_SBGGR10_1X10` while `ov2722_set_fmt()` assigns `MEDIA_BUS_FMT_SGRBG10_1X10`; the mismatch can confuse graph negotiation.
- `ov2722_remove()` assumes `dev->platform_data` is valid; incomplete probe paths use separate cleanup, but defensive checks would reduce crash risk.
- File-scope mutable resolution globals are shared driver state and would be fragile if multiple instances ever bind.
- The retry loop in `set_fmt()` performs power cycling under `input_lock`; slow or failing hardware can block other subdev operations.
- Exposure programming updates multiple registers without explicit group-hold transaction control in the function, so partial updates may be visible on hardware if the sensor is streaming.

## Test Signals
Useful validation includes successful ACPI/I2C probe for `INT33FB`, sensor ID detection for `0x2722` or `0x2720`, V4L2 media graph registration, enumeration of three preview frame sizes, format selection and startup for each mode, stream on/off register writes, `ATOMISP_IOC_S_EXPOSURE` with zero-gain rejection, link-frequency control values matching selected mode, and fault injection for I2C failures and power callback failures.
