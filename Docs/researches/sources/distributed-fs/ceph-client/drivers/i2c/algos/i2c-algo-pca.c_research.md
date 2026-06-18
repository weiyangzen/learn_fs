<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c

Purpose: reusable I2C master algorithm for Philips/NXP PCA9564 and PCA9665 parallel-bus I2C controllers. It exports `i2c_pca_add_bus` and `i2c_pca_add_numbered_bus`.

Important APIs and flow: hardware callbacks come from `struct i2c_algo_pca_data`: `write_byte`, `read_byte`, `wait_for_completion_cb`, optional reset, clock data, and bus settings. `pca_xfer` waits for idle status `0xf8`, then walks the PCA state machine for START, repeated START, address ACK/NAK, TX, RX, arbitration lost, and bus error statuses. `pca_reset`, `pca_probe_chip`, and `pca_init` distinguish PCA9564 from PCA9665 and program clock/mode timing.

State and dependencies: the algorithm persists per-adapter chip type, requested clock, and reset-time bus settings. It depends on I2C core message semantics and PCA register definitions from `linux/i2c-algo-pca.h`.

Risks and tests: state-machine status handling is hardware-sensitive; reset must restore PCA9665 indirect-register timing; NAK/arbitration cases can return partial progress. Test with both chip variants, invalid clock rates, NAKs, arbitration loss, stuck SDA/SCL, repeated-start transfers, and module debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c -->
