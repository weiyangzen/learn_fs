## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600.h

Purpose: central shared header for the InvenSense ICM-426xx driver family. It defines chip variants, register addresses/fields, configuration/state structures, timing constants, and cross-object APIs.

Important APIs, types, and functions: enums cover chips, bus slew rates, sensor modes, gyro/accel full-scale values including ICM42686-specific ranges, ODRs, and filters. `struct inv_icm42600_conf` stores current gyro/accel/temp config; `struct inv_icm42600_state` is the shared device state containing lock, chip/name/regmap, vddio regulator, IRQ, orientation, active config, suspended config, gyro/accel IIO devices, interrupt timestamps, APEX/WoM state, FIFO state, and DMA-aligned scratch buffer. `struct inv_icm42600_sensor_state` is per-IIO-device state for scale table, desired power mode/filter, and timestamp helper. The header declares regmap configs, PM ops, probe/init functions, sensor configuration setters, FIFO parser hooks, debugfs access, and WoM event helpers.

Control flow: bus wrappers call `inv_icm42600_core_probe()` with a chip ID and bus setup callback. Core initializes `struct inv_icm42600_state`, then gyro/accel/temp/buffer objects interact through the declared functions and shared state. FIFO decode/parse APIs bridge the common buffer code to the per-sensor parsers.

State and persistence behavior: the header documents the split between chip-global state and per-sensor IIO state. Runtime/system suspend stores prior sensor modes in `struct inv_icm42600_suspended`. APEX/WoM state persists threshold and enable flags. FIFO state persists enable bits, sample period, requested/effective watermarks, counters, and the 2080-byte FIFO buffer.

Dependencies and integration points: depends on regmap, mutex, regulators, IIO core, mount matrices, common InvenSense timestamp helper, and `inv_icm42600_buffer.h`. Register definitions span virtual banked addresses, FIFO configuration, interrupt routing, timestamp, interface, power, APEX/WoM, and calibration offset registers.

Risks and edge cases: many register fields are banked virtual addresses, so regmap range setup must match these constants. ODR enum values are not dense from zero and include reserved entries, so array indexing must respect `INV_ICM42600_ODR_NB`. Shared `st->buffer` is small and protected by `st->lock`; callers must hold the lock when using it across register operations.

Test signals: compile all common objects against the header, verify all chip IDs map to valid WHOAMI/default configs, exercise ODR-to-period mapping for every exposed ODR, and validate suspend/FIFO/APEX state interactions.
