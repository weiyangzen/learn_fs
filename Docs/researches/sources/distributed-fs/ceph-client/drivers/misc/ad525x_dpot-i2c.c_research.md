## sources/distributed-fs/ceph-client/drivers/misc/ad525x_dpot-i2c.c

Purpose: this file is the I2C transport wrapper for the Analog Devices AD525x digital potentiometer core. It translates the common `ad525x_dpot` bus operations into SMBus byte/byte-data/word-data transactions and registers an I2C driver with a table of supported potentiometer part IDs.

Important APIs, types, and functions: bus callbacks `write_d8()`, `write_r8d8()`, `write_r8d16()`, `read_d8()`, `read_r8d8()`, and `read_r8d16()` populate `struct ad_dpot_bus_ops bops`. `ad_dpot_i2c_probe()` builds `struct ad_dpot_bus_data`, validates `I2C_FUNC_SMBUS_WORD_DATA`, and calls `ad_dpot_probe()`. `ad_dpot_i2c_remove()` calls `ad_dpot_remove()`. `ad_dpot_id[]` maps I2C modalias names to core chip IDs.

Control flow: I2C device matching invokes probe. Probe checks adapter SMBus word-data support, passes the client, ops table, `driver_data`, and part name to the shared core, then relies on the core for sysfs/state setup. Remove delegates cleanup to the shared core. `module_i2c_driver()` supplies module init/exit.

State and persistence: this wrapper holds no long-lived private state beyond what the shared core stores on the device. Hardware wiper/EEPROM state is accessed through SMBus transactions; sysfs persistence behavior is defined in the core.

Dependencies and integration points: depends on I2C/SMBus, module infrastructure, and local `ad525x_dpot.h`. It is built by `CONFIG_AD525X_DPOT_I2C` and paired with common `ad525x_dpot.o`.

Risks and test signals: requiring word-data support may reject adapters even for parts that only need byte operations. SMBus word endianness must match core expectations for 16-bit register values. Test signals include I2C modalias binding, SMBus functionality failure returning `-EIO`, core probe creating sysfs attributes, read/write operations on supported parts, and clean remove.
