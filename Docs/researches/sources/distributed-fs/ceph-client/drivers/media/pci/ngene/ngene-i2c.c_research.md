# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-i2c.c

Purpose: Implements Linux I2C adapters for nGene channels by translating I2C transfers into firmware commands sent through the core `ngene_command()` API.

Important APIs, types, and functions: `ngene_command_i2c_read()` builds `CMD_I2C_READ` firmware commands, validates the returned address byte, and copies read data. `ngene_command_i2c_write()` builds `CMD_I2C_WRITE`. `ngene_i2c_set_bus()` switches external I2C bus routing through GPIO commands when card metadata requests it. `ngene_i2c_master_xfer()` is the adapter transfer implementation, and `ngene_i2c_init()` registers one adapter for a channel.

Control flow: `ngene_i2c_master_xfer()` locks `dev->i2c_switch_mutex`, switches bus to the channel number if needed, then supports three patterns: write followed by read, single write, and single read. Successful firmware commands return `num`; unsupported patterns or command failures return `-EIO`. Adapter initialization sets the channel as adapter data, names it "nGene", assigns algorithm callbacks, sets the PCI device parent, and calls `i2c_add_adapter()`.

State and persistence: I2C routing state is `dev->i2c_current_bus`. The function also uses channel number and card `i2c_access` flags. No transfer queue or cache is maintained in this file; firmware and hardware own actual bus state.

Dependencies and integration points: Depends on `ngene_command()` and `ngene_command_gpio_set()` from core, card metadata from `struct ngene_info`, and Linux I2C core. Two adapters are registered by `ngene_start()` and later removed by `ngene_stop()`.

Risks: Only simple I2C transfer shapes are supported; SMBus emulation may generate patterns not accepted here despite `I2C_FUNC_SMBUS_EMUL` being advertised. Read length and write length are packed into firmware buffers sized for short commands, so callers rely on I2C core/device drivers to keep transactions within protocol limits. Bus switching uses GPIO commands and must remain serialized with the mutex.

Test signals: Validate accepted single write, single read, and write-read transfers; reject multi-message non-read patterns; bus switching for cards with `i2c_access & 2`; firmware error mapping; returned-address mismatch; and concurrent transfers on both registered adapters.
