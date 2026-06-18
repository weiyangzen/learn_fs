# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-sensor.c

## Purpose
`fimc-is-sensor.c` maps OF sensor compatible strings to FIMC-IS firmware sensor metadata.

## Important APIs, Types, and Functions
It defines `s5k6a3_drvdata` with firmware sensor id `FIMC_IS_SENSOR_ID_S5K6A3` and open timeout `S5K6A3_OPEN_TIMEOUT`. The OF match table recognizes `samsung,s5k6a3`. `fimc_is_sensor_get_drvdata()` returns the matched `struct sensor_drv_data`.

## Control Flow
FIMC-IS probe scans ISP I2C child nodes and calls `fimc_is_sensor_get_drvdata()` for each sensor node. This function performs `of_match_node()` and returns match data or `NULL`.

## State and Persistence
The only state is static constant match data. Runtime sensor state is stored in `struct fimc_is_sensor` in `fimc-is.h`.

## Dependencies and Integration Points
The file depends on OF matching and `fimc-is-sensor.h`. FIMC-IS uses the returned id and timeout in `fimc_is_parse_sensor_config()` and `fimc_is_hw_open_sensor()`.

## Risks and Edge Cases
Only S5K6A3 is supported here. Additional sensors require both firmware id metadata and OF match entries. A missing match causes FIMC-IS sensor parsing to fail probe/init for that sensor.

## Test Signals
Validate OF matching for `samsung,s5k6a3`, rejection of unsupported sensors, correct firmware id passed in `HIC_OPEN_SENSOR`, and timeout behavior using the S5K6A3 open timeout.
