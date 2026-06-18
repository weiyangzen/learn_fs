# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Kconfig

Purpose: defines build configuration for the legacy InvenSense MPU6050/MPU6500/ICM206xx/IAM20680 IIO driver family.

Important entries: hidden `INV_MPU6050_IIO` selects IIO buffer, triggered buffer, and timestamp helper support. `INV_MPU6050_I2C` depends on I2C, selects I2C mux support and regmap-I2C, and covers MPU6050/9150, MPU6500/6515/6880/9250/9255, ICM206xx, and IAM20680 devices. `INV_MPU6050_SPI` depends on SPI master and selects regmap-SPI for the SPI-capable subset.

Control flow and state: build-time only. Selecting either bus pulls in the shared core/ring/trigger/aux/magnetometer code.

Dependencies and integration: integrates with IIO triggered-buffer infrastructure, timestamp helper, I2C mux for auxiliary bus, and regmap transports.

Risks and tests: Kconfig coverage must reflect actual bus support; MPU6050 itself is I2C while MPU6000 is SPI. Test signals include allmodconfig builds, transport module link tests, I2C mux symbols available for I2C builds, and modpost namespace checks for `IIO_MPU6050`.
