# subset-b-003801 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-input.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-input.c

## Purpose

`hid-input.c` is the generic HID-to-Linux-input bridge. It walks parsed HID reports, maps HID usages into `input_dev` event capabilities, creates one or more input devices for a HID device, dispatches incoming HID values into input events, manages output-report LEDs, exposes keymap get/set callbacks, negotiates resolution multipliers, and optionally registers HID battery usages as `power_supply` devices.

## Important APIs, Types, and Functions

- `hidinput_connect(struct hid_device *hid, unsigned int force)`: top-level input registration path. It initializes `hid->inputs` and LED work, runs feature/battery mapping, configures input/output report usages, adjusts resolution multipliers, and registers populated `input_dev` instances.
- `hidinput_disconnect(struct hid_device *hid)`: unregisters/free input devices and cancels pending LED work.
- `hidinput_hid_event(...)`: value-level dispatch from HID core to input core. It handles power-supply updates, hat switches, digitizer tool state, high-resolution wheels, relative volume emulation, absolute inversion quirks, MSC scan events, and relative-key release synthesis.
- `hidinput_report_event(...)`: emits `input_sync()` for each input device unless `HID_QUIRK_NO_INPUT_SYNC` is set.
- `hidinput_configure_usage(...)`: central usage-to-event mapper. It covers keyboard, button, simulation, generic desktop, LED, digitizer, telephony, consumer, battery, camera, HP vendor, PID, and fallback pages, while giving HID drivers `input_mapping` and `input_mapped` hooks.
- `hidinput_calc_abs_res(...)`: exported helper that derives input-axis resolution from HID logical/physical extents and units, including cm/inch, radians/degrees, and gram/newton conversion.
- LED helpers: `hidinput_get_led_field`, `hidinput_count_leds`, `hidinput_find_field`, `hidinput_led_worker`, and `hidinput_input_event`.
- Battery helpers under `CONFIG_HID_BATTERY_STRENGTH`: `hidinput_setup_battery`, `hidinput_update_battery`, query/scaling helpers, quirk table, and `hidinput_get_battery_property`.
- Device construction helpers: `hidinput_allocate`, `hidinput_match`, `hidinput_match_application`, `hidinput_configure_usages`, and cleanup helpers.

## Control Flow

Connection starts by rejecting non-input devices unless forced. Feature reports are scanned first so feature-backed battery strength and driver-specific feature mappings are available. Input and output reports are then walked; depending on quirks, reports are grouped by report id, by application, or into a default input device. Each field is tagged with a multi-touch slot index when a collection contains `HID_DG_CONTACTID`, then every usage is configured.

Generic mapping first lets the specific HID driver override or suppress a usage. Otherwise it maps by usage page and usage id, sets event bits, resolves duplicate codes, sets absolute parameters/resolution, creates hat-switch paired axes, and records `EV_MSC/MSC_SCAN` support for keys. Populated inputs are passed through the driver's `input_configured` hook and registered; empty ones are discarded.

Runtime events arrive through `hidinput_hid_event`. Power usages update `struct hid_battery`; normal usages are clamped or ignored according to HID null-state rules, transformed for digitizer tool state and scroll handling, filtered when unchanged, and sent via `input_event`. Report completion calls `hidinput_report_event`, which synchronizes all input devices for the HID device.

Output events from input userspace enter `hidinput_input_event`. Force-feedback events are delegated to `input_ff_event`; LED events update the matching HID output field and schedule `hidinput_led_worker`, which sends a HID output or set-report request.

## State and Persistence Behavior

Persistent state is attached to `struct hid_device`: the `hid->inputs` list, `hid->batteries`, `led_work`, quirk bits, report field mappings, and resolution multiplier state. Each `struct hid_input` owns one `input_dev`, optional generated name, application id, registration flag, and associated report list. Each `struct hid_usage` is mutated with input `type`, `code`, priority, hat metadata, wheel accumulator, and resolution multiplier.

Battery state persists in `struct hid_battery` instances allocated with devres: min/max, report id/type, capacity, status, presence, charge status, avoid-query flag, and rate-limit timestamp. LED state persists in HID output field values and is sent asynchronously through workqueue context. No file-backed persistence exists; all state is rebuilt on device re-probe or reset-resume.

## Dependencies and Integration Points

This file depends on HID core report parsing, HID driver hooks (`input_mapping`, `input_mapped`, `feature_mapping`, `input_configured`), input core APIs, power-supply APIs when enabled, workqueues, low-level HID request/output callbacks, KUnit test inclusion under `CONFIG_HID_KUNIT_TEST`, and constants from `linux/hid.h`, `linux/input.h`, and `hid-ids.h`. It exports several helpers for other HID code, including LED-field lookup/counting and report synchronization.

## Risks and Edge Cases

- Usage mapping is intentionally broad and highly compatibility-sensitive; changes can alter userspace-visible event codes for many devices.
- Duplicate-code suppression can silently ignore usages unless `HID_QUIRK_INCREMENT_USAGE_ON_DUPLICATE` is set.
- Descriptor-derived logical/physical ranges and units are trusted after limited sanity checks; malformed descriptors can yield missing resolution, ignored axes, or bad input ranges.
- Battery querying assumes small raw reports and may block in property reads unless the device is marked avoid-query.
- LED output work reads report fields without the HID core lock by design; it relies on later queued workers to converge if userspace races LED updates.
- Digitizer tool ordering depends on usage priorities and report ordering. Regressions can leave stale `BTN_TOOL_*` or `BTN_TOUCH` state.
- `hidinput_connect` has a broad unwind path; newly added allocation or registration work must be covered by `hidinput_disconnect` or explicit cleanup.

## Test Signals

Useful signals include `CONFIG_HID_KUNIT_TEST` coverage for mapping and resolution helpers, hid-tools replay tests for keyboards, mice, tablets, remotes, multi-touch devices, and high-resolution wheels, power-supply tests for report and feature battery devices, lockdep/workqueue checks around LED updates and disconnect, reset-resume tests for resolution multipliers, and userspace-visible event regression tests for duplicate usages, keymap remapping, digitizer eraser/in-range behavior, hat switches, and relative volume controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ite.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-ite.c

## Purpose

`hid-ite.c` handles ITE and ITE-like keyboard-controller HID devices that need small descriptor or event corrections. It fixes Acer/Synaptics keyboard-dock touchpad toggle descriptors, maps vendor-page touchpad on/off usages to the function keys expected by userspace, and synthesizes rfkill button press/release events for devices that only report a zero-valued release-like packet.

## Important APIs, Types, and Functions

- `QUIRK_TOUCHPAD_ON_OFF_REPORT`: per-device driver-data bit enabling Acer keyboard-dock descriptor and mapping fixes.
- `ite_report_fixup(...)`: checks exact descriptor sizes and byte offsets, then changes specific input items from absolute/variable to relative for touchpad on/off reports.
- `ite_input_mapping(...)`: maps vendor page `0x00880078` to `KEY_F22` and `0x00880079` to `KEY_F23`; suppresses other usages on that page for the quirked devices.
- `ite_event(...)`: intercepts `HID_GD_RFKILL_BTN` and emits a complete `KEY_RFKILL` press/release sequence.
- `ite_probe(...)`: stores `id->driver_data`, opens/parses the report descriptor with `hid_open_report`, and starts the hardware with default HID connections.
- `ite_devices` and `ite_driver`: match ITE, 258A, and specific Synaptics/Acer USB HID devices and register the fixup/mapping/event hooks.

## Control Flow

During probe the driver stores the quirk mask in HID drvdata before parsing. Descriptor parsing calls `ite_report_fixup`; quirked Acer dock descriptors are recognized by size and byte signatures, then a single item flag byte is patched. Input mapping later sees the corrected usages and remaps the two touchpad state events to F22/F23. Runtime rfkill reports are intercepted after input claiming; the driver obtains the report's `field->hidinput->input` device and sends press, sync, release, sync.

## State and Persistence Behavior

The only persistent state is the quirk bit stored via `hid_set_drvdata`. Descriptor mutation is in-memory for the current parsed HID device. The rfkill path stores no state and always treats a received rfkill usage as an instantaneous button press.

## Dependencies and Integration Points

This driver integrates with HID core report fixup, input mapping, and event hooks. It depends on HID/input constants, `hid-ids.h` IDs, and the generic HID input path for all normal events. Userspace compatibility is explicit: Acer touchpad toggles are mapped to `KEY_F22` and `KEY_F23`.

## Risks and Edge Cases

- Descriptor fixes are exact offset patches; firmware revisions with shifted descriptors will bypass the fix or could be mispatched if they match accidentally.
- `ite_event` assumes the rfkill report semantics are unique enough that any report means a press, regardless of value.
- Quirk storage casts integer driver data through `void *`; adding larger state would require a real allocation.
- The input mapping suppresses all other vendor page `0x00880000` usages on quirked devices.

## Test Signals

Test with affected Acer Switch/One docks should show F22/F23 events for touchpad toggles, no spurious axes from the toggle descriptor, and complete rfkill press/release events despite zero values. Descriptor regression tests should include the three known size/offset layouts and a nonmatching descriptor that remains unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-ite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-jabra.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-jabra.c

## Purpose

`hid-jabra.c` is a narrow Jabra USB HID input-mapping filter. It leaves standard HID usages to generic mapping but suppresses vendor-defined usages so Jabra headset control surfaces do not create noisy or misleading generic input events.

## Important APIs, Types, and Functions

- `HID_UP_VENDOR_DEFINED_MIN` / `HID_UP_VENDOR_DEFINED_MAX`: page-range bounds used to classify vendor-defined usage pages.
- `jabra_input_mapping(...)`: logs usage metadata with `dbg_hid`, returns `-1` for vendor-defined pages to ignore them, and returns `0` for normal generic mapping.
- `jabra_devices`: matches any USB HID product from `USB_VENDOR_ID_JABRA`.
- `jabra_driver`: registers only the input-mapping hook.

## Control Flow

When a Jabra HID device is parsed and generic HID input mapping examines each usage, `jabra_input_mapping` checks the usage page. Vendor-defined pages in `0xff00_0000` through `0xffff_0000` are suppressed. All other usages flow back into `hid-input.c` default mapping.

## State and Persistence Behavior

The driver has no allocated state, no mutable per-device data, and no persistence. It only affects the usage mapping decision made during input-device setup.

## Dependencies and Integration Points

It depends on HID core input mapping, module HID driver registration, and Jabra USB IDs from `hid-ids.h`. Its behavior is intentionally tied to generic `hid-input.c`: standard telephony, consumer, and keyboard usages remain available there.

## Risks and Edge Cases

- Suppressing all vendor-defined usages may hide useful controls if a future Jabra device exposes meaningful input semantics only on vendor pages.
- Matching `HID_ANY_ID` for all Jabra USB HID products makes the policy broad.
- The page-range check is page-based, not collection- or report-based, so mixed vendor/standard reports are partially mapped.

## Test Signals

Attach representative Jabra headsets and verify standard mute/call/media controls still appear while vendor pages do not create `KEY_UNKNOWN`, `BTN_MISC`, or `ABS_MISC` events. HID descriptor replay should cover standard-only, vendor-only, and mixed reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-jabra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kensington.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-kensington.c

## Purpose

`hid-kensington.c` supplies input mappings for Kensington Slimblade Trackball vendor-page button usages. It converts two Microsoft/vendor-page usages into standard mouse button codes so userspace sees middle and side buttons.

## Important APIs, Types, and Functions

- `ks_input_mapping(...)`: handles `HID_UP_MSVENDOR` usages `0x01` and `0x02`, mapping them to `BTN_MIDDLE` and `BTN_SIDE`.
- `ks_map_key(c)`: small wrapper around `hid_map_usage`.
- `ks_devices`: matches `USB_DEVICE_ID_KS_SLIMBLADE`.
- `ks_driver`: registers the input-mapping hook.

## Control Flow

During generic HID input setup, only Microsoft/vendor-page usages are considered by this driver. Usage `0x01` becomes `BTN_MIDDLE`; usage `0x02` becomes `BTN_SIDE`; all other usages fall through to generic mapping.

## State and Persistence Behavior

No driver-private state is allocated. The only persistent effect is the input capability and per-usage mapping stored by generic HID input setup.

## Dependencies and Integration Points

The file integrates with `hid-input.c` through `input_mapping`, uses HID/input constants, and matches the Kensington Slimblade USB ID from `hid-ids.h`.

## Risks and Edge Cases

- The mapping is device-specific but still assumes the vendor-page usage meanings stay stable for that PID.
- Unknown vendor usages fall through rather than being suppressed, so generic fallback behavior may still expose unexpected miscellaneous events.

## Test Signals

On a Slimblade Trackball, middle and side physical controls should emit `BTN_MIDDLE` and `BTN_SIDE`. Descriptor replay should verify non-MSVENDOR usages are unchanged and unknown MS vendor usages do not break probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kensington.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-keytouch.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-keytouch.c

## Purpose

`hid-keytouch.c` replaces the broken report descriptor for the Keytouch IEC keyboard with a known-good boot-keyboard-like descriptor that exposes modifier keys, LEDs, and six key slots.

## Important APIs, Types, and Functions

- `keytouch_fixed_rdesc`: complete replacement HID report descriptor.
- `keytouch_report_fixup(...)`: logs the fixup, replaces `*rsize`, and returns `keytouch_fixed_rdesc`.
- `keytouch_devices`: matches `USB_DEVICE_ID_KEYTOUCH_IEC`.
- `keytouch_driver`: registers the descriptor fixup hook.

## Control Flow

HID core calls `report_fixup` during report parsing. This driver unconditionally swaps the device descriptor with the static replacement for the matched Keytouch IEC device. Generic HID parsing and `hid-input.c` then build the input device from the fixed descriptor.

## State and Persistence Behavior

There is no mutable driver-private state. The replacement descriptor is static read-only data; its effect persists only in the parsed HID device for the current probe.

## Dependencies and Integration Points

The driver relies on HID core descriptor fixup, module registration, and Keytouch USB IDs. All input event behavior after descriptor replacement is delegated to generic HID input.

## Risks and Edge Cases

- The descriptor is an unconditional replacement for the PID. If a hardware revision uses the same ID with a different protocol, the driver will hide it.
- The replacement descriptor is minimal; any vendor-specific extra controls in the original descriptor are intentionally lost.
- Returning a static descriptor is correct for fixup but must remain immutable.

## Test Signals

The Keytouch IEC should parse without HID descriptor errors, expose keyboard keys and LED outputs, and register through generic HID input. Regression tests should compare descriptor size and key/LED capabilities against the fixed descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-keytouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kye.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-kye.c

## Purpose

`hid-kye.c` supports Kye/Genius mice, keyboards, and tablets with non-compliant descriptors. It patches incorrect mouse/keyboard consumer-control descriptors, replaces tablet descriptors with model-specific sane descriptors, adds optional mouse/control collections, and sends a feature report that enables absolute tablet mode.

## Important APIs, Types, and Functions

- Static control descriptors such as `easypen_m406_control_rdesc`, `pensketch_m912_control_rdesc`, and `mousepen_m508x_control_rdesc`: model-specific consumer-control reports for tablet buttons.
- `kye_tablet_rdesc` and `kye_tablet_mouse_rdesc`: descriptor templates for stylus and optional mouse-mode reports.
- `struct kye_tablet_info`: per-product logical/physical maxima, units, mouse support, and optional control descriptor metadata.
- `kye_consumer_control_fixup(...)`: clamps overly broad Consumer Control usage maxima in several Genius devices.
- `kye_tablet_fixup(...)`: replaces the descriptor with templates and patches model-specific X/Y/pressure ranges and units using unaligned little-endian writes.
- `kye_report_fixup(...)`: dispatches product-specific descriptor fixes.
- `kye_tablet_enable(...)`: finds feature report id 5, fills seven magic values, and sends `HID_REQ_SET_REPORT` to enable full tablet mode.
- `kye_probe(...)`: parses, starts HID hardware, applies a Manticore open/close workaround, and enables tablet mode for tablet products.

## Control Flow

Descriptor parsing calls `kye_report_fixup`. Older mice get byte-level descriptor edits; gaming keyboards/mice get Consumer Control usage maximums reduced; tablet products get a synthesized descriptor assembled from templates and `kye_tablets_info`. After `hid_hw_start`, probe applies runtime workarounds: Manticore is opened once so all interfaces become functional, and tablets receive the feature report that switches them from relative mouse behavior to absolute stylus behavior.

## State and Persistence Behavior

The driver has no heap state of its own. Persistent runtime effects are in the HID core: the modified descriptor, parsed reports, input devices, and any device-side tablet mode enabled by feature report id 5. Descriptor template data is static. Tablet mode is device state and may need reapplication after unplug or reset, but this file has no explicit resume hook.

## Dependencies and Integration Points

The driver depends on HID parser/start/request APIs, unaligned endian helpers, model IDs from `hid-ids.h`, and generic HID input mapping for the corrected descriptors. It integrates with HID feature reports for tablet mode switching and with userspace through standard digitizer, mouse, and consumer-control input events.

## Risks and Edge Cases

- `kye_tablet_fixup` assumes template byte offsets remain synchronized with comments; changing template bytes without updating offsets corrupts ranges/units.
- Descriptor replacement reuses the original descriptor buffer and requires the original `*rsize` to be large enough for all appended templates.
- Unknown tablet products in the switch but missing from `kye_tablets_info` fail fixup with an error and keep the original descriptor.
- `kye_tablet_enable` linearly searches for feature report id 5 and assumes at least seven values in field 0.
- There is no reset-resume re-enable path for tablet mode.
- The Manticore open/close workaround ignores the return except to close on success-like paths, so behavior relies on device side effects.

## Test Signals

Replay descriptors for each listed product and verify patched usage maxima, stylus axes, pressure ranges, optional mouse report, and control buttons. Hardware tests should confirm tablets report absolute coordinates after probe, Manticore extra interfaces work after the open/close workaround, feature report id 5 is present, and no descriptor buffer overrun warnings occur. Input tests should verify consumer buttons map to expected standard keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kye.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kysona.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-kysona.c

## Purpose

`hid-kysona.c` adds support for Kysona M600 and VXE Dragonfly mouse battery reporting. It periodically sends vendor output reports requesting online and battery information, parses matching raw input reports, and exposes the data through a `power_supply` device while leaving normal HID input connected.

## Important APIs, Types, and Functions

- `struct kysona_drvdata`: per-device state with HID pointer, online flag, power-supply descriptor/device, capacity, charging flag, voltage, and delayed work.
- `kysona_battery_get_property(...)`: reports status, present, capacity, scope, model name, voltage, and online state.
- `kysona_m600_fetch_online(...)` / `kysona_m600_fetch_battery(...)`: allocate request buffers and send fixed output reports through `hid_hw_raw_request`.
- `kysona_battery_timer_tick(...)`: periodic polling worker that requests online and battery reports every five seconds.
- `kysona_battery_probe(...)`: initializes defaults, registers the power supply, does initial fetches, and schedules polling.
- `kysona_probe(...)`: validates USB transport, allocates state, parses/starts HID, and only registers battery support on USB interface number 1.
- `kysona_raw_event(...)`: parses fixed-size online and battery reports, updating cached power data.
- `kysona_remove(...)`: cancels battery work if registered and stops HID hardware.

## Control Flow

Probe requires a USB HID device, stores devres-managed state, parses the descriptor, and starts with `HID_CONNECT_DEFAULT`. For interface 1 it registers a battery power supply and starts polling. Each timer tick sends online and battery request reports, then reschedules itself. When the device replies, `raw_event` identifies reports by size, report id, and second byte, then updates `online`, capacity, charging, and voltage fields.

## State and Persistence Behavior

Battery state is cached in `kysona_drvdata` and exposed via power-supply reads. Defaults are capacity 100 and voltage 4200 mV until reports arrive. Polling persists through delayed work until remove cancels it. There is no explicit `power_supply_changed()` call after raw updates, so userspace may observe updates by polling properties rather than receiving immediate change notifications.

## Dependencies and Integration Points

The driver depends on USB HID parent interfaces, HID raw requests/events, delayed work, devres allocation, and power-supply APIs. It matches Kysona and VXE USB IDs and delegates regular mouse input to the generic HID stack.

## Risks and Edge Cases

- Battery support is hard-wired to USB interface number 1; changed interface layouts will skip power support.
- Request and response formats are fixed 17-byte packets with magic trailing bytes.
- `kysona_probe` logs a stale `ret` value if `kysona_battery_probe` fails because it does not assign the call result.
- Raw-event updates do not notify the power-supply core, which can delay userspace visibility.
- The driver rejects non-USB transport even if future devices expose the same protocol elsewhere.
- Polling every five seconds creates recurring output reports; suspend/resume behavior is not explicitly handled.

## Test Signals

Hardware tests should verify interface 1 creates `kysona-*-battery`, capacity/online/charging/voltage update after reports, normal mouse input still works, and remove cancels polling cleanly. Negative tests should cover short raw requests, malformed reports, non-interface-1 devices, non-USB matches, and unplug during delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-kysona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lcpower.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lcpower.c

## Purpose

`hid-lcpower.c` maps vendor-page usages from the LC Power RC1000MCE remote control to standard Linux key codes, mainly colored media keys and TV/VCR/menu/home controls.

## Important APIs, Types, and Functions

- `ts_input_mapping(...)`: handles `HID_UP_LOGIVENDOR` usages and maps known values to `KEY_YELLOW`, `KEY_GREEN`, `KEY_BLUE`, `KEY_RED`, `KEY_HOME`, `KEY_TV`, `KEY_VCR`, and `KEY_MENU`.
- `ts_map_key_clear(c)`: wrapper around `hid_map_usage_clear`.
- `ts_devices`: matches `USB_DEVICE_ID_LCPOWER_LC1000`.
- `ts_driver`: registers the input-mapping hook.

## Control Flow

Generic HID input setup calls `ts_input_mapping` for each usage. Non-Logitech/vendor-page usages fall back to generic mapping. Known vendor usages are converted to standard remote-control keys and reported as handled; unknown usages fall through.

## State and Persistence Behavior

The driver has no private state. Its only persistent effect is the configured per-usage input mapping in the generic HID input device.

## Dependencies and Integration Points

It depends on HID input mapping helpers, input key constants, the LC Power USB ID, and generic HID input for probe and event dispatch.

## Risks and Edge Cases

- The driver uses a vendor page named `HID_UP_LOGIVENDOR` for an LC Power device, reflecting descriptor reality but making the mapping easy to misread.
- Unknown vendor usages are not suppressed, so generic fallback may expose miscellaneous events.
- Mapping is fixed to this one PID; remote variants need explicit ID additions.

## Test Signals

An RC1000MCE remote should emit the expected color, home, TV, VCR, and menu key codes. Descriptor replay should confirm non-vendor usages still follow generic mapping and unknown vendor usages do not prevent input registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lcpower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-led.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-led.c

## Purpose

`hid-led.c` is a simple USB HID RGB LED driver for several notification-light devices. It registers red, green, and blue LED class devices for each supported RGB unit and translates LED brightness changes into each device's HID feature or output report protocol.

## Important APIs, Types, and Functions

- `struct hidled_config`: per-device protocol configuration: type, names, max brightness, RGB unit count, report size/type, optional init callback, and write callback.
- `struct hidled_device`, `struct hidled_rgb`, and `struct hidled_led`: runtime topology for HID device, RGB units, and individual LED class devices.
- `hidled_send(...)`: serialized report sender using either `hid_hw_raw_request(... SET_REPORT)` or `hid_hw_output_report`.
- `hidled_recv(...)`: RAW_REQUEST-only helper that sends a command and reads a feature report response.
- Device protocol callbacks: `riso_kagaku_write`, `dream_cheeky_init/write`, `thingm_init/write`, `delcom_init/write`, and `luxafor_write`.
- `hidled_init_led(...)` / `hidled_init_rgb(...)`: register LED class devices with stable names and `LED_HW_PLUGGABLE`.
- `hidled_probe(...)`: parses HID, selects config from `driver_data`, runs protocol init, starts HIDRAW, gets the hidraw minor for LED names, allocates RGB state, and registers LEDs.
- `hidled_table`: maps Riso Kagaku, Dream Cheeky, ThingM blink(1), Delcom Visual Indicator, and Luxafor USB IDs to config types.

## Control Flow

Probe allocates `hidled_device` and a DMA-safe-ish report buffer, parses the HID descriptor, chooses a protocol config, optionally performs an init/readback check, allocates one `hidled_rgb` per RGB unit, and starts HID with `HID_CONNECT_HIDRAW`. It then registers red/green/blue LED class devices for each unit. When userspace changes any color LED brightness, the device-specific write callback reads the sibling color brightnesses, builds the protocol packet, and calls `hidled_send` under a mutex.

## State and Persistence Behavior

Runtime state is devres-managed and lives for the HID device lifetime: selected config, HID pointer, shared buffer, mutex, RGB array, LED names, and LED class brightness values. Device firmware state changes persist in the USB device until overwritten or reset. `thingm_init` can swap the config to a v1 variant based on firmware version readback.

## Dependencies and Integration Points

The driver integrates HID core, HIDRAW, LED class, mutexes, and device IDs. It exposes standard LED class devices rather than input events. It uses a module parameter, `riso_kagaku_switch_green_blue`, to adapt devices with swapped green/blue wiring.

## Risks and Edge Cases

- Protocol packets are hand-coded and device-specific; report size mismatches return `-EMSGSIZE`.
- `hidled_send` uses caller stack buffers as sources but copies into `ldev->buf` before HID I/O because raw requests require a separate buffer.
- `hidled_recv` is only valid for RAW_REQUEST configs and performs a SET_REPORT before GET_REPORT.
- Delcom devices share VID/PID; the init readback rejects non-family-2 devices.
- LED names include hidraw minor, so names can change across replug.
- Brightness writes for one component send all three current component values; concurrent LED writes are serialized but userspace may observe intermediate colors.

## Test Signals

Hardware tests should verify LED class device creation, RGB writes for each supported protocol, ThingM v1 detection, Delcom family rejection, Luxafor multi-unit naming, and Riso green/blue module-parameter behavior. Fault tests should cover short HID writes, unsupported report types, unregister during brightness writes, and probe failure cleanup after partial LED registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go-s.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go-s.c

## Purpose

`hid-lenovo-go-s.c` implements the Lenovo Legion Go S gamepad configuration interface. It sends synchronous 64-byte MCU commands, receives raw-event responses, exposes gamepad/IMU/MCU/mouse/touchpad sysfs controls, registers a multicolor LED for joystick-ring RGB, and preserves selected OS mode across reset-resume.

## Important APIs, Types, and Functions

- Global `drvdata` (`struct hid_gos_cfg`): cached configuration state, completion, mutex, HID pointer, delayed setup work, LED pointer, and per-feature values.
- `struct command_report` and `struct version_report`: packed views of 64-byte command/response packets.
- Command enums: `GET_VERSION`, `GET_MCU_ID`, `GET_GAMEPAD_CFG`, `SET_GAMEPAD_CFG`, `GET_TP_PARAM`, `SET_TP_PARAM`, `GET_RGB_CFG`, `SET_RGB_CFG`, and `GET_PL_TEST`.
- Raw-event handlers: `hid_gos_version_event`, `hid_gos_mcu_id_event`, `hid_gos_gamepad_cfg_event`, `hid_gos_touchpad_event`, `hid_gos_pl_test_event`, `hid_gos_light_event`, and `hid_gos_set_event_return`.
- `mcu_property_out(...)`: serializes one output report, waits for `send_cmd_complete`, reinitializes completion, and handles longer PL_TEST timeouts.
- Sysfs helpers: `gamepad_property_*`, `touchpad_property_*`, `test_property_show`, `mcu_id_show`, RGB show/store helpers, and macro-generated attributes.
- LED integration: `gos_rgb_subled_info`, `gos_cdev_rgb`, and `hid_gos_brightness_set`.
- Lifecycle: `hid_gos_probe`, `hid_gos_cfg_probe`, `cfg_setup`, `hid_gos_cfg_remove`, `hid_gos_reset_resume`, and `hid_gos_remove`.

## Control Flow

Probe parses and starts HID with `HID_CONNECT_HIDRAW`, opens the device, and distinguishes the configuration interface by endpoint `0x84`. Non-config interfaces stay as generic HIDRAW devices. The config interface creates sysfs groups, registers the multicolor LED, initializes completion, and schedules delayed setup because immediate MCU calls during probe can lock the MCU.

Sysfs writes parse text into protocol values, then call `mcu_property_out` with a set command. Sysfs reads issue a get command, wait for raw-event completion, and render the cached value populated by the matching raw-event handler. RGB writes build a six-byte profile payload containing effect, three color intensities, brightness, and speed. LED brightness writes use the active RGB profile and current subled intensities.

Raw events are accepted only from the config endpoint and only if they are exactly 64 bytes. The first byte selects the response command; handlers update `drvdata` and complete the pending command.

## State and Persistence Behavior

All configuration state is stored in one file-scope `drvdata`, so the implementation assumes at most one active Go S configuration interface. The mutex serializes command/response transactions, and the completion couples each output report to a later raw event. Cached fields back sysfs read formatting and RGB writes. Device-side settings persist in the MCU; the driver explicitly rewrites and verifies `FEATURE_OS_MODE` in reset-resume.

## Dependencies and Integration Points

The file depends on USB endpoint inspection, HID raw output/input reports, sysfs attribute groups, completions, delayed work, mutex guards, LED multicolor class, unaligned little-endian reads, and IDs from `hid-ids.h`. It integrates with generic HID by only taking special action on the configuration endpoint.

## Risks and Edge Cases

- Static global `drvdata`, static LED class data, and static subled arrays make multiple simultaneous devices unsafe.
- `mcu_property_out` maps timeout to `-EBUSY` internally but returns `0` at the end even after nonzero wait results, so interrupted waits may be hidden.
- Completion matching is command-agnostic; unexpected raw events on the config endpoint can complete the wrong sysfs transaction.
- Some stores send zero-length payloads when value is zero, relying on firmware interpreting absence as zero.
- Config removal holds `cfg_mutex` while cancelling delayed work; if the work is blocked on the same mutex, this can deadlock.
- RGB mode store rejects mode index 0 by using `ret <= 0`, so only "custom" is accepted from the two-value table.
- Raw-event size mismatch returns `-EINVAL`, which may be harsh if the interface emits other report sizes.

## Test Signals

Test signals include sysfs read/write round-trips for every attribute group, raw-event timeout and interruption behavior, reset-resume OS mode restoration, RGB LED class brightness and color updates, unplug during delayed setup, multiple-device probing, and malformed 64-byte responses with invalid indexes. Hardware tests should confirm endpoint `0x84` is the only configuration interface and generic interfaces still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go-s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go.c

## Purpose

`hid-lenovo-go.c` implements the Lenovo Legion Go series gamepad configuration driver. It exposes MCU, dongle, left/right controller, touchpad, FPS mouse-DPI, OS mode, rumble/calibration, and RGB controls through sysfs and LED multicolor APIs while passing non-configuration HID reports back into generic HID input handling.

## Important APIs, Types, and Functions

- Global `drvdata` (`struct hid_go_cfg`): cached versions, feature states, rumble/touchpad/RGB state, calibration status, command completion, mutex, HID pointer, delayed work, and LED pointer.
- `struct command_report`: packed 64-byte packet with report id, id, command, subcommand, device type, and payload.
- Protocol enums: command ids (`MCU_CONFIG_DATA`, `OS_MODE_DATA`, `GAMEPAD_DATA`), MCU commands, device types, feature/motor/calibration/RGB/status indexes, and OS mode values.
- Raw handlers: `hid_go_version_event`, `hid_go_feature_status_event`, `hid_go_motor_event`, `hid_go_fps_dpi_event`, `hid_go_light_event`, `hid_go_device_status_event`, `hid_go_os_mode_cfg_event`, and `hid_go_set_event_return`.
- `hid_go_raw_event(...)`: handles config responses from endpoint `0x83`; all other reports are forwarded with `hid_input_report`.
- `mcu_property_out(...)`: sends 64-byte output report id `0x05`, serializes through `cfg_mutex`, waits up to 50 ms for completion, and reinitializes completion.
- Sysfs helpers: `version_show`, `feature_status_*`, `motor_config_*`, `fps_mode_dpi_*`, `device_status_show`, `calibrate_config_*`, `os_mode_*`, and RGB helpers.
- Attribute macros create large sysfs groups for MCU, TX dongle, left/right handles, touchpad, and RGB.
- Lifecycle: `hid_go_probe`, `hid_go_cfg_probe`, `cfg_setup`, `hid_go_cfg_remove`, and `hid_go_remove`.

## Control Flow

Probe sets `HID_QUIRK_INPUT_PER_APP` and `HID_QUIRK_MULTI_INPUT`, parses HID, starts default HID connections, opens the device, and checks the endpoint. Non-`0x83` interfaces remain generic. The configuration interface creates sysfs groups and RGB LED attributes, initializes completion, and schedules delayed version fetching.

Each sysfs read sends a matching get command, waits for a raw response, and formats the updated cache. Writes validate the input string or number, encode a small payload, send a set command, and return the write count on success. Calibration attributes are write-only command triggers with companion option/status attributes. RGB attributes and LED brightness combine cached profile/effect/speed/subled state into six-byte profile writes.

Incoming raw reports are parsed only when they are 64-byte packets on endpoint `0x83`. Recognized MCU/OS-mode response packets update caches and complete pending operations. Other reports are explicitly forwarded to `hid_input_report` so normal controls still generate events.

## State and Persistence Behavior

State is global rather than per-device, so only one configuration device is safe. Cached version/feature/RGB/calibration values are updated by raw-event responses and used by sysfs and LED callbacks. `cfg_mutex` serializes command traffic; `send_cmd_complete` is the only pairing mechanism between requests and responses. Device-side settings persist in firmware/MCUs. There is no reset-resume handler in this file.

## Dependencies and Integration Points

The driver depends on USB endpoint inspection, HID raw reports, generic HID input forwarding, sysfs, completions, delayed work, mutex guards, LED multicolor class, endian helpers, and Lenovo IDs. It integrates with `hid-input.c` by setting multi-input quirks and by forwarding pass-through reports from `raw_event`.

## Risks and Edge Cases

- Static `drvdata`, LED class device, and subled data are not multi-device safe.
- `mcu_property_out` converts timeout to `-EBUSY` internally but returns `0` at the end, hiding timeout/interruption failures after the wait.
- The right-handle definitions contain suspicious device-type indexes: `imu_enabled_right` uses `FEATURE_IMU_BYPASS`, and `reset_right` targets `LEFT_CONTROLLER`.
- Config removal does not cancel `go_cfg_setup`, so delayed work may run after sysfs removal or device teardown.
- Completion matching is not tied to command id/device type; stray configuration responses can complete the wrong transaction.
- Several "unknown" enum index 0 values are rejected in stores by design, but zero-length payload behavior for value 0 is firmware-dependent.
- RGB speed is inverted on store but show returns cached raw value after refresh, which may be inconsistent with the comment's user-facing intent.
- `hid_go_remove` returns early on endpoint lookup failure and may skip stopping hardware.

## Test Signals

Hardware and replay tests should cover all endpoints, pass-through input reports, sysfs get/set for MCU/dongle/left/right/touchpad groups, right-controller IMU/reset behavior, delayed setup cancellation on remove, command timeout propagation, RGB LED brightness/color/profile writes, FPS DPI validation, calibration status updates, and multi-device attach. Regression tests should check that generic gamepad events still flow despite the raw-event hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo-go.c -->
