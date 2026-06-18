# sources/distributed-fs/ceph-client/drivers/media/i2c/rj54n1cb0c.c

## Purpose
`rj54n1cb0c.c` implements the Sharp RJ54N1CB0C CMOS image sensor as an I2C V4L2 sub-device. It exposes one source pad, several media-bus formats, active-only crop and format programming, basic flip/gain/white-balance controls, sensor clock and GPIO power sequencing, and chip detection from legacy platform data.

## Important APIs, Types, and Functions
The driver state is `struct rj54n1`, which stores the `v4l2_subdev`, control handler, external clock, optional `powerup` and `enable` GPIOs, the cached I2C register bank, selected `rj54n1_datafmt`, crop/output geometry, resize coefficient, timing-generator clock, and clock-divider values. Low-level register access is through `reg_read()`, `reg_write()`, `reg_set()`, and `reg_write_multiple()`, which select the high-byte register bank through register `0xff` and use SMBus byte data operations.

Geometry and mode programming is centered in `rj54n1_sensor_scale()`, `rj54n1_set_rect()`, `rj54n1_set_selection()`, `rj54n1_get_selection()`, `rj54n1_get_fmt()`, and `rj54n1_set_fmt()`. Hardware bring-up uses `rj54n1_s_power()`, `rj54n1_set_clock()`, `rj54n1_reg_init()`, `rj54n1_commit()`, `rj54n1_video_probe()`, `rj54n1_probe()`, and `rj54n1_remove()`. Controls are implemented by `rj54n1_s_ctrl()`.

## Control Flow
Probe requires platform data and SMBus byte-data support. It allocates state, initializes the subdev and controls, sets default full-frame geometry and YUYV format, obtains the external clock and optional GPIOs, computes `tgclk_mhz` from platform `mclk_freq`, and calls `rj54n1_video_probe()`. Video probe powers the chip, reads the two device-code registers, programs IO polarity from platform data, runs control setup, then powers back down before async subdev registration.

Power-on asserts optional GPIOs, waits briefly, and enables the clock. Sensor register initialization is lazy: `rj54n1_set_fmt()` reads `RJ54N1_RESET_STANDBY` and calls `rj54n1_reg_init()` when the external-clock bit is not set. Format setting validates the requested bus code, bounds output size, programs output selector/byte-swap/raw alignment bits, clamps the crop to the maximum 1:16 scale, and calls `rj54n1_sensor_scale()`. Streaming only toggles still/preview mode through `RJ54N1_STILL_CONTROL`.

## State and Persistence
All persistent state is in the in-memory `struct rj54n1`; hardware state lives in volatile sensor registers. The driver caches the currently selected register bank and geometry but has no runtime PM state, firmware file, or filesystem persistence.

## Dependencies and Integration Points
The file depends on Linux I2C SMBus byte-data transfers, clocks, GPIO descriptors, V4L2 subdev/control/media-bus APIs, `media/i2c/rj54n1cb0c.h` platform data, and async subdev registration. It integrates with board code through legacy platform data rather than device tree.

## Risks and Edge Cases
The driver is active-format only for crop/selection and rejects TRY selection. There is no lock around most state updates or register-bank caching, so concurrent control and format calls rely on higher-level serialization. The scaling algorithm contains sensor-specific prohibited resize ranges and long fixed sleeps. `rj54n1_s_ctrl()` writes hardware unconditionally and can fail if controls are set while the chip is powered down. Probe requires platform data, so OF-only systems cannot bind it as written.

## Test Signals
Useful signals include successful ID read `0x51:0x10`, correct clock/GPIO sequencing, SMBus bank changes without errors, successful full initialization after first active format, correct YUYV/YVYU/RGB565/raw bus-code output and byte order, stable resize/crop behavior, flip/gain/auto-white-balance controls taking effect, still/preview stream toggling, and clean async registration/removal.
