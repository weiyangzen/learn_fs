# sources/distributed-fs/ceph-client/drivers/hid/hid-speedlink.c

Purpose: fixes Speedlink Vicious and Divine Cezanne USB mouse behavior by ignoring bogus LED usages on the keyboard endpoint and filtering invalid relative X/Y motion events that cause a jumpy cursor.

Important APIs/types/functions: `speedlink_input_mapping()` rejects HID LED page usages. `speedlink_event()` filters selected relative motion events. `speedlink_grabbed_usages` limits `.event` interception to `HID_GD_X` and `HID_GD_Y`. `speedlink_driver` binds the X-Tensions Speedlink VAD Cezanne device.

Control flow: during input mapping, any usage from `HID_UP_LED` returns `-1`, preventing nonexistent keyboard LEDs from being exposed. Runtime event handling receives only grabbed X/Y relative events; it drops events where `abs(value) >= 256` and also drops zero-distance events, returning `1` to stop normal processing. Other values pass through.

State and persistence: no private state. Behavior is purely descriptor/input mapping and runtime event filtering.

Dependencies/integration: depends on HID usage tables, Linux relative input processing, and `hid-ids.h` device IDs.

Risks: the motion filter is intentionally heuristic. If a future valid high-resolution device reuses the same ID and sends deltas >= 256, the driver would suppress legitimate motion. Dropping zero relative events is normally harmless but can hide protocol diagnostics. The usage table makes the event hook narrow.

Test signals: affected mouse should no longer jump on clicks or bogus reports; normal small relative movement should pass; LED devices should not appear for the keyboard endpoint; logs should not show parse failures.
