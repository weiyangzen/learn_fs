# sources/distributed-fs/ceph-client/drivers/hid/hid-apple.c

## Purpose

`hid-apple.c` is the main Linux HID quirk driver for Apple keyboards, touchpad-keyboard composites, Magic Keyboard variants, Mighty Mouse, and related Apple-like devices. It fixes selected report descriptors, translates Fn-layer keys, supports ISO layout swapping, optional modifier swaps, PowerBook numlock emulation, Mighty Mouse button/wheel quirks, Magic Keyboard battery polling, and keyboard backlight LED integration for both older Apple HID reports and newer Magic backlight reports.

## Important APIs, Types, and Functions

- Module parameters: `fnmode`, `iso_layout`, `swap_opt_cmd`, `swap_ctrl_cmd`, and `swap_fn_leftctrl` control runtime key translation policy.
- Quirk bits such as `APPLE_HAS_FN`, `APPLE_ISO_TILDE_QUIRK`, `APPLE_MIGHTYMOUSE`, `APPLE_NUMLOCK_EMULATION`, `APPLE_RDESC_BATTERY`, `APPLE_BACKLIGHT_CTL`, `APPLE_MAGIC_BACKLIGHT`, and `APPLE_DISABLE_FKEYS` select device-specific behavior from `apple_devices[]`.
- `struct apple_sc` is per-device state: HID pointer, quirks, Fn state, whether an Fn usage was found, pressed numlock bitmap, battery polling timer, and optional backlight state.
- `struct apple_key_translation` and the many translation tables map Apple Fn-layer, Touch Bar Fn-row, ISO, modifier-swap, and numlock-emulation keys.
- `hidinput_apple_event()` is the core key translation engine. It resolves effective `fnmode`, applies optional modifier/layout swaps, tracks Fn key state, selects the product-specific translation table, handles held translated keys, and emits translated events.
- `apple_report_fixup()` patches known JIS logical maximum errors and Magic Keyboard USB battery descriptors.
- `apple_fetch_battery()` and `apple_battery_timer_tick()` periodically request Magic Keyboard battery reports when `CONFIG_HID_BATTERY_STRENGTH` is enabled and the device uses the battery descriptor quirk.
- `apple_backlight_init()` registers an LED class device for older keyboard backlight reports discovered through vendor input usages and configured through raw HID reports.
- `apple_magic_backlight_init()` registers a LED class device for the Magic backlight endpoint, using existing feature reports for power and brightness.
- `apple_probe()` allocates state, parses and starts HID hardware, starts optional battery polling, and initializes optional backlight support.

## Control Flow

The match table supplies quirk bits for a large set of Apple USB and Bluetooth device IDs. Probe stores those bits in `struct apple_sc`, calls `hid_parse()`, starts hardware, then enables optional services: battery polling for `APPLE_RDESC_BATTERY`, legacy keyboard backlight for `APPLE_BACKLIGHT_CTL`, and Magic backlight for `APPLE_MAGIC_BACKLIGHT`. If Magic backlight initialization fails, probe tears down the battery timer if present and stops HID hardware.

Before parsing finishes, `apple_report_fixup()` can mutate descriptor bytes. It expands JIS keyboard logical maximums from `0x65` to `0xe7` for known descriptor layouts and rewrites a Magic Keyboard USB battery descriptor from vendor-defined usage to Generic Desktop Keyboard by shortening the descriptor view by one byte and patching the first bytes.

Input mapping handles the Apple Fn usage on Custom, Microsoft vendor, or HP vendor pages with usage ID `3`. When found, it maps the usage to `KEY_FN`, enables repeat, records `fn_found`, and pre-enables all possible translated keys. `apple_input_configured()` disables Fn handling if a claimed Fn-capable device did not expose Fn, and marks known non-Apple keyboards that reuse Apple IDs so default `fnmode=3` behaves as fkeys-first.

At event time, `apple_event()` first handles Mighty Mouse horizontal-wheel inversion. If the device has Fn handling, it calls `hidinput_apple_event()`. That function applies optional Fn/Ctrl, ISO, Option/Command, and Control/Command remapping before Fn-layer decisions. It selects a translation table by product family, computes whether a function key should become a media/system key or stay an F-key based on `fnmode`, `APPLE_DISABLE_FKEYS`, non-Apple detection, and current Fn state, handles numlock emulation, and emits translated events with `MSC_SCAN` where needed.

## State and Persistence Behavior

Per-device runtime state is devm-managed through `struct apple_sc`. `fn_on` tracks current Fn key state, `fn_found` records input descriptor discovery, and `pressed_numlock` tracks original keys currently held while numlock emulation is active so release events translate consistently. The battery timer persists until remove and periodically reschedules only if `apple_fetch_battery()` succeeds. LED class devices are devm-registered and persist until device removal.

There is no persistent storage across boots. Module parameters are global driver configuration and affect all bound Apple devices. Hardware state can be changed through backlight reports and battery GET_REPORT requests; keyboard backlight is explicitly set to zero during initialization in both backlight paths.

## Dependencies and Integration Points

- Depends on HID core hooks for descriptor fixup, input mapping, input-mapped adjustment, input configuration, events, probe, and remove.
- Uses Linux input key codes, LED state, `EV_MSC/MSC_SCAN`, relative wheel events, and key bitmaps.
- Uses timer APIs and jiffies for battery polling.
- Integrates with `CONFIG_HID_BATTERY_STRENGTH` through `hid_get_battery()` and HID report metadata.
- Uses LED class devices and `dt-bindings/leds/common.h` for keyboard backlight naming.
- Uses raw HID report requests for legacy backlight configuration/output and normal HID feature report updates for Magic backlight.
- Relies heavily on `hid-ids.h` Apple product constants and on exact HID descriptor byte layouts for fixups.

## Risks and Edge Cases

- Descriptor fixups match hard-coded offsets and byte values. A small firmware descriptor change can bypass the fixup or, worse, match an unintended descriptor.
- `fnmode`, swap parameters, and ISO layout are global. Mixed Apple and Apple-ID-clone keyboards can need different behavior, but only some clone handling is built in.
- `apple_backlight_init()` allocates `0x200` bytes but requests only `sizeof(*rep)` bytes from report ID `0xBF`; if the device returns a larger config report, the current code only validates the small header it requested.
- Legacy backlight report structs contain `u16` fields sent through raw HID without explicit little-endian conversion. This assumes the report ABI and CPU layout agree.
- Magic backlight writes directly into `rep->field[*]->value[0]` and assumes both reports have at least two fields; it validates maxfield but not field value array sizes beyond normal HID report invariants.
- Battery polling only reschedules after successful fetch. A transient failure can stop future polling until rebinding.
- Translation logic tries to preserve press/release pairing by checking currently set source and target keys. Changes in module parameters while keys are held can still produce surprising sequences.
- Non-Apple keyboard detection is name-prefix based and can miss clones or misclassify devices with similar names.

## Test Signals

- Descriptor tests should cover JIS fixups and Magic Keyboard USB battery descriptor rewrites, including no-op behavior for near matches.
- Key translation tests should exercise `fnmode` values 0, 1, 2, 3, and 4; Fn press/release state; Touch Bar Fn-row mappings; ISO swap; Option/Command swap modes; Control/Command swap; Fn/left-Ctrl swap; and numlock emulation.
- Event tests should verify `MSC_SCAN` emission when translated key events are generated and no duplicate events are produced for unchanged mappings.
- Mighty Mouse tests should verify button swap, Z-to-horizontal mapping, and horizontal wheel inversion.
- Battery tests with `CONFIG_HID_BATTERY_STRENGTH` should verify initial fetch, timer rescheduling, non-rescheduling on failure, and teardown on remove.
- Backlight tests should validate LED class registration, max brightness, suspend/resume flags, report request contents, and failure cleanup for both legacy and Magic backlight paths.
- Device table tests should ensure newly added Apple IDs carry the intended quirk bits and do not unintentionally select incompatible translation tables.
