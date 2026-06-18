
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pnx.c

Purpose: this platform driver supports Philips/NXP PNX IP3204-style I2C controllers. It implements a full interrupt-driven `i2c_algorithm` with START/STOP generation, byte transmit/receive through FIFOs, timeout/reset handling, clock divider programming, OF binding, and suspend/resume clock control.

Important APIs, types, and functions: `struct i2c_pnx_mif` carries per-transfer return code, mode, completion, buffer pointer, remaining length, and receive-order count. `struct i2c_pnx_algo_data` stores MMIO base, transfer state, last-message flag, clock, adapter, IRQ, and timeout. `i2c_pnx_start()`, `i2c_pnx_stop()`, `i2c_pnx_master_xmit()`, and `i2c_pnx_master_rcv()` implement the core state machine. `i2c_pnx_interrupt()` dispatches arbitration failure, NACK, transmit-data-needed, and receive-data events. `i2c_pnx_xfer()` is the adapter transfer entry point.

Control flow: probe maps registers, enables the clock, calculates clock high/low dividers from `clock-frequency`, resets the controller, requests IRQ, and adds a numbered adapter. A transfer resets active/stale bus state, iterates messages, rejects ten-bit addresses, initializes `mif`, enables master interrupts, writes START and address, then waits for completion. TX interrupts push bytes and attach STOP to the final byte of the last message; RX uses dummy writes to clock data into the receive FIFO and NACK/STOP on the final byte. Timeout disables interrupts, resets the controller, and returns `-EIO`. After all messages, stale active/FIFO/NACK state triggers reset cleanup.

State and persistence: transfer state lives in `mif` and is cleared after each `i2c_pnx_xfer()`. Adapter and clock state persist for device lifetime. Runtime PM-like simple suspend/resume only disables/enables the clock; register contents are not fully reinitialized on resume in this file.

Dependencies and integration points: it uses platform resources, OF compatible `nxp,pnx-i2c`, Linux clocks, completions, IRQs, MMIO, and I2C core registration. `subsys_initcall()` ensures this adapter is available before USB initialization.

Risks: only 7-bit addressing is supported. Busy-bus and FIFO cleanup rely on reset and fixed timeouts. STOP wait in interrupt context uses a tight microsecond loop. Clock divider math clamps high values but does not validate all low-frequency timing corners beyond the clamp. Resume only enables the clock, so external reset or lost register state could require additional reconfiguration.

Test signals: transfer tests for read, write, zero-length write, multi-message sequences, NACK, arbitration loss, busy bus at start, timeout recovery, clock-frequency variants, suspend/resume transfer after clock cycling, and early boot ordering with dependent devices.
