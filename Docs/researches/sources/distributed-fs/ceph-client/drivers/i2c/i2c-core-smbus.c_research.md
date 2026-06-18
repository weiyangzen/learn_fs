# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-smbus.c

Purpose: always-built SMBus helper and emulation layer. It implements exported SMBus read/write convenience APIs, PEC calculation/checking, native SMBus transfer dispatch, I2C-message emulation fallback, block-read emulation, and automatic SMBus Alert client creation hook.

Important APIs: exports include `i2c_smbus_pec()`, byte/byte-data/word/block/I2C-block read-write helpers, `i2c_smbus_xfer()`, `__i2c_smbus_xfer()`, `i2c_smbus_read_i2c_block_data_or_emulated()`, `i2c_new_smbus_alert_device()`, and conditionally `i2c_setup_smbus_alert()`.

Control flow: public helpers fill `union i2c_smbus_data` and call `i2c_smbus_xfer()`. The locked wrapper calls `__i2c_smbus_xfer()`, which rejects invalid block lengths, traces, chooses native normal/atomic SMBus callbacks when available, retries arbitration loss, and falls back to `i2c_smbus_xfer_emulated()` when native support returns `-EOPNOTSUPP`. Emulation builds one or two `i2c_msg` objects, handles special protocols, optional DMA-safe temporary buffers, PEC insertion/checking, and copies replies back to the data union.

State and persistence: no persistent device state except temporary stack/heap message buffers and adapter timeout/retry effects. Alert setup instantiates a client at address `0x0c`.

Dependencies and integration: depends on I2C core transfer locking, trace events, adapter functionality bits, firmware properties for `smbus_alert`, and optional `CONFIG_I2C_SMBUS` module support.

Risks: block length validation, PEC length adjustment, and `I2C_M_RECV_LEN` buffer sizing are error-prone. Emulation only works when adapter I2C transfers support the required flags. Atomic-mode fallback requires atomic master transfers. `I2C_SMBUS_I2C_BLOCK_DATA` intentionally excludes PEC.

Test signals: native and emulated protocol tests, PEC mismatch returns `-EBADMSG`, invalid block-size `-EINVAL`, arbitration retries, tracepoint coverage, DMA temp buffer free paths, and SMBALERT auto-instantiation from IRQ/GPIO properties.
