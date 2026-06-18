<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c

Purpose: The transient trigger provides a one-shot timed activation for LEDs, primarily for GPIO/PWM hardware that needs a temporary state then restoration.

Important APIs and state: `struct transient_trig_data` stores activate flag, target state, restore state, duration, timer, and LED pointer. Sysfs attributes are `activate`, `duration`, and `state`.

Control flow: Activation allocates state and initializes the timer. Writing `state` selects the transient brightness as full or off. Writing `duration` sets the timer length in milliseconds. Writing `activate=1` starts a timer only if not already active and duration is nonzero, sets the LED to target state, computes opposite restore state, and arms the timer. Writing `activate=0` while active deletes the timer and restores state immediately. Timer expiry clears activate and restores brightness. Deactivation shuts down the timer, restores brightness, and frees state.

State and persistence: State is per LED and in memory only. `restore_state` is computed as the opposite of target state, not the previous LED brightness.

Dependencies and integration: It uses LED trigger sysfs, kernel timers, and LED brightness helpers.

Risks and test signals: There is no mutex around sysfs/timer fields, so tests should stress concurrent sysfs writes and expiry. `timer_delete()` in sysfs cancel is not synchronous, while deactivate uses `timer_shutdown_sync()`. Test duration zero, repeated activate writes, state toggles, cancel behavior, and deactivation during active timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-transient.c -->
