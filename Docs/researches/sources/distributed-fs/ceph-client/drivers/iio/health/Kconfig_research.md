# sources/distributed-fs/ceph-client/drivers/iio/health/Kconfig

## Purpose
Kconfig menu for IIO health sensors, currently heart-rate and pulse-oximeter AFEs/sensors.

## Important APIs, Types, And Functions
Defines visible symbols `AFE4403`, `AFE4404`, `MAX30100`, and `MAX30102`, with bus and helper selections.

## Control Flow
The menu groups health sensors under "Health Sensors" and "Heart Rate Monitors". Each symbol controls driver compilation and selects the required regmap/buffer support.

## State And Persistence
No runtime state; configuration persists in kernel build files and controls module availability.

## Dependencies And Integration Points
`AFE4403` depends on SPI_MASTER and selects REGMAP_SPI, IIO_BUFFER, and IIO_TRIGGERED_BUFFER. Other entries depend on I2C and select REGMAP_I2C plus buffer support.

## Risks
Help/module names must stay synchronized with Makefile. Missing IIO trigger/buffer selection would break driver builds or runtime buffered capture.

## Test Signals
Kconfig build combinations for SPI-only/I2C-only configs, allmodconfig, and module-name verification against Makefile outputs.
