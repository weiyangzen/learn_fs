<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c

Purpose: Mainstone/PXA machine-ops driver for accelerated continuous touchscreen sampling on Wolfson WM9705, WM9712, and WM9713 AC97 codecs. It plugs board-specific continuous-sampling callbacks into the generic `wm97xx` touchscreen driver.

Important APIs/types/functions: `struct continuous` and `cinfo[]` map codec IDs and requested `cont_rate` to codec continuous-mode codes and per-tick read counts. Module parameters `cont_rate`, `pen_int`, `pressure`, and `ac97_touch_slot` tune sampling, pen IRQ usage, pressure reads, and AC97 slot. Machine callbacks are `wm97xx_acc_pen_up()`, `wm97xx_acc_pen_down()`, `wm97xx_acc_startup()`, and `wm97xx_acc_shutdown()`, collected in `mainstone_mach_ops`. Probe/remove call `wm97xx_register_mach_ops()` and `wm97xx_unregister_mach_ops()`.

Control flow: startup validates the AC97 codec, chooses the nearest supported continuous speed, sets `wm->acc_rate` and slot, optionally obtains a touch GPIO and maps it as a pen IRQ, and configures WM9712/WM9713 codec GPIOs. During pen-down sampling, the driver drains AC97 MODR values, validates ADC selector tags for X/Y/pressure, reports coordinates and pressure, and returns `RC_PENDOWN | RC_AGAIN` until samples become stale or invalid. Pen-up flushes the AC97 slot FIFO differently for PXA27x and PXA3xx.

State and persistence: global module state stores selected speed index, optional GPIO descriptor, and module parameters. Runtime device state is held by the generic `wm97xx` object; no nonvolatile state is changed.

Dependencies/integration: depends on generic `wm97xx` input infrastructure, PXA AC97 helpers, PXA CPU detection, codec GPIO configuration, optional GPIO-backed pen IRQ, and platform driver name `wm97xx-touch`.

Risks and test signals: globals make multiple codec instances questionable. Test fallback from missing pen GPIO to polling, codec-specific GPIO setup, pressure disabled/enabled paths, stale sample detection through static `last/tries`, AC97 slot selection, PXA27x/PXA3xx FIFO flushes, and cleanup of `gpiod_irq` after startup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c -->
