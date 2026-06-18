# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.h

## Purpose
`fimc-is-sensor.h` defines FIMC-IS sensor ids, supported sensor constants, ISP I2C bus ids, sensor metadata structures, and the OF metadata lookup prototype.

## Important APIs, Types, and Functions
Important constants are `S5K6A3_OPEN_TIMEOUT`, `S5K6A3_SENSOR_WIDTH`, `S5K6A3_SENSOR_HEIGHT`, `enum fimc_is_sensor_id`, `IS_SENSOR_CTRL_BUS_I2C0`, and `IS_SENSOR_CTRL_BUS_I2C1`. `struct sensor_drv_data` stores firmware sensor id and open timeout. `struct fimc_is_sensor` stores matched driver data, ISP I2C bus index, and test-pattern flag. The header declares `fimc_is_sensor_get_drvdata()`.

## Control Flow
There is no executable control flow. FIMC-IS parsing and open-sensor command flow consume these definitions.

## State and Persistence
The header defines in-memory sensor state fields but does not allocate or persist them.

## Dependencies and Integration Points
It includes OF and basic type headers and is included by FIMC-IS core, register, and sensor lookup code.

## Risks and Edge Cases
The enum exposes several sensor ids but only S5K6A3 has match data in the implementation. Width/height constants are not automatically enforced by the parser. The `test_pattern` byte influences initial ISP OTF input format when set by higher-level code.

## Test Signals
Compile coverage, OF sensor parsing, firmware open command arguments, default sensor framerate selection, and test-pattern initialization paths are the relevant signals.
