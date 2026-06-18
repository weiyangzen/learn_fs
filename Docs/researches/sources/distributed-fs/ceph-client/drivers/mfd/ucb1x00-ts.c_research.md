# sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-ts.c

## Purpose
`ucb1x00-ts.c` implements the input touchscreen child driver for UCB1x00-based resistive touch panels. It uses UCB touchscreen control registers and ADC channels to report X, Y, pressure, and touch state through the Linux input subsystem.

## Important APIs, Types, And Functions
Driver state is `struct ucb1x00_ts`, which stores the input device, parent UCB pointer, IRQ wait queue, kernel sampling thread, plate resistance limits, IRQ-disable flag, and ADC sync mode. Sampling helpers are `ucb1x00_ts_read_pressure()`, `ucb1x00_ts_read_xpos()`, `ucb1x00_ts_read_ypos()`, `ucb1x00_ts_read_xres()`, `ucb1x00_ts_read_yres()`, `ucb1x00_ts_pen_down()`, and `ucb1x00_ts_mode_int()`. Event helpers are `ucb1x00_ts_evt_add()` and `ucb1x00_ts_event_release()`. Runtime callbacks are `ucb1x00_thread()`, `ucb1x00_ts_irq()`, `ucb1x00_ts_open()`, `ucb1x00_ts_close()`, `ucb1x00_ts_add()`, and `ucb1x00_ts_remove()`. The module parameter `adcsync` selects synchronized ADC conversions.

## Control Flow
When attached by the UCB core, `ucb1x00_ts_add()` allocates state and an input device, configures EV_ABS and BTN_TOUCH capabilities, measures X/Y plate resistance via ADC, sets ABS ranges, and registers the input device. Opening the input device requests the TSPX IRQ with rising edge on Collie or falling edge otherwise, measures resistance again, and starts kernel thread `ktsd`. The IRQ handler disables the touch IRQ and wakes the thread. The thread repeatedly enables ADC access, samples X, Y, and pressure, switches hardware back to interrupt mode, disables ADC, waits 10 ms, checks pen state, reenables the IRQ on release, emits release if a valid touch was active, or reports a sample and polls again after `HZ / 100`. It is freezer-aware and suppresses one sample after thaw. Close stops the thread, frees the IRQ, clears `UCB_TS_CR`, and disables the parent device.

## State, Persistence, And Dependencies
Runtime state is per child instance: thread pointer, IRQ wait queue, `irq_disabled`, plate resistance, and input device state. Hardware state is the touchscreen control register mode, ADC control held through the UCB core, and Collie-specific GPIO table-check control. The driver depends on the UCB core's ADC, IO, register, and nested IRQ APIs; Linux input subsystem; kthreads; freezer support; and machine-specific Collie helpers from `mach/collie.h` and `machine_is_collie()`.

## Integration Points
The driver registers through the UCB pseudo-driver list, so it is bound by `ucb1x00_register_driver()` rather than OF/ACPI matching. It consumes `ucb->irq_base + UCB_IRQ_TSPX`, UCB ADC inputs `TSPX/TSPY/AD2`, and UCB touchscreen register bits. User space sees a standard input device named `"Touchscreen panel"` with ABS_X, ABS_Y, ABS_PRESSURE, and BTN_TOUCH.

## Risks
The code uses legacy machine-specific Collie conditionals, limiting portability and testability. The thread intentionally leaves filtering to user space, so noisy panels can emit raw jitter. `BUG_ON(ts->rtask)` in open is harsh if input open/close state becomes inconsistent. IRQ disable/enable is coordinated manually with `irq_disabled`; missed transitions can leave the touch IRQ disabled or reenabled too early. Synchronized ADC mode can hang user-visible touch behavior if ADCSYNC pulses stop, as noted in the file comment. The pressure ABS range is initialized with max 0, which may constrain consumers depending on input stack interpretation.

## Test Signals
Tests should register and open the input device, confirm IRQ request flags on Collie and non-Collie systems, and verify the thread reports press samples followed by release events. ADC sync and non-sync modes should be exercised. Hardware tests should compare measured X/Y resistance and raw coordinate ranges against known panel positions. Suspend/freezer tests should confirm no stale sample is emitted immediately after thaw. Close/unload tests should verify thread stop, IRQ free, and touchscreen register clear.
