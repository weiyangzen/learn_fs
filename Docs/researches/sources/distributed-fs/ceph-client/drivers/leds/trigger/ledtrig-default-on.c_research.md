<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c

Purpose: The default-on trigger sets an LED to maximum brightness when the trigger is activated.

Important APIs and control flow: `defon_trig_activate()` calls `led_set_brightness_nosleep()` with `max_brightness`. `module_led_trigger(defon_led_trigger)` registers the trigger named `default-on`.

State and dependencies: There is no per-trigger state, no sysfs attributes, and no persistence beyond the LED class brightness. It depends only on the LED trigger core.

Risks and test signals: Behavior is intentionally minimal. Test that selecting the trigger on a LED sets full brightness and that the module alias `ledtrig:default-on` resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-default-on.c -->
