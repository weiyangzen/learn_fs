# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-i2c.c

Purpose: I2C adapter implementation for MxL111SF devices. It supports a software bit-banged bus for v6 silicon and a USB-command-driven hardware I2C engine for newer revisions, exposing a single `master_xfer` used by demods, tuners, EEPROM, and GPIO expanders.

Important APIs/types/functions: `mxl111sf_i2c_xfer()` is the exported adapter entry point. Software helpers implement start/stop, ACK/NACK, byte send/receive, and `mxl111sf_i2c_sw_xfer_msg()`. Hardware helpers build 26-byte USB I2C command buffers using `USB_WRITE_I2C_CMD`, `USB_READ_I2C_CMD`, `I2C_*` register constants, `mxl111sf_i2c_send_data()`, `mxl111sf_i2c_get_data()`, status/fifo polling, and `mxl111sf_i2c_hw_xfer_msg()`.

Control flow: the main driver's I2C algorithm calls `mxl111sf_i2c_xfer()`, which locks `d->i2c_mutex`, chooses hardware I2C when `state->chip_rev > MXL111SF_V6`, loops each `i2c_msg`, and returns `num` or `-EREMOTEIO`. Software mode emits start, address byte, payload bytes or reads, ACKs all but the last byte, NACKs at the end, and stops. Hardware mode enables the I2C mux, writes control/slave/address/timeout commands, transfers data in 8-byte blocks plus leftover bytes, retries FIFO-empty read tails through `mxl111sf_i2c_readagain()`, then disables the mux and stops.

State and persistence: no private allocation exists here; it uses `mxl111sf_state`, the bridge USB control buffers, chip revision, and the shared I2C mutex. Hardware engine configuration is transient per message, but the function attempts to deinitialize the mux at exit.

Dependencies and integration: depends on the shared MxL111SF register/control message APIs in `mxl111sf.c`, Linux I2C core, and chip revision discovery. All board EEPROM reads, tuner/demod register access, and PCA9534 GPIO operations pass through this adapter.

Risks: hardware mode is complex and frequently ignores return values from cleanup/status helper calls, so a failed STOP/deinit can be hidden. `mxl111sf_i2c_check_status()` and FIFO polling return only a boolean and do not propagate USB errors. Software mode has a FIXME that it stops after every write transaction, which can break combined transactions that require repeated-start semantics. Hardware write lengths are not explicitly capped against the 8-byte block protocol beyond the 26-byte command buffer shape.

Test signals: v6 bitbang transfers for EEPROM, tuner, and demod; v8 hardware transfers for simple reads/writes and combined write-read register reads; NACK behavior against absent I2C addresses; long transfer block and leftover paths; FIFO-empty readagain path; no deadlocks under concurrent frontend/tuner access.
