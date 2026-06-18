# sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.h

Purpose: public attach header for the legacy MT20xx Microtune driver.

Important APIs/types: includes Linux I2C and DVB frontend headers, declares `microtune_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c_adap, u8 i2c_addr)` when `CONFIG_MEDIA_TUNER_MT20XX` is reachable, and provides a warning stub returning `NULL` otherwise.

Control flow and integration: board/tuner-core code calls `microtune_attach()` with a frontend, I2C adapter, and tuner I2C address. The C file detects the chip and populates `fe->ops.tuner_ops` with MT2032 or MT2050 operations.

State and persistence: no state is defined here; private state is in `mt20xx.c`.

Dependencies: relies on `struct dvb_frontend`, `struct i2c_adapter`, Kconfig reachability, `printk()`, and fixed-width integer types available through included kernel headers.

Risks: as an attach-only legacy interface, failures are signaled by `NULL`; callers must handle unsupported chips and disabled Kconfig gracefully. There is no public config structure for board-specific IF or antenna quirks; behavior is controlled by module parameters and hard-coded logic in the C file.

Test signals: build with enabled/disabled Kconfig, verify call sites handle `NULL`, and test that expected board code passes the correct I2C address.
