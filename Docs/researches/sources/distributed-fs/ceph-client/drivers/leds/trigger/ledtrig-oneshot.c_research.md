<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c

Purpose: The oneshot trigger exposes a manual pulse trigger with configurable on/off delays and invert behavior.

Important APIs and state: `struct oneshot_trig_data` stores `invert`. Sysfs attributes are `delay_on`, `delay_off`, `invert`, and write-only `shot`. `led_shot()` calls `led_blink_set_oneshot()` using the LED's delay fields and invert flag.

Control flow: Activation allocates state and, for LEDs initialized with a default trigger pattern, reads a two-value default pattern into `blink_delay_on/off` or falls back to 100 ms defaults. Writing `shot` starts a oneshot blink. Writing `invert` updates the idle brightness to full or off. Deactivation frees state and turns the LED off.

State and persistence: Delay values are stored in the LED class device; invert is per-trigger data. Default-trigger initialization clears `LED_INIT_DEFAULT_TRIGGER` to avoid repeated parsing.

Dependencies and integration: It uses LED class blink helpers, firmware default pattern helpers, and trigger sysfs groups.

Risks and test signals: Default pattern size must be exactly two values. Deactivation should stop any ongoing blink. Test pattern initialization, invalid sysfs values, invert idle state, repeated shot writes, and LEDs with hardware blink support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-oneshot.c -->
