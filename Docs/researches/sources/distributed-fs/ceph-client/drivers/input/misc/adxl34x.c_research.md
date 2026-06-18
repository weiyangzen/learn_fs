<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c

Purpose: bus-neutral ADXL345/ADXL346 three-axis accelerometer input driver. It configures sensor thresholds, FIFO/data-ready interrupts, tap/free-fall/activity/orientation events, calibration sysfs, and power transitions.

Important APIs/types/functions: `struct adxl34x` stores device, input, platform data, calibration, saved axes, disabled/opened/suspended flags, IRQ, model, interrupt mask, and bus ops. `adxl34x_probe()` performs detection, input setup, register programming, IRQ request, and exports sysfs groups. `adxl34x_irq()` handles tap, double tap, free fall, activity/inactivity, orientation, FIFO/data samples, and overrun. Sysfs attributes are `disable`, `calibrate`, `rate`, `autosleep`, and `position`.

Control flow and state: probe copies platform data or defaults, verifies `DEVID`, configures input capabilities based on EV_ABS/EV_REL and optional events, writes all threshold/rate/format/FIFO registers, and enables selected interrupts. Input open/close toggles measurement mode unless disabled or suspended. IRQ reads status, reports event keys, drains one or more axis samples, updates `saved`, applies software calibration, and syncs input.

State and persistence behavior: runtime state includes calibration (`hwcal`, `swcal`), latest raw axes, orientation debounce values, and power flags. Hardware offset registers persist until reset; sysfs writes update registers immediately but are not stored across module/device removal.

Dependencies and integration points: uses Linux input, IRQ, sysfs attribute groups, device PM, platform data from `linux/input/adxl34x.h`, and bus operations from `adxl34x.h`. I2C and SPI wrappers call the exported `adxl34x_probe()`.

Risks: many register writes ignore return values through `AC_WRITE`. Platform data values are trusted for event codes, thresholds, data format, FIFO mode, and orientation arrays. Calibration depends on previously saved data, so writing `calibrate` before a sample can produce misleading offsets. FIFO sample count adds one to `FIFO_STATUS` entries, which should be validated against hardware behavior.

Test signals: verify default and custom platform data, device ID rejection, ABS and REL reporting, calibration sysfs math, disable/autosleep/rate sysfs behavior, tap/double-tap/free-fall/activity/orientation events, FIFO drain timing, and open/close/suspend/resume transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c -->
