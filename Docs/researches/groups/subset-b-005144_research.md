# subset-b-005144 Research

Grouped source research for Lenovo, LG, MSI, MXM, NVIDIA, MeeGoPad, and Meraki x86 platform drivers. Each section preserves the original source path and is bounded for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c

## Purpose
This Lenovo WMI camera button driver converts a Lenovo camera shutter WMI event into the Linux input switch `SW_CAMERA_LENS_COVER`. It targets the event GUID `50C76F1F-D8E4-D895-0A3D-62F4EA400013` and reports whether the physical privacy shutter is open or closed.

## Important APIs, Types, And Functions
The private state is `struct lenovo_wmi_priv`, holding an `input_dev` pointer and a `notify_lock` mutex. `camera_shutter_input_setup()` allocates and registers the input device, sets `EV_SW/SW_CAMERA_LENS_COVER`, and seeds the switch state from the first WMI event. `lenovo_wmi_notify()` validates the ACPI event object, lazily creates the input device, and reports switch changes. `lenovo_wmi_probe()` allocates state and initializes the mutex; `lenovo_wmi_remove()` unregisters the input device and destroys the mutex. The module is registered as a `wmi_driver` with `min_event_size = sizeof(u8)` and `no_singleton = true`.

## Control Flow
Probe only allocates state; the input device is not registered until a valid event arrives. Notify accepts only one-byte ACPI buffers: `0` means camera closed, `1` means camera open. The driver reports Linux switch value `1` for lens covered and `0` for uncovered, so it inverts the firmware's open/closed value when needed. Invalid object types, buffer lengths, and mode values are rejected with device log messages.

## State And Persistence
State is runtime-only: an input device pointer plus a mutex. No firmware value is persisted by the driver. The initial userspace-visible switch state is whichever valid camera mode is delivered by the first event.

## Dependencies And Integration Points
The driver depends on ACPI/WMI, input core, and Lenovo firmware event semantics. Userspace consumes the switch through evdev/libinput-style input interfaces. `PROBE_PREFER_ASYNCHRONOUS` and `no_singleton` allow multiple WMI instances without blocking boot.

## Risks And Edge Cases
Because the input device is lazily created, systems that never emit an initial event will not expose the switch. Firmware returning unexpected buffer encodings is ignored. The notify mutex serializes lazy registration and reporting, but there is no cached last value outside the input core.

## Test Signals
Useful checks include WMI event injection with mode `0` and `1`, validation that `/dev/input` reports `SW_CAMERA_LENS_COVER` with inverted semantics, malformed-event tests for non-buffer and wrong-length objects, module remove after lazy registration, and multi-instance WMI enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c

## Purpose
This driver caches Lenovo WMI capability data blocks used by Lenovo Legion "Other Mode" features. It supports Capability Data 00, Capability Data 01, and Fan Test Data WMI GUIDs, then exposes cached records to peer drivers through the Linux component framework and exported lookup helpers.

## Important APIs, Types, And Functions
`enum lwmi_cd_type` distinguishes `LENOVO_CAPABILITY_DATA_00`, `LENOVO_CAPABILITY_DATA_01`, and `LENOVO_FAN_TEST_DATA`. `struct lwmi_cd_priv` stores the WMI device, cached `cd_list`, ACPI notifier, and optional sub-master state. `struct cd_list` contains a mutex, type, count, and a flexible array of `capdata00`, `capdata01`, or `capdata_fan` records. Exported APIs are `lwmi_cd_match_add_all()`, `lwmi_cd00_get_data()`, `lwmi_cd01_get_data()`, and `lwmi_cd_fan_get_data()`. Internal setup flows include `lwmi_cd_alloc()`, `lwmi_cd_cache()`, `lwmi_cd_fan_list_alloc_cache()`, `lwmi_cd_sub_master_add()`, and component bind/unbind callbacks.

## Control Flow
Probe receives a table entry from the WMI ID context, allocates the appropriate cache, and reads all WMI block instances. Data 00 and 01 become components for `lenovo-wmi-other`. Data 00 can also become a sub-master for Fan Test Data if the fan-test capability is valid. Data 01 registers an ACPI notifier and refreshes cached data on AC adapter status changes, because capability bounds may vary with power source.

## State And Persistence
Capability data is cached in devm-managed memory and protected by `list_mutex`. The cache is refreshed for CD01 on AC power notifications; otherwise it is a probe-time snapshot. Component pointers handed to consumers are valid only while component bindings remain active. No values are written back to firmware.

## Dependencies And Integration Points
The file depends on Lenovo WMI data-block GUIDs, ACPI notifier infrastructure, `wmi-helpers.h`, `wmi-capdata.h`, and the component framework. Its main consumer is `lenovo-wmi-other`, which uses CD00 for fan support, CD01 for tunable attributes, and optional fan data for RPM constraints.

## Risks And Edge Cases
Fan Test Data is packed and variable length; incomplete buffers are ignored and large fan counts are truncated to `U8_MAX`. Missing fan-test support is represented by an `ERR_PTR(-ENODEV)` sub-component marker so master callbacks can still receive `NULL`. Component reprobe ordering is delicate; the code clears master callback state to avoid double-calling after fan-data reprobes. Unsupported or dummy ACPI objects can silently produce empty caches.

## Test Signals
Validation should cover all three GUIDs, block counts and buffer lengths, CD00/CD01 lookups by encoded attribute ID, AC adapter notifications refreshing CD01, component bind/unbind/reprobe ordering, missing Fan Test Data behavior, and integration with `lenovo-wmi-other` hwmon/firmware-attributes registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h

## Purpose
This header defines the shared ABI between Lenovo capability-data providers and consumers. It describes support flags, encoded attribute IDs, data record layouts, the binder object used by the component framework, and lookup function prototypes.

## Important APIs, Types, And Functions
`LWMI_SUPP_VALID`, `LWMI_SUPP_GET`, and `LWMI_SUPP_SET` describe attribute validity and access support. The attribute ID is packed with device, feature, mode, and type fields using `LWMI_ATTR_*_MASK`. `lwmi_attr_id()` builds this packed ID using `FIELD_PREP()`. `struct capdata00` carries `id`, `supported`, and `default_value`; `struct capdata01` adds `step`, `min_value`, and `max_value`; `struct capdata_fan` carries fan ID plus min/max RPM. `struct lwmi_cd_binder` carries CD00/CD01 list pointers and an optional callback for Fan Test Data.

## Control Flow
The header has no executable control flow except the inline encoder. Runtime behavior is supplied by `wmi-capdata.c` and consumers such as `wmi-other.c`. The intended flow is: consumer asks `lwmi_cd_match_add_all()` to match capdata components, receives list pointers through `lwmi_cd_binder`, then calls the typed `lwmi_cd*_get_data()` helpers with packed IDs.

## State And Persistence
The header owns no state. It documents pointer lifetime for `cd_fan_list_cb`: the fan list pointer is only valid during the callback and must not be retained by consumers.

## Dependencies And Integration Points
The header depends on Linux bitfield helpers and forward declarations for `device`, `component_match`, and `cd_list`. It is imported by Lenovo WMI capdata and "Other Mode" drivers and is part of the `LENOVO_WMI_CAPDATA` exported namespace.

## Risks And Edge Cases
Incorrectly encoded attribute IDs cause silent lookup failures or wrong feature mapping. Consumers must respect support bits and callback lifetime. The packed ID layout is firmware ABI, so changing masks or field order would break all capdata lookups.

## Test Signals
Tests should verify `lwmi_attr_id()` field packing, support-flag interpretation, consumer handling of missing CD lists, and compile-time integration between `wmi-capdata.c` and `wmi-other.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c

## Purpose
This Lenovo WMI events driver provides a central WMI event subscription point for hardware-triggered Lenovo events. In this file, the implemented event is thermal mode changes from GUID `D320289E-8FEA-41E0-86F9-911D83151B5F`.

## Important APIs, Types, And Functions
The global `events_chain_head` is a blocking notifier chain. Exported APIs are `lwmi_events_register_notifier()`, `lwmi_events_unregister_notifier()`, and `devm_lwmi_events_register_notifier()`, all exported in namespace `LENOVO_WMI_EVENTS`. `struct lwmi_events_priv` stores the `wmi_device` and event type derived from WMI ID context. `lwmi_events_notify()` validates and dispatches firmware events. `lwmi_events_probe()` initializes per-device state.

## Control Flow
Probe stores the event type from the WMI ID table context. Notify handles `LWMI_EVENT_THERMAL_MODE`: it requires an ACPI integer, validates that the selected profile is one of quiet, balanced, performance, extreme, or custom, then calls the blocking notifier chain with action `LWMI_EVENT_THERMAL_MODE` and a pointer to the selected profile integer. Invalid types and unknown thermal modes are ignored or logged.

## State And Persistence
Only notifier registrations and per-WMI-device type state are maintained. The current thermal mode is not cached here; consumers such as `wmi-gamezone.c` maintain their own state after notifications.

## Dependencies And Integration Points
The driver depends on ACPI/WMI, Linux notifier chains, `wmi-events.h`, and thermal mode constants from `wmi-helpers.h`. `lenovo-wmi-gamezone` subscribes to this chain to update platform-profile state when firmware reports a mode change.

## Risks And Edge Cases
The notifier receives a pointer to a stack-local integer during notify, so subscribers must not retain the pointer. `NOTIFY_BAD` is logged but does not retry. Only thermal mode events are currently supported; new GUIDs require table and dispatch updates.

## Test Signals
Validation should inject valid and invalid thermal mode WMI integers, confirm notifier delivery and `platform_profile_notify()` behavior through subscribers, test devm unregister on consumer removal, and ensure unknown modes do not mutate consumer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h

## Purpose
This header exposes the Lenovo WMI event notifier API. It defines event type identifiers and lets Lenovo platform drivers subscribe to events without binding directly to WMI GUID handlers.

## Important APIs, Types, And Functions
`enum lwmi_events_type` currently defines `LWMI_EVENT_THERMAL_MODE = 1`. The exported functions are `lwmi_events_register_notifier()`, `lwmi_events_unregister_notifier()`, and `devm_lwmi_events_register_notifier()`. Forward declarations keep the header lightweight.

## Control Flow
There is no direct runtime control flow. Consumers create a `notifier_block`, assign `notifier_call`, and register it. The implementation in `wmi-events.c` later invokes subscribers through a blocking notifier chain when firmware events arrive.

## State And Persistence
The header owns no state. Notifier state is stored by the implementation and by each consumer's `notifier_block`.

## Dependencies And Integration Points
The interface integrates `wmi-events.c` with consumers such as `wmi-gamezone.c`. It uses standard Linux notifier semantics and is exported under the Lenovo WMI events namespace.

## Risks And Edge Cases
Consumers must handle the data pointer as event-specific and transient. Adding new event types requires keeping enum values and implementation dispatch synchronized.

## Test Signals
Build tests should verify namespace imports and prototypes. Runtime tests should register and unregister a dummy notifier and confirm only expected action IDs reach it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c

## Purpose
This Lenovo GameZone WMI driver maps Lenovo Legion thermal modes to the Linux `platform_profile` interface. It also exposes the current GameZone thermal mode to other Lenovo WMI drivers through the helper notifier chain.

## Important APIs, Types, And Functions
`struct lwmi_gz_priv` stores current thermal mode, event and mode notifier blocks, a spinlock, WMI device, extreme-mode support, and registered platform-profile device. WMI method IDs `43`, `44`, and `45` query support, set SmartFan mode, and get SmartFan mode. `lwmi_gz_profile_get()` and `lwmi_gz_profile_set()` implement `platform_profile_ops`; `lwmi_gz_platform_profile_probe()` populates supported profile choices. `lwmi_gz_event_call()` consumes thermal mode events from `wmi-events.c`; `lwmi_gz_mode_call()` answers `LWMI_GZ_GET_THERMAL_MODE` requests from `wmi-helpers.c`.

## Control Flow
Probe registers a platform-profile provider, initializes the spinlock, reads current thermal mode, subscribes to WMI thermal events, and registers a thermal-mode query notifier. Profile get reads firmware and updates cached mode. Profile set converts Linux profile options to Lenovo thermal modes, calls WMI method `SMARTFAN_SET`, and updates cached mode. Event notifications update cached mode and call `platform_profile_notify()`.

## State And Persistence
The cached `current_mode` is protected by `gz_mode_lock`; firmware remains authoritative and is read during profile get. No persistent state is stored by the driver beyond WMI-set thermal mode in firmware/EC.

## Dependencies And Integration Points
The driver depends on Lenovo GameZone WMI GUID `887B54E3-DDDC-4B2C-8B88-68A26A8835D0`, `platform_profile`, DMI quirks, `wmi-events`, and `wmi-helpers`. `wmi-other.c` queries current mode before exposing or setting custom CPU power attributes.

## Risks And Edge Cases
Extreme mode is gated by interface version and DMI firmware-bug quirks for Legion Go models that report support but lack correct BIOS entries. The profile set path does not explicitly reject unsupported `MAX_POWER` when the bit was not advertised, relying on platform-profile choices to prevent selection. Notifier pointer handling in `lwmi_gz_mode_call()` is pointer-to-pointer and must match `lwmi_tm_notifier_call()`.

## Test Signals
Tests should verify supported profile bitmaps for WMI support versions below and above 6, DMI quirk suppression of extreme mode, get/set WMI method behavior, event-driven profile notifications, and `wmi-other` custom-mode gating through `lwmi_tm_notifier_call()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-gamezone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c

## Purpose
This file provides shared Lenovo Legion WMI helper functionality: a common method evaluator for integer-returning WMI methods and a blocking notifier chain for querying the current GameZone thermal mode.

## Important APIs, Types, And Functions
`lwmi_dev_evaluate_int()` wraps `wmidev_evaluate_method()`, passes arbitrary input buffers, and accepts either ACPI integer returns or little-endian u32 values in ACPI buffers. `lwmi_tm_register_notifier()`, `lwmi_tm_unregister_notifier()`, and `devm_lwmi_tm_register_notifier()` manage the thermal-mode notifier chain. `lwmi_tm_notifier_call()` asks subscribers for the current thermal mode using action `LWMI_GZ_GET_THERMAL_MODE`.

## Control Flow
The WMI helper builds input and output ACPI buffers, calls the WMI method, validates output only if a return pointer is requested, and converts accepted object types into a u32 result. The notifier helper registers a consumer-owned `notifier_block`; `lwmi_tm_notifier_call()` calls the chain and returns `-EINVAL` unless the non-stop status is `NOTIFY_OK`.

## State And Persistence
The only persistent state is the global blocking notifier chain. No WMI state is cached here.

## Dependencies And Integration Points
The file depends on ACPI/WMI, notifier chains, cleanup helpers, unaligned little-endian reads, and `wmi-helpers.h`. `wmi-gamezone.c` registers the thermal-mode responder; `wmi-other.c` uses `lwmi_tm_notifier_call()` before reading or writing mode-dependent attributes; several Lenovo WMI drivers use `lwmi_dev_evaluate_int()`.

## Risks And Edge Cases
Firmware may return buffers instead of integers; this file intentionally handles that Windows-compatible behavior. Short buffers and unsupported object types return `-ENXIO`. `lwmi_tm_notifier_call()` passes `&mode` to the notifier chain, so responders expect an `enum thermal_mode **`; mismatched consumers would corrupt results.

## Test Signals
Tests should cover integer returns, buffer returns, null or short outputs, WMI call failures, notifier registration/unregistration, and `lwmi_tm_notifier_call()` behavior when no provider is registered or a provider returns a non-OK status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h

## Purpose
This header declares shared Lenovo WMI helper types, thermal mode values, and exported helper functions used by Lenovo Legion WMI drivers.

## Important APIs, Types, And Functions
`struct wmi_method_args_32` is the common two-u32 WMI argument payload. `enum lwmi_event_type` defines `LWMI_GZ_GET_THERMAL_MODE`. `enum thermal_mode` maps Lenovo thermal mode values: none, quiet, balanced, performance, extreme, and custom. Function prototypes cover integer WMI evaluation, thermal-mode notifier registration, devm notifier registration, and thermal-mode query calls.

## Control Flow
The header contains no executable control flow. It defines the ABI between `wmi-helpers.c`, `wmi-gamezone.c`, and consumers such as `wmi-other.c`.

## State And Persistence
No state is owned here. State lives in implementation files and firmware/EC mode registers.

## Dependencies And Integration Points
The header forward-declares Linux device/notifier/WMI structures and includes Linux integer types. The thermal-mode enum is shared with `wmi-events.c` validation and `wmi-gamezone.c` platform-profile conversion.

## Risks And Edge Cases
Changing thermal mode numeric values would break firmware ABI. The two-u32 method payload must remain compatible with Lenovo WMI methods that expect packed 32-bit arguments.

## Test Signals
Build coverage should verify all Lenovo WMI modules agree on enum and struct definitions. Runtime signals come from successful GameZone get/set and Other Mode custom-attribute access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c

## Purpose
This Lenovo Super Hotkey Utility WMI extras driver exposes firmware-controlled audio mute and microphone mute LEDs as Linux LED class devices.

## Important APIs, Types, And Functions
The driver targets WMI GUID `CE6C0974-0407-4F50-88BA-4FC3B6559AD8`. `struct wmi_led_args` is the SetFeature payload. `struct lenovo_super_hotkey_wmi_private` stores two `led_classdev` objects and the WMI device. `lsh_wmi_mute_led_set()` maps LED brightness to firmware feature IDs for mic or audio mute. `lenovo_super_hotkey_wmi_led_init()` queries support version, validates expected version constants, initializes LED classdev names/triggers, and registers them.

## Control Flow
Probe allocates private data, stores the WMI device, and calls setup for mic then audio LEDs. Each setup call invokes `WMI_LUD_GET_SUPPORT`; version `0` means unsupported, exact version matches enable registration. Brightness changes use `WMI_LUD_SET_FEATURE` with one of four on/off feature IDs.

## State And Persistence
The driver does not cache brightness. LED state is held in firmware and controlled through WMI calls. LED class devices are devm-registered and cleaned up with device removal.

## Dependencies And Integration Points
It depends on WMI, ACPI buffer calls, LED class devices, and default audio triggers `audio-micmute` and `audio-mute`. Userspace and ALSA trigger logic can drive the LEDs through the standard LED subsystem.

## Risks And Edge Cases
Unsupported or unexpected firmware LED versions are silently skipped after warnings. SetFeature failures return `-EIO` to LED core. The driver accepts any non-zero brightness as `LED_ON` through wrapper callbacks but registers max brightness as `LED_ON`.

## Test Signals
Validation should include support-version queries for both LED types, LED class device names `platform::micmute` and `platform::mute`, trigger activation, WMI SetFeature payload inspection, suspend/resume LED restoration, and behavior on unsupported version returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-hotkey-utilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-other.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-other.c

## Purpose
This Lenovo Other Mode WMI driver exposes Legion firmware controls that do not fit existing kernel classes. It registers firmware-attributes sysfs groups for CPU power limits and an hwmon fan interface for fan input/target/min/max values.

## Important APIs, Types, And Functions
`struct lwmi_om_priv` stores component bindings to CD00/CD01, hwmon and firmware-attributes devices, an IDA id, WMI device, fan metadata, and collection flags. `lwmi_om_fan_get_set()` performs WMI get/set for fan RPM using `LWMI_FEATURE_VALUE_GET/SET`. `lwmi_om_hwmon_*()` implements fan visibility, reads, and writes. `lwmi_om_fw_attr_add()` creates a firmware-attributes class device and sysfs groups generated by macros for `ppt_pl1_spl`, `ppt_pl2_sppt`, and `ppt_pl3_fppt`. `attr_current_value_show/store()` read or set current values after checking GameZone thermal mode.

## Control Flow
Probe creates a component master and matches capdata components. Master bind initializes fan state, binds CD00/CD01, collects fan support from CD00, receives optional Fan Test Data through a callback, registers hwmon once both data sources are processed, and creates firmware-attributes groups for supported CD01 attributes. Current value writes are allowed only in custom thermal mode and are range-checked against CD01 min/max before WMI set.

## State And Persistence
Runtime state includes fan support bits, min/max RPM, and `last_target`, initialized to `0` because EC fans reset to auto on boot. Fan target writes update firmware/EC and cache the rounded target. Firmware-attributes values are read live through WMI; capability limits come from cached capdata.

## Dependencies And Integration Points
The file integrates WMI Other Mode GUID `DC2A8805-3A8C-41BA-A6F7-092E0089CD3B`, `wmi-capdata`, `wmi-helpers`, GameZone thermal-mode notifier, hwmon, firmware-attributes class, IDA, and the component framework. Module parameters `expose_all_fans` and `relax_fan_constraint` alter hwmon exposure and write validation.

## Risks And Edge Cases
Fan tuning is intentionally hidden when RPM constraints are missing unless unsafe module parameters are set. `last_target` may not reflect out-of-band firmware changes. CD list pointers are valid only while bound. Attribute support detection probes both custom and no-mode encodings and assumes non-zero current value means supported. WMI set success is inconsistent across firmware, so fan set accepts return values `0` and `1`.

## Test Signals
Tests should cover component bind ordering, missing capdata/fan data, hwmon visibility under module-parameter combinations, fan target bounds and divisor rounding, firmware-attributes group creation, custom-mode gating, AC power-driven capdata refresh effects, and unbind cleanup of ksets, IDA ids, hwmon, and component links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-other.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c

## Purpose
The Lenovo Yoga Mode Control driver reports convertible posture changes, especially tablet mode, from Lenovo YMC WMI events to the input subsystem and to the ideapad-laptop notifier.

## Important APIs, Types, And Functions
The event GUID is `06129D99-6083-4164-81AD-F092F9D773A6`; the query GUID is `09B0EE6E-C3FD-4243-8DA1-7911FF80BB8C`. `lenovo_ymc_keymap` maps firmware states to `SW_TABLET_MODE`, ignoring uninitialized state and treating tablet, drawing board, and tent as tablet mode. `lenovo_ymc_notify()` queries current mode through `wmi_evaluate_method()`, reports the sparse keymap event, and calls `ideapad_laptop_call_notifier()`. `lenovo_ymc_probe()` gates loading by convertible/detachable DMI chassis type unless `force=1`.

## Control Flow
Probe allocates/registers an input device, sets up the sparse keymap, stores private data, and calls notify once to report initial state. Each WMI event triggers a separate query method call; the event payload itself is not used.

## State And Persistence
Runtime state is only the input device pointer. Mode state is reported through input core; firmware remains authoritative. No settings are persisted by the driver.

## Dependencies And Integration Points
The driver depends on WMI, DMI, input sparse-keymap, ACPI, and `ideapad-laptop` notifier namespace. It imports `IDEAPAD_LAPTOP` to notify other Lenovo code of YMC events.

## Risks And Edge Cases
The DMI table name has a typo (`chasis`) but behavior is clear. Non-integer query results are ignored. The notifier call is made after freeing/handling the ACPI object path with `code`, so unknown key codes still propagate to ideapad listeners.

## Test Signals
Validation should cover convertible and non-convertible DMI matching, `force=1`, initial state report on probe, all keymap states, malformed query returns, and ideapad notifier delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c

## Purpose
This driver implements the custom fast-charging handshake for Lenovo Yoga Tablet 2 Pro 1380F/1380L. It creates a serdev device on UART3, sends a charger command, then switches USB data lines to GPIO-high mode so the original charger can move from 5V to 12V.

## Important APIs, Types, And Functions
`struct yt2_1380_fc` stores pinctrl states, GPIOs, extcon, notifier, work item, and device pointer. `yt2_1380_fc_worker()` performs the retry handshake. `yt2_1380_fc_extcon_evt()` schedules work on charger state changes. `yt2_1380_fc_serdev_probe()` initializes extcon, pinctrl, GPIOs, serdev baud rate, and extcon notifier. `yt2_1380_fc_pdev_probe()` registers pinctrl mappings, locates the `PNP0501` serial controller, creates a serdev child, and manually attaches the serdev driver.

## Control Flow
Module init registers the serdev driver before the platform driver because platform probe creates and attaches the serdev. The worker exits if already fast charging, otherwise retries up to five times: select UART mode, confirm DCP charger, write `"SC"` at 600 baud, wait, confirm charger still connected, select GPIO mode, wait for voltage switch, and check `EXTCON_CHG_USB_FAST`. Failure restores UART mode.

## State And Persistence
The driver has no persistent policy state; it reacts to extcon state and pinctrl mode. GPIO line mode is actively changed between UART and output-high GPIO during the protocol.

## Dependencies And Integration Points
It depends on extcon state from `i2c-lc824206xa`, serdev helpers, pinctrl mappings for `INT33FC:00`, GPIO descriptors propagated through fwnode from x86-android-tablets, and platform alias `lenovo-yoga-tab2-pro-1380-fastcharger`.

## Risks And Edge Cases
The protocol is timing-sensitive and charger-specific. Work is scheduled from extcon notifications and initial probe; removal does not explicitly cancel work in this file, relying on device lifecycle ordering. Manual serdev attachment maps `-EAGAIN` back to `-EPROBE_DEFER`. Incorrect pinctrl/GPIO definitions could drive USB data lines incorrectly.

## Test Signals
Validation needs original and non-original chargers, DCP-only and fast-charger extcon transitions, retry/failure logging, pinctrl mode switching, UART write length, probe deferral for extcon/serial controller, and removal while work may be pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yoga-tab2-pro-1380-fastcharger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c

## Purpose
This driver manages Lenovo Yoga Book YB1 keyboard-half mode switching. The device can expose either a capacitive touch keyboard or a Wacom digitizer, but not both at once; the driver switches child device driver binding, pen LED, and keyboard backlight based on hall sensor and mode button events.

## Important APIs, Types, And Functions
`struct yogabook_data` holds ACPI/I2C device references, GPIOs, IRQs, PWM, LED devices, work item, flags, and backlight callback. `yogabook_work()` is the central state machine. `yogabook_toggle_digitizer_mode()` flips digitizer mode and schedules work. Shared probe/remove/suspend/resume logic is in `yogabook_probe()`, `yogabook_remove()`, `yogabook_suspend()`, and `yogabook_resume()`. The WMI path uses `KBLC()` on the Goodix ACPI device; the platform path uses PWM and GPIO.

## Control Flow
The module registers both WMI and platform drivers. WMI targets Windows Yoga Book models through button WMI GUID `243FEC1D-1963-41C1-8100-06A9D82A94B4`; platform probe targets Android models by device names and GPIO/PWM lookups. The work function disables currently active devices before enabling the selected one, using `device_release_driver()` and `device_reprobe()`. Tablet mode disables both keyboard and digitizer.

## State And Persistence
Flags track keyboard on, digitizer on, digitizer mode, tablet mode, and suspended state. Brightness is cached in `data->brightness`. Device binding state is manipulated at runtime and restored on remove if either child was released.

## Dependencies And Integration Points
The driver integrates ACPI device lookup, WMI events, I2C device lookup, GPIO lookup tables, PWM, LED class devices, IRQs, workqueues, and PM callbacks. It also uses a lookup for the pen indicator LED provider.

## Risks And Edge Cases
The driver deliberately unbinds/reprobes other drivers, so ordering with Goodix and Wacom probes matters and can defer. Work is scheduled to avoid ACPI deadlocks from event context. Suspend suppresses switching and turns off keyboard backlight if needed. Removal must reprobe released child devices, and failures are only warned.

## Test Signals
Tests should cover WMI and platform variants, mode button toggles, backside hall IRQ tablet transitions, pen touch IRQ on Android models, backlight LED brightness persistence, suspend/resume with pending work, child driver reprobe failures, and cleanup of ACPI/device references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/yogabook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c

## Purpose
This LG Gram platform driver exposes LG ACPI/WMI hotkeys, platform controls, battery charge limiting, LEDs, keyboard backlight, and an LG-specific ACPI operation-region handler.

## Important APIs, Types, And Functions
The driver uses WMI event GUIDs for hotkeys and ACPI methods `WMAB`, `WMBB`, and `\_SB.GGOV`. `lg_wmab()` and `lg_wmbb()` wrap firmware calls. Sysfs attributes include `fan_mode`, `usb_charge`, `reader_mode`, `fn_lock`, `charge_control_end_threshold`, and legacy `battery_care_limit`. LED class devices are `kbd_backlight` and `tpad_led`. `wmi_input_setup()` registers sparse hotkeys and WMI notify handlers. `lg_laptop_address_space_handler()` services LG address space `0x8F`. `acpi_probe()` installs the handler, creates a platform device, registers sysfs/LED/input/battery hooks, and selects WMBB battery-limit path based on DMI-derived year.

## Control Flow
ACPI platform probe for `LGEX0820` installs an opregion handler, registers a child platform device, creates attributes, registers optional LEDs, sets up WMI input handlers, and registers a battery hook. WMI notify maps known event codes to sparse key events or hardware-changed keyboard-backlight notification. Sysfs show/store methods perform firmware get/set calls and validate return object types.

## State And Persistence
Global state includes the platform device pointer, WMI input device, initialization bitmask, battery-limit method selection, and LED classdevs. Feature values live in firmware/EC. The address-space handler does not persist values; it logs or returns debug flags.

## Dependencies And Integration Points
Dependencies include ACPI platform matching, WMI legacy notify handlers, input sparse-keymap, LED class, ACPI battery hooks, DMI product parsing, and the LG firmware methods. Battery threshold is exposed both on the platform device and battery power-supply device.

## Risks And Edge Cases
The code uses global singleton state and legacy WMI APIs. WMBB buffer layout relies on fixed offsets such as `0x10`. DMI year parsing is heuristic and controls battery-limit method selection. LED registration failures are ignored as optional. Unknown opregion writes are ratelimited and ignored to keep firmware running.

## Test Signals
Tests should exercise all sysfs attributes, WMAB/WMBB object type validation, keyboard backlight hardware-change notifications, battery hook file creation/removal, opregion read/write callbacks with `fw_debug`, DMI model-year parsing, and clean unload after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lg-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c

## Purpose
This I2C driver powers on the Analogix ANX7428 USB Type-C crosspoint switch on MeeGoPad T8/T9 Cherry Trail boxes. Firmware leaves the chip powered off, so the driver asserts GPIOs and waits for the on-chip microcontroller.

## Important APIs, Types, And Functions
The driver defines ACPI GPIO mappings for `enable-gpios` and `reset-gpios`, a DMI allowlist for the MeeGoPad board, and an ACPI match for `ANXO7418` even though the hardware is ANX7428. `anx7428_probe()` performs board gating, GPIO sequencing, `TX_STATUS` polling for `OCM_STARTUP`, and vendor/device ID reads.

## Control Flow
Probe refuses unknown boards unless `force=1`. It adds ACPI GPIO mappings, obtains enable GPIO high, waits 10 ms, obtains reset GPIO low, polls `TX_STATUS` up to 50 ms, then reads `VENDOR_ID` and `DEVICE_ID` registers for diagnostics.

## State And Persistence
The driver keeps no runtime state after probe. GPIO descriptors are devm-managed but only used for power sequencing. The ANX7428 autonomous firmware owns Type-C and DisplayPort behavior after startup.

## Dependencies And Integration Points
It depends on ACPI-enumerated I2C, DMI matching, gpiolib ACPI mapping, SMBus byte/word reads, and delay/poll helpers. It intentionally does not integrate with USB Type-C role or alternate-mode frameworks.

## Risks And Edge Cases
The DMI allowlist uses generic firmware strings, so `force` exists for unknown boards but can power unexpected hardware. GPIO sequencing is undocumented and copied from downstream sources. Failure to start OCM means no Type-C switching. The ACPI ID mismatch may surprise maintainers.

## Test Signals
Validation should include DMI allow/deny behavior, force probing, GPIO sequencing on a scope or trace, OCM startup polling, ID register reads, and USB3/DisplayPort functionality after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c

## Purpose
This board platform driver describes Cisco Meraki MX100 GPIO LEDs and reset button using software nodes and platform devices.

## Important APIs, Types, And Functions
The file defines a `gpio_ich` software node, child software nodes for many `leds-gpio` LEDs, and a `gpio-keys-polled` reset key node. `tink_board_init()` gates on DMI vendor/product, forces GPIO60 into GPIO mode with direct I/O to `GPIO_USE_SEL2`, registers software nodes, and creates `leds-gpio` and `gpio-keys-polled` platform devices. `tink_board_exit()` unregisters devices and nodes.

## Control Flow
Module init checks for DMI vendor `Cisco` and product `MX100-HW`. On match it writes bit 28 at I/O port `0x530` so GPIO60 is usable for reset, registers the software-node graph, creates the LED platform device with the LEDs node fwnode, then creates the keys platform device with the keys node fwnode. Errors unwind in reverse order.

## State And Persistence
Persistent runtime state is limited to two platform device pointers and registered software nodes. GPIO line state is handled by downstream `gpio_ich`, `leds-gpio`, and `gpio-keys-polled` drivers.

## Dependencies And Integration Points
Dependencies include DMI, x86 I/O port access, software nodes, GPIO property descriptors, `leds-gpio`, `gpio-keys-polled`, and the ICH GPIO controller. Userspace sees labeled LEDs and a reset key event `KEY_RESTART`.

## Risks And Edge Cases
Direct port I/O is board-specific and assumes the documented PCH register layout. LED polarity varies per line and must match board wiring. The reset button is polled every 20 ms with 100 ms debounce. Loading on non-MX100 hardware is prevented only by DMI.

## Test Signals
Tests should verify DMI gating, software-node registration, all LED labels and GPIO polarities, reset key event generation, cleanup on partial platform-device failure, and GPIO60 mode after the I/O register write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meraki-mx100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c

## Purpose
This MSI embedded controller driver selects an EC register map by firmware version and exposes battery charge start/end thresholds through the ACPI battery extension hook.

## Important APIs, Types, And Functions
Most of the file is a table of `struct msi_ec_conf` instances (`CONF0` through `CONF13`) with allowed firmware strings and EC addresses for charge control, webcam, function key swap, cooler boost, shift mode, fan mode, sensors, LEDs, and keyboard backlight. The active configuration is copied into global `conf`. `ec_read_seq()` and `ec_get_firmware_version()` read the universal firmware version bytes. `load_configuration()` matches firmware against `CONFIGS`. `charge_control_threshold_show/store()` implement offset-adjusted EC threshold reads/writes. `msi_battery_add/remove()` add or remove power-supply attributes.

## Control Flow
Module init reads EC firmware version at address `0xa0`, matches it against allowed firmware lists, and fails with `-EOPNOTSUPP` if unsupported. On success it registers a battery hook. When a battery power supply appears, the hook creates `charge_control_start_threshold` and `charge_control_end_threshold` files. Stores parse u8 percentages, add firmware-specific offsets, enforce configured raw ranges, and write the EC threshold register.

## State And Persistence
The selected `conf` is global module state. Threshold values are persisted in EC/firmware behavior, not in driver memory. The driver does not expose the many non-battery fields in the config table in this version.

## Dependencies And Integration Points
It depends on ACPI EC helpers `ec_read()`/`ec_write()`, ACPI battery hooks, DMI module metadata, and `msi-ec.h` configuration structs. Userspace integration is through power-supply sysfs battery threshold attributes.

## Risks And Edge Cases
The configuration table must exactly match firmware EC layouts; unsupported firmware is rejected to avoid writing wrong EC addresses. `MSI_EC_ADDR_UNKNOWN` and `MSI_EC_ADDR_UNSUPP` have the same sentinel value in the header, so table comments carry semantic nuance not represented programmatically. Only firmware version strings are used for selection.

## Test Signals
Tests should cover firmware string reads, each supported config match, unsupported/invalid firmware rejection, threshold show/store offset math, range checks, EC read/write failures, battery hook add/remove, and absence of attributes when init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h

## Purpose
This header defines the MSI EC configuration schema used by `msi-ec.c` to describe firmware-specific EC register layouts.

## Important APIs, Types, And Functions
It defines driver name, universal firmware-info addresses and lengths, unknown/unsupported sentinel addresses, and configuration structs for charge control, webcam, Fn/Win swap, cooler boost, shift mode, super battery, fan mode, CPU/GPU sensors, mute LEDs, and keyboard backlight. `struct msi_ec_mode` maps names to EC values. `struct msi_ec_conf` aggregates all feature sub-configurations and the allowed firmware string list.

## Control Flow
There is no executable control flow. `msi-ec.c` fills these structs in static tables and copies the matching one at module init.

## State And Persistence
The header owns no state. Its structs describe EC-backed state owned by firmware.

## Dependencies And Integration Points
The header depends only on Linux integer types. It is a private contract between MSI EC configuration tables and code that reads/writes EC addresses.

## Risks And Edge Cases
Both `MSI_EC_ADDR_UNKNOWN` and `MSI_EC_ADDR_UNSUPP` are defined as `0xff01`, so code cannot distinguish them without external comments. Fixed-size mode arrays require manual NULL termination with `MSI_EC_MODE_NULL`.

## Test Signals
Build checks should validate structure initializers and array sizes. Runtime validation comes from correct firmware match and safe threshold behavior in `msi-ec.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c

## Purpose
This legacy MSI laptop driver supports older MSI S270/S271/S420 and related netbook models. It exposes EC-controlled backlight, wireless device state, rfkill devices, touchpad/turbo/eco status, fan auto mode, and special SCM-load behavior.

## Important APIs, Types, And Functions
`struct quirk_entry` controls old EC model, SCM-load model, EC delay, and read-only behavior. Hardware helpers include `set_lcd_level()`, `get_lcd_level()`, `get_auto_brightness()`, `set_auto_brightness()`, `set_device_state()`, and wireless state readers. Sysfs attributes are grouped under `msi-laptop-pf`. RFKill handlers call `set_device_state()`. `msi_laptop_i8042_filter()` watches keyboard controller scan codes and schedules delayed work for rfkill or touchpad updates. `load_scm_model_init()` disables BIOS Fn-key handling and sets up rfkill/input/filter.

## Control Flow
Module init checks ACPI and DMI, defaults to SCM quirk if no DMI match, and uses `force` to select old EC behavior. Old EC models can register a vendor backlight when ACPI video detection allows. The platform driver/device are registered, sysfs groups are created, and SCM models initialize rfkill/input/i8042 filtering. Cleanup reverses this and restores automatic brightness for old EC models unless disabled by module parameter.

## State And Persistence
Global state tracks selected quirks, wireless booleans, 3G presence, rfkill objects, input device, platform/backlight devices, and delayed works. EC writes change firmware-controlled device state and brightness. SCM-load state is restored on resume by setting the EC bit again.

## Dependencies And Integration Points
Dependencies include ACPI EC transactions, DMI, backlight core, platform devices, rfkill, i8042 filter hooks, input sparse-keymap, ACPI video backlight detection, and delayed workqueues.

## Risks And Edge Cases
The module relies on old EC command semantics and DMI quirks. Installing an i8042 filter can affect keyboard event handling. Read-only models update rfkill hardware state but do not write EC bits. `force` may load on unsupported hardware. Delayed work and global rfkill cleanup require careful ordering.

## Test Signals
Tests should cover DMI quirk selection, old EC backlight get/set, auto-brightness policy, rfkill state changes, read-only behavior, i8042 scan-code-triggered updates, touchpad key reporting, resume SCM-load bit restoration, and cleanup with pending delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c

## Purpose
This MSI WMI platform driver exposes fan speed readings through hwmon and creates debugfs endpoints for MSI's generic WMI method interface.

## Important APIs, Types, And Functions
`enum msi_wmi_platform_method` enumerates method IDs from package, EC, BIOS, SMBus, battery, thermal, fan, device, power, debug, AP, data, and WMI operations. `struct msi_wmi_platform_data` stores the WMI device and a mutex required because the firmware method is not thread-safe. `msi_wmi_platform_query()` serializes WMI method calls and validates 32-byte ACPI buffer replies with `msi_wmi_platform_parse_buffer()`. `msi_wmi_platform_read()` implements hwmon fan input conversion. Debugfs uses `struct msi_wmi_platform_debugfs_data` plus file operations to write a 32-byte payload and read the last response.

## Control Flow
Module init gates on MSI DMI vendor unless `force=1`, then registers a WMI driver for GUID `ABBC0F6E-8EA1-11D1-00A0-C90629100000`. Probe initializes state and mutex, checks WMI interface major version, checks EC information and Tiger Lake flag, creates debugfs files for all methods, then registers hwmon with four fan input channels.

## State And Persistence
Runtime state is WMI device data, a mutex, and per-debugfs response buffers protected by rwsems. Fan values are read live from firmware. Debugfs stores only the last method response per file.

## Dependencies And Integration Points
Dependencies include WMI, DMI, hwmon, debugfs, mutex/rwsem locking, unaligned big-endian reads, and ACPI buffer behavior. The GUID is generic Microsoft sample-derived, so DMI gating prevents binding to non-MSI firmware that reused it.

## Risks And Edge Cases
The firmware method is explicitly not thread-safe, making the mutex critical. The reply parser treats first response byte `0` as `-EIO`. Debugfs allows raw privileged calls to all methods and can change firmware state through `set_*` methods. Interface and EC checks can be overridden by unsafe `force`.

## Test Signals
Validation should cover DMI whitelist, interface version rejection and force override, non-Tiger Lake rejection, fan RPM conversion including zero divisor, debugfs exact 32-byte write requirement, concurrent debugfs/hwmon access serialization, and cleanup of debugfs on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c

## Purpose
This MSI WMI hotkeys driver handles MSI and MSI Wind WMI events and optionally exposes a vendor WMI backlight device.

## Important APIs, Types, And Functions
The driver uses BIOS GUID `551A1F84-FBDD-4125-91DB-3EA8F44F1D45`, MSI event GUID `B6F3EEF2-3D2F-49DC-9DE3-85BCE18C62F2`, and Wind event GUID `5B3CC38A-40D9-7245-8AE6-1145B751BE3F`. `msi_wmi_keymap` maps generic brightness/volume/mute and Wind turbo/eco events, ignoring keys handled elsewhere. `msi_wmi_query_block()` and `msi_wmi_set_block()` implement WMI data-block access. `bl_get()`/`bl_set_status()` implement six-level backlight mapping. `msi_wmi_notify()` reports sparse key events and suppresses duplicate GPE storms for one event GUID.

## Control Flow
Module init searches for an event GUID, registers input and notify handler for the first match, then registers a WMI backlight if the BIOS GUID exists and ACPI video says vendor backlight should be used. If neither hotkeys nor backlight are present, init fails. Cleanup removes the notify handler, input device, and backlight.

## State And Persistence
Global state tracks selected event GUID metadata, last event timestamp, input device, and backlight device. Brightness state lives in firmware and is mapped through `backlight_map`.

## Dependencies And Integration Points
Dependencies include legacy WMI query/set/notify APIs, input sparse-keymap, backlight core, ACPI video backlight detection, and kernel time helpers. Userspace sees input events and optionally `/sys/class/backlight/msi-wmi`.

## Risks And Edge Cases
Duplicate suppression ignores events within 50 ms for the MSI event GUID because one keypress can generate many GPEs. Brightness key events are suppressed when ACPI video should handle them unless this driver owns backlight. Init error unwind only unregisters input if `event_wmi` was set, so failures before assignment require careful review.

## Test Signals
Tests should cover both event GUID families, duplicate suppression timing, unknown event logging, brightness map get/set, ACPI video backlight gating, absence of BIOS/event GUIDs, and cleanup after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c

## Purpose
This small MXM WMI helper exposes functions for GPU mux switching through the MXM WMMX WMI GUID.

## Important APIs, Types, And Functions
The target GUID is `F6CB5C3C-9CAE-4EBD-B577-931EA32A2CC0`. `struct mxds_args` carries function code, args, and xarg. Exported functions are `mxm_wmi_call_mxds()`, `mxm_wmi_call_mxmx()`, and `mxm_wmi_supported()`. Function codes are four-character constants for `MXDS` and `MXMX`.

## Control Flow
`mxm_wmi_supported()` checks GUID presence. The call helpers build the argument struct with selected function code and call `wmi_evaluate_method()` using the adapter value as method ID. They print before and after the call and return ACPI failure status directly or `0` on success.

## State And Persistence
The file maintains no state. Any mux state change is performed by firmware in response to WMI calls.

## Dependencies And Integration Points
It depends on WMI and exports symbols through GPL for graphics or platform code that needs MXM mux operations. It also relies on public `linux/mxm-wmi.h` declarations.

## Risks And Edge Cases
Return values on ACPI failure are raw `acpi_status`, not normalized Linux negative errno. The helpers use `printk()` instead of structured device logging and have no locking or result validation. Firmware behavior is opaque and adapter method IDs must match platform expectations.

## Test Signals
Tests should verify GUID detection, successful MXDS/MXMX calls on supported hardware, caller handling of raw ACPI failure values, and no calls on unsupported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/mxm-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c

## Purpose
This NVIDIA WMI EC backlight driver registers a firmware backlight device for systems where panel brightness is controlled through NVIDIA's WMI-wrapped EC methods.

## Important APIs, Types, And Functions
It uses platform data definitions from `linux/platform_data/x86/nvidia-wmi-ec-backlight.h`, especially `WMI_BRIGHTNESS_GUID`, method IDs, modes, and `struct wmi_brightness_args`. `wmi_brightness_notify()` validates method/mode, calls `wmidev_evaluate_method()`, and reads/writes the in-place argument struct. Backlight operations are `nvidia_wmi_ec_backlight_update_status()` and `nvidia_wmi_ec_backlight_get_brightness()`. Probe queries max and current brightness and registers `nvidia_wmi_ec_backlight`.

## Control Flow
Probe refuses to bind unless ACPI video detection selected `acpi_backlight_nvidia_wmi_ec`, unless `force=1`. It marks the device as `BACKLIGHT_FIRMWARE`, reads maximum brightness with `GET_MAX_LEVEL`, reads current brightness with `GET`, then registers a devm backlight device. Updates call WMI `SET` with the requested brightness.

## State And Persistence
The backlight core stores current requested brightness; firmware/EC stores actual brightness. The driver has no separate persistent state.

## Dependencies And Integration Points
Dependencies include WMI, ACPI video backlight detection, backlight core, and NVIDIA WMI EC platform data. It is intended to be prioritized over raw GPU backlights by using firmware backlight type.

## Risks And Edge Cases
The module parameter description has a missing closing parenthesis but no behavior impact. The WMI helper reuses the same buffer for input and output and assumes firmware updates `args.ret`. Invalid method or mode returns `-EINVAL`; ACPI failures become `-EIO`. `force` can create duplicate or wrong backlight devices.

## Test Signals
Tests should cover ACPI video backlight type gating, force override, max/current brightness queries, set/get round trips, invalid method/mode rejection, ACPI failure handling, and userspace backlight priority against GPU raw backlights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c -->
