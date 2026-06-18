# sources/distributed-fs/ceph-client/drivers/iio/temperature/Makefile

Purpose: Kbuild mapping from IIO temperature Kconfig symbols to object files.

Important APIs/types/functions: requested mappings include `iqs620at-temp.o`, `ltc2983.o`, `hid-sensor-temperature.o`, `maxim_thermocouple.o`, `max30208.o`, `max31856.o`, `max31865.o`, and `mcp9600.o`. The file also maps MLX/TMP/TSYS drivers.

Control flow: Kbuild conditionally compiles each object based on the associated `CONFIG_*` symbol.

State and persistence: no runtime state; output is determined by kernel config.

Dependencies/integration: must stay synchronized with Kconfig symbols and source filenames. It is the final connection between selected options and built modules.

Risks and test signals: typos in object names or duplicated symbols can hide build coverage issues. Test requested temperature configs as modules and built-ins, and verify that each module name matches help text.
