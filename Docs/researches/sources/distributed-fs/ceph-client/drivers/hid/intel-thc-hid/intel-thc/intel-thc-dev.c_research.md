# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.c

Purpose: Intel Touch Host Controller common MMIO/regmap support. It initializes `struct thc_device`, clears controller state, exports PIO transactions, interrupt setup/decoding, LTR control, SPI port configuration, I2C sub-IP setup, and optional I2C Rx throttling features to QuickSPI/QuickI2C transports.

Important APIs: `thc_dev_init()`, `thc_tic_pio_read()`, `thc_tic_pio_write()`, `thc_tic_pio_write_and_read()`, `thc_interrupt_config()`, `thc_interrupt_handler()`, `thc_port_select()`, `thc_spi_read_config()`, `thc_spi_write_config()`, `thc_i2c_subip_init()`, save/restore helpers, and I2C max-size/interrupt-delay toggles are namespace-exported as `INTEL_THC`.

Control flow: `thc_dev_init()` allocates, binds regmap to MMIO, clears stale status/counters, initializes locks/waitqueues, and creates DMA context. PIO paths serialize on `thc_bus_lock`, call `prepare_pio()`, start the software sequence, poll for done, then harvest data/status. Interrupt handling prioritizes non-DMA device interrupts and fatal/transaction errors before DMA completion and I2C sub-IP raw status bits.

State and persistence: persistent runtime state lives in `struct thc_device`: port type, PIO interrupt support, waitqueue completion flags, performance limit, I2C sub-IP register shadow, and feature-enable flags. I2C sub-IP save/restore preserves register state across suspend-like flows. Hardware state is modified through write-one-to-clear status registers and bitfield updates.

Dependencies and integration: depends on regmap, MMIO accessors, `intel-thc-hw.h` register definitions, and `intel-thc-dma.h`. Protocol drivers call these helpers after PCI resource mapping and before HID report exchange.

Risks: many paths rely on correct register W1C semantics and fixed timeouts. `thc_interrupt_quiesce()` waits for HW status even in the unquiesce path before clearing the enable bit, so sequencing matters. PIO buffer sizes are expressed in bytes but bulk reads/writes operate in dwords. Interrupt handler returns early for several error classes, so callers must handle partial status coverage.

Test signals: boot/probe logs, PIO read/write success, interrupt bit classification, resume restore of I2C sub-IP registers, DMA waitqueue wakeups, and hardware tests that cover SPI and I2C ports.
