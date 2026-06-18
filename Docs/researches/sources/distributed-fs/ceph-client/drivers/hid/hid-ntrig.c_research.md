# sources/distributed-fs/ceph-client/drivers/hid/hid-ntrig.c

## Purpose

`hid-ntrig.c` handles older N-Trig USB touchscreens that need special filtering and activation logic beyond generic HID multitouch. It supports pen, single-touch, and multitouch reports, exposes sysfs tunables for physical/logical sensor sizes and contact filtering thresholds, reports firmware version for USB devices, and implements an activation/deactivation state machine to avoid noisy or bogus touch frames.

## Important APIs, Types, and Functions

- Module parameters `min_width`, `min_height`, `activate_slack`, `deactivate_slack`, `activation_width`, and `activation_height` seed per-device filtering thresholds.
- `struct ntrig_data` stores current contact fields, multitouch footer accumulation, activation state, slack values, thresholds, and sensor physical/logical dimensions.
- `ntrig_version_string()`, `ntrig_get_mode()`, `ntrig_set_mode()`, and `ntrig_report_version()` decode firmware information and nudge newer firmware modes.
- Sysfs show/set functions expose sensor dimensions and threshold/slack tuning through `ntrig_attribute_group`.
- `ntrig_input_mapping()` maps logical multitouch X/Y/width/height fields, captures sensor dimensions, suppresses untrusted/contact-control usages, and lets pen/single-touch physical fields use generic handling.
- `ntrig_event()` consumes HID events, accumulates contact data and vendor footer bytes, filters contacts by confidence/size/pen activity, emits MT events, and updates BTN_TOUCH/BTN_TOOL_DOUBLETAP at contact-count frame boundaries.
- Probe/remove allocate/free `ntrig_data`, apply duplicate-usage quirks, start HID, adjust mode, create sysfs, and stop hardware on removal.

## Control Flow

Probe applies `HID_QUIRK_MULTI_INPUT` and `HID_QUIRK_NO_INIT_REPORTS` for listed devices, initializes per-device thresholds and sensor defaults, parses and starts HID, sends a feature-report wake/mode sanity sequence if report `0x0a` exists, reports firmware version through a USB control message, and creates sysfs attributes. Descriptor mapping stores sensor scale information from logical multitouch X/Y fields and initializes physical-unit thresholds.

Runtime event handling distinguishes pen, single-touch, and multitouch. A vendor usage marks the start of a multitouch group. X/Y/width/height/contact ID/tip/confidence fields are cached. Vendor footer usage `0xff000002` arrives four times per contact; once complete, the driver detects pen activity, placeholders, size threshold failures, activation threshold shortcuts, confidence failures, first-contact single-touch emulation, and emits MT position/major/minor/orientation plus `input_mt_sync()`. On `HID_DG_CONTACTCOUNT`, it updates the activation state machine and reports touch buttons if the frame is active.

## State and Persistence Behavior

All mutable state is in `struct ntrig_data` and sysfs-adjustable at runtime. Thresholds are stored in logical sensor units but shown and accepted in physical dimensions. `act_state` tracks inactive, active, and pen-termination phases; `reading_mt` and footer counters reset across frames. There is no persistent storage beyond module parameters used for new devices.

## Dependencies and Integration Points

The file integrates HID core mapping/event/configured callbacks, input MT protocol B-era helpers (`input_mt_sync`), sysfs attributes, USB control transfers for firmware version, usbhid helpers, and N-Trig IDs. It grabs all usages through `ntrig_grabbed_usages` so it can filter events before generic hidinput emits them.

## Risks and Edge Cases

- Sysfs threshold conversions divide by sensor physical/logical dimensions; probe seeds them to 1, but malformed descriptors with zero physical size could still make scale behavior questionable.
- `ntrig_get_mode()` and `ntrig_set_mode()` rely on specific feature report IDs and do limited validation.
- The activation state machine is sensitive to footer order, contact count semantics, and pen activity frames; small firmware differences can cause stuck or suppressed touch.
- `ntrig_input_mapped()` clears generic mappings for many usages, so missed custom emission can remove input events entirely.
- Size filtering marks confidence false for small contacts but still uses them for activation state, which is intentional but tricky.

## Test Signals

Test pen-only reports, physical single-touch reports, logical multitouch frames, footer accumulation, placeholder contacts, pen-activity termination, activation/deactivation slack transitions, threshold sysfs conversions and bounds, duplicate usage devices, mode sanity path, firmware-version control transfer, and input device naming. Regression hardware tests should verify no stuck BTN_TOUCH after empty frames or pen transitions.
