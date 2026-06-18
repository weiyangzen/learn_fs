<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c

Purpose: platform driver for Aspeed AST24xx/25xx/26xx I2C controllers with interrupt-driven master transfers, optional slave mode, bus recovery, clock setup, and reset handling.

Important APIs and flow: `struct aspeed_i2c_bus` stores adapter, MMIO base, reset, spinlock, completion, clock function, transfer state, multi-master flag, and optional slave state. `aspeed_i2c_master_xfer` prepares message state, recovers a busy single-master bus if needed, starts transfer, waits for completion, and resets/recovers on timeout. `aspeed_i2c_master_irq` advances a detailed master state machine across START, TX, RX, STOP, error, SMBus block receive length, and bus-recovery completion. Slave IRQ support maps hardware events to `i2c_slave_event`. Probe maps resources, reads clock/reset/frequency/OF match, initializes hardware, requests IRQ, and registers the adapter.

State and dependencies: persistent state is per bus, protected by spinlock and I2C bus locking. Dependencies include OF compatibles, clocks, resets, IRQs, completions, optional `CONFIG_I2C_SLAVE`, and MMIO registers.

Risks and tests: coalesced master/slave interrupts, pending master during slave activity, bus recovery, clock divider clamping, and timeout reset are high-risk. Test AST2400/2500/2600 compatibles, multi-master, slave mode, SMBus block receive, hung SDA/SCL recovery, NAK/arbitration, suspend-like reset, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c -->
