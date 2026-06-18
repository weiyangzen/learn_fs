# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-st.c

Purpose: provides an I2C master adapter for STMicroelectronics SSC communication controllers configured in I2C mode. The driver programs SSC timing/deglitch registers, services FIFO-driven interrupt transfers, and supports bus recovery by temporarily using the SSC block in a clock-generating mode.

Important APIs/types/functions: `struct st_i2c_dev` owns the adapter, MMIO base, IRQ, clock, mode, deglitch timing, active `struct st_i2c_client`, completion, and `busy` flag. `st_i2c_timings` defines standard/fast-mode timing constants. Adapter hooks are `st_i2c_xfer()` and `st_i2c_func()`; recovery is exposed through `st_i2c_recovery_info`. Core helpers include `st_i2c_hw_config()`, `st_i2c_wait_free_bus()`, FIFO fill/drain helpers, `st_i2c_terminate_xfer()`, and threaded ISR `st_i2c_isr_thread()`.

Control flow: probe maps resources, obtains the SSC clock and IRQ, chooses standard or fast mode from `clock-frequency`, reads required deglitch properties, configures pinctrl idle/default states, requests a threaded IRQ, and registers the adapter. `st_i2c_xfer()` sets `busy`, enables the clock, selects active pins, reinitializes hardware, and executes each message with `st_i2c_xfer_msg()`. Message setup writes the 8-bit address, pre-fills write data or dummy read clocks, enables NACK/TX-empty/arbitration interrupts, starts only the first message, and completes on STOP or repeated-start interrupt. The ISR prioritizes enabled status bits, handles TX empty, NACK, arbitration loss, STOP, and repeated start.

State and persistence: transfer progress lives in `client.count`, `client.xfered`, `client.buf`, `client.result`, and `client.stop`. Hardware is reconfigured for each transfer; clocks are enabled only around transfers. Suspend refuses while `busy` is true, then selects sleep pinctrl; resume restores default/idle pin states.

Dependencies and integration: depends on OF compatibles `st,comms-ssc-i2c` and `st,comms-ssc4-i2c`, an `ssc` clock, IRQ, pinctrl states, deglitch DT properties, and the I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: required deglitch properties return errors only for malformed values, so absent values leave zero pulse widths. Bus recovery intentionally switches out of I2C mode and writes a 9-bit word; regressions here can break stuck-bus recovery. The ISR uses `__fls(sta & ien)`, so interrupt priority follows highest set bit and must match error-first expectations. Timeouts leave recovery to later attempts.

Test signals: standard and fast timing setup, missing/invalid deglitch properties, write/read/multi-message repeated-start transfers, NACK and arbitration paths, `i2c_recover_bus()`, and suspend while `busy` are key tests.
