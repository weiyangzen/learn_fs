# sources/distributed-fs/ceph-client/drivers/rtc/rtc-meson-vrtc.c

Purpose: implements Amlogic virtual wakeup RTC timer support, exposing current system wall time as RTC time and programming a relative wakeup alarm register during suspend.

Important APIs and types: `struct meson_vrtc_data` stores the alarm MMIO pointer, absolute alarm time, and enabled flag. RTC callbacks are `meson_vrtc_read_time()`, `meson_vrtc_set_alarm()`, and `meson_vrtc_alarm_irq_enable()`. PM callbacks are `meson_vrtc_suspend()` and `meson_vrtc_resume()`.

Control flow: probe maps the alarm register, marks wakeup-capable, allocates and registers an RTC. Reads return `ktime_get_real_ts64()`. Setting an alarm stores the absolute alarm epoch seconds if enabled, or zero otherwise. On suspend the driver subtracts current real time from stored alarm time and writes the positive relative seconds to the wakeup register. Resume clears stored alarm time and hardware wakeup value.

State and persistence: no real RTC hardware time is stored; time comes from kernel wall clock. The only hardware state is a wakeup countdown/seconds register. Alarm state is volatile software state.

Dependencies and integration: platform MMIO, OF compatible `amlogic,meson-vrtc`, RTC class, device wakeup, and PM sleep hooks.

Risks: `alarm_irq_enable()` stores `enabled` but suspend only checks `alarm_time`, so disabled alarms with stale nonzero time would be a risk if `set_alarm()` did not clear it. There is no read_alarm callback and no interrupt reporting. If alarm time has already passed, suspend logs an error and leaves the wakeup register unchanged.

Test signals: current-time read, set alarm then suspend relative conversion, disabled alarm clearing, passed-alarm suspend path, resume clearing, and wakeup register writes.
