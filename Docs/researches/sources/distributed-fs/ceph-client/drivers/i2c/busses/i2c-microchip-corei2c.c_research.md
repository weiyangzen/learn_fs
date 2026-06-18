# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-microchip-corei2c.c

Purpose: Microchip CoreI2C platform driver for MPFS hard I2C peripherals and CoreI2C soft FPGA cores. It exposes a normal I2C adapter plus an SMBus emulation path over the same interrupt-driven master state machine.

Important APIs/types: `struct mchp_corei2c_dev` stores MMIO base, clock, active message queue, transfer completion, cached ISR status, current address/buffer/length, and repeated-start state. Main entry points are `mchp_corei2c_probe()`, `mchp_corei2c_xfer()`, `mchp_corei2c_smbus_xfer()`, `mchp_corei2c_isr()`, `mchp_corei2c_handle_isr()`, and the `mchp_corei2c_algo` `i2c_algorithm`.

Control flow: probe maps registers, obtains IRQ and clock, reads `clock-frequency`, programs a CoreI2C divisor, enables the clock, and registers the adapter. Transfers seed `msg_queue`, `total_num`, `current_num`, `addr`, `msg_len`, and `buf`, then set `CTRL_STA`; subsequent progress is driven by interrupt status values. The ISR reads `CORE_I2C_STATUS`, handles start/address/data ACK/NACK/arbitration-lost states, reads or writes `CORE_I2C_DATA`, emits STOP when needed, advances to the next message, and completes the wait.

State and persistence: persistent device state is per-platform-device and held in `struct mchp_corei2c_dev`; runtime transaction state is reused for each transfer and completed through `msg_complete`. Hardware persistence is limited to controller enable/divisor bits and the clock state. Remove disables the clock and unregisters the adapter.

Dependencies and integration: integrates with platform devices, OF compatibles `microchip,mpfs-i2c` and `microchip,corei2c-rtl-v7`, the Linux I2C core, IRQ handling, MMIO byte accessors, and the common clock framework. SMBus operations are translated into `i2c_msg` arrays before using the adapter transfer path.

Risks: the state machine is sensitive to status-code ordering and only marks selected failures, so unexpected status values can silently fall through until timeout. `mchp_corei2c_smbus_xfer()` advertises SMBus emulation but the `I2C_SMBUS_QUICK` case returns without issuing a bus transaction. Shared IRQ handling depends on `idev->buf` being valid to distinguish own interrupts. Timeout recovery returns `-ETIMEDOUT` but does not reset the controller in the transfer path.

Test signals: useful tests include probe with valid and invalid `clock-frequency`, raw I2C write/read/repeated-start transactions, SMBus byte/word/block cases, arbitration loss and NACK status injection, timeout handling, shared IRQ noise, and remove/unbind clock cleanup.
