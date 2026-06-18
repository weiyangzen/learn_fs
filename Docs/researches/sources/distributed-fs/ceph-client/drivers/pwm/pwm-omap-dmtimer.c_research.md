<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c

Purpose: implements PWM output using an OMAP dual-mode timer instance, turning timer load/match/toggle behavior into a one-channel PWM provider.

Important APIs/types/functions: `struct pwm_omap_dmtimer_chip` holds the PWM chip, timer pointer, mutex, clock rate, and timer ops. `pwm_omap_dmtimer_config()`, `pwm_omap_dmtimer_set_polarity()`, `pwm_omap_dmtimer_apply()`, `pwm_omap_dmtimer_start()`, `pwm_omap_dmtimer_is_enabled()`, and `pwm_omap_dmtimer_polarity()` implement behavior around dmtimer callbacks.

Control flow: probe requests a timer by phandle or platform data, gets timer ops and functional clock rate, configures PWM capability, and registers one PWM. Apply locks, programs load and match values for requested period/duty, configures output trigger mode and polarity, starts/stops the timer according to enabled state, and preserves timer state rules needed by OMAP hardware.

State and persistence: timer hardware holds counter, load, match, trigger, and enable state. The driver stores timer handle and clock rate but no persistent waveform cache. Remove unregisters the PWM and releases/stops the timer.

Dependencies and integration: depends on OMAP dmtimer platform APIs, clock rate from timer fclk, mutexes, platform/OF, and PWM core. It is an integration layer over another kernel timer driver rather than direct MMIO.

Risks and test signals: timer ownership conflicts and dmtimer callback semantics are the main risks. Test phandle lookup, unavailable timers, polarity changes, load minimum values, long/short periods, remove while enabled, and timer clock-rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c -->
