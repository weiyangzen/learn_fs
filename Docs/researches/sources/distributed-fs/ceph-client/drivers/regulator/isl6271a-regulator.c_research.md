<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c

Purpose: I2C regulator driver for the Intersil ISL6271A, exposing one programmable core buck and two fixed LDO outputs.

Important APIs/types/functions: `struct isl_pmic` stores the client and mutex. `isl6271a_get_voltage_sel()` and `_set_voltage_sel()` perform raw SMBus byte read/write for the core buck. Descriptor array `isl_rd[]` defines the core and fixed LDO regulators.

Control flow: `subsys_initcall()` registers the I2C driver. Probe checks SMBus byte-data support, allocates state, initializes the mutex, and registers all three descriptors, applying platform init data only to the core regulator.

State and persistence: the driver caches no hardware selector; it reads the core selector on demand. Fixed LDOs are static descriptors. Hardware voltage state persists in the device register.

Dependencies and integration: I2C SMBus byte operations, platform regulator init data, and regulator linear helpers.

Risks and test signals: no DT support and no enable/disable operations. The core selector is not bounds-checked before SMBus write beyond framework selector validation. Test signals include adapter functionality rejection, locked I2C access, selector read/write errors, and registration of fixed LDO voltage values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/isl6271a-regulator.c -->
