<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c

Purpose: Provides regmap support for 1-Wire slaves using simple command sequences for 8/8, 8/16, and 16/16 register/value formats.

Important APIs/types/functions: Read/write callbacks are `w1_reg_a8_v8_*`, `w1_reg_a8_v16_*`, and `w1_reg_a16_v16_*`. Bus definitions are `regmap_w1_bus_a8_v8`, `regmap_w1_bus_a8_v16`, and `regmap_w1_bus_a16_v16`. `regmap_get_w1_bus()`, `__regmap_init_w1()`, and `__devm_regmap_init_w1()` provide selection and initialization.

Control flow: Each operation obtains the `w1_slave` from the device, validates the register fits the selected address width, locks the master bus mutex, resets/selects the slave, emits either `W1_CMD_READ_DATA` or `W1_CMD_WRITE_DATA`, sends little-endian address bytes, and reads or writes little-endian value bytes. Reset/select failure returns `-ENODEV`.

State and persistence behavior: No adapter state is stored. The only transient state is the bus mutex and command bytes on the 1-Wire master.

Dependencies and integration points: Depends on W1 core primitives and regmap core. It allows simple 1-Wire device drivers to use regmap abstractions.

Risks: Values are not range-checked before byte writes, so regmap value width must constrain callers. All multi-byte values are little-endian by command order. The bus mutex serializes access, but slow 1-Wire transactions can block other devices on the master. Only three fixed format combinations are supported.

Test signals: Validate format selection, register bounds, reset/select failure handling, exact command/address/value byte sequences, and bus mutex coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c -->
