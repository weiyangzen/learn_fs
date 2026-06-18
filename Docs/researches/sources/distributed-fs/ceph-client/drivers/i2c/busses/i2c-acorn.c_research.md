<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c

Purpose: Acorn IOC/IOMD platform I2C adapter implemented through the generic bit-banging algorithm. It targets the Acorn system bus where devices such as PCF8583 RTC/static RAM live.

Important APIs and flow: `ioc_setscl`, `ioc_setsda`, `ioc_getscl`, and `ioc_getsda` manipulate `IOC_CONTROL` bits while preserving unrelated control bits. `force_ones` tracks output values for SCL/SDA and fixed high bits. `ioc_data` provides `struct i2c_algo_bit_data` with 80 us delay and HZ timeout; `ioc_ops` defines numbered adapter 0. `i2c_ioc_init` initializes SCL/SDA high and calls `i2c_bit_add_numbered_bus`.

State and dependencies: state is global `force_ones` and IOC hardware register contents. It depends on Acorn architecture headers, raw IOC I/O helpers, and `i2c-algo-bit`.

Risks and tests: preserving non-I2C bits in `IOC_CONTROL` is critical; there is no remove path because this is init-only platform support. Test on ARCH_ACORN or compile coverage, line toggling, bit-algo bus test, and adapter numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c -->
