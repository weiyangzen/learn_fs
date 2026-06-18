# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm831x-ts.c

## Purpose
`wm831x-ts.c` is a platform input driver for the touchscreen block inside WM831x PMICs. It alternates between pen-detect and data IRQ modes and reports X/Y plus optional pressure.

## Important APIs, Types, And Functions
`struct wm831x_ts` stores the input device, parent WM831x handle, data and pen-down IRQs, pressure enable, pen state, and work item used to re-enable the opposite IRQ after state transitions. `wm831x_ts_pen_down_irq()` enables data collection on pen down. `wm831x_ts_data_irq()` reads X/Y/Z registers, reports samples, detects release, disables data IRQ, and re-enables pen detect via work. Input open/close enable or shut down the touchscreen registers.

## Control Flow
Probe obtains parent MFD data and optional touch platform data, resolves IRQs, configures five-wire/current/rate bits, requests a no-auto-enable data IRQ and an enabled pen IRQ, initializes input axes, and registers input. During use, pen IRQ starts coordinate conversion; data IRQ reports until a sample lacks the pen-down bit, then returns to pen-detect mode.

## State And Persistence
Hardware register bits hold mode/rate/current configuration. Runtime `pen_down` selects which IRQ should be enabled. No persistent storage is used.

## Dependencies And Integration Points
It depends on the WM831x MFD core, WM831x IRQ mapping, optional platform data, direct register/bulk access helpers, workqueues, and input core.

## Risks
IRQ transition correctness is subtle because handlers disable IRQs and schedule work to re-enable the counterpart. Remove frees IRQs but does not flush pending work explicitly. Five-wire mode suppresses pressure even if platform data requested it.

## Test Signals
Test platform data overrides, direct versus mapped IRQs, pressure and five-wire modes, pen-down to data IRQ switching, release reporting, input close while pen is down, IRQ request failure unwinding, and remove with pending work.
