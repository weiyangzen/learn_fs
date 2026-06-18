# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb_i2c.c

Purpose: Provides the internal two-bus I2C controller driver for NetUP Universal Dual DVB-CI cards. It adapts the bridge's TWI/FIFO register block to Linux `i2c_adapter` transfers used by the demodulator, tuner, and LNB drivers.

Important APIs, types, and functions: `struct netup_i2c_regs` and `struct netup_i2c_fifo_regs` define the packed MMIO layout for clock, control/status, address/control, length, TX FIFO, and RX FIFO registers. `netup_i2c_interrupt()` decodes completion, address NACK, data NACK, RX FIFO, and TX FIFO interrupt causes and wakes waiters. `netup_i2c_xfer()` is the `i2c_algorithm.master_xfer` implementation. `netup_i2c_reset()`, `netup_i2c_start_xfer()`, `netup_i2c_fifo_tx()`, and `netup_i2c_fifo_rx()` implement the transfer state machine. `netup_i2c_register()` and `netup_i2c_unregister()` create or remove both adapters.

Control flow: Adapter registration initializes spinlock/waitqueue, maps bus 0 or bus 1 register base under BAR0, resets the controller/FIFOs, clones the static adapter template, and calls `i2c_add_adapter()`. A transfer serially processes each `i2c_msg`, starting the hardware command, then repeatedly drops the spinlock and waits up to one second for interrupt-driven state transitions. WANT_READ drains the RX FIFO, WANT_WRITE fills the TX FIFO, DONE optionally drains final read bytes, and ERROR or timeout aborts.

State and persistence: `struct netup_i2c` stores the adapter, register pointer, current message pointer, transfer byte count, waitqueue, spinlock, and state enum. There is no persistent bus transaction history. TWI clock divider and FIFO reset state are hardware registers reset at adapter init/remove or when the state is unexpectedly non-DONE.

Dependencies and integration points: Used by `netup_unidvb_core.c` after BAR mapping and before frontend attachment. The shared PCI ISR dispatches `NETUP_UNIDVB_IRQ_I2C0` and `NETUP_UNIDVB_IRQ_I2C1` to `netup_i2c_interrupt()`. Exposes `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: The transfer path uses a spinlock across state setup and FIFO access, but waits outside the lock; state transitions rely on IRQ ordering and correct re-enabling of TWI IRQ bits. Only one active message is tracked per adapter, so concurrent transfers depend on I2C core serialization. FIFO count fields are trusted. Timeouts leave hardware reset only on the next transfer's initial state check. The adapter class is `I2C_CLASS_HWMON`, which may invite probing unrelated to media use.

Test signals: Validate write-only, read-only, and write-then-read message sequences; FIFO refill/drain for messages larger than 16 bytes; address and data NACK handling; timeout recovery on missing IRQ; reset before new transfers after stale states; unregister while idle; and two independent bus register bases.
