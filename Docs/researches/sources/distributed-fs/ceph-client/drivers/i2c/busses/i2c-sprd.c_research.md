# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sprd.c

Purpose: implements the Spreadtrum SC9860 I2C controller as a Linux platform I2C adapter. It maps the controller registers, programs 100 kHz or 400 kHz timing, drives FIFO-based master transfers, and integrates with runtime/system power management.

Important APIs/types/functions: `struct sprd_i2c` holds adapter, MMIO base, clocks, active `i2c_msg`, transfer buffer/count, IRQ, completion, and error state. The public adapter hooks are `sprd_i2c_xfer()` and `sprd_i2c_func()` via `sprd_i2c_algo`. Transfer helpers program count/address/mode/stop, feed or drain FIFOs, and wait on `complete`. `sprd_i2c_isr()` masks FIFO interrupts and wakes the threaded handler; `sprd_i2c_isr_thread()` continues FIFO movement or completes with `0`/`-EIO`. Probe/remove and PM entry points are `sprd_i2c_probe()`, `sprd_i2c_remove()`, runtime suspend/resume, and noirq system suspend/resume.

Control flow: probe allocates private state, maps registers, obtains IRQ and clocks, validates `clock-frequency`, enables the clock, initializes timing/FIFO/interrupts, requests a threaded IRQ, and registers a numbered adapter. Each transfer resumes runtime PM, sends all messages in order, and keeps STOP disabled for intermediate write messages. `sprd_i2c_handle_msg()` resets FIFO, configures address/count/direction, preloads write data or enables RX full interrupts, starts hardware, then waits up to `I2C_XFER_TIMEOUT`. IRQ bottom-half either moves another FIFO chunk or clears ACK/START and completes.

State and persistence: persistent state is only in driver-private memory and controller registers. Runtime suspend disables the enable clock; runtime resume re-enables and reprograms controller timing/FIFO state. System sleep marks the adapter suspended/resumed around runtime force suspend/resume.

Dependencies and integration: depends on platform device resources, OF compatible `sprd,sc9860-i2c`, clocks named `i2c`, `source`, and `enable`, runtime PM, threaded IRQs, and the Linux I2C core. It advertises `I2C_FUNC_I2C | I2C_FUNC_SMBUS_EMUL`.

Risks: only exact 100 kHz and 400 kHz bus rates are accepted. `sprd_i2c_clk_init()` falls back to a hard-coded 26 MHz source when `clk_set_parent()` succeeds, which is easy to misread and should be checked against hardware expectations. Reads always set STOP, while intermediate write messages suppress STOP, so mixed combined-message behavior depends on hardware semantics. Timeout/error recovery is limited to clearing bits and runtime reinitialization.

Test signals: probe with valid/invalid clock-frequency, runtime PM autosuspend/resume, NACK write returning `-EIO`, long read/write FIFO threshold paths, combined transfers, and suspend/resume with active adapters are the useful coverage points.
