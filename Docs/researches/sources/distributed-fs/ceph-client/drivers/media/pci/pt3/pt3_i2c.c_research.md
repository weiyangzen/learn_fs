# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3_i2c.c

Purpose: Implements the PT3 custom I2C adapter by translating Linux I2C messages into compact FPGA command nibbles written into the board's internal memory, then triggering the FPGA sequencer.

Important APIs, types, and functions: `enum ctl_cmd` defines encoded line-control commands. `cmdbuf_add()`, `put_start()`, `put_byte_write()`, `put_byte_read()`, `put_stop()`, and `translate()` build the command stream in `struct pt3_i2cbuf`. `send_i2c_cmd()` runs a translated command at an internal memory address and waits for status. Exported functions are `pt3_i2c_master_xfer()`, `pt3_i2c_functionality()`, `pt3_i2c_reset()`, `pt3_init_all_demods()`, and `pt3_init_all_mxl301rf()`.

Control flow: Normal transfers reject `I2C_M_RECV_LEN`, translate all messages into command nibbles, copy the command bytes to BAR2 internal memory at `PT3_I2C_BASE`, run the normal command address, then copy read data back from internal memory. Board initialization paths run pretranslated ROM sequences for all demods and for the two MXL301RF tuners. `wait_i2c_result()` polls `REG_I2C_R` until `STAT_SEQ_RUNNING` clears and fails on timeout or sequencer error.

State and persistence: `pt3->i2c_buf` holds transient translated command data. Hardware sequencer state is reset by `pt3_i2c_reset()` and represented by status bits in `REG_I2C_R`. Hidden ROM command sequences persist in the FPGA/board, not in driver memory.

Dependencies and integration points: Registered as the board's I2C algorithm in `pt3.c`. Used by module-probed demod/tuner drivers and by board-wide initialization in `pt3_fe_init()`. Requires both BAR0 registers and BAR2 internal memory to be mapped.

Risks: `memcpy_toio()` length uses `cbuf->num_cmds`, which counts nibbles, not bytes; because commands are packed two per byte and bounded by array writes, this may copy extra stale command bytes beyond the packed stream unless the hardware ignores them after `I_END`. The code bounds data writes in `cmdbuf_add()` but does not fail if too many commands are generated, so oversized I2C messages can silently truncate commands. Only plain I2C functionality is advertised, and SMBus block receive is explicitly unsupported.

Test signals: Validate command translation for write, read, repeated starts, ACK/NACK command positions, odd command counts and end padding, maximum message lengths near `PT3_I2C_MAX`, sequencer timeout/error handling, ROM init command addresses, readback offset ordering, and rejection of `I2C_M_RECV_LEN`.
