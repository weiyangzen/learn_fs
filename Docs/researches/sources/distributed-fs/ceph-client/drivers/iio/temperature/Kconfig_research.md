# sources/distributed-fs/ceph-client/drivers/iio/temperature/Kconfig

Purpose: Kconfig menu for IIO temperature sensor drivers. It includes the requested IQS620AT, LTC2983, Maxim thermocouple, HID temperature, MAX30208, MAX31856, MAX31865, and MCP9600 options plus other temperature drivers in the folder.

Important APIs/types/functions: no runtime APIs. Symbols declare bus and subsystem dependencies such as MFD_IQS62X, SPI, I2C, HID_SENSOR_HUB, REGMAP_SPI/I2C, IIO_BUFFER, IIO_TRIGGERED_BUFFER, and HID sensor common/trigger helpers.

Control flow: each tristate option controls whether the corresponding object can be built in or as a module. Help text names supported chips and module names.

State and persistence: selected options persist in kernel configuration and drive Kbuild. There is no runtime state.

Dependencies/integration: integrates with the temperature Makefile and with subsystem dependency selection. `MAXIM_THERMOCOUPLE` and `HID_SENSOR_TEMP` select buffer support because their drivers use triggered buffers.

Risks and test signals: dependency mismatch can produce compile failures or missing modules. Test all requested symbols under `m`, `y`, and COMPILE_TEST where applicable; compare module names with Makefile object names.
