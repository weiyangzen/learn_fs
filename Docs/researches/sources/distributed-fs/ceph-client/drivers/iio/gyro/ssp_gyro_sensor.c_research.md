# sources/distributed-fs/ceph-client/drivers/iio/gyro/ssp_gyro_sensor.c

## Purpose
Samsung Sensor Platform gyroscope IIO consumer driver exposing sensorhub gyroscope data as three angular velocity channels with kfifo buffering and sample-frequency control.

## Important APIs, Types, And Functions
Uses `ssp_sensor_data` and helper macros from SSP IIO common code. Key functions are `ssp_gyro_read_raw`, `ssp_gyro_write_raw`, `ssp_process_gyro_data`, `ssp_gyro_probe`, and buffer setup ops using common SSP postenable/postdisable.

## Control Flow
Probe allocates IIO state, sets SSP process callback/type, configures channels and scan mask, sets up a kfifo buffer, registers the IIO device, then registers as an SSP gyroscope consumer. Sample frequency reads/writes convert between SSP delay and IIO frequency.

## State And Persistence
Sensor delay is stored by the parent SSP data structure. This driver stores process callback/type in IIO private data and relies on devm cleanup for buffer/IIO registration.

## Dependencies And Integration Points
Depends on Samsung SSP common sensorhub, `ssp_iio_sensor.h`, IIO kfifo buffers, platform bus name `ssp-gyroscope`, and `IIO_SSP_SENSORS` namespace.

## Risks
Parent data is reached through `indio_dev->dev.parent->parent`, so device hierarchy changes can break it. `ssp_convert_to_time` return is used directly as delay even if conversion semantics change.

## Test Signals
Probe under an SSP parent, read/write sampling frequency, enable buffer, feed sensorhub frames through `ssp_process_gyro_data`, and confirm consumer registration happens after IIO setup.
