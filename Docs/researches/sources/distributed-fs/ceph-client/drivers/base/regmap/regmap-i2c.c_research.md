<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c

Purpose: Implements regmap access over I2C and SMBus, choosing the best available transfer method for a client adapter and honoring adapter length quirks.

Important APIs/types/functions: Key bus implementations are `regmap_i2c`, `regmap_i2c_smbus_i2c_block`, `regmap_i2c_smbus_i2c_block_reg16`, `regmap_smbus_byte_word_reg16`, `regmap_smbus_byte`, `regmap_smbus_word`, and `regmap_smbus_word_swapped`. `regmap_get_i2c_bus()` selects and possibly clones a bus. `__regmap_init_i2c()` and `__devm_regmap_init_i2c()` export initialization.

Control flow: Selection prefers raw I2C transfers, then SMBus I2C block for 8-bit values with 8- or 16-bit registers, then a byte/word fallback for 16-bit EEPROM-style addresses, then SMBus word or byte operations. Raw I2C writes use `i2c_master_send()`, gather writes use two-message `I2C_M_NOSTART` when supported, and reads use write-then-read messages. SMBus paths validate register/value sizes and translate partial transfers into `-EIO`. If adapter quirks cap message sizes, the code duplicates the bus definition, sets `free_on_exit`, and adjusts max raw read/write sizes.

State and persistence behavior: No per-client state is owned except optional cloned `struct regmap_bus` data freed by the regmap core when `free_on_exit` is set. Underlying device state is external.

Dependencies and integration points: Depends on I2C/SMBus APIs, adapter functionality flags, adapter quirks, endian selection, and regmap core formatting. This is the canonical I2C bridge for many kernel drivers using `devm_regmap_init_i2c()`.

Risks: Transfer capability fallback changes semantics and maximum raw lengths. The SMBus 16-bit register fallback supports only single-byte writes. The reg16 SMBus read path uses a write-byte-data address setup followed by current-address byte reads, so it assumes devices auto-increment as described. Incorrect endian settings for SMBus word values lead to swapped data. Gather write may fall back through the core when `I2C_FUNC_NOSTART` is absent.

Test signals: Exercise adapter capability matrices, quirk truncation, big/little 16-bit word values, partial-transfer `-EIO`, and reg16 EEPROM-style reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c -->
