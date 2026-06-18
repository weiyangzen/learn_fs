<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c

## Purpose

`hid-magicmouse.c` is the Apple Magic Mouse and Magic Trackpad HID driver. It switches supported Apple devices into multitouch mode, decodes proprietary touch reports, reports multitouch slots and pointer/button events through the input subsystem, emulates middle button and scroll wheel behavior for Magic Mouse devices, normalizes trackpad input capabilities, and polls USB Magic Mouse 2 and Magic Trackpad 2 battery reports when needed.

## Important APIs, Types, and Functions

- Module parameters control behavior: `emulate_3button`, `emulate_scroll_wheel`, `scroll_speed`, `scroll_acceleration`, and `report_undeciphered`.
- `struct magicmouse_sc` is the per-device state. It stores the input device, touch count, scroll acceleration and timing, per-tracking-ID touch/scroll state, raw tracking IDs, HID device pointer, delayed multitouch work, and USB battery timer.
- `magicmouse_emit_touch` decodes raw touch records for Magic Mouse, Magic Mouse 2, Magic Trackpad, and Magic Trackpad 2 formats, updates tracking state, emits multitouch ABS events, and optionally synthesizes scroll wheel events.
- `magicmouse_emit_buttons` applies three-button emulation based on existing button state and the position of the single firm touch.
- `magicmouse_raw_event` validates report sizes, handles mouse, trackpad, mouse2, trackpad2 USB/Bluetooth, and double-report packets, then emits relative motion, buttons, multitouch frames, and input sync.
- `magicmouse_setup_input`, `magicmouse_input_mapping`, and `magicmouse_input_configured` reshape hidinput capabilities for mice and trackpads.
- `magicmouse_enable_multitouch` sends feature reports needed to enable touch data for each transport and product family; `magicmouse_enable_mt_work` retries one problematic Magic Mouse 2 case.
- `magicmouse_fetch_battery` and `magicmouse_battery_timer_tick` request USB battery reports under `CONFIG_HID_BATTERY_STRENGTH`.
- `magicmouse_report_fixup` adjusts USB Magic Mouse 2 and Magic Trackpad 2 battery descriptors so they expose a Generic Desktop Mouse usage instead of a vendor usage.

## Control Flow

Probe allocates `magicmouse_sc` with devm, initializes scroll acceleration, stores driver data, parses the HID descriptor, and starts hardware. USB Magic Mouse 2 and Magic Trackpad 2 devices set up a timer that periodically fetches battery reports. Some USB devices return early after generic hidinput setup because they expose their multitouch-capable input differently. Other devices ensure an input node was configured, register the proprietary touch report IDs, set a nominal report size, and send the feature report that enables multitouch data. If Magic Mouse 2 returns `-EIO` for the enable command, a delayed retry is scheduled because that error is treated as a known device behavior.

Raw input is the main runtime path. Each supported report ID has strict size and alignment checks before touch records are decoded. `DOUBLE_REPORT_ID` recursively processes two embedded reports after validating the embedded length. For mouse products, touch state is decoded before clicks so middle/right/left emulation can use current finger position; relative motion and click state are reported afterward. Trackpad products report buttonpad state and multitouch frames, using pointer emulation for the first-generation trackpad and tracked multitouch for Trackpad 2.

Input setup clears unwanted buttons and relative axes for trackpads, sets buttonpad properties, initializes 16 multitouch slots, configures per-product coordinate ranges and resolutions, exposes pressure where available, adds high-resolution wheel axes for scroll emulation, optionally enables raw MSC reporting for unknown touch-state bits, and disables autorepeat.

## State and Persistence Behavior

Per-device touch and scroll state persists in `magicmouse_sc` across reports. Each tracking ID stores the last coordinate, touch size, scroll anchors, high-resolution scroll anchors, and active-axis flags. `ntouches` is reset for each report and counts current down touches. `scroll_accel` and `scroll_jiffies` persist across scroll gestures to implement optional accelerated scrolling and reset behavior. Button state is read from the input device key bitmap so emulation can keep an existing button held until release.

The delayed multitouch work and battery timer persist until remove or probe failure cleanup. Remove cancels delayed work, deletes the battery timer for USB Magic Mouse 2 and Trackpad 2 devices, and stops HID hardware. Module parameters are global and affect all matching devices while the module is loaded.

## Dependencies and Integration Points

The driver integrates with HID report parsing, report fixup, raw-event callbacks, input mapping/configuration, feature reports, and HID battery infrastructure. It uses the input multitouch helper API, relative and absolute input events, workqueues, timers, jiffies, module parameters, and Apple IDs from `hid-ids.h`. It exposes normal Linux input devices and, when configured, battery state through the HID battery layer. Its descriptor fixup affects how the HID core sees battery-capable USB devices before input setup.

## Risks and Edge Cases

- Proprietary report decoding relies on packed bit extraction and fixed offsets. Incorrect size validation or a new Apple report format can produce wrong coordinates, IDs, or button state.
- `MOUSE2_REPORT_ID` allows size 8, but computes `npoints = (size - 14) / 8`; integer division makes this zero for size 8, which is intentional but easy to misread.
- Recursive double-report handling must reject short or inconsistent embedded lengths to avoid out-of-bounds reads; the current code performs those checks.
- Scroll speed is constrained to 0..63 to avoid divide-by-zero from `(64 - scroll_speed)`.
- Middle-button emulation depends on the single firm touch heuristic and x thresholds; unusual hand posture can produce unexpected button choices.
- USB battery polling only runs when HID battery support is enabled and only for selected USB products.
- The descriptor fixup shifts the descriptor pointer by one byte and reduces size, which is unusual and should be tested against descriptor ownership assumptions.

## Test Signals

Raw-report tests should cover each report ID, invalid sizes, maximum 15 touch points, double-report recursion, no-touch reports, and per-device coordinate decoding. Input tests should verify Magic Mouse left/right/middle emulation, scroll and high-resolution scroll emission, trackpad buttonpad behavior, multitouch slot lifetimes, pressure on Trackpad 2, and suppression of default Magic Mouse 2 hidinput button handling. Configuration tests should cover module parameter changes, feature-report failures including the Magic Mouse 2 `-EIO` retry path, battery timer setup/removal, and descriptor fixup for USB Magic Mouse 2 and Magic Trackpad 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c -->
