
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-isa.c

Purpose: this driver exposes PCA9564/PCA9665 I2C controllers wired on ISA I/O ports. It provides the bus-specific register access and completion callbacks required by the generic `i2c-algo-pca` algorithm, with module parameters for base address, IRQ, and controller clock.

Important APIs, types, and functions: global parameters `base`, `irq`, and `clock` configure the ISA instance. `pca_isa_writebyte()` and `pca_isa_readbyte()` perform byte I/O with `outb()` and `inb()` at `base + reg`. `pca_isa_waitforcompletion()` either blocks on `pca_wait` until `I2C_PCA_CON_SI` is set or polls with `udelay(100)`. `pca_handler()` wakes the wait queue. `pca_isa_data` wires these callbacks into `struct i2c_algo_pca_data`; `pca_isa_ops` is the statically allocated `struct i2c_adapter`. Probe requests the I/O region, optionally requests the IRQ, sets the algorithm clock, and calls `i2c_pca_add_bus()`.

Control flow: `pca_isa_match()` requires a nonzero module-supplied base address and warns if polling mode will be used. Probe initializes the wait queue, validates legacy PPC I/O availability, reserves four I/O ports, requests the IRQ if specified, sets `i2c_clock`, and registers the adapter. Failure unwinds IRQ and region allocation. Remove deletes the adapter, disables/frees IRQ when present, and releases the I/O region.

State and persistence: the driver is effectively singleton-style because the adapter, wait queue, and configuration are static globals. Runtime transfer state is mostly held in the generic PCA algorithm; this file stores no per-transfer buffers. Configuration persists only for the module lifetime.

Dependencies and integration points: it depends on the ISA bus, module parameters, legacy I/O port allocation, optional IRQ delivery, wait queues, and `i2c-algo-pca`. It integrates into the I2C core through `i2c_pca_add_bus()` and exposes clock choices matching PCA9564/PCA9665 hardware capabilities.

Risks: there is no hardware auto-discovery; wrong `base` or `force`-style configuration can access unrelated I/O ports. The reset callback only logs that reset is unsupported, so stuck hardware may require external reset. Polling mode has coarser latency and depends on jiffies timeout. The static singleton model is inappropriate for multiple ISA adapters.

Test signals: load with valid `base`, with and without `irq`, verify adapter creation, simple I2C transfers, timeout behavior when SI never sets, region conflict handling, IRQ wakeup behavior, and unload cleanup.
