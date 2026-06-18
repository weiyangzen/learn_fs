<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c

Purpose: generic bit-banging I2C master algorithm for adapters that expose callbacks to set/read SDA and SCL. It exports `i2c_bit_algo`, `i2c_bit_add_bus`, and `i2c_bit_add_numbered_bus`.

Important APIs and flow: `struct i2c_algo_bit_data` callbacks drive `sdalo`, `sdahi`, `scllo`, and `sclhi`; `sclhi` waits for clock stretching up to `adap->timeout`. `bit_xfer` runs optional `pre_xfer`, emits START/repeated START/STOP, calls `bit_doAddress`, then `sendbytes` or `readbytes`. Reads support `I2C_M_RECV_LEN`; addressing supports 7-bit, 10-bit, `I2C_M_REV_DIR_ADDR`, `I2C_M_IGNORE_NAK`, `I2C_M_NOSTART`, and `I2C_M_STOP`. `bit_xfer_atomic` reuses the normal path after warning if the adapter is not marked atomic-capable.

State and dependencies: per-adapter state lives in callback data, `udelay`, `timeout`, quirks, and optional pre/post hooks. Module parameters `bit_test` and debug level influence diagnostics. Integration is through `i2c_adapter.algo` and I2C core registration.

Risks and tests: clock-stretch timeouts, write-only line callbacks, incomplete arbitration handling, and invalid SMBus block lengths are key risks. Test with GPIO-backed adapters, forced NAK/timeouts, `bit_test=2`, SMBus emulation, 10-bit addressing, and atomic-transfer callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c -->
