# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-highlander.c

Purpose: Renesas Highlander FPGA SMBus adapter for R0P7780/R0P7785 boards. It supports a narrow SMBus command set through FPGA registers, with interrupt or polling completion and module parameters for mode, timeout, speed, and read delay workarounds.

Important APIs/types/functions: `struct highlander_i2c_dev` stores MMIO base, adapter, command completion, last read time, IRQ, and active buffer. Core functions are `highlander_i2c_setup()`, `highlander_i2c_reset()`, `highlander_i2c_wait_for_bbsy()`, `highlander_i2c_wait_for_ack()`, `highlander_i2c_read()`, `highlander_i2c_write()`, `highlander_i2c_smbus_xfer()`, and `highlander_i2c_probe()/remove()`.

Control flow: probe maps the resource manually, chooses IRQ or polling, configures fast/normal mode, resets the FPGA controller, and registers a numbered HWMON-class adapter. SMBus transfers accept only byte-data and I2C-block-data forms, select an FPGA mode based on transfer length 1/8/16/32, clear old completion, program address and command bytes, then read or write 16-bit data registers and start the transfer.

State and persistence: active transfer state is the buffer pointer/length and completion object. `last_read_time` enforces an optional inter-read delay for FPGA quirks. Hardware state persists in mode/control/address/data registers. Module parameters are global driver state.

Dependencies and integration: depends on platform MMIO resources, optional IRQ, Linux SMBus algorithm hooks, completions, Renesas board platform devices, and HWMON-class client probing through the I2C core.

Risks: transfer support is intentionally limited; arbitrary I2C messages are not supported. Buffer conversion uses fixed `u16 data[16]`, matching the maximum 32-byte mode, so size validation is essential. Polling can busy-loop until timeout. IRQ wait ignores the return value of `wait_for_completion_timeout()` and relies on later ACK checking. Manual allocation/mapping requires explicit unwind correctness.

Test signals: byte and block transfers at supported lengths, unsupported sizes returning `-EINVAL`, forced polling mode, IRQ completion path, ACK abnormality reset path, read-delay workaround, and remove freeing IRQ/MMIO/adapter.
