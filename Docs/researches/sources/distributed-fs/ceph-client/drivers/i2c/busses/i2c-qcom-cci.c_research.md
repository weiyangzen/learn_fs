
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-cci.c

Purpose: this driver exposes Qualcomm Camera Control Interface controllers as one or two I2C adapters. CCI is queue-command based and intended for camera sensor/control traffic with small transfer limits. The driver programs master timing parameters for standard, fast, or fast-plus mode, loads write/read commands into per-master queues, waits for report/read-done interrupts, and integrates with runtime PM.

Important APIs, types, and functions: `struct cci` owns the MMIO base, IRQ, match data, clock bulk, and two possible `struct cci_master` objects. `struct cci_data` describes number of masters, queue sizes, adapter quirks, and per-speed `struct hw_params`. `cci_isr()` clears/handles reset, read-done, queue-report, halt-ack, and error interrupts. `cci_reset()`, `cci_halt()`, and `cci_init()` manage controller state and timing registers. `cci_i2c_write()` and `cci_i2c_read()` load queue commands and consume read FIFO data. `cci_xfer()` wraps multi-message transfers with `pm_runtime_get_sync()` and `pm_runtime_put_autosuspend()`.

Control flow: probe allocates the controller, reads match data, iterates available child nodes as masters, configures each adapter and speed mode from `clock-frequency`, maps MMIO, obtains all clocks, enables clocks, requests IRQ, resets and initializes the controller, enables runtime PM, and registers each configured master adapter. Transfers validate queue emptiness, write `SET_PARAM` and `READ`/`WRITE` commands to queue 1 or 0 respectively, add report commands for writes, start the queue, wait for completion, and return `num` on success. Read completion checks the expected read word count and discards the first status/metadata byte before copying data.

State and persistence: per-master completion and status persist for adapter lifetime. The controller timing registers are reprogrammed during init and runtime resume. Runtime suspend disables all clocks; resume enables clocks and calls `cci_init()`. No persistent storage exists.

Dependencies and integration points: it depends on platform/OF child nodes, clock bulk APIs, completions, IRQs, runtime PM, and I2C adapter quirks. OF compatibles select v1, v1.5, v2, or msm8953 timing/quirk tables. Child `reg` selects master index and child `clock-frequency` selects bus mode.

Risks: transfer sizes are limited by quirks (`max_write_len` around 10/11 and `max_read_len` 12), queue size, and the local fixed `load[12]` write buffer. Queue validation returns `-EINVAL` when full. Timeouts reset and reinitialize the whole controller. Error handling halts queues and maps NACK to `-ENXIO`, other CCI errors to `-EIO`. Probe error paths must carefully release OF node references for registered masters.

Test signals: probe with one-master and two-master compatibles, per-child clock-frequency modes, max-length write/read limits, NACK/error IRQ mapping, queue timeout reset/reinit path, runtime autosuspend/resume followed by transfer, and remove halting each master.
