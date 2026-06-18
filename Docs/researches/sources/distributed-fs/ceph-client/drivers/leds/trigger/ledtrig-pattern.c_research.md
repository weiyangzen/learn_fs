<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c

Purpose: The pattern trigger plays brightness/duration tuples through software timers, high-resolution timers, or LED hardware pattern callbacks when available.

Important APIs and state: `struct pattern_trig_data` holds the LED, up to 1024 `struct led_pattern` tuples, current/next pointers, mutex, repeat counters, interpolation state, pattern type, timer, and hrtimer. Sysfs exposes `pattern`, `hr_pattern`, `hw_pattern` when hardware supports it, and `repeat`. Activation validates hardware `pattern_set`/`pattern_clear` pairing and initializes timers.

Control flow: Pattern stores cancel current playback, clear hardware pattern if needed, parse tuples from text or firmware default data, set the requested type, and call `pattern_trig_start_pattern()`. Software playback requires at least two tuples and starts either timer. The common timer function advances current/next tuples, handles finite repeat counts, applies step changes immediately, interpolates brightness every 50 ms for gradual dimming, and schedules the next callback. Hardware pattern playback delegates the full tuple array and repeat count to the LED driver. Repeat changes restart playback with the new repeat mode.

State and persistence: Per-LED trigger state persists until deactivation. Pattern tuples and repeat values are in memory only. `LED_INIT_DEFAULT_TRIGGER` is cleared after default pattern parsing. Hardware pattern state may persist in the LED driver until `pattern_clear()`.

Dependencies and integration: It integrates with LED class pattern callbacks, firmware `led_get_default_pattern()`, normal timers, hrtimers, sysfs attribute visibility, and LED brightness helpers.

Risks and test signals: Text parsing must avoid exceeding `MAX_PATTERNS` and must reject brightness over max. `pattern_trig_show_patterns()` assumes count is nonzero before writing newline. Timer/hrtimmer cancellation under sysfs mutation is protected by the mutex. Test finite and indefinite repeats, invalid tuple counts, gradual dimming, zero-duration tuples, hrtimer mode, hardware callbacks, default pattern init, and deactivation during active playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-pattern.c -->
