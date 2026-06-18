<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c

Purpose: The panic trigger redirects LEDs marked `LED_PANIC_INDICATOR` to a panic blink trigger and installs the global `panic_blink` hook.

Important APIs and state: A global `trigger` pointer stores the simple trigger named `panic`. `led_trigger_set_panic()` moves a LED class device onto the panic trigger list and clears blink delays to avoid delayed blinking. `led_trigger_panic_notifier()` scans global `leds_list` for panic indicators. `led_panic_blink()` emits full/off events for the panic blink state.

Control flow: Device init registers the trigger, registers an atomic panic notifier, and assigns `panic_blink`. On panic, matching LEDs are forcibly rebound to the panic trigger without normal locking because panic context is special.

State and persistence: Once panic occurs, LED trigger list membership is changed for panic-indicator LEDs. There is no unload path.

Dependencies and integration: It depends on LED core internals (`leds_list`, trigger lists), panic notifier chain, and the global panic blink callback.

Risks and test signals: Panic context intentionally bypasses normal locking, so only minimal list operations are performed. Test with LEDs flagged as panic indicators, no-indicator systems, and panic blinking in atomic context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-panic.c -->
