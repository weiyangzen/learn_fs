# Research: subset-b-003807

Grouped research for HID Roccat, Saitek, Samsung, Semitek, sensor custom/hub, SiGma Micro, SmartJoy, Sony, Speedlink, Steam, SteelSeries, and Sunplus drivers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat.c

Purpose: provides the shared Roccat character-device bridge used by Roccat HID subdrivers to expose vendor-specific events to user space. It is not a normal `struct hid_driver`; it registers a char-device major, allocates up to eight minor devices with `roccat_connect()`, and lets device-specific HID drivers push special reports with `roccat_report_event()`.

Important APIs/types/functions: `struct roccat_device` owns one HID device, report size, reader list, waitqueue, and a fixed 16-slot circular buffer. `struct roccat_reader` stores each file reader's read pointer. Exported APIs are `roccat_connect()`, `roccat_disconnect()`, and `roccat_report_event()`. File operations are `roccat_open`, `roccat_read`, `roccat_poll`, `roccat_release`, and `roccat_ioctl`, with `ROCCATIOCGREPSIZE` exposing report size.

Control flow: module init allocates a char-device region and installs one cdev. A Roccat HID subdriver calls `roccat_connect()` with its class, HID device, and report size; the helper reserves a minor under `devices_lock`, creates `/dev/roccat<driver><minor>`, and initializes locks and queues. User open allocates a reader, powers and opens the HID device for the first reader, and starts at the current circular-buffer end so old events are not replayed. Interrupt-side producer code calls `roccat_report_event()`, which `kmemdup()`s the report with `GFP_ATOMIC`, replaces the next slot, advances `cbuf_end`, moves slow readers forward on overrun, and wakes waiters. Read blocks unless nonblocking or interrupted, copies at most one report, and advances only that reader.

State and persistence: global persistent state is `roccat_major`, `roccat_cdev`, and `devices[8]`. Per-device state persists until disconnect and last close complete. Event data persists only in the in-memory circular buffer and is dropped on overflow or if the caller supplies a shorter userspace read buffer. `exist` gates read and release behavior after disconnect; open count gates HID power/open lifetime.

Dependencies/integration: integrates Linux char devices, device-class sysfs naming, HID runtime power/open/close, waitqueues, poll, and the exported `linux/hid-roccat.h` ABI. The exported symbols are consumed by Roccat model drivers that know the vendor report layout.

Risks: `roccat_report_event()` dereferences `devices[minor]` without taking `devices_lock`, so caller lifetime discipline around disconnect matters. The function claims interrupt-handler use but takes mutexes; this assumes the HID callback context can sleep or is otherwise safe in the calling path. Disconnect races are mitigated by `exist`, wakeups, and delayed free while open, but invalid minors or stale minors would be fatal. Slow readers silently lose oldest events. A short read truncates and discards the rest of a report by design.

Test signals: load/unload with multiple connected devices; open/read/poll in blocking and nonblocking modes; disconnect while blocked in read; multiple readers with one slow reader; ioctl report-size query; event bursts above 16 reports; first-open power/open and last-close close/power transitions; invalid minor open behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-saitek.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-saitek.c

Purpose: implements Saitek/Mad Catz HID quirks for the PS1000 gamepad and R.A.T./M.M.O. gaming mice. It fixes a broken PS1000 report descriptor and converts mode-button state changes on several mice into normal press/release input events.

Important APIs/types/functions: `struct saitek_sc` stores `quirks` and previous `mode`. Quirk bits are `SAITEK_FIX_PS1000`, `SAITEK_RELEASE_MODE_RAT7`, and `SAITEK_RELEASE_MODE_MMO7`. Main callbacks are `saitek_probe`, `saitek_report_fixup`, `saitek_raw_event`, and `saitek_event`.

Control flow: probe allocates driver data, records `id->driver_data`, initializes mode to `-1`, parses HID, and starts hardware. Descriptor fixup checks the exact PS1000 descriptor size and byte pattern, converts a spurious axis item into a no-op logical minimum, and clears constant bits for buttons/d-pad. Raw-event handling for R.A.T. devices reads the mode bits from the report, clears those bits so they do not stay permanently pressed, and injects one chosen mode bit only when the mode changes after the initial state. The `.event` callback sees that synthetic press and immediately reports a release to compensate for missing hardware release events.

State and persistence: only per-device `mode` persists across reports. No sysfs, files, or power-supply state is created. Descriptor edits persist only for the parsed in-memory HID descriptor.

Dependencies/integration: depends on HID core parse/start, report-fixup and raw-event hooks, input event reporting, `hid-ids.h` vendor/product IDs, and standard mouse button code offsets relative to `BTN_MOUSE`.

Risks: raw-event logic is size- and bit-position-sensitive (`size == 7` for R.A.T.7-style, `size == 8` for M.M.O.7). New firmware variants with different layouts will bypass or be corrupted by the mapping. The event callback assumes specific button offsets for mode buttons. PS1000 fixup is exact-pattern guarded, which is safe but leaves unknown descriptors untouched.

Test signals: PS1000 descriptor should expose working buttons and d-pad; mode cycling on each listed R.A.T./M.M.O. mouse should generate one button click per mode transition with no stuck buttons; initial mode report should not create a false click; unrelated reports should pass through unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-saitek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-samsung.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-samsung.c

Purpose: supports several Samsung special HID devices, mainly the USB Samsung IrDA remote and Samsung wireless keyboard, keyboard/mouse, gamepad, action mouse, universal keyboard, and multi-HOGP keyboard devices. It corrects malformed descriptors and remaps nonstandard consumer/keyboard/button usages to Linux input codes.

Important APIs/types/functions: descriptor handling is split into `samsung_report_fixup()` and `samsung_irda_report_fixup()`. Input mapping helpers are `samsung_kbd_mouse_input_mapping`, `samsung_kbd_input_mapping`, `samsung_gamepad_input_mapping`, `samsung_actionmouse_input_mapping`, and `samsung_universal_kbd_input_mapping`; `samsung_input_mapping()` dispatches by product ID. `samsung_probe()` handles parse/start and special IrDA connection masks.

Control flow: report fixup only applies to the USB IrDA remote. Four descriptor variants are recognized by size and byte pattern: 184-byte vendor report reinterpretation, 203-byte report logical range fix, 135-byte logical range fix, and 171-byte logical range fix. Input mapping checks usage pages and product IDs, then maps selected consumer usages to media/browser/system keys, keyboard usages to corrected layout keys with repeat enabled, gamepad buttons to `BTN_*`, and vendor-ish Samsung hotkeys to `BTN_TRIGGER_HAPPY*` or explicit key codes. Probe parses the descriptor; for the 184-byte IrDA variant it disables hidinput and forces hiddev because userspace must reconstruct the vendor report.

State and persistence: no private per-device state is allocated. State consists of in-memory descriptor mutations and input mapping decisions made during HID input setup. The only persistent behavioral switch is `cmask` in probe for the IrDA 184-byte variant.

Dependencies/integration: depends on HID core, USB interface inspection for keyboard/mouse interface number, Linux input key namespaces, hiddev force connection for old IrDA userspace, and product IDs in `hid-ids.h`.

Risks: mappings encode device-specific usage values and may conflict if Samsung reuses product IDs with different descriptors. Some mappings use raw numeric key codes where no named key exists, increasing ABI-readability risk. IrDA fixups are byte-offset-specific; bad guards could corrupt descriptors, while overly narrow guards leave devices broken. The USB keyboard/mouse mapping reads the USB interface, so it is intentionally USB-only.

Test signals: descriptor dump for each IrDA size should show adjusted logical ranges or vendor report shape; wireless keyboard media/browser/hotkeys should produce expected Linux keys; gamepad buttons and consumer Back/Home/Menu should map correctly; action mouse usage `0x301` should map; Bluetooth universal and multi-HOGP keyboard brightness, Dex, screen capture, and hotkey usages should be visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-semitek.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-semitek.c

Purpose: provides a narrow descriptor quirk for Semitek keyboards whose interface 2 incorrectly describes report ID `0x04` as an array of keycodes rather than a bitmask.

Important APIs/types/functions: the only behavioral callback is `semitek_report_fixup()`, registered in `semitek_driver`. The device table matches `USB_VENDOR_ID_SEMITEK` and `USB_DEVICE_ID_SEMITEK_KEYBOARD`.

Control flow: HID core calls report fixup before parsing. If the descriptor is exactly `0xcb` bytes and bytes `0x83/0x84` match the expected `Input` item with value `0x00`, the driver changes byte `0x84` to `0x02`, turning the field into Data/Variable/Absolute semantics. Otherwise it returns the descriptor unchanged. There is no custom probe; default HID driver flow handles parsing and input setup.

State and persistence: there is no driver-private state. The only state is the in-memory descriptor byte patch used for this device instance.

Dependencies/integration: depends on HID report descriptor parsing and the Semitek vendor/product IDs in `hid-ids.h`.

Risks: byte-offset fixups are fragile if firmware changes the descriptor length or layout. The guard is tight, so unknown variants fail safe by not patching but may remain unusable. Because no probe validation exists, regressions show up during HID parse/input behavior rather than driver-specific errors.

Test signals: affected keyboard should no longer emit broken key arrays for report `0x04`; `hid-recorder` or evtest should show independent key bits; descriptor parse should succeed without adding unrelated mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-semitek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-custom.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-custom.c

Purpose: implements the platform driver for generic/custom HID sensors exposed by `hid-sensor-hub`. For unknown custom sensors it creates sysfs attributes for feature/input fields plus a misc character device that streams raw samples. For known custom sensors it remaps the HID sensor hub child into a more specific platform device name based on sensor properties and optional DMI constraints.

Important APIs/types/functions: `struct hid_sensor_custom` owns locks, callbacks, field metadata, enable state, power/report-state fields, FIFO, waitqueue, miscdevice, and optional remapped platform device. `struct hid_sensor_custom_field` stores one HID field's attribute info and generated sysfs group. Key functions include `enable_sensor_store`, `set_power_report_state`, `show_value`, `store_value`, `hid_sensor_capture_sample`, `hid_sensor_send_event`, `hid_sensor_custom_add_attributes`, `hid_sensor_custom_dev_if_add`, known-sensor match helpers, and `hid_sensor_custom_probe/remove`.

Control flow: probe allocates `sensor_inst`, installs sensor-hub callbacks, and first tries to identify a known custom sensor by reading serial/model/manufacturer feature properties. If matched, it registers a replacement platform device named like `HID-SENSOR-<tag>-<usage>` and returns. Otherwise it registers callbacks for the hub usage, creates `enable_sensor`, scans input and feature reports belonging to this collection, creates one sysfs group per field, then registers a misc device. Enabling opens the hub device and writes power/reporting feature enums when those fields exist; disabling writes off/no-events and closes the hub. Input callbacks append a packed `hid_sensor_sample` header followed by raw report bytes into a kfifo and wake readers at report completion.

State and persistence: `enable` persists the current sensor power/reporting state. `fields` persists discovered field metadata and generated sysfs attributes until remove. `data_fifo` persists unread raw samples only while the misc device exists. `misc_opened` enforces a single reader. Known-sensor matching uses property strings from the device, not saved host state.

Dependencies/integration: depends on exported `hid-sensor-hub` helpers (`sensor_hub_register_callback`, `sensor_hub_get_feature`, `sensor_hub_set_feature`, `sensor_hub_device_open/close`, `sensor_hub_input_get_attribute_info`, `sensor_hub_input_attr_get_raw_value`), platform bus matching for `HID-SENSOR-2000e1/2000e2`, sysfs, miscdevice, kfifo, DMI, and HID sensor usage IDs.

Risks: sysfs attribute names encode report index and usage and are parsed back with `sscanf`; changes to naming break show/store. `hid_sensor_custom_add_field()` frees `sensor_inst->fields` on `krealloc` failure, which leaves the pointer stale for later cleanup if callers are not careful. FIFO overflow skips the rest of the current sample; readers must tolerate dropped samples. Feature value decoding casts unaligned byte arrays to `u16/u32/u64`, which may be architecture-sensitive. Enable/disable does not flush the FIFO. Known-sensor promotion bypasses generic sysfs/misc registration, so matching must be precise.

Test signals: generic custom sensors should expose `enable_sensor`, feature/input field groups with `name/units/unit-expo/minimum/maximum/size/value`; feature `value` writes should call SET_REPORT; misc read should block/poll and return header plus full sample data; FIFO pressure should drop cleanly; known Intel/Lenovo sensors should register the expected specific platform device only when properties and DMI match; remove while a reader waits should wake and deregister without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-custom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-hub.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-hub.c

Purpose: implements the HID Sensor Hub driver. It parses a sensor-hub HID device, creates one MFD child per physical/application sensor collection, dispatches input reports to registered child callbacks, and exports helper APIs for child sensor drivers to query/set HID feature and input attributes.

Important APIs/types/functions: `struct sensor_hub_data` holds the synchronous request mutex, pending lock, callback list, MFD cell array, child count, and open refcount. Exported helpers include `sensor_hub_register_callback`, `sensor_hub_remove_callback`, `sensor_hub_set_feature`, `sensor_hub_get_feature`, `sensor_hub_input_attr_get_raw_value`, `hid_sensor_get_usage_index`, `sensor_hub_input_get_attribute_info`, `sensor_hub_device_open`, and `sensor_hub_device_close`. Driver callbacks are `sensor_hub_probe`, `sensor_hub_remove`, `sensor_hub_raw_event`, `sensor_hub_suspend`, `sensor_hub_resume`, and `sensor_hub_report_fixup`.

Control flow: probe allocates hub state, parses HID, starts hardware with `HID_CONNECT_DRIVER`, counts physical/application collections, allocates MFD cells, and for each relevant collection allocates a `hid_sensor_hub_device` with collection boundaries and usage-based name `HID-SENSOR-<usage>`. MFD children then bind to sensor-specific platform drivers. Child drivers register callbacks for a usage or collection. Raw input reports skip the report ID, iterate HID fields, locate the callback matching physical/application usage and collection range, satisfy pending synchronous reads, invoke `capture_sample` per field, and call `send_event` after the report. Feature helpers serialize GET/SET_REPORT operations on `data->mutex`.

State and persistence: hub state persists for the HID device lifetime. Child `hid_sensor_hub_device` instances persist as platform data for MFD children. `ref_cnt` tracks shared `hid_hw_open/close` across children. Each child has a pending synchronous read state protected by its own mutex pointer and the hub pending spinlock. Callback registrations persist until child remove.

Dependencies/integration: integrates HID group `HID_GROUP_SENSOR_HUB`, MFD hotplug devices, platform sensor child drivers, HID feature/input report APIs, PM callbacks, and a Lenovo/TI Yoga descriptor fixup for invalid magnetic flux logical minima.

Risks: `sensor_hub_get_callback()` is called while `sensor_hub_raw_event()` already holds `pdata->lock`, then it takes the callback-list lock; callback register/remove use only the callback-list lock, so ordering must remain simple to avoid deadlocks. Raw-event pointer advancement assumes field sizes match the wire report layout. Synchronous read waits up to five seconds but does not return timeout as a distinct error; a missing report can look like zero. `sensor_hub_device_close()` blindly decrements `ref_cnt`, so open/close pairing is mandatory. Remove completes pending reads after stopping hardware and before removing MFD devices.

Test signals: hub should create one MFD child per collection with correct collection boundaries; feature get/set should work for scalar and multi-count fields; synchronous input raw reads should complete on matching report fields; callback unregister should stop delivery; suspend/resume should call child callbacks; remove during pending sync read should complete without hang; Lenovo Yoga descriptor should expose corrected magnetometer ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sensor-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sigmamicro.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sigmamicro.c

Purpose: fixes a SiGma Micro keyboard descriptor whose report ID 4 describes keyboard bits incorrectly. The driver recognizes a complete known descriptor and changes one input item to variable semantics.

Important APIs/types/functions: `sm_0059_rdesc` is the expected descriptor template. `sm_report_fixup()` compares the live descriptor against the template and patches byte 99. `sm_driver` registers only the report-fixup callback for `USB_DEVICE_ID_SIGMA_MICRO_KEYBOARD2`.

Control flow: HID core invokes `sm_report_fixup()` before parsing. If size and full descriptor contents match `sm_0059_rdesc`, the driver logs a fixup and sets `rdesc[99] = 0x02`, changing the modifier report input from array to variable. If not, it returns the descriptor untouched. No custom probe, input mapping, or runtime callbacks exist.

State and persistence: no per-device allocation or persistent state. The descriptor patch is in-memory and per device instance.

Dependencies/integration: depends on HID descriptor parsing and `hid-ids.h` SiGma Micro IDs. The complete descriptor table doubles as both documentation and a strict guard.

Risks: full-descriptor matching avoids false positives but may miss devices with harmless descriptor differences. The byte index is meaningful only for the exact template. There is no runtime validation beyond whether HID input behaves correctly after parsing.

Test signals: affected keyboards should emit independent key bit events for report ID 4; descriptor mismatch variants should still bind without modification; no extra input devices or sysfs artifacts should appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sigmamicro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sjoy.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sjoy.c

Purpose: supports SmartJoy PLUS and related PS2-to-USB adapters, including optional force-feedback rumble support when `CONFIG_SMARTJOYPLUS_FF` is enabled, plus device-specific HID quirks for multi-input and broken output reports.

Important APIs/types/functions: `struct sjoyff_device` stores the output report used for rumble. `hid_sjoyff_play()` maps Linux rumble magnitudes to the adapter's output fields. `sjoyff_init()` locates output reports per input device and creates memless force feedback. `sjoy_probe()` applies table quirks, parses HID, starts hardware without generic FF, and calls `sjoyff_init()`.

Control flow: probe ORs `id->driver_data` into `hdev->quirks`, parses the device, starts HID with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF`, then initializes driver-specific FF. FF setup walks each HID input and the output report list in tandem, validates at least one field and three values, allocates `sjoyff_device`, seeds output bytes, sends an initial SET_REPORT, sets `FF_RUMBLE`, and registers `input_ff_create_memless()`. A rumble effect scales strong magnitude to 0..255 and converts weak magnitude to an on/off bit, writes fields 1 and 2, and sends SET_REPORT.

State and persistence: when FF is enabled, each input device owns a small heap `sjoyff_device` as memless FF data and references a HID output report. The adapter output state persists in device firmware until overwritten. Without `CONFIG_SMARTJOYPLUS_FF`, no extra state is created.

Dependencies/integration: depends on HID core, Linux input FF, output-report lists, and vendor/product IDs for WiseGroup and Play.com adapters. Uses HID quirk flags `HID_QUIRK_NOGET`, `HID_QUIRK_MULTI_INPUT`, and `HID_QUIRK_SKIP_OUTPUT_REPORTS`.

Risks: FF initialization assumes output reports correspond to input devices by list order; devices with unexpected report ordering fail or rumble the wrong port. Allocated `sjoyff_device` lifetime is tied to input FF cleanup, so failures after allocation must free correctly. Probe ignores `sjoyff_init()` return value, so lack of FF does not prevent basic input. Devices marked skip-output-reports may not expose FF.

Test signals: all listed adapters should create correct numbers of input devices; quirked devices should avoid broken GET/output behavior; with FF enabled, rumble should change strong/weak motors as expected and stop on zero effect; missing output report should log but keep joystick input working.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sjoy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sony.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sony.c

Purpose: large Sony/PlayStation and rhythm-instrument HID driver. It supports PS3 Sixaxis, Navigation, Motion, Buzz, PS3 remotes, Sony RF mice, NSG remotes, third-party PS3-compatible pads, Guitar Hero/Rock Band/DJ Hero instruments, and newer PS4/PS5 Rock Band guitars. It provides descriptor replacements, input mappings, battery reporting, LEDs, force feedback, sensor/touchpad devices, duplicate-controller filtering, and special USB keepalive pokes.

Important APIs/types/functions: `struct sony_sc` is the per-device state: locks, HID/input devices, LED classdevs, quirks, state worker, battery, device ID, output buffer, FF state, MAC address, deferred init, GHL URB/timer, and RB3 poke timing. Major callbacks are `sony_probe`, `sony_input_configured`, `sony_mapping`, `sony_report_fixup`, `sony_raw_event`, `sony_remove`, `sony_suspend`, and `sony_resume`. Important helpers include `sixaxis_set_operational_usb/bt`, `sony_leds_init`, `sixaxis_send_output_report`, `motion_send_output_report`, `sony_battery_probe`, `sony_check_add`, `sony_register_sensors`, `sony_register_touchpad`, `ghl_init_urb`, and instrument mapping functions.

Control flow: probe derives quirks from the HID ID and sometimes `hdev->name`, allocates `sony_sc`, parses HID, adjusts connect mask/version for HIDDEV and SDL compatibility, and starts hardware. HID input setup later calls `sony_input_configured()`, which allocates a device ID, performs duplicate MAC detection for Sixaxis/Navigation USB-vs-Bluetooth pairs, allocates output buffers, sets operational mode, registers sensors/touchpad if needed, initializes LED class devices, registers battery power supply, opens HID for battery reports, and initializes FF. Raw-event handling decodes battery/sensor data for Sixaxis/Motion/Navigation, filters bogus BT reports, parses NSG touchpad packets, updates RB4 guitar whammy/tilt and PS5 battery, and periodically pokes RB3 Pro instruments into full-report mode. GHL dongles allocate a USB control URB and timer that resubmits magic data every eight seconds.

State and persistence: persistent runtime state includes controller MAC and global duplicate list, allocated Sixaxis device IDs via IDA, LED brightness/blink arrays, deferred-initialization flag, battery capacity/status, FF magnitudes, output report buffer, sensor/touchpad input devices, GHL timer/URB, and RB3 poke timestamp. Most allocations are devm-managed except URB/timer and ID/list entries that remove explicitly cleans. Battery/LED state is host-side state mirrored to hardware by output reports.

Dependencies/integration: integrates HID core report fixup/mapping/raw-event/input-configured hooks, Linux input/MT/FF, LED class, power_supply, USB control URBs, timers, IDA, spinlocks, workqueues, and `hid-ids.h`. It also coordinates with Bluetooth HIDP `uniq` formatting for MAC discovery and SDL userspace expectations via version bit patching.

Risks: this driver has high regression surface because quirks combine across many devices. Duplicate filtering can reject valid devices if MAC extraction or connection-type logic is wrong. Deferred initialization for USB Sixaxis depends on the first input report. Work/timer/URB cancellation ordering is critical on remove. Raw report handlers use fixed offsets and sizes for several protocols. LED/FF output report paths differ for SHANWAN, Motion, and normal Sixaxis. Battery reporting is updated from raw events and protected by spinlocks but exposed through power_supply callbacks.

Test signals: Sixaxis USB/BT should become operational, avoid duplicate USB+BT exposure, expose sensors, battery, LEDs, and FF; bogus BT all-zero report should not create false input; Navigation should map only present controls; Motion should use replacement descriptor and RGB/rumble output; Buzz LEDs and button mappings should work; PS3 remote replacement descriptor should expose remote keys and battery; NSG remote should create touchpad MT/relative events; GHL dongles should keep reporting after periodic magic pokes; RB3 Pro instruments should switch to full reports; RB4 PS4/PS5 guitars should expose whammy/tilt and PS5 battery; suspend should stop rumble and resume should reinitialize USB controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-speedlink.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-speedlink.c

Purpose: fixes Speedlink Vicious and Divine Cezanne USB mouse behavior by ignoring bogus LED usages on the keyboard endpoint and filtering invalid relative X/Y motion events that cause a jumpy cursor.

Important APIs/types/functions: `speedlink_input_mapping()` rejects HID LED page usages. `speedlink_event()` filters selected relative motion events. `speedlink_grabbed_usages` limits `.event` interception to `HID_GD_X` and `HID_GD_Y`. `speedlink_driver` binds the X-Tensions Speedlink VAD Cezanne device.

Control flow: during input mapping, any usage from `HID_UP_LED` returns `-1`, preventing nonexistent keyboard LEDs from being exposed. Runtime event handling receives only grabbed X/Y relative events; it drops events where `abs(value) >= 256` and also drops zero-distance events, returning `1` to stop normal processing. Other values pass through.

State and persistence: no private state. Behavior is purely descriptor/input mapping and runtime event filtering.

Dependencies/integration: depends on HID usage tables, Linux relative input processing, and `hid-ids.h` device IDs.

Risks: the motion filter is intentionally heuristic. If a future valid high-resolution device reuses the same ID and sends deltas >= 256, the driver would suppress legitimate motion. Dropping zero relative events is normally harmless but can hide protocol diagnostics. The usage table makes the event hook narrow.

Test signals: affected mouse should no longer jump on clicks or bogus reports; normal small relative movement should pass; LED devices should not appear for the keyboard endpoint; logs should not show parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-speedlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-steam.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-steam.c

Purpose: supports Valve Steam Controller wired/wireless interfaces and Steam Deck HID input. It creates native Linux input devices, manages the controller's mouse/keyboard emulation "lizard mode", exposes wireless battery state, forwards hidraw access through a layered virtual HID client, and parses Steam Deck gamepad plus motion-sensor reports.

Important APIs/types/functions: `struct steam_device` owns HID pointers, lock, feature-report mutex, RCU-protected input/sensors/power_supply pointers, connection state, serial, battery, mode-switch state, rumble work, and unregister/connect work. Key functions include `steam_probe/remove`, `steam_register/unregister`, `steam_raw_event`, `steam_input_register`, `steam_sensors_register`, `steam_set_lizard_mode`, `steam_create_client_hid`, `steam_client_ll_*`, `steam_do_input_event`, `steam_do_deck_input_event`, `steam_do_deck_sensors_event`, and battery/haptic helpers.

Control flow: probe parses HID. Virtual client devices tagged `HID_GROUP_STEAM` start only hidraw. Non-Valve emulation interfaces start normally. Real Valve interfaces allocate `steam_device`, start without hidraw, open hardware, register immediately for wired/Deck or request connection status for wireless receivers, then create a virtual hidraw client whose low-level driver forwards raw requests to the real HID device. When hidraw client opens, work unregisters native input/sensors to avoid duplicate input; when it closes, work recreates native devices and restores lizard mode. Raw 64-byte reports are decoded by type: controller input, Deck input/sensors, wireless connect/disconnect, or battery status.

State and persistence: connection and client-open counts are protected by a spinlock. Feature report traffic is serialized by `report_mutex`. Input, sensor, and battery objects are RCU pointers so raw-event paths can safely read while unregister work replaces them. The global `steam_devices` list supports the writable `lizard_mode` module parameter, applying changes to all connected devices without open hidraw clients. Wireless battery voltage/capacity and Deck mode-switch state persist in `steam_device`.

Dependencies/integration: depends on HID core and low-level virtual HID devices, Linux input and FF, power_supply, workqueues, RCU, module parameters, little-endian helpers, and Valve IDs. User-space integration is deliberate: Steam Client can keep hidraw behavior while the kernel driver suppresses duplicate evdev input.

Risks: layered hidraw recursion is subtle; `HID_GROUP_STEAM` must prevent re-entering the real probe path. Workqueue ordering around remove, hidraw open/close, and wireless connect/disconnect is high risk. Raw report parsing uses fixed offsets and assumes size 64 plus header bytes `1,0`. RCU object lifetime must remain correct around `steam_input_unregister`, `steam_sensors_unregister`, and battery unregister. Lizard-mode writes send feature reports and can race with client open state if locking changes. The Deck mode-switch delay and `client_opened` checks affect user-visible input availability.

Test signals: wired controller should expose a native gamepad and virtual hidraw; Steam Client hidraw open should remove native input and close should restore it; lizard mode should toggle on input open/close and module-param writes; wireless receiver should create/remove devices on connect events and update battery; Deck should expose gamepad plus motion sensors, mode-switch by Start hold should toggle behavior with haptic pulses; FF rumble on Deck should send rumble reports; remove during pending work should not leave input, sensors, battery, or client HID behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-steam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-steelseries.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-steelseries.c

Purpose: supports SteelSeries SRW-S1 wheel and Arctis 1/9 wireless headsets. SRW-S1 gets a replacement descriptor and LED class devices for RPM LEDs; Arctis headsets get power_supply battery reporting, wireless status updates, and periodic battery queries.

Important APIs/types/functions: `struct steelseries_device` tracks headset HID device, quirks, delayed battery work, removal flag, power_supply descriptor, capacity, connection, and charging state. `struct steelseries_srws1_data` tracks SRW-S1 LED state and LED classdevs. Key callbacks include `steelseries_probe`, `steelseries_remove`, `steelseries_srws1_report_fixup`, and `steelseries_headset_raw_event`. Helpers cover SRW-S1 LED output reports and Arctis battery request/parsing.

Control flow: SRW-S1 report fixup replaces the descriptor when a known byte pattern is seen, exposing hidden dials under Generic Desktop usages. SRW-S1 probe validates output report values, starts HID, initializes all LEDs off, then registers one "all" LED and 15 individual RPM LEDs; brightness writes update a bitmask and send an output report. Headset probe parses HID, validates Arctis 9 vendor usage page, starts and opens hardware, registers a battery power_supply, sends an initial query, and schedules retries for Arctis 9. Raw events parse Arctis 1/9 formats, update connection/capacity/charging, call `power_supply_changed()`, set USB wireless status, and schedule the next query unless removed.

State and persistence: SRW-S1 LED bitmask persists in driver data and hardware until changed. Headset state persists capacity, connection, charging, delayed-work status, and a `removed` flag protected by spinlock. Power_supply names are allocated per headset instance.

Dependencies/integration: depends on HID raw requests, HID output reports, LED class, power_supply, USB wireless status, delayed work, and SteelSeries IDs. Arctis support assumes USB transport for wireless-status integration.

Risks: SRW-S1 LED report assumes the first output report has at least 16 values; probe validates this before use. LED state updates are not separately locked, so concurrent sysfs LED writes could interleave. Headset raw parsing is model-specific; malformed events can keep scheduling battery requests. `hid_hw_open()` failure after `hid_hw_start()` returns without stopping hardware in probe, which is a cleanup-risk pattern. Battery capacity mapping for Arctis 9 is empirical.

Test signals: SRW-S1 descriptor should show dials as RX/RZ-style desktop axes and all 16 LED class devices should control hardware; Arctis 1 should report connected status and raw capacity from matching response; Arctis 9 should map raw capacity and charging status; unplug/remove should cancel delayed work and stop rescheduling; power_supply properties should update on raw events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-steelseries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sunplus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-sunplus.c

Purpose: handles Sunplus Wireless Desktop quirks by correcting a bad descriptor logical maximum and remapping two nonstandard consumer usages to zoom keys.

Important APIs/types/functions: `sp_report_fixup()` patches descriptor bytes when the expected pattern is present. `sp_input_mapping()` maps consumer usages `0x2003` and `0x2103` with `hid_map_usage_clear()`. `sp_driver` registers report-fixup and input-mapping callbacks for `USB_DEVICE_ID_SUNPLUS_WDESKTOP`.

Control flow: descriptor fixup checks size at least 112 and a specific long-item pattern at offsets 104-106, then changes both related maximum bytes so usages decode as `0x2103` rather than the broken `0x0380` style value. During input mapping, only Consumer page usages are considered; zoom-in and zoom-out usages become `KEY_ZOOMIN` and `KEY_ZOOMOUT`.

State and persistence: no private state. Effects are in-memory descriptor edits and input mapping decisions.

Dependencies/integration: depends on HID parser, Linux input consumer-key mapping, and Sunplus IDs.

Risks: byte-offset descriptor patch can miss firmware variants or patch an unintended descriptor if the guard is too broad; current guard includes size and exact bytes. Only two consumer usages are custom mapped, so other vendor hotkeys still depend on generic HID behavior.

Test signals: descriptor should parse the Sunplus zoom usages correctly; zoom controls should emit `KEY_ZOOMIN/KEY_ZOOMOUT`; unrelated consumer keys should remain generic; devices with different descriptors should not be patched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-sunplus.c -->
