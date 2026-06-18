# sources/distributed-fs/ceph-client/drivers/iio/imu/Kconfig

Purpose: Kconfig menu for IIO inertial measurement unit drivers and the shared ADIS helper library.

Important APIs/types/functions: Declares ADIS IMU drivers (`ADIS16400`, `ADIS16460`, `ADIS16475`, `ADIS16480`, `ADIS16550`) with SPI dependencies and selections of `IIO_ADIS_LIB` and optionally `IIO_ADIS_LIB_BUFFER`. Includes subdirectory Kconfig files for BMI, BNO055, INV, SMI, and ST IMU families. Declares hidden/shared symbols `FXOS8700`, `IIO_ADIS_LIB`, and `IIO_ADIS_LIB_BUFFER`.

Control flow: Build-time only. Selections determine which modules and common libraries are compiled and whether triggered-buffer ADIS helpers are included.

State and persistence: Configuration persists in `.config` and module selection. No runtime state.

Dependencies and integration points: Integrates SPI, I2C, regmap transports, IIO buffers/triggers, CRC32 for some ADIS families, and nested Kconfig files.

Risks: ADIS drivers select buffer helpers only if `IIO_BUFFER`; direct-mode builds must still compile without buffer support. Alphabetical ordering is documented and should be preserved. Hidden library options must remain selected by all consumers of exported ADIS symbols.

Test signals: `allmodconfig`, `allyesconfig`, and targeted configs for ADIS with and without `IIO_BUFFER`; verify subdirectory Kconfig inclusion and module dependency resolution.
