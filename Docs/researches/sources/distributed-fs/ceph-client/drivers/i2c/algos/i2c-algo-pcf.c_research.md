<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c

Purpose: generic algorithm for PCF8584 I2C controllers. It exports `i2c_pcf_add_bus`, initializes the chip, and exposes an I2C master algorithm.

Important APIs and flow: callbacks in `struct i2c_algo_pcf_data` read/write PCF data/control registers and supply own address, clock, wait-for-PIN, optional transfer begin/end, and arbitration-lost delay. `pcf_init_8584` performs register detection and initialization. `pcf_xfer` waits for bus free, sends an address, issues START for the first message, waits for PIN, checks LRB ACK, then uses `pcf_sendbytes` or `pcf_readbytes`. Multi-message transfers end with STOP or repeated START.

State and dependencies: state is mostly hardware register state plus adapter callbacks; arbitration loss resets control bits via `handle_lab`. It depends on I2C core, PCF public callback definitions, and local PCF bit masks.

Risks and tests: timeout constants are short and polling/callback timing is board-specific. Risks include incorrect dummy-read receive sequencing, lost arbitration recovery, and no 10-bit handling despite protocol-mangling functionality. Test PCF detection, ACK/NAK, multi-message repeated starts, LAB events, stuck bus, and begin/end hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c -->
