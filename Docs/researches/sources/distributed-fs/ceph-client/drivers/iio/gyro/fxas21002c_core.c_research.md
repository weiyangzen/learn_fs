# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_core.c

## Purpose
Common IIO core for the NXP FXAS21002C 3-axis gyroscope, providing raw temperature/axis reads, scale/range, ODR, LPF/HPF controls, optional data-ready trigger, triggered buffers, regulators, and runtime/system PM.

## Important APIs, Types, And Functions
`struct fxas21002c_data` tracks chip ID, mode/previous mode, mutex, regmap and fields, trigger, timestamp, IRQ, regulators, and scan buffer. Key functions include field conversion helpers, `fxas21002c_mode_get/set`, `fxas21002c_write`, PM get/put, temp/axis reads, ODR/filter/scale get/set, raw sysfs handlers, trigger handler and IRQ thread, chip init, trigger probe, regulator helpers, core probe/remove, and PM callbacks.

## Control Flow
Core probe allocates IIO state, allocates every regmap field, enables regulators, registers a power-disable action, validates chip ID, initializes standby mode and 200 Hz ODR, optionally sets up an IRQ-backed trigger, installs triggered buffer support, enables runtime PM autosuspend, then registers the IIO device. Writes that require standby/ready transitions go through `fxas21002c_write`.

## State And Persistence
Hardware state includes active/ready mode bits, ODR, LPF/HPF, range and double-range bit, interrupt routing/polarity, and regulator power. Software caches current and previous mode, timestamp from IRQ top half, and chip ID.

## Dependencies And Integration Points
Depends on regmap fields supplied by bus shims, regulators `vdd`/`vddio`, firmware IRQ properties including `INT1` and `drive-open-drain`, IIO triggers/buffers, runtime PM, and namespace exports for bus modules.

## Risks
Mode transitions and `prev_mode` are central; failures mid-write can leave the sensor in READY. `fxas21002c_regulators_get` uses `dev->parent`, so bus-device hierarchy matters. The trigger probe logs INT2 even after selecting INT1. The source includes a duplicated `*val = 0;` in HPF read.

## Test Signals
Probe over I2C and SPI, validate both chip IDs, read/write ODR, LPF, HPF, and scale including invalid ODR/filter combinations, enable buffered capture with IRQ, test rising/open-drain interrupt properties, and exercise runtime/system suspend/resume.
