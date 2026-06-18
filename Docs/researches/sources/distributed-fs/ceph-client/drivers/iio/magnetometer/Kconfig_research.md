<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig

Purpose: Kconfig menu for Linux IIO magnetometer and Hall-effect sensor drivers. It declares user-visible driver options, hidden shared-core symbols, bus-wrapper symbols, dependencies, selected helper subsystems, and module names for the magnetometer directory.

Important APIs/types/functions: this is declarative Kconfig, not C code. Key user-visible symbols include `AF8133J`, `AK8974`, `AK8975`, `ALS31300`, `BMC150_MAGN_I2C`, `BMC150_MAGN_SPI`, `MAG3110`, `HID_SENSOR_MAGNETOMETER_3D`, `MMC35240`, `MMC5633`, `IIO_ST_MAGN_3AXIS`, `INFINEON_TLV493D`, `SENSORS_HMC5843_I2C`, `SENSORS_HMC5843_SPI`, `SENSORS_RM3100_I2C`, `SENSORS_RM3100_SPI`, `SI7210`, `TI_TMAG5273`, and `YAMAHA_YAS530`. Hidden core symbols include `BMC150_MAGN`, `SENSORS_HMC5843`, and `SENSORS_RM3100`.

Control flow: menuconfig processing presents `menu "Magnetometer sensors"` and enables objects indirectly through selected symbols. Bus wrappers select shared cores and regmap backends: BMC150 I2C/SPI select `BMC150_MAGN`, HMC5843 I2C/SPI select `SENSORS_HMC5843`, and RM3100 I2C/SPI select `SENSORS_RM3100`. Several drivers select `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER` when buffered capture is implemented.

State/persistence: Kconfig choices are persisted in the kernel `.config`; no runtime state exists. Hidden symbols ensure shared core objects are built only when a supported bus front-end is enabled.

Dependencies/integration: integrates with the kernel build system, I2C/SPI/I3C/HID subsystems, regmap, IIO buffers/triggers, `GPIOLIB`, `OF`, `SYSFS`, `HID_SENSOR_HUB`, and ST sensor helper libraries. It also carries compatibility/deprecation policy such as `AK09911` selecting `AK8975`.

Risks: dependency drift can break builds if a driver starts using a helper without selecting or depending on it. Hidden shared-core symbols must stay aligned with `Makefile` object names and module namespace imports. Help text and module names must remain accurate for package builders.

Test signals: run `make olddefconfig`, `make menuconfig`, and targeted `make M=drivers/iio/magnetometer` for representative built-in/module combinations across I2C, SPI, I3C, HID, OF, and COMPILE_TEST configurations. Confirm every selected symbol produces the intended object list and all hidden cores are built when wrappers require them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig -->
