<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h -->
# Research: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h

`stv6110x_priv.h` contains private logging, bitfield, clock, and state definitions for `stv6110x.c`. It is not a public board-driver interface.

The logging section defines verbosity levels and `dprintk()`, which selects kernel log levels based on the module parameter `verbose` declared in the C file. Bitfield helpers `STV6110x_SETFIELD()` and `STV6110x_GETFIELD()` depend on field offset/width macros from `stv6110x_reg.h`; they are used throughout the tuner code to update shadow registers. Utility macros include `MAKEWORD16`, `LSB`, `MSB`, `TRIALS`, `R_DIV`, and reference clock conversions.

`struct stv6110x_state` is the driver's runtime state: DVB frontend pointer, I2C adapter, config pointer, eight-byte register cache, and devctl pointer. This state persists for the lifetime of the attached tuner or I2C client and is freed by release/remove.

Dependencies are the public `stv6110x_config`/`devctl` declarations, register layout macros, and the `verbose` variable in the implementation. Integration is tight: the setter/getter macros assume identifiers such as `STV6110x_WIDTH_CTRL1_K` and `STV6110x_OFFST_CTRL1_K` exist, and `REFCLOCK_kHz` assumes local functions name their state pointer `stv6110x`.

Risks are macro side effects and type width limits. `STV6110x_SETFIELD()` evaluates its `mask` lvalue more than once and does not range-check `val`; oversized values can spill into neighboring bits before masking behavior is considered. The clock macros are context-sensitive and fragile outside the existing implementation style. Test signals include compile coverage after register macro changes, field set/get round trips for each register field, frequency calculations with unusual refclocks, and verbose logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stv6110x_priv.h -->
