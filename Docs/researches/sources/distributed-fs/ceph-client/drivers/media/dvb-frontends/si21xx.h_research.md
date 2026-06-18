<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h

## Purpose
`si21xx.h` is the public board-driver interface for the SI21XX DVB-S demodulator driver. It defines the minimal configuration object, declares `si21xx_attach()`, and provides a small register-write helper for users that already hold a `struct dvb_frontend`.

## Important APIs, Types, And Functions
`struct si21xx_config` carries the demodulator I2C address and a `min_delay_ms` retune delay hint. When `CONFIG_DVB_SI21XX` is reachable, `si21xx_attach(const struct si21xx_config *config, struct i2c_adapter *i2c)` is available. Otherwise, the inline fallback logs that the driver is disabled and returns `NULL`, allowing board drivers to compile without the module. `si21xx_writeregister()` sends a two-byte register/value buffer through `fe->ops.write` if the attached frontend exposes it.

## Control Flow
Board code constructs a static config, calls `si21xx_attach()`, and then registers the returned frontend with the DVB adapter. Later code can call `si21xx_writeregister()`; it delegates to the frontend write op implemented in `si21xx.c` as `si21_write()`.

## State And Persistence
The header owns no state. It defines the externally supplied config that `si21xx.c` stores by pointer, so the config lifetime must outlive the frontend. Register writes persist only in hardware state.

## Dependencies And Integration Points
The header depends on `linux/dvb/frontend.h` and `media/dvb_frontend.h`. Its main integration point is board-level DVB adapter setup and optional direct frontend register access.

## Risks And Test Signals
The helper silently does nothing when `fe->ops.write` is absent, returning `0`, which can hide misuse. Config lifetime and address correctness are critical because the driver keeps a pointer rather than copying the config. Test signals are successful compilation in both enabled and disabled Kconfig states, attach success on valid hardware, and helper writes that produce visible register-side behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si21xx.h -->
