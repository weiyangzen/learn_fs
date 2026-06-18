<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c

Purpose: I2C transport wrapper for the CMA3000-D0x accelerometer core.

Important APIs/types/functions: `cma3000_i2c_set()` and `cma3000_i2c_read()` wrap SMBus byte writes/reads and log message-specific errors. `cma3000_i2c_bops` sets `BUS_I2C` and I2C control mode. Probe delegates to `cma3000_init()`, remove calls `cma3000_exit()`, and PM calls core suspend/resume.

Control flow and state: probe creates core state and stores it in clientdata. Remove and PM retrieve that pointer and delegate. The module registers an I2C driver for `cma3000_d01`.

State and persistence behavior: this file owns no independent state beyond clientdata. Core controls hardware mode and input state.

Dependencies and integration points: depends on I2C SMBus byte APIs, local `cma3000_d0x.h`, `linux/input/cma3000.h`, and module I2C registration.

Risks: no explicit I2C functionality check is performed before SMBus operations. PM assumes clientdata exists and core init completed.

Test signals: test read/write error logging, probe failure propagation, remove cleanup, suspend/resume delegation, and binding by I2C ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c -->
