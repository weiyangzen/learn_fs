<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c

Purpose: The activity trigger blinks an LED according to immediate aggregate CPU usage, with faint slow flashes when idle and higher duty/frequency under load. On panic it leaves the LED at full brightness.

Important APIs and state: `struct activity_data` stores a timer, LED pointer, last CPU-used and boot-time totals, remaining timing budget, blink state, and `invert` sysfs setting. `led_activity_function()` is the timer callback. `activity_activate()` allocates state and starts the timer; `activity_deactivate()` shuts it down. Sysfs exposes `invert`. Reboot and panic notifier blocks unregister or force panic behavior.

Control flow: The timer samples per-CPU kernel cpustats and boot time, computes a percentage, toggles LED state when the current pulse expires, calculates the next on/off delay, caps sleeps to 100 ms for responsiveness, and rearms itself. It also handles `LED_BLINK_BRIGHTNESS_CHANGE`. Activation initializes blink brightness and calls the timer function once to start the cycle.

State and persistence: Per-LED state is heap allocated and stored as trigger data. A global `panic_detected` flag permanently changes behavior after panic notification. There is no persistence across trigger deactivation.

Dependencies and integration: It depends on cpustat accessors, timers, reboot and panic notifier chains, LED trigger registration, and internal LED work flags.

Risks and test signals: CPU accounting math shifts values down to avoid overflow; large CPU-count systems and wraparound deserve coverage. Timer teardown uses `timer_shutdown_sync()`, so deactivate should be safe against callbacks. Test invert sysfs, brightness changes, panic/reboot notifier behavior, and CPU-load response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-activity.c -->
