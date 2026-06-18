# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm97xx-core.c

## Purpose
`wm97xx-core.c` is the common touchscreen/AUX/GPIO/battery core for Wolfson WM9705, WM9712, and WM9713 AC97 codecs. It detects the codec, selects codec-specific callbacks, registers input and child platform devices, reads touch samples, and manages PM.

## Important APIs, Types, And Functions
Exports include `wm97xx_reg_read()`, `wm97xx_reg_write()`, `wm97xx_read_aux_adc()`, GPIO get/set/config helpers, `wm97xx_set_suspend_mode()`, and machine-ops registration. `wm97xx_read_samples()` calls codec or machine sampling, filters out-of-range readings, reports input events, and adjusts poll interval. `wm97xx_ts_reader()` is the delayed work loop. `_wm97xx_probe()` validates vendor IDs, selects `wm9705_codec`, `wm9712_codec`, or `wm9713_codec`, initializes physical settings, caches GPIOs, and registers touch.

## Control Flow
The module registers both an AC97 bus driver and an MFD platform driver. Probe allocates `struct wm97xx`, detects codec ID, registers a touchscreen input device and `wm97xx-touch` child, then registers a battery child. Input open creates an ordered workqueue, enables digitizer/continuous mode, initializes delayed work, and requests pen IRQ if available. Close frees IRQ, cancels work, destroys the workqueue, and disables digitizer/continuous mode.

## State And Persistence
State includes digitizer and GPIO register caches, misc register, machine ops, pen state, suspend mode, delayed work interval, input device state, and child devices. Module parameters define input absolute ranges. No persistent storage is changed.

## Dependencies And Integration Points
It integrates AC97 bus ops, MFD platform data, WM97xx codec callback structs, input core, platform child devices for touch/battery, workqueues, IRQs, PM wakeup, and optional machine acceleration hooks.

## Risks
The core has complex lifetime interactions: IRQ allocation happens on input open, work rearms itself, and child platform devices are registered after input. `wm97xx_reg_read()` returns `-1` without an AC97 handle, which can look like register data. Suspend writes digitizer registers partly bypassing the cache. Machine ops can change sampling semantics substantially.

## Test Signals
Test all codec IDs and disabled-codec config paths, input open/close with and without IRQ, polling interval backoff, out-of-range filtering, AUX ADC timeout, GPIO helpers, battery child registration failure unwinding, AC97 and MFD probe/remove, suspend/resume with wakeup mode, and machine-op registration conflicts.
