# sources/distributed-fs/ceph-client/include/linux/delay.h

Purpose: Defines kernel delay and sleep helpers ranging from calibrated busy waits to flexible sleeps that choose an appropriate delay mechanism.

Important APIs, types, and functions: Exposes `loops_per_jiffy`, `lpj_fine`, architecture `udelay()` integration, `mdelay()`, `ndelay()`, `calibrate_delay()`, `calibrate_delay_is_known()`, weak `calibration_delay_done()`, `msleep()`, `msleep_interruptible()`, `usleep_range_state()`, `usleep_range()`, `usleep_range_idle()`, `ssleep()`, and `fsleep()`.

Control flow: `mdelay()` uses direct `udelay()` for small compile-time constants and loops millisecond chunks otherwise to avoid overflow. `ndelay()` rounds to microseconds if an architecture does not provide native nanosecond delay. `fsleep()` busy-waits for very short sleeps, uses `usleep_range()` when jiffy-based `msleep()` would exceed the target slack, and otherwise uses `msleep()`.

State and persistence: Calibration state is held in global loop-per-jiffy values. Sleep functions do not persist state beyond scheduler/timer state.

Dependencies and integration points: Depends on architecture delay loops, scheduler task states, jiffies, math helpers, hrtimer/timer behavior, and boot-time calibration.

Risks and test signals: Risks include busy-waiting too long in sleepable contexts, inaccurate calibration, overflow on high bogomips systems, and unexpected load-average effects. Test delay calibration, `fsleep()` boundaries, interruptible sleeps, idle sleeps, non-high-res timer kernels, and architecture overrides.
