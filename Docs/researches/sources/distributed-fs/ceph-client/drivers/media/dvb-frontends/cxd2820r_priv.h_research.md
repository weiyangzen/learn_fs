# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2820r_priv.h

Purpose: private shared header for CXD2820R core and delivery-system implementation files.

Important APIs and types: `struct reg_val_mask` represents register, value, and mask table entries used by mode programming. `CXD2820R_CLK` defines the 41 MHz demod clock used in IF calculations. `struct cxd2820r_priv` contains the two I2C clients/regmaps, parent adapter, DVB frontend, TS/AGC/spectrum config, DVBv3/DVBv5 BER state, GPIO cache and optional `gpio_chip`, current delivery system, and `last_tune_failed`. The header declares core register/GPIO helpers and all DVB-C/T/T2 per-system entry points.

Control flow and integration: this header is the internal ABI across `cxd2820r_core.c`, `cxd2820r_c.c`, `cxd2820r_t.c`, and `cxd2820r_t2.c`. Per-system files rely on the private state layout and helper prototypes to write shared registers and update common counters.

State and persistence: defines all persistent in-memory state for the demodulator. The state persists for the life of the frontend/I2C client only.

Dependencies: DVB frontend internals, integer log helpers, GPIO driver API, math64, regmap, and the public `cxd2820r.h`.

Risks and test signals: duplicate declaration of `cxd2820r_wr_regs()` suggests header drift. Changes to struct layout or helper prototypes affect all split translation units. Test signals include compile coverage with and without `CONFIG_GPIOLIB`, all delivery-system files included, and BER/GPIO state transitions.
