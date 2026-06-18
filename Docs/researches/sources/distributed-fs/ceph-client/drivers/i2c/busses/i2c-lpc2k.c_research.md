# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-lpc2k.c

Purpose: implements an interrupt-driven I2C master driver for NXP LPC2xxx/LPC178x controllers. The hardware exposes a classic I2C status-code state machine, and the driver pumps one message at a time through IRQs with support for `I2C_M_NOSTART`.

Important APIs, types, and functions: `struct lpc2k_i2c` stores MMIO base, clock, IRQ, wait queue, adapter, current message, byte index, message status, and last-message flag. `i2c_lpc2k_xfer()` is the algorithm hook. `i2c_lpc2k_pump_msg()` interprets controller status codes and drives data/address/ACK/STOP sequencing. Probe programs SCL high/low divisors based on requested bus frequency and mode duty-cycle constants.

Control flow: probe maps MMIO, gets IRQ and clock, requests IRQ, disables it until transfers, resets the controller, reads optional `clock-frequency`, writes SCL timing registers, and registers the adapter. A transfer first verifies idle status or tries `i2c_lpc2k_clear_arb()`, then processes messages sequentially. `lpc2k_process_msg()` emits START or continues `NOSTART`, enables IRQ, and waits for `msg_status` to leave `-EBUSY`. The IRQ handler checks SI and calls the pump.

State and persistence: persistent state includes programmed SCL timing and enabled controller state. Transfer state is stored in `msg`, `msg_idx`, `msg_status`, and `is_last`. IRQ is enabled only during a message and disabled when the message completes or fails. Suspend disables the clock; resume re-enables it and resets the controller.

Dependencies and integration points: integrates with OF compatible `nxp,lpc1788-i2c`, platform IRQ/MMIO, clock framework, noirq PM callbacks, wait queues, and I2C core. SMBus support is emulated by the core.

Risks: status-code sequencing is strict; clearing SI at the wrong time can stall the hardware. Read NACK status is treated as successful final read data, which is intentional. The code increments `msg_idx` in write ACK cases even when no more data is sent, so off-by-one changes are dangerous. Timeout disables IRQ but bus cleanup depends on later transfer idle checks. `I2C_M_NOSTART` is warned for zero length and only directly seeds write data.

Test signals: START and repeated START transfers, read lengths one and multiple bytes, final-byte NACK behavior, write data ACK/NACK, address NACK mapping to `-ENXIO`, arbitration lost mapping to `-EAGAIN`, bus-not-idle clear/reset path, `I2C_M_NOSTART` write continuation, timeout with disabled IRQ, clock divider programming for standard/fast/fast-plus requests, and suspend/resume.
