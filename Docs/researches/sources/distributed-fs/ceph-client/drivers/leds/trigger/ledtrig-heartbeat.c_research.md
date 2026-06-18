<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c

Purpose: The heartbeat trigger produces a double-pulse LED pattern whose period varies with the one-minute load average.

Important APIs and state: `struct heartbeat_trig_data` stores the LED, phase, period, timer, and invert flag. `led_heartbeat_function()` implements the phase machine. Sysfs exposes `invert`. Reboot and panic notifiers unregister or suppress blinking on panic.

Control flow: Activation allocates trigger data, initializes a timer, sets blink brightness, starts the heartbeat function, and marks software blinking. The timer cycles through four phases: on pulse, pause, second on pulse, long pause. Phase 0 recalculates period from `avenrun[0]`. Deactivation shuts down the timer and clears software blink state.

State and persistence: Per-LED phase state is transient. Global `panic_heartbeats` stops heartbeat output once a panic is observed.

Dependencies and integration: It uses LED core, timers, scheduler load average, panic notifier, and reboot notifier chains.

Risks and test signals: Delay arithmetic assumes period stays larger than pulse widths; load-average extremes should be checked. Test invert behavior, panic path, reboot unregister, brightness-change work flag, and trigger deactivation while timer is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-heartbeat.c -->
