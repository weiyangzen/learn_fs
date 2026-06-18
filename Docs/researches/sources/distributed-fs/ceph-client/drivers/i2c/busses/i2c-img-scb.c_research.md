# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-img-scb.c

Purpose: Imagination Technologies Serial Control Bus I2C adapter. It supports raw line control, atomic low-level I2C commands, automatic FIFO-driven transfers, reset/stop command sequences, timer-assisted abort detection, runtime PM, and system sleep handling.

Important APIs/types/functions: `struct img_i2c` contains adapter, MMIO, clocks, bitrate, completion, spinlock, active message copy, mode, interrupt mask, line-status accumulator, timer, halt state, atomic/sequence state, and raw timeout. Major functions include `img_i2c_switch_mode()`, raw/atomic operation helpers, `img_i2c_read_fifo()`, `img_i2c_write_fifo()`, `img_i2c_auto()`, `img_i2c_atomic()`, `img_i2c_sequence()`, `img_i2c_isr()`, `img_i2c_reset_bus()`, `img_i2c_xfer()`, `img_i2c_init()`, and PM callbacks.

Control flow: probe maps MMIO, gets `sys` and `scb` clocks, requests IRQ, initializes the check timer, reads `clock-frequency`, enables runtime PM, initializes timing registers, performs a reset sequence, and registers a numbered adapter. Transfers reject zero-length reads, choose atomic mode for zero-length writes or `I2C_M_IGNORE_NAK`, runtime-resume the device, copy each message into driver state, clear stale interrupts/line status, start automatic FIFO or atomic operation, wait for completion, delete the timer, and autosuspend. The ISR clears interrupts, accumulates line status, dispatches by mode, handles fatal SCLK-low timeout, and completes only after register access is finished.

State and persistence: mode, interrupt mask, line status, active message copy, transaction halt, timer state, and atomic sequence cursor persist during a transfer. Timing registers, clock/filter setup, and soft-reset state persist while runtime active. Suspend marks `MODE_SUSPEND`; resume reinitializes hardware.

Dependencies and integration: depends on OF compatible `img,scb-i2c`, platform MMIO/IRQ, clock framework, runtime PM, timers, completions, spinlocks, and I2C core.

Risks: the state machine is complex and mode-dependent. Automatic mode intentionally suppresses some interrupts and relies on a 1 ms timer for abort detection. FIFO status reads need a hardware-specific write/read fence on affected revisions. Fatal clock-low timeout switches to `MODE_FATAL`, permanently rejecting future transfers until reinit. Timing math must remain within hardware constraints.

Test signals: standard/fast timing setup, hardware revision rejection, automatic read/write and repeated-start transfers, atomic zero-byte probe transfers, ignore-NACK behavior, reset and stop sequences, abort detection via timer, fatal timeout path, runtime suspend/resume, and system sleep resume reinitialization.
