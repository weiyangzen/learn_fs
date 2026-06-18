# Research: subset-b-003798

Grouped research for HID core and selected HID device drivers under `sources/distributed-fs/ceph-client/drivers/hid/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-kbd.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-kbd.c

Purpose: implements the Apple Touch Bar keyboard mode driver for T2 MacBook Pro iBridge display devices. It turns the Touch Bar HID output report into kernel-managed modes (`ESC`, function keys, media/special keys, off), translates Touch Bar key usages into normal Linux input key events, handles Fn toggling, and optionally dims/offlines the Touch Bar backlight after inactivity.

Important APIs/types/functions: `struct appletb_kbd` stores the HID mode field, input handler/handles, backlight device, delayed/workqueue state, and saved/current modes. `appletb_kbd_set_mode()` writes the HID output field via `hid_set_field()` and `hid_hw_request()`. `mode_show()`/`mode_store()` expose sysfs control through `DEVICE_ATTR_RW(mode)`. `appletb_kbd_hid_event()` filters Touch Bar key usages and injects special-key translations through `sparse_keymap`. The input-handler callbacks (`appletb_kbd_inp_event`, connect, disconnect, match) watch the internal Apple keyboard and trackpad for activity and Fn presses. Probe/remove/suspend/resume are registered through `struct hid_driver`.

Control flow: probe parses the HID descriptor, locates the vendor mode output field with `hid_find_field()`, starts/open the HID device, obtains `appletb_backlight`, registers an input handler that matches internal Apple USB keyboard/trackpad devices, sets the default mode, and finally installs driver data. HID events first check keyboard-page EV_KEY usages, ignore non-Touch-Bar keys, reset the inactivity timer, and either synthesize translated special keys in special mode or swallow events when off. Fn input events temporarily toggle between special and function modes until key release. Suspend saves current mode and turns the Touch Bar off; resume restores the saved mode.

State/persistence: state is per-HID-device and not persisted across driver unload. Module parameters control default mode, Fn toggle behavior, autodim, dim timeout, and idle timeout. Runtime state includes current/saved mode plus backlight dim/off booleans. Delayed work dims to brightness 1, then to 0; restore work returns brightness to 2 after activity.

Dependencies/integration: integrates HID core, USB device matching, Linux input, sparse-keymap, sysfs device groups, the backlight class, workqueues, and the separate `hid_appletb_bl` backlight driver via soft dependency.

Risks: mode setting powers the device up and down around report writes, so failures or resume races can leave `current_mode` stale. Input handle lifetime depends on careful register/open/unregister/put ordering. The internal-device match searches USB parent names and product strings, which is pragmatic but fragile. Work items must be canceled before the backlight reference is dropped.

Test signals: verify sysfs mode read/write and invalid mode rejection, Touch Bar F-key/media translation, off-mode event suppression, Fn hold toggling and release restore, activity-based dim/off/restore, suspend/resume restoration, driver remove turning off the Touch Bar, and behavior when `appletb_backlight` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-asus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-asus.c

Purpose: provides ASUS-specific HID support for notebook keyboards, keyboard docks, I2C/USB touchpads, ROG keyboards, ROG Ally controls, Medion-branded ASUS hardware, keyboard backlight integration, Fn-lock synchronization, battery reporting, and multiple broken descriptor/input quirks.

Important APIs/types/functions: `struct asus_drvdata` carries quirks, HID/input devices, touchpad geometry, keyboard backlight listener, power-supply state, and Fn-lock work. `struct asus_touchpad_info` describes contact format and coordinate limits. Touchpad decoding is handled by `asus_report_input()`, `asus_report_contact_down()`, and `asus_report_tool_width()`. Raw-event filtering and device-specific packets are handled by `asus_raw_event()` and `asus_e1239t_event()`. Keyboard feature report helpers include `asus_kbd_set_report()`, `asus_kbd_init()`, `asus_kbd_get_functions()`, `asus_kbd_disable_oobe()`, `asus_kbd_set_fn_lock()`, and MCU version validation helpers. Battery support is exposed through `asus_battery_probe()` and `asus_battery_get_property()`. `asus_input_mapping()`, `asus_input_configured()`, `asus_report_fixup()`, `asus_probe()`, and `asus_remove()` form the main HID driver contract.

Control flow: probe allocates `asus_drvdata`, applies ID-table quirks, refines quirks from product name, USB interface number, DMI product, and platform type, optionally registers battery support, parses the report descriptor, detects ASUS vendor applications, starts HID hardware, performs feature-report handshakes for available report IDs, registers keyboard backlight support if advertised, renames input devices, and starts multitouch when needed. Input mapping handles ASUS vendor usages, Microsoft vendor usages, consumer-page suppression, and Medion mute/touchpad toggle workarounds. Raw events consume battery reports, hand-decode custom multitouch packets, synthesize Medion key releases, filter ROG spurious reports, route fan-control to `asus-wmi`, and block a Claymore II sleep packet.

State/persistence: all runtime state is per device. Battery values are cached and rate-limited with `battery_next_query`. Keyboard backlight brightness is stored under a spinlock and pushed asynchronously. Fn-lock state is toggled on `KEY_FN_ESC` and synced by workqueue. Touchpad slot state is owned by input-mt. No settings are persisted beyond firmware/device state.

Dependencies/integration: depends on HID core, input-mt, USB interface inspection, DMI, ACPI/platform ASUS WMI interfaces, `asus_hid` listener APIs, power_supply, LED/backlight related interfaces, and `hid-ids.h` device IDs.

Risks: this file has a large quirk surface; descriptor offsets, report IDs, and DMI/interface assumptions are device-specific and easy to regress. Raw-event handlers must return the right convention (`-1` to stop processing for filtered reports, `1` for consumed manual reports, `0` to continue). Async LED/Fn work must be canceled before teardown. Battery and feature report requests depend on exact report sizes. The post-`hid_hw_start()` input pointer checks avoid a known UAF class when no input device is claimed.

Test signals: cover each quirk class with descriptor fixups, ASUS vendor hotkey mapping, ROG spurious packet filtering, fan WMI forwarding fallback, keyboard backlight listener registration and resume restore, Fn-lock toggling, T100/T100CHI/T90CHI/Medion multitouch decoding, battery property polling and autonomous updates, MCU version warning path, and removal with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-asus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-aureal.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-aureal.c

Purpose: supplies a minimal HID report-descriptor fixup for the Aureal Cy se W-01RN USB_V3.1 device so the generic HID stack can parse and expose the device correctly.

Important APIs/types/functions: `aureal_report_fixup()` is the only driver callback. It checks the descriptor size and bytes at offsets 52 and 53, logs a fixup message, and changes a logical maximum byte from `0x01` to `0x65`. `aureal_devices[]` matches `USB_VENDOR_ID_AUREAL` and `USB_DEVICE_ID_AUREAL_W01RN`. The `aureal_driver` registers only `.id_table` and `.report_fixup`.

Control flow: when HID core binds this driver, `hid_open_report()` invokes the fixup on a mutable descriptor copy before parsing. The driver does not implement probe/remove, input mapping, or raw events; all normal parsing, input registration, and device operation remain generic after descriptor correction.

State/persistence: no private runtime state is allocated and no setting persists. The only state change is in-memory descriptor mutation for the current device parse.

Dependencies/integration: integrates with HID core report fixup infrastructure and `hid-ids.h`. The corrected descriptor is consumed by the generic HID parser and input layer.

Risks: the fixup is byte-offset based; if a related device has a different descriptor but the same ID, the guard must prevent incorrect mutation. If the descriptor changes and the guard no longer matches, the device falls back to the broken original descriptor.

Test signals: attach the W-01RN device or feed its descriptor through HID parsing, confirm the fixup log appears for the known descriptor, confirm parsing succeeds, and confirm nonmatching descriptor sizes/bytes are left untouched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-aureal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-axff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-axff.c

Purpose: adds force-feedback rumble support for ACRUX game controllers while leaving normal input handling to HID/input.

Important APIs/types/functions: `struct axff_device` stores the output report used for rumble. Under `CONFIG_HID_ACRUX_FF`, `axff_init()` locates the first HID input and first output report, zeroes all output fields, validates field count for most devices, sets `FF_RUMBLE`, and registers a memless force-feedback callback with `input_ff_create_memless()`. `axff_play()` scales strong/weak magnitudes from 16-bit input FF values to 8-bit report values and alternates left/right values across report fields. `ax_probe()` parses and starts the device with generic FF disabled, initializes custom FF, and opens the HID device to keep polling active. `ax_remove()` closes and stops hardware.

Control flow: probe calls `hid_parse()`, `hid_hw_start(HID_CONNECT_DEFAULT & ~HID_CONNECT_FF)`, attempts `axff_init()`, warns rather than failing if FF setup fails, then calls `hid_hw_open()` because the controller otherwise stops producing reports. The input FF core later calls `axff_play()` for rumble effects, which updates the cached output report and submits `HID_REQ_SET_REPORT`.

State/persistence: per-device FF state is a small heap allocation attached as the memless FF private data. Rumble state lives in HID report field values and on the device after each set-report. No persistent settings are stored by the driver.

Dependencies/integration: depends on HID core report parsing/request APIs, Linux input FF memless support, `CONFIG_HID_ACRUX_FF`, and ACRUX USB IDs.

Risks: `axff_init()` assumes the first output report layout corresponds to rumble channels. The memless private allocation is not explicitly freed in this driver and relies on input FF/device teardown. Always opening the HID device increases lifecycle sensitivity: remove must close if open succeeded. FF setup failure is nonfatal, so tests must inspect warnings as well as probe return.

Test signals: verify controller input still works without FF, rumble produces expected left/right strength, product `0xf705` tolerates fewer than four fields, probe failure after `hid_hw_open()` closes/stops hardware, and builds with `CONFIG_HID_ACRUX_FF=n` still bind without FF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-axff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-belkin.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-belkin.c

Purpose: handles a small set of Belkin/Labtec special HID devices by forcing HIDDEV for one KVM and remapping several consumer usages on a wireless keyboard.

Important APIs/types/functions: quirk bits `BELKIN_HIDDEV` and `BELKIN_WKBD` are carried in `id->driver_data` and stored with `hid_set_drvdata()`. `belkin_input_mapping()` maps consumer usages `0x03a`, `0x03b`, and `0x03c` to `KEY_SOUND`, `KEY_CAMERA`, and `KEY_DOCUMENTS` when the wireless-keyboard quirk is set. `belkin_probe()` parses the descriptor and starts HID hardware, adding `HID_CONNECT_HIDDEV_FORCE` when requested.

Control flow: the HID driver matches either the Belkin Flip KVM or Labtec wireless keyboard. Probe records the quirk mask, parses, and starts HID with default listeners plus optional forced hiddev. During input mapping, only consumer-page usages on `BELKIN_WKBD` are intercepted; other usages continue through generic mapping.

State/persistence: the only driver state is the quirk bitmask stored as driver data. No dynamic state, sysfs attributes, or persistent settings are created.

Dependencies/integration: depends on HID parser/start APIs, HID input mapping helpers, hiddev connection flags, Linux input key codes, and IDs from `hid-ids.h`.

Risks: the driver stores an integer quirk mask through a pointer-shaped `void *`; this is common in old HID drivers but depends on safe cast width for these small flags. The KVM path intentionally exposes hiddev even if normal generic handling would not. The wireless mapping is narrow and may miss related usages.

Test signals: confirm the Flip KVM creates/claims hiddev, the Labtec keyboard maps the three special keys to the expected input codes, unrelated consumer usages remain generic, and parse/start errors propagate from probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-belkin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-betopff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-betopff.c

Purpose: enables rumble force-feedback for several Betop gamepad/adaptor USB IDs whose output reports use separate bytes for left and right motors.

Important APIs/types/functions: `struct betopff_device` stores the selected output report. `hid_betopff_play()` maps 16-bit strong/weak magnitudes to bytes by dividing by 256 and writes field 2 and field 3 before `hid_hw_request(..., HID_REQ_SET_REPORT)`. `betopff_init()` finds the first input and output report, validates at least four fields with values, zeroes all report values, enables `FF_RUMBLE`, and registers a memless FF callback. `betop_probe()` optionally sets `HID_QUIRK_MULTI_INPUT` from `driver_data`, parses, starts HID with generic FF disabled, and calls `betopff_init()`.

Control flow: normal input devices are connected by `hid_hw_start(HID_CONNECT_DEFAULT & ~HID_CONNECT_FF)`. Custom FF setup occurs afterward and is intentionally not checked by probe; if FF initialization fails, the device still remains usable as an input device. Rumble calls only update the cached output report and issue a set-report.

State/persistence: the driver allocates one `betopff_device` per successful FF setup. Current rumble values persist in HID report fields and the device until changed. No sysfs or persistent configuration exists.

Dependencies/integration: uses HID report lists, input FF memless support, Linux input rumble effect format, and Betop vendor/product IDs.

Risks: the report layout is assumed rather than described by symbolic usages; if a matched adapter exposes a different first output report, field indexes 2 and 3 may be wrong. Probe ignores `betopff_init()` failure, so FF regressions may be silent except for logs. As with other memless FF drivers, allocation lifetime relies on input teardown.

Test signals: test all listed IDs in both adapter and controller modes, verify normal input remains available when FF setup fails, confirm strong/weak rumble drive field 2/3 independently, and inspect dmesg for "not enough fields" or "no values" errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-betopff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-bigbenff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-bigbenff.c

Purpose: provides descriptor correction, LED class devices, and rumble force-feedback for the BigBen Interactive PS3OFMINIPAD gamepad.

Important APIs/types/functions: `pid0902_rdesc_fixed[]` replaces the original 137-byte descriptor with a gamepad-correct mapping. `struct bigben_device` stores the HID output report, LED state, rumble state, lock, removed flag, four LED class devices, and worker. `bigben_worker()` serializes LED and FF output messages into the output report using `hid_output_report()` and sends raw set-report requests. `hid_bigben_play_effect()` updates right/left motor state for `FF_RUMBLE`. `bigben_set_led()`/`bigben_get_led()` implement LED class operations. `bigben_probe()` parses, starts HID with generic FF disabled, validates the output report, registers memless FF and four LEDs, and schedules initial LED/rumble state. `bigben_remove()` marks removed, cancels work, and stops hardware.

Control flow: report fixup runs before parsing and fully substitutes the descriptor when the original size matches. Probe connects normal input, validates there is an output report with eight values, registers FF and LED devices, initializes LED1 on and rumble off, then schedules the worker. LED brightness changes and FF callbacks only set state and work flags under a spinlock; actual HID transfers happen in process-context work.

State/persistence: LED and motor values persist in `struct bigben_device` and are mirrored to the controller. The removed flag prevents new work from being scheduled during teardown. LED class registrations are devm-managed, while worker cancellation is explicit.

Dependencies/integration: depends on HID parser/output helpers, input FF memless, LED classdev, workqueues, spinlocks, and BigBen USB IDs.

Risks: output report format is hard-coded. The same buffer is reused for LED and FF messages in one worker run, so ordering and work flags matter. LED `brightness_set` can run concurrently with remove; the removed flag and cancel path are the main protection. Unexpected descriptors are allowed but warned, which may leave mappings wrong.

Test signals: verify descriptor replacement, all four LEDs via `/sys/class/leds`, initial LED1 state, rumble weak/strong behavior, no output after remove, warning on descriptor-size mismatch, and normal gamepad button/axis mappings matching Linux gamepad expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-bigbenff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cherry.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-cherry.c

Purpose: handles Cherry Cymotion special keyboards by fixing an invalid report descriptor and mapping three nonstandard consumer usages to programmable key codes.

Important APIs/types/functions: `ch_report_fixup()` checks descriptor bytes around offsets 11/12 and rewrites two usage/logical range pairs to `0x03ff`, allowing parsing of the broken Cymotion descriptor. `ch_input_mapping()` maps consumer usages `0x301`, `0x302`, and `0x303` to `KEY_PROG1`, `KEY_PROG2`, and `KEY_PROG3`. `ch_devices[]` matches the wired and solar Cymotion IDs. `ch_driver` registers report fixup and input mapping only.

Control flow: HID core calls the descriptor fixup before parsing. During HID input setup, consumer usages matching the three Cherry special keys are consumed and mapped; all other usages fall through to generic HID input mapping.

State/persistence: no private state is allocated. The descriptor mutation is per parse and the key mappings become part of the input device capabilities.

Dependencies/integration: uses HID report fixup and `hid_map_usage_clear()` integration with hid-input. It depends on Cherry IDs from `hid-ids.h` and standard input key codes.

Risks: offset-based descriptor mutation assumes the known broken descriptor layout. The key mapping only handles three usages; additional model-specific special keys may still be unmapped or generic. Because there is no probe callback, failures are surfaced by generic HID probe paths.

Test signals: parse both Cymotion device IDs, confirm the fixup log and successful input device creation, press the three special keys and observe `KEY_PROG1..3`, and verify unrelated consumer/media keys still work through generic mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cherry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-chicony.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-chicony.c

Purpose: supports Chicony special keyboards/devices by mapping Microsoft-vendor usages, synthesizing wireless radio control key events, and fixing an Acer Switch 12 descriptor that exceeds `HID_MAX_USAGES`.

Important APIs/types/functions: `ch_report_wireless()` turns wireless-radio-control reports with ID `0x11` into a press/release of `KEY_RFKILL`. `ch_raw_event()` routes wireless radio control application reports to that helper. `ch_input_mapping()` maps selected `HID_UP_MSVENDOR` usages to button and hotkey codes such as `BTN_1..BTN_B`, `KEY_WLAN`, brightness, display off, camera, and `KEY_PROG1`. `ch_switch12_report_fixup()` inspects USB interface 1 and rewrites `0x7fff` usage/logical maximums to `0x2fff` for the Acer Switch 12. `ch_probe()` requires USB, sets `HID_QUIRK_INPUT_PER_APP`, parses, and starts HID.

Control flow: probe ensures the device is USB, enables per-application input splitting, parses with possible descriptor fixup, and starts normal HID listeners. Input mapping consumes Microsoft-vendor usages. Raw events for the wireless radio controls application bypass normal mapping by manually reporting `KEY_RFKILL`.

State/persistence: no driver-private heap state is allocated. The only persistent runtime effect is input capability registration and descriptor mutation for the active device.

Dependencies/integration: depends on USB interface access, HID raw-event callbacks, hid-input mapping, input event reporting, `HID_QUIRK_INPUT_PER_APP`, and Chicony/Acer IDs.

Risks: `ch_switch12_report_fixup()` assumes a USB parent and specific descriptor offsets; probe rejects non-USB to keep that safe. `ch_report_wireless()` assumes `report->field[0]->hidinput` is valid when the report shape matches. Manual RFKILL press/release injection must not duplicate generic events.

Test signals: verify per-application input devices, Microsoft-vendor hotkeys, wireless RFKILL report synthesis, Acer Switch 12 descriptor fixup on interface 1 only, rejection of non-USB matches, and absence of duplicate RFKILL events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-chicony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cmedia.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-cmedia.c

Purpose: implements two C-Media HID drivers in one module: CM6533 headphone jack detection through raw HID packets, and HS-100B report descriptor correction for audio mute controls.

Important APIs/types/functions: `struct cmhid` stores the input device, HID device, and switch map for CM6533. `cmhid_raw_event()` recognizes 16-byte jack packets by suffix and prefix and reports `SW_HEADPHONE_INSERT` through `hp_ev()`. `cmhid_input_configured()` forces the input device to expose only EV_SW headphone insertion capability. `cmhid_input_mapping()` returns `-1` to suppress generic mappings. `cmhid_probe()` sets `HID_QUIRK_HIDINPUT_FORCE`, parses, and starts HID with `HID_CONNECT_HIDDEV_FORCE`. `cmhid_hs100b_report_fixup()` replaces the 60-byte HS-100B descriptor with `hs100b_rdesc_fixed[]`, which marks microphone mute as an absolute telephony usage. `cmedia_init()` registers both HID drivers and unwinds the first if the second fails.

Control flow: CM6533 probe allocates private state, forces input creation, parses, and starts HID. When raw packets arrive, the driver checks claimed input state, exact packet length, known suffix, then known plug-in/plug-out prefixes and emits switch changes. HS-100B devices bind to a separate HID driver whose only behavior is descriptor replacement before generic parsing.

State/persistence: CM6533 keeps a heap `cmhid` until remove, with current switch state stored in the input subsystem. HS-100B keeps no private state. No persistent settings are written.

Dependencies/integration: integrates HID core, forced hidinput/hiddev connection, Linux input switch events, module-level multi-driver registration, and C-Media IDs.

Risks: raw jack detection is based on observed packet bytes and may miss firmware variants. `cmhid_input_mapping()` suppresses all generic input mapping, so CM6533 exposes only the switch. Probe uses manual allocation/free rather than devm, so error and remove paths must remain paired. HS-100B descriptor replacement is size-based only.

Test signals: verify CM6533 plug/unplug reports `SW_HEADPHONE_INSERT`, no generic bogus input usages appear, hiddev remains available, remove frees private data, HS-100B exposes correct mute/volume controls with the fixed descriptor, and module init unwinds cleanly if one driver registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cmedia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-core.c

Purpose: implements the Linux HID core bus, report descriptor parser, report field model, input/raw/hiddev dispatch path, low-level hardware wrappers, driver matching/probing/removal, dynamic IDs, sysfs attributes, and module initialization for the HID subsystem.

Important APIs/types/functions: parser/report construction includes `hid_register_report()`, `hid_register_field()`, `open_collection()`, `hid_add_usage()`, `hid_add_field()`, `fetch_item()`, `hid_parse_report()`, `hid_open_report()`, and `hid_close_report()`. Report utilities include `hid_validate_values()`, `hid_setup_resolution_multiplier()`, `hid_field_extract()`, `hid_output_report()`, `hid_alloc_report_buf()`, `hid_set_field()`, and `hid_find_field()`. Input dispatch is centered on `hid_input_report()`, `hid_safe_input_report()`, `__hid_input_report()`, `hid_report_raw_event()`, `hid_process_report()`, and `hid_process_event()`. Bus/lifecycle APIs include `hid_connect()`, `hid_disconnect()`, `hid_hw_start/stop/open/close/request/raw_request/output_report()`, `hid_add_device()`, `hid_allocate_device()`, `hid_destroy_device()`, `__hid_register_driver()`, and `hid_unregister_driver()`.

Control flow: low-level transport drivers allocate a `hid_device`, parse the physical descriptor into `dev_rdesc`, and call `hid_add_device()`. Core scans the descriptor to assign groups, registers a device on the HID bus, matches drivers by bus/group/vendor/product or dynamic ID, applies HID-BPF descriptor fixups, calls the driver probe or default probe, runs report fixups, parses collections/reports/fields, starts low-level hardware, and connects hidinput/hiddev/hidraw listeners. Incoming reports pass through the driver input lock, HID-BPF event hook, optional driver `raw_event`, hidraw/hiddev notification, field extraction/differential event processing, driver `event` callbacks, hidinput events, and final input report sync. Removal calls driver remove or default stop, releases devres, closes parsed reports, clears the driver pointer, and disconnects listeners.

State/persistence: `struct hid_device` owns descriptor copies (`dev_rdesc`, `bpf_rdesc`, `rdesc`), report enums, collections, claimed listener bits, locks, low-level open count, dynamic status bits, debug state, and bus device identity. `struct hid_report` owns fields and priority ordering; `struct hid_field` stores cached previous and new values. Driver dynamic IDs persist in `hdrv->dyn_list` until driver unregister. No on-disk persistence exists.

Dependencies/integration: integrates with the Linux device model/bus core, hidraw, hiddev, hidinput, HID debugfs, HID quirks, HID-BPF hooks, PM callbacks, waitqueues/semaphores/mutexes/spinlocks, sysfs `report_descriptor`, `country`, `modalias`, and low-level transport operations such as USB, Bluetooth, I2C, SoundWire, and sensor hubs.

Risks: descriptor parsing is security-sensitive: bounds, report sizes, collection stack growth, signedness, and max usage handling must be correct for untrusted devices. Report input paths can race with probe/remove; `driver_input_lock`, `io_started`, and open-count locking are critical. `hid_compare_device_paths()` assumes separators exist in both physical paths. Raw report size padding/truncation must respect the allocated buffer size to avoid overreads/writes. Driver callbacks can consume, block, or transform events, so return-value conventions are important.

Test signals: fuzz and regression-test report descriptors, oversized reports, numbered/unnumbered reports, malformed usages, resolution multipliers, report fixups, hidraw-only devices, hiddev-forced devices, dynamic `new_id`, driver reprobe after special driver registration/removal, HID-BPF descriptor/event/raw hooks, suspend/resume callbacks, listener connect/disconnect, safe input report short-buffer handling, and key-pressed checks during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-corsair-void.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-corsair-void.c

Purpose: supports Corsair Void wired and wireless headsets by exposing battery state, wireless connection status, microphone boom position, firmware versions, sidetone control, and alert requests through HID, USB control transfers, sysfs, and power_supply.

Important APIs/types/functions: `struct corsair_void_drvdata` stores device identity, wired/wireless type, sidetone limit, battery data, mic/connection status, firmware versions, power-supply descriptor, delayed status/firmware work, and battery work flags. `corsair_void_process_receiver()` decodes status reports. `corsair_void_battery_get_property()` exposes battery properties. Sysfs methods expose `microphone_up`, receiver/headset firmware versions, `sidetone_max`, write-only `send_alert`, and write-only `set_sidetone`. `corsair_void_request_status()` requests status/firmware refresh. Battery add/remove/update is serialized by `corsair_void_battery_work_handler()`. `corsair_void_raw_event()` decodes report IDs `0x64` and `0x66`.

Control flow: probe requires USB, allocates driver data, determines wired/wireless from ID-table `driver_data`, initializes unknown battery/wireless state, parses the HID descriptor, prepares a battery descriptor, creates the sysfs group, starts HID hardware, and schedules delayed status and firmware refreshes. Raw status reports update mic state, connection state, battery status/capacity/level, USB wireless status, and queue power_supply changes. Wireless connection transitions add or remove the battery and request firmware data. Sysfs writes send either HID output/feature reports or a USB control message depending on headset type.

State/persistence: battery, mic, connection, and firmware values are cached in driver data. Battery registration is dynamic for wireless headsets and stable for connected/wired state. Work flags in `battery_work_flags` serialize add/remove/update decisions. No persistent configuration is stored.

Dependencies/integration: depends on HID raw reports, USB interface wireless-status helpers, USB control messages, power_supply, sysfs attribute groups, delayed work/workqueues, bitfield helpers, and Corsair USB IDs.

Risks: packet layouts are reverse-engineered and comments note uncertainty. `microphone_up` and write sysfs operations reject disconnected devices, so connection state must be accurate. Battery work can race with remove and connection transitions; remove cancels work and unregisters the supply if present. The status report handler assumes sufficient packet length for indexed fields.

Test signals: verify all matched wired/wireless IDs, battery registration/removal on wireless connect/disconnect, power_supply property changes for normal/low/critical/full/charging, USB wireless status updates, mic boom sysfs value, firmware refresh values, sidetone bounds for wired versus wireless, alert send rejection on wired/disconnected devices, and remove with pending delayed/battery work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-corsair-void.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-corsair.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-corsair.c

Purpose: supports Corsair gaming keyboards and mice, especially K90 macro/backlight controls, K70/K90 special-key mapping, and descriptor fixups for GLAIVE RGB and Scimitar Pro RGB mice.

Important APIs/types/functions: `struct corsair_drvdata` stores quirk flags plus K90 macro/backlight state. `struct k90_led` wraps LED classdev state and work. Module parameters `gkey_codes`, `recordkey_codes`, and `profilekey_codes` customize keycodes. `corsair_usage_to_gkey()` and `corsair_input_mapping()` translate G-keys, macro record, and profile usages. K90 LED/sysfs support is implemented by `k90_init_backlight()`, `k90_init_macro_functions()`, cleanup helpers, `k90_backlight_work()`, `k90_record_led_work()`, and sysfs `macro_mode`/`current_profile`. `corsair_event()` tracks macro record start/stop to update record LED state. `corsair_mouse_report_fixup()` corrects a bad logical maximum item on specific mouse interface descriptors.

Control flow: probe requires USB, allocates driver data, parses, starts HID, and on interface 0 initializes K90 macro and/or backlight facilities according to ID quirks. Input mapping consumes keyboard-page usages for G keys and special macro/profile controls, returning `-1` for unsupported special usages. LED brightness changes schedule USB vendor-control work. Sysfs reads/writes issue vendor USB control requests for macro mode and profile. Remove cleans macro and backlight resources before stopping HID.

State/persistence: driver state includes current LED brightness and K90 resource pointers. Hardware macro mode, profile, and backlight state may persist in the device firmware, but the driver itself only caches LED brightness. Keycode module parameter arrays are global runtime configuration.

Dependencies/integration: uses HID core, USB control transfers, LED classdev, sysfs attribute groups, Linux input mapping, and Corsair IDs. The mouse fixup depends on USB interface number to target the correct interface.

Risks: K90 support uses manual allocation and explicit cleanup; partial initialization must stay paired. LED work checks `removed` but no spinlock protects the flag, so teardown ordering and `cancel_work_sync()` matter. USB control message return conventions differ between reads and writes and are validated manually. Descriptor fixup is byte-offset based and comments contain historical typo context, so regression tests should focus on behavior not comments.

Test signals: verify G1-G18, macro record, and profile key mappings including module parameter overrides; K90 backlight LED class brightness get/set; record LED follows macro start/stop events; `macro_mode` and `current_profile` sysfs validation and USB errors; descriptor fixup only on interface 1 of the two mouse IDs; and cleanup after partial macro/backlight init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-corsair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cougar.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-cougar.c

Purpose: supports Cougar 500k/700k gaming keyboards whose programmable keys arrive on a separate vendor HID interface, translating those vendor reports into key events on the real keyboard input device.

Important APIs/types/functions: `cougar_mapping` maps vendor key codes to `KEY_F13..KEY_F17`, `KEY_SPACE` or `KEY_F18` for G6, and `KEY_SCREENLOCK`. Module parameter `g6_is_space` controls G6 mapping through custom param ops. `struct cougar_shared` stores shared per-physical-device state: kref, enabled flag, keyboard HID device, and input device pointer. `struct cougar` stores per-interface state and a pointer to shared state. `cougar_report_fixup()` clamps an excessive usage count to `HID_MAX_USAGES - 1`. `cougar_bind_shared_data()` links multiple HID interfaces from the same physical device using `hid_compare_device_paths()`. `cougar_raw_event()` decodes vendor reports and injects input events.

Control flow: probe parses the interface. If the top-level collection is the vendor usage, it starts HIDRAW only and opens the interface for raw events; otherwise it starts normal HID. Shared state is created or reused under a global mutex and released through devm action/kref. The keyboard interface records its registered input device and enables shared event injection. The vendor interface preinitializes the G6 mapping and opens HID. Raw events from the vendor interface are blocked from further processing and, when mapped, reported to the shared keyboard input device.

State/persistence: shared state persists until all interfaces for the physical device release their references. `enabled` prevents vendor-interface injection after keyboard removal. The G6 mapping is global and can be changed at runtime through the module parameter.

Dependencies/integration: depends on HID core, HIDRAW, input event injection, device physical path comparison, krefs, mutex-protected global list management, and Solid Year/Cougar USB IDs.

Risks: multi-interface ordering is delicate: the vendor interface may receive reports before the keyboard input pointer is available, returning `-EPERM`. `hid_compare_device_paths()` requires valid physical paths containing the separator. The raw report parser indexes fixed bytes without size checks in `cougar_raw_event()`, relying on device report shape. Shared-state list/kref logic must avoid leaks and stale input pointers.

Test signals: test both keyboard and vendor interfaces probing in either order, G1-G6 and lock key translation, `g6_is_space` runtime changes, unmapped-key warnings only on press, remove of either interface while the other remains, descriptor usage-count fixup, and no injected events after `enabled` is cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-cougar.c -->
