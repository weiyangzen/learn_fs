<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c

Purpose: The input-events trigger turns LEDs on after input activity and off after a configurable idle delay, intended for keyboard or capacitive-button backlights.

Important APIs and state: Global `input_events_data` contains delayed work, a spinlock, `led_on`, and `led_off_time`. Module parameter `led_off_delay_ms` controls idle timeout. An input handler subscribes to devices with EV_KEY, EV_REL, or EV_ABS support. `input_events_led_trigger` is the simple trigger pointer.

Control flow: Init initializes work and lock, registers the trigger named `input-events`, then registers the input handler. On each input event, the spinlocked path turns the trigger on if not already on, updates the off deadline, and schedules delayed work. The work function checks if the deadline has actually passed before turning the trigger off, avoiding races with new events.

State and persistence: State is global across all input devices and all LEDs bound to the trigger. It persists until module exit. LED on/off is trigger-wide rather than per input device.

Dependencies and integration: It depends on the input core, system per-CPU workqueue, LED trigger core, jiffies timing, and module parameters.

Risks and test signals: High event rates should not repeatedly call `led_trigger_event(LED_FULL)` thanks to `led_on`. Race coverage around delayed work and new events is important. Test handler connect/disconnect, off delay parameter, multiple input devices, nonblocking module exit, and delayed work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-input-events.c -->
