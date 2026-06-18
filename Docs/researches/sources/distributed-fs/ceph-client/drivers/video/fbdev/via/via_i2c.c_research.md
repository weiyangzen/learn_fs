<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c

Purpose: Platform I2C driver for VIA display I2C/GPIO-backed ports. It creates bit-banged I2C adapters from the port configuration supplied by `via-core.c` and exposes byte read/write helpers for LVDS/TMDS and EDID code.

Important APIs/types/functions: Public helpers are `viafb_i2c_readbyte()`, `viafb_i2c_writebyte()`, `viafb_i2c_readbytes()`, `viafb_find_i2c_adapter()`, `viafb_i2c_init()`, and `viafb_i2c_exit()`. Bit algorithm callbacks are `via_i2c_setscl()`, `via_i2c_getscl()`, `via_i2c_setsda()`, and `via_i2c_getsda()`. Platform hooks are `viafb_i2c_probe()` and `viafb_i2c_remove()`, with `create_i2c_bus()` setting up `i2c_algo_bit_data`.

Control flow and state: Probe stores the singleton `i2c_vdev`, scans up to `VIAFB_NUM_PORTS`, and creates adapters only for configs with a nonzero type and `VIA_MODE_I2C`. Each adapter uses the same static `via_i2c_par[]` entry for algorithm, adapter, and active flag. Read/write helpers check `is_active`, build I2C messages using `target_addr / 2`, and normalize successful transfer counts to zero. Remove deletes active adapters.

Dependencies and integration points: Depends on platform devices from `via-core.c`, `linux/via-core.h`, `linux/via_i2c.h`, I2C bit-bang support, delay, and register helpers protected by `vdev->reg_lock`. Used by `via_aux.c`, `lcd.c`, `vt1636.c`, and DVI/LVDS sensing code. Risks include singleton state, old 8-bit target-address convention (`/ 2`), very short timeout (`2`), shared GPIO/I2C register bits, and no per-adapter locking beyond register access. Test signals are adapter registration, EDID reads, VT1636/VT1631 ID reads, GPIO-backed I2C on port 2C, inactive adapter `-ENODEV`, and removal without stale active flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_i2c.c -->
