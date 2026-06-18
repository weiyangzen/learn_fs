# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Kconfig

Purpose: Kconfig menu for Samsung Sensor Platform sensorhub support and its IIO common layer.

Important symbols: `IIO_SSP_SENSORHUB` is the SPI-backed Samsung sensorhub driver and selects `MFD_CORE`. `IIO_SSP_SENSORS_COMMONS` depends on `IIO_SSP_SENSORHUB` and selects `IIO_BUFFER` plus `IIO_KFIFO_BUF`; it builds common IIO support for SSP sensors.

Control flow: users enable the sensorhub first, then the IIO commons layer becomes available. The local Makefile maps these to `sensorhub` and `ssp_iio` objects.

State and persistence: no runtime state here. It defines build-time dependencies and menu visibility.

Dependencies and integration: ties SPI, MFD core, sensorhub transport, and IIO buffered sensor support together.

Risks and test signals: enabling commons without sensorhub would be invalid and is prevented by dependency. Test signals are Kconfig resolution, module names matching help text, and builds with SPI and MFD dependencies enabled.
