<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/Kconfig

Purpose: top-level Kconfig menu for the Linux I2C subsystem in this source tree. It gates `CONFIG_I2C`, ACPI operation-region support, board info, the userspace character device, mux/ATR support, SMBus protocol helpers, algorithm and bus-driver menus, test stubs, slave backends, and debug switches.

Important interfaces: `CONFIG_I2C` selects `RT_MUTEXES` and `IRQ_DOMAIN`; `ACPI_I2C_OPREGION` depends on built-in I2C plus ACPI; `I2C_CHARDEV`, `I2C_MUX`, `I2C_ATR`, `I2C_SMBUS`, `I2C_STUB`, `I2C_SLAVE`, `I2C_SLAVE_EEPROM`, and `I2C_SLAVE_TESTUNIT` define public build surfaces. It sources `drivers/i2c/muxes/Kconfig`, `algos/Kconfig`, and `busses/Kconfig`.

Control flow and state: this file has no runtime logic. Its persistence is Kconfig state saved in kernel configuration and used by kbuild to choose objects. Dependencies integrate I2C with ACPI, OF, slave support, debug flags, and helper auto-selection.

Risks and tests: incorrect dependency changes can hide drivers, break module/built-in link order, or expose helpers without core support. Test by running Kconfig sync/olddefconfig, checking expected symbols in `.config`, and building I2C core plus representative algorithm, bus, slave, and debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Kconfig -->
