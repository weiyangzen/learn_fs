# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-i2c.c

Purpose: exposes the FlexCop internal two-wire controller as three Linux I2C adapters for demodulator, EEPROM, and tuner access.

Important APIs/functions: exported `flexcop_i2c_request()` performs chunked register reads/writes up to four bytes per hardware transaction. `flexcop_i2c_init()` registers the three adapters and marks `FC_STATE_I2C_INIT`; `flexcop_i2c_exit()` unregisters them. `flexcop_master_xfer()` adapts Linux `i2c_msg` sequences to FlexCop register operations. Internal `flexcop_i2c_operation()` starts a transfer and polls `tw_sm_c_100`.

Control flow: `master_xfer` serializes through `fc->i2c_mutex`, treats common one-byte/zero-byte read probes as successful no-ops, folds write-then-read message pairs into read requests, and maps other messages to writes. Request handling splits large buffers into four-byte transfers, increments base addresses, and retries reads for known card/gate quirks.

State/persistence: adapter state lives in `fc->fc_i2c_adap[]`, including port and `no_base_addr`; no persistent storage. Hardware state is reset per transfer by writing zero then command into `tw_sm_c_100`.

Dependencies/integration: depends on FlexCop IBI register definitions, Linux I2C core, device type `FC_SKY_REV27` workaround, and callers such as EEPROM/frontend/tuner setup.

Risks/test signals: polling limit (`FC_MAX_I2C_RETRIES`) can busy-loop; unsupported probe reads are intentionally faked. Tests should cover multi-chunk transfers, no-base-address writes, read retry behavior, adapter registration unwind, mutex interruption, and error mapping to `-EREMOTEIO`/`-ERESTARTSYS`.
