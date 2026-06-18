# Research: sources/distributed-fs/ceph-client/drivers/usb/common/led.c

Purpose: registers two LED triggers, `usb-gadget` and `usb-host`, and exposes `usb_led_activity` so USB code can blink activity indicators for gadget or host events.

Important APIs: `DEFINE_LED_TRIGGER` creates `ledtrig_usb_gadget` and `ledtrig_usb_host`. `usb_led_activity(enum usb_led_event ev)` maps the event to a trigger and calls `led_trigger_blink_oneshot` with 30 ms on/off delays. `ledtrig_usb_init` registers the triggers, and `ledtrig_usb_exit` unregisters them.

Control flow and state: initialization registers simple triggers under the LED subsystem. Runtime events are one-shot blink requests; `led_trigger_blink_oneshot` tolerates a NULL trigger, so unsupported/unknown paths do not crash. Exit unregisters both triggers.

Dependencies and integration points: depends on LED class/trigger APIs and USB event enum definitions. Called from `usb_common_init/exit` through `common.h` only when `USB_LED_TRIG` is enabled. Exported `usb_led_activity` is available to host/gadget code.

Risks: trigger registration return values are ignored, so failures are silent. The trigger globals are shared and must be unregistered only after users stop generating events during usb-common teardown. Event enum additions require updating the switch.

Test signals: build with LED trigger support, verify `/sys/class/leds/*/trigger` lists `usb-gadget` and `usb-host`, generate host/gadget activity, and test unload/reload without dangling triggers.
