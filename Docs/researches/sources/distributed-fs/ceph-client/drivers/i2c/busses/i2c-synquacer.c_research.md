# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-synquacer.c

Purpose: implements the Socionext/Fujitsu SynQuacer I2C controller as an interrupt-driven master adapter with OF and ACPI binding support.

Important APIs/types/functions: `struct synquacer_i2c` tracks completion, current message array, message index/pointer, IRQ/device/MMIO, PCLK rate, selected speed, timeout, state machine, and adapter. The algorithm is `synquacer_i2c_xfer()` plus `synquacer_i2c_functionality()`. Hardware helpers initialize/reset timing registers, start a master transfer, and stop with completion. `synquacer_i2c_isr()` runs the transfer state machine.

Control flow: probe reads bus speed from ACPI or `clock-frequency`, gets PCLK from a clock or property, validates it, maps MMIO, requests IRQ, initializes adapter state, chooses standard or fast mode, programs hardware, and registers a numbered adapter. `synquacer_i2c_xfer()` computes a timeout from message bytes, retries up to adapter retries on `-EAGAIN`, and resets hardware between retries. `synquacer_i2c_doxfer()` initializes hardware, checks bus busy, stores message state, starts the first address, and waits for completion. The ISR handles bus error/arbitration loss, START ACK, WRITE data/next-message repeated starts, READ address/data phases, ACK control, STOP, and completion.

State and persistence: transfer state is explicit in `state`, `msg`, `msg_num`, `msg_idx`, and `msg_ptr`. `synquacer_i2c_stop()` clears BCR, resets state to idle, updates `msg_idx` or error code, and completes. Hardware timing is reinitialized each attempt; reset disables clock registers and waits PCLK cycles.

Dependencies and integration: supports OF compatible `socionext,synquacer-i2c` and ACPI ID `SCX0003`, optional `pclk`, `socionext,pclk-rate`, platform IRQ/MMIO, and Linux I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: timeout returns `-EAGAIN` and is converted to `-EIO` only after retries, so callers may see retries for multiple fault classes. PCLK must be 14-200 MHz. The read path ignores the first-byte-transfer address echo; state transitions rely on correct BSR flags. Bus recovery is limited to hardware reset, not I2C core bus recovery.

Test signals: OF and ACPI probe, PCLK boundary validation, standard/fast timing, read/write and combined transfers, zero-length last message, NACK, arbitration loss, bus error, timeout/retry behavior, and hardware reset between retries.
