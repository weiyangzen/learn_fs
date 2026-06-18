## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/stef48h28.c

Purpose: provides static PMBus hwmon support for the ST STEF48H28 controller/eFuse.

Important APIs, types, and functions: `stef48h28_info` declares one page, direct formats for voltage/current/power/temperature, direct coefficients, and a broad function mask including VIN, VOUT, IIN, IOUT, PIN, POUT, TEMP1/TEMP2, and related statuses. `stef48h28_probe()` delegates to `pmbus_do_probe()`.

Control flow: module registers an I2C driver with OF and I2C IDs. Probe has no custom detection or callbacks; the PMBus core handles attribute creation and SMBus runtime access.

State and persistence behavior: no private state, no hardware configuration writes, and no custom persistence behavior.

Dependencies and integration points: depends on PMBus core for conversion, status, sysfs, and fault handling. Device tree compatible is `st,stef48h28`.

Risks and test signals: risk centers on coefficient correctness and whether all declared sensors/status registers exist on hardware. Test direct scaling for all classes, TEMP2 exposure, and alarms for input/output/current/temperature.
