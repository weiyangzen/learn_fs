# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-omap.c

## Purpose
Implements the TI OMAP I2C bus adapter for multiple OMAP IP revisions. It handles revision-specific register maps, clock/FIFO programming, interrupt-threaded and polling transfers, hardware errata, bus-busy validation, generic SCL recovery, runtime PM, mux state, and system suspend/resume.

## Important APIs, Types, And Functions
`struct omap_i2c_dev` contains the adapter, MMIO base, revision flags, FIFO settings, transfer buffers, completion, saved PM register state, errata flags, and recovery state. `omap_i2c_xfer_irq()` and `omap_i2c_xfer_polling()` call `omap_i2c_xfer_common()`. `omap_i2c_xfer_msg()` programs a single transaction; `omap_i2c_xfer_data()` is the IRQ/poll data pump. Probe identifies revision scheme, initializes clocks/FIFOs/errata, requests IRQ, and registers a numbered adapter.

## Control Flow
Probe maps MMIO, obtains speed from OF/platform data, enables runtime PM, detects register scheme/revision, derives errata and FIFO size, selects optional mux state, initializes the controller, requests old-style or threaded IRQ, and registers the adapter with recovery info. Transfer resumes the device, waits until the BB bit is valid and bus is free, optionally sets MPU latency, performs each message, waits for bus free, and autosuspends. IRQ-thread or polling code drains/fills RX/TX, handles ARDY/NACK/AL/overrun/underflow, and completes the command.

## State And Persistence
Runtime state includes active buffer pointer/length, receiver flag, command errors, saved interrupt and clock registers, FIFO threshold, and BB validity. Hardware state is restored in runtime resume via `__omap_i2c_init()`. There is no on-disk persistence.

## Dependencies And Integration Points
Depends on platform/OF matching (`ti,omap2420-i2c` through `ti,omap4-i2c`), runtime PM, pinctrl, mux state, clocks, I2C core, and generic bus recovery. It uses `subsys_initcall()` because I2C may be needed early. Platform data can provide clock rate and MPU wake latency hooks.

## Risks
The BB bit is unreliable after reset on newer revisions, requiring careful validation to avoid corrupting multi-master transfers. Errata I207 and I462 alter interrupt handling and TX timing. FIFO threshold sizing affects latency and overrun/underflow risk. Runtime PM must save/restore interrupt state correctly. NACK with `I2C_M_IGNORE_NAK` deliberately returns success.

## Test Signals
Signals include transfers on OMAP1/2/3/4-compatible revisions, FIFO and no-FIFO modes, high-speed and standard/fast timing, threaded IRQ and atomic polling paths, NACK/arbitration/overrun/underflow injection, BB-valid recovery in multi-master scenarios, SCL recovery through SYSTEST mode, autosuspend/resume, and suspend_noirq/resume_noirq availability.
