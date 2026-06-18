# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-meson.c

Purpose: implements the Amlogic Meson I2C bus driver for Meson6, GXBB, and AXG-style controllers. The hardware executes token lists with up to eight data bytes per batch, and the driver supports interrupt and atomic polling transfers.

Important APIs, types, and functions: `struct meson_i2c` stores adapter, device, MMIO registers, clock, current message, transfer state, last-message flag, byte count/position, error, spinlock, completion, two token registers, and SoC data. `struct meson_i2c_data` provides the SoC-specific clock divider function. `meson_i2c_xfer()` and `meson_i2c_xfer_atomic()` share `meson_i2c_xfer_messages()`. Token helpers build START, address, DATA, DATA_LAST, and STOP sequences.

Control flow: probe parses I2C timings, maps registers, requests IRQ, enables the clock, clears the START bit, disables input filters, programs the SoC-specific clock divider, and registers the adapter. For each message, transfer setup resets tokens, configures ACK-ignore from `I2C_M_IGNORE_NAK`, optionally emits START/address unless `I2C_M_NOSTART`, prepares a token batch and write data, sets START, then waits by completion or atomic polling. The IRQ clears START, checks error/status, copies read data, advances position, either completes or queues the next token batch and restarts.

State and persistence: persistent state includes clock divider/filter register configuration and SoC clock algorithm. Per-transfer state is protected by `lock` because timeouts can race with late IRQs. `tokens[0]`, `tokens[1]`, `num_tokens`, `pos`, `count`, `state`, and `error` persist across batched IRQ completions for a message.

Dependencies and integration points: integrates with OF compatibles `amlogic,meson6-i2c`, `amlogic,meson-gxbb-i2c`, and `amlogic,meson-axg-i2c`, platform MMIO/IRQ, clock framework, firmware timing parsing, I2C atomic transfer API, and SMBus emulation through the I2C core.

Risks: token batches are limited to eight data bytes, so batching and restart logic must preserve position exactly. The controller auto-generates STOP on NAK when ACK-ignore is not set; the driver maps this to `-ENXIO`. Atomic mode only calls transfer completion once after polling the hardware status bit, so multi-batch atomic messages are risky unless the hardware has finished the prepared batch and state is updated correctly. Clock divider formulas subtract filter delay and clamp low frequencies to 12-bit fields.

Test signals: Meson6 and GXBB/AXG clock divider paths, read/write messages of 0/1/8/9+ bytes, multi-message transfers with STOP only on last message, `I2C_M_NOSTART`, `I2C_M_IGNORE_NAK`, interrupt and atomic paths, timeout with late IRQ race, NAK error mapping, filter disabled state, and remove clock disable.
