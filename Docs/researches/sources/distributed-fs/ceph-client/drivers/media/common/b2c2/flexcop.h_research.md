# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.h

Purpose: private FlexCop chip-source header that sets the log prefix, includes common FlexCop declarations, and defines debug-print categories.

Important APIs/types: declares `extern int b2c2_flexcop_debug`; defines `dprintk(level, args...)` under `CONFIG_DVB_B2C2_FLEXCOP_DEBUG`; category macros include `deb_info`, `deb_tuner`, `deb_i2c`, `deb_ts`, `deb_sram`, `deb_rdump`, and `deb_i2c_dump`.

Control flow: debug logging compiles to a runtime bitmask check when debug is enabled and to `no_printk` otherwise, preserving format checking without emitting code.

State/persistence: no owned state; logging behavior depends on the module parameter defined in `flexcop.c`.

Dependencies/integration: all common FlexCop C files include this header. It depends on `flexcop-common.h` for the actual device structure, exported prototypes, and Linux media definitions.

Risks/test signals: mismatched debug bit documentation and macro definitions can make field diagnosis harder. Build tests with debug enabled and disabled are the main signal; runtime tests can verify category bits emit expected logs without affecting non-debug builds.
