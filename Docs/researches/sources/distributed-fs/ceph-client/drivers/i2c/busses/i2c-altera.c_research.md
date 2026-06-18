<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c

Purpose: platform driver for Altera Soft IP I2C controllers, using MMIO registers, FIFO thresholds, clocks, and threaded interrupts.

Important APIs and flow: `struct altr_i2c_dev` stores register base, current message, completion, clock, FIFO size, cached interrupt state, and adapter. `altr_i2c_init` programs bus timing from input clock and `clock-frequency`. `altr_i2c_xfer_msg` prepares one message, drains RX FIFO, writes START/address, enables RX/TX/error interrupts, waits for completion, checks timeout and idle state, and disables the core. Top-level `altr_i2c_xfer` processes messages sequentially. The IRQ pair captures status quickly then handles FIFO service, NACK, arbitration loss, RX overflow, and completion.

State and dependencies: runtime state is per device and protected by `isr_mutex`. Dependencies include platform resources, OF compatible `altr,softip-i2c-v1.0`, clocks, IRQs, completions, MMIO, and I2C core.

Risks and tests: multi-message transfers get STOP per message rather than combined repeated-start semantics; IRQ masking must match status bits; FIFO sizing from firmware matters. Test reads/writes, NACK/arbitration/RX overflow, clock-frequency limits, timeout, remove, and OF probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c -->
