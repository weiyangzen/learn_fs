# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.c

Purpose: implements ddbridge hardware-backed I2C adapters. It maps board register metadata into Linux `i2c_adapter` instances, performs MMIO-buffered transfers, and uses ddbridge IRQ completions to wait for transaction completion.

Important APIs/types/functions: `ddb_i2c_init()` creates adapters for each link whose `i2c_mask` enables a controller; `ddb_i2c_release()` removes them. `ddb_i2c_master_xfer()` supports single read, single write, and write-then-read transactions. `ddb_i2c_cmd()` writes `I2C_COMMAND`, waits up to one second, checks hardware error bits, and logs timeout diagnostics. `i2c_handler()` completes pending commands.

Control flow: during `ddb_init()`, adapters are registered after board reset and before port probing. Port detection and frontend attach then use those adapters. IRQ dispatch from `ddbridge-core.c` invokes `i2c_handler()` through `ddb_irq_set()`.

State and persistence: each `struct ddb_i2c` stores adapter identity, link, register offsets, hardware buffer offsets, buffer size, and a completion. State is runtime-only and tied to the PCI device lifetime.

Dependencies/integration: depends on `ddbridge.h`, register constants, MMIO helpers, Linux I2C core, and board register maps from `ddbridge-hw.c`.

Risks and test signals: risks include timeout handling, I2C buffer length limits, shared read/write buffer assumptions, interrupt loss, and error propagation as generic `-EIO`. Test with probe-time frontend detection, EEPROM/temperature reads, forced absent devices, concurrent frontend gate use, and interrupt-disabled timeout paths.
