# subset-b-005135 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-uart-backlight.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-uart-backlight.c

Purpose: implements a Dell all-in-one serial backlight controller. It only binds when `acpi_video_get_backlight_type()` returns `acpi_backlight_dell_uart`, locates the ACPI-described `DELL0501` serial controller through `get_serdev_controller()`, creates a synthetic serdev child, manually attaches a serdev driver, and registers a `BACKLIGHT_PLATFORM` device named `dell_uart_backlight`.

Important APIs, types, and functions: `struct dell_uart_backlight` stores the current command transaction, response buffer, wait queue, mutex, backlight device, and tracked power state. `dell_uart_bl_command()` serializes command writes with `mutex_lock_killable()`, sends via `serdev_device_write_buf()`, and waits up to one second. `dell_uart_bl_receive()` is the receive state machine: it parses the length byte, verifies echoed command, enforces maximum response length, checks the checksum, and wakes the waiter. `dell_uart_set_brightness()`, `dell_uart_get_brightness()`, and `dell_uart_set_bl_power()` implement protocol commands. `dell_uart_update_status()` bridges backlight core writes to firmware.

Control flow: platform probe verifies Dell UART backlight selection, creates the serdev, registers and manually binds the serdev driver. Serdev probe opens the UART at 9600 baud, queries firmware version, forces panel power on, reads brightness, then registers the backlight class device. Remove unregisters the serdev driver and removes the child serdev.

State and persistence: brightness and power are stored in controller firmware; the driver only caches `power` because no get-power command exists. In-flight command state is protected by the transaction mutex and completed by the async receive callback.

Dependencies and integration: uses ACPI video backlight selection, serdev helpers, serdev core, wait queues, and backlight core. It is Dell AIO-specific and depends on the `DELL0501` controller path.

Risks: out-of-band bytes after timeout are dropped, so controller desynchronization can cause transient failures. The receive parser trusts the response buffer sized by each command but clamps to caller-provided `resp_max_len`. Manual driver binding is fragile if serdev matching semantics change. Test signals include probe success, firmware-version debug output, backlight sysfs brightness reads/writes, timeout/error logs, checksum mismatch logs, and suspend/resume behavior through the backlight core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-uart-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-aio.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-aio.c

Purpose: provides legacy WMI hotkey support for Dell all-in-one systems exposing either `EVENT_GUID1` or `EVENT_GUID2`. It maps volume, mute, brightness, display-toggle, and video-switch scancodes into Linux input events.

Important APIs, types, and functions: `struct dell_wmi_event` describes the newer buffer event format with length, type, and event array. `dell_wmi_aio_keymap` is a sparse-keymap table. `dell_wmi_aio_event_check()` validates buffer events with type `0` or `0xf` and at least one payload word. `dell_wmi_aio_notify()` accepts either integer ACPI objects, new-format buffers, or broken one-byte buffers and reports scancodes through `sparse_keymap_report_event()`. `dell_wmi_aio_find()` selects the first known GUID present.

Control flow: module init searches for a GUID, allocates/registers one global input device, and installs a WMI notify handler. Notify dispatch decodes the ACPI object and emits a sparse-keymap event if a scancode is found. Exit removes the handler for the currently present GUID and unregisters the input device.

State and persistence: only a global `input_dev` pointer is retained. Firmware state is not modified; the driver only translates notifications. There is no per-device private data and no suspend/resume state.

Dependencies and integration: integrates with the old `wmi_install_notify_handler()` API rather than `struct wmi_driver`, input core, and sparse-keymap. It is separate from `dell-wmi-base` and targets all-in-one GUIDs.

Risks: global state and GUID rediscovery on exit assume the same GUID remains available. The buffer fallback for broken firmware treats the first byte as a scancode, which is intentionally permissive but can report spurious keys from malformed data. Test signals include module load on systems with each GUID, integer and buffer event decoding, unknown scancode behavior through sparse-keymap, and clean handler removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-base.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-base.c

Purpose: main Dell WMI hotkey/event driver for laptop-class systems using event GUID `9DBB5994-A997-11DA-B012-B622A1EF5492`. It translates WMI event buffers into input events, tablet switch events, privacy events, and Dell laptop notifier callbacks.

Important APIs, types, and functions: `struct dell_wmi_priv` stores the main input device, optional tablet switch device, and descriptor interface version. Static keymaps cover WMI event types `0x0000`, `0x0010`, `0x0011`, and `0x0012`; DMI type `0xB2` hotkey tables can augment type `0x0010`. `handle_dmi_entry()` builds a runtime sparse keymap from BIOS keycodes. `dell_wmi_process_key()` handles brightness suppression when ACPI video owns brightness keys, keyboard illumination notification, tablet-mode switch reporting, ePrivacy key selection, and ultra-performance value handling. `dell_wmi_notify()` parses one or more length-prefixed u16 events and delegates to privacy handling first for eligible type `0x0012` events. `dell_wmi_events_set_enabled()` uses Dell SMBIOS application registration on specific DMI systems.

Control flow: late init checks DMI quirks, optionally enables WMI events through SMBIOS, registers the Dell privacy subdriver, then registers a WMI driver. Probe gates on `dell_wmi_get_descriptor_valid()` and descriptor interface version, then creates sparse-keymap input. Notify parses buffers differently for descriptor interface version 0 to avoid stale trailing data.

State and persistence: runtime input devices and tablet switch device live per WMI device. `wmi_requires_smbios_request` is a module-global DMI quirk. Firmware event registration is enabled at init and disabled at exit for affected systems.

Dependencies and integration: depends on `dell-wmi-descriptor`, `dell-smbios`, `dell-laptop` notifier, `dell-wmi-privacy`, ACPI video, WMI, input, and sparse-keymap.

Risks: event parsing depends on firmware-provided lengths and the version-specific stale-buffer workaround. Keymap merging has duplicate-suppression only for DMI-derived type `0x0010` entries. Privacy and hotkey handling share type `0x0012`, so ordering matters. Test signals include descriptor probe ordering, DMI hotkey-table systems, type 0/1 multi-event buffers, privacy events, tablet-mode event `0xe070`, brightness-key suppression under ACPI video, and SMBIOS registration error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-ddv.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-ddv.c

Purpose: exposes Dell DDV WMI sensor and battery data through hwmon, ACPI battery extensions, sysfs ePPID attributes, and debugfs raw buffers. It supports DDV interface versions 2 and 3 unless `force` is set.

Important APIs, types, and functions: `enum dell_ddv_method` enumerates DDV WMI method IDs for battery, fan, thermal, analytics, and interface-version queries. `dell_wmi_ddv_query_type()`, `_integer()`, `_buffer()`, and `_string()` wrap `wmidev_evaluate_method()` with ACPI type and package validation. `struct dell_wmi_ddv_sensors` caches fan/thermal package objects for one second under a mutex. `dell_wmi_ddv_hwmon_add()` builds dynamic hwmon channel info from detected fan and thermal entries. Battery support uses `struct acpi_battery_hook`, `power_supply_register_extension()`, `dell_wmi_ddv_battery_translate()`, and property handlers for health, temperature, and manufacture date.

Control flow: probe reads interface version, allocates device data, creates debugfs entries, registers a battery hook if ACPI battery is reachable, and registers hwmon if sensors are available. HWMON reads refresh cached WMI buffers, validate channel indexes, then decode packed fan RPM or temperature records. Battery property reads translate a Linux `power_supply` to Dell battery index by serial number and then query the requested method.

State and persistence: sensor buffers are cached per device and invalidated on resume. Battery translation cache maps up to three Dell indexes to `power_supply` pointers and is invalidated on battery removal. No firmware settings are persisted; data is read-only.

Dependencies and integration: WMI, ACPI battery hook, power-supply extension API, hwmon, debugfs, PM sleep hooks, unaligned access helpers, and Dell firmware-specific DDV package formats.

Risks: firmware package shape is critical; `_query_buffer()` rejects mismatched count/type/size and warns on inconsistent lengths. Serial translation must handle decimal and hexadecimal ACPI serial strings. Manufacturer-access health decoding may see unknown subcodes. Test signals include supported/unsupported interface versions, systems with no sensors, fan/temp labels and values, debugfs raw files, battery ePPID lengths, health-code mapping, cache invalidation after resume, and hot-remove battery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-ddv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.c

Purpose: provides a shared Dell WMI descriptor probe and exported query helpers used by other Dell WMI drivers to validate the common descriptor GUID and learn interface metadata.

Important APIs, types, and functions: `struct descriptor_priv` stores one descriptor instance on `wmi_list` with `interface_version`, `size`, and `hotfix`. Exported functions `dell_wmi_get_descriptor_valid()`, `dell_wmi_get_interface_version()`, `dell_wmi_get_size()`, and `dell_wmi_get_hotfix()` are the integration surface. Probe reads `DELL_WMI_DESCRIPTOR_GUID` block 0 and validates ACPI object type, exact 128-byte length, and `"DELL WMI"` signature.

Control flow: the module registers a WMI driver for the descriptor GUID. Before descriptor probe completes, `descriptor_valid` is `-EPROBE_DEFER`. On valid probe it becomes `0`, and the metadata object is appended to a mutex-protected global list. Remove deletes the instance from the list. Consumers typically call `dell_wmi_get_descriptor_valid()` during their probe and defer or fail accordingly.

State and persistence: the module maintains process-local descriptor state only. `descriptor_valid` is global and reflects the most recent descriptor validity result; metadata is per WMI device but helpers return the first list entry.

Dependencies and integration: depends on ACPI/WMI, list/mutex infrastructure, and exports GPL symbols to Dell WMI consumers such as `dell-wmi-base`.

Risks: multiple descriptor devices are represented as a list but accessors return only the first entry. The code casts the ACPI buffer to `u32 *` and also checks `obj->string.pointer`, relying on union layout over the buffer pointer. Invalid descriptor state is sticky through `descriptor_valid`. Test signals include absence of GUID, probe defer before descriptor driver binds, invalid type/length/signature paths, unknown interface-version warning, and consumer probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.h -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.h

Purpose: declares the public interface for the Dell WMI descriptor helper. It lets dependent Dell WMI modules determine whether the descriptor GUID exists and whether descriptor probing has accepted or rejected the firmware buffer.

Important APIs/types/functions: `dell_wmi_get_descriptor_valid()` returns `-ENODEV` for missing descriptor GUID, `-EPROBE_DEFER` before descriptor probing, `0` for valid descriptors, and another negative errno for invalid descriptors. `dell_wmi_get_interface_version()`, `dell_wmi_get_size()`, and `dell_wmi_get_hotfix()` return `bool` success and fill a caller-provided `u32`.

Control flow and integration: the header is included by consumers such as `dell-wmi-base`, which uses descriptor validity as a probe gate and interface version to decide WMI event-buffer parsing. The helper signatures hide the internal WMI driver and list state.

State and persistence: the header itself has no state; it documents an external, runtime descriptor state owned by `dell-wmi-descriptor.c`.

Dependencies: includes `<linux/wmi.h>` for WMI-related type availability and is GPL-only in the companion implementation.

Risks and test signals: consumers must handle `false` returns from metadata getters because descriptor probing may not have produced a list entry even when the GUID exists. Probe-order tests should exercise `-EPROBE_DEFER`, missing GUID, valid metadata, and invalid metadata behavior. Because this header is small, regression tests are mostly build coverage for all including drivers and behavioral tests through descriptor consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-led.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-led.c

Purpose: registers a Dell lid/panel-back LED class device backed by Dell WMI method GUID `F6E4FE6E-909D-47cb-8BAB-C9F6F2F8D396`.

Important APIs, types, and functions: `struct bios_args` is the six-byte firmware command/response buffer. `dell_led_perform_fn()` calls `wmi_evaluate_method()` method 1 with a BIOS argument buffer and returns the firmware result code. `led_on()`, `led_off()`, and `led_blink()` wrap command IDs 16, 17, and 18 for device ID 1. `dell_led_set()` maps LED brightness to on/off. `dell_led_blink()` converts millisecond delays to 125 ms units, clamps to 1..255, updates caller delay values, and invokes firmware blink.

Control flow: init checks for the WMI GUID, sends `led_off()` as a functional probe, and registers `dell::lid` with `LED_CORE_SUSPENDRESUME`. Exit unregisters and turns the LED off.

State and persistence: the Linux LED class holds brightness metadata; the hardware state is changed directly in firmware and explicitly reset to off on module exit. No persistent settings are stored.

Dependencies and integration: uses legacy WMI evaluate API, ACPI object buffers, LED class core, and module aliasing for the Dell LED GUID.

Risks: firmware error codes are returned directly rather than mapped to standard errno in most paths, and `dell_led_set()` ignores failures because the LED core setter is void. `dell_led_perform_fn()` returns raw ACPI status on WMI failure, which may not be a Linux errno. Test signals include GUID absence, successful off probe, brightness toggles, blink delay normalization, firmware result-code failures, suspend/resume LED state, and exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.c

Purpose: handles Dell hardware privacy status for microphone, camera shutter, and ePrivacy screen capability/status reporting. It registers a WMI driver through `dell-wmi-base`, exposes sysfs status, reports input events, and provides a micmute LED device used as an EC acknowledgement trigger.

Important APIs, types, and functions: `struct privacy_wmi_data` stores input device, WMI device, list node, LED classdev, supported feature mask, and last status. `dell_privacy_has_mic_mute()` and `dell_privacy_process_event()` are exported for other Dell modules. `get_current_status()` reads an 8-byte WMI block containing supported devices and current state. `dell_privacy_wmi_probe()` builds a sparse keymap for type `0x0012` privacy events, conditionally registers camera switch support, reports initial camera-cover state, and registers `dell-privacy::micmute` if audio privacy is present. `dell_privacy_micmute_led_set()` evaluates EC method `ECAK`.

Control flow: `dell-wmi-base` calls `dell_privacy_register_driver()` during module init and delegates type `0x0012` events to `dell_privacy_process_event()`. Audio events set `last_status` and emit `KEY_MICMUTE`; camera events emit `SW_CAMERA_LENS_COVER` according to the status bit. Sysfs attributes render supported and current state per privacy type.

State and persistence: a mutex-protected global WMI list stores active privacy devices, but helpers use the first entry. `last_status` is updated from initial WMI block and event payloads. The LED operation does not set brightness itself; it acknowledges firmware/EC sequencing.

Dependencies and integration: WMI, ACPI EC, input sparse-keymap, switch events, LED trigger `audio-micmute`, sysfs device groups, and `dell-wmi-base` event parsing.

Risks: only the first privacy device is used. EC method `ECAK` may be missing. Incorrect status-bit interpretation would invert camera cover or mic state. Test signals include initial sysfs state, camera-cover switch registration only when supported, micmute LED trigger behavior, WMI block validation, unknown privacy event logging, and integration with audio codec micmute notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.h -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.h

Purpose: declares the integration contract between Dell WMI hotkey/event handling and the optional Dell privacy driver.

Important APIs: when `CONFIG_DELL_WMI_PRIVACY` is enabled, the header declares `dell_privacy_has_mic_mute()`, `dell_privacy_process_event(int type, int code, int status)`, `dell_privacy_register_driver()`, and `dell_privacy_unregister_driver()`. When disabled, inline stubs make privacy support compile away: the query and process helpers return `false`, registration returns `0`, and unregister is a no-op.

Control flow and integration: `dell-wmi-base` can unconditionally include this header, register/unregister privacy support, and offer privacy event payloads to `dell_privacy_process_event()` without surrounding all call sites in Kconfig conditionals. Event type/code/status semantics are implemented in the `.c` file.

State and persistence: no state is defined here. The enabled implementation owns runtime WMI device state, supported-feature bits, input devices, and LED class devices.

Dependencies: deliberately minimal; it is a small Kconfig-aware header. The enabled implementation depends on WMI/input/LED/ACPI EC, but consumers only need this declaration layer.

Risks and test signals: disabled builds should still register `dell-wmi-base` and process non-privacy events because stubs are harmless. Enabled builds should verify symbol availability and ordering with `dell-wmi-base`. Build tests should cover `CONFIG_DELL_WMI_PRIVACY=y/m/n`, and runtime tests should verify that privacy events fall through to generic key processing when the privacy driver is absent or declines an event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/Makefile -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/Makefile

Purpose: defines the object composition for the Dell WMI System Management driver under `CONFIG_DELL_WMI_SYSMAN`.

Important build entries: `obj-$(CONFIG_DELL_WMI_SYSMAN) += dell-wmi-sysman.o` makes the composite module conditional. `dell-wmi-sysman-y` links `sysman.o`, `enum-attributes.o`, `int-attributes.o`, `string-attributes.o`, `passobj-attributes.o`, `biosattr-interface.o`, and `passwordattr-interface.o` into one module.

Control flow: this file has build-time control flow only. It ensures the shared global `wmi_priv`, sysfs population code, attribute validators, and both WMI setter/password interface drivers are linked into one module so symbols remain local to the composite object unless exported elsewhere.

State and persistence: no runtime state. The link composition matters because `wmi_priv` is global across all included objects and the module init/exit lives in `sysman.c`.

Dependencies and integration: participates in the kernel Kbuild system and depends on Kconfig selection of the sysman feature plus the source files' dependencies on WMI and `firmware_attributes_class`.

Risks and test signals: omitting one object breaks unresolved symbols for populate/exit helpers or WMI interface init/exit functions. Build tests should compile `CONFIG_DELL_WMI_SYSMAN=m` and `=y`. Runtime tests are indirect through successful sysman module load and sysfs creation. Because file order is explicit, adding a new attribute type requires updating this Makefile and header prototypes together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/biosattr-interface.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/biosattr-interface.c

Purpose: implements firmware write operations for Dell BIOS attributes: setting one attribute and resetting BIOS defaults through the Dell BIOS attributes WMI interface GUID.

Important APIs, types, and functions: `call_biosattributes_interface()` wraps `wmidev_evaluate_method()` for method IDs `SETBIOSDEFAULTS_METHOD_ID` and `SETATTRIBUTE_METHOD_ID`, extracts integer firmware status, maps it through `map_wmi_error()`, and sets `wmi_priv.pending_changes` plus a `KOBJ_CHANGE` uevent when a write occurs. `set_attribute()` constructs a security buffer from `current_admin_password`, then UTF-16 string buffers for attribute name and value. `set_bios_defaults()` builds a security buffer plus one-byte reset type. Probe/remove callbacks store or clear `wmi_priv.bios_attr_wdev`.

Control flow: sysfs store handlers in enum/int/string attribute files validate input and call `set_attribute()`. The top-level `reset_bios` sysfs store calls `set_bios_defaults()`. Module init in `sysman.c` registers this WMI driver before creating firmware-attributes sysfs.

State and persistence: successful writes change BIOS firmware settings and mark `pending_changes`. The current admin password is stored in global `wmi_priv` and copied into every security buffer. The WMI device pointer is protected by `wmi_priv.mutex`.

Dependencies and integration: WMI device API, shared sysman helpers for security/string buffers, firmware attributes class uevents, and Dell-specific status-code mapping.

Risks: `print_hex_dump_bytes()` logs the full set-attribute buffer, including the security area, which is sensitive if debug logging is enabled. Firmware may require admin password and returns `-EOPNOTSUPP`/`-EACCES` for missing/invalid credentials. Test signals include setting each attribute type, pending-reboot sysfs changes and uevents, reset defaults, password-required paths, invalid WMI object output, and concurrent sysfs writes under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/biosattr-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/dell-wmi-sysman.h -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/dell-wmi-sysman.h

Purpose: central shared header for the Dell WMI System Management module. It defines WMI GUIDs, shared data structures, attribute constants, helper macros, and cross-object function prototypes.

Important APIs/types: `struct wmi_sysman_priv` is the module-global state: current admin/system passwords, WMI device pointers, firmware-attributes class device, ksets, per-type attribute arrays/counts, pending-change flag, and mutex. `struct enumeration_data`, `integer_data`, `str_data`, and `po_data` cache firmware metadata. GUID macros identify enumeration, integer, string, password-object, BIOS-attributes, and password-interface WMI blocks. Macros such as `get_instance_id`, `attribute_s_property_show`, `attribute_n_property_show`, and `attribute_property_store` generate repeated sysfs handlers.

Control flow and integration: each attribute implementation includes this header to allocate/populate its metadata array, validate writes, and create sysfs groups. `sysman.c` owns init/exit and WMI object enumeration. `biosattr-interface.c` and `passwordattr-interface.c` implement write methods declared here.

State and persistence: the header declares but does not allocate `wmi_priv`. It documents global password buffers and pending-change state, which persist for the module lifetime and are not scrubbed on exit in the declarations themselves.

Dependencies: Linux WMI, device, module, kernel, and capability headers, plus the local firmware-attributes class in implementation files.

Risks and test signals: generated macros rely on naming conventions such as `wmi_priv.type##_data` and `validate_##type##_input()`. Off-by-one risk exists in generated `get_instance_id()` loops because it uses `<= count`. Build coverage across all objects is essential. Runtime tests should exercise every attribute type, absent GUIDs, duplicate attribute names, long strings bounded by `MAX_BUFF`, and password state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/dell-wmi-sysman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/enum-attributes.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/enum-attributes.c

Purpose: implements Dell BIOS enumeration attributes under the firmware-attributes sysfs tree. Enumeration attributes expose metadata, possible values, current value, and a write path for setting the current value.

Important APIs and functions: `alloc_enum_data()` sizes `wmi_priv.enumeration_data` from WMI instance count. `populate_enum_data()` validates ACPI package element types, caches attribute name/display/default/modifier fields, parses variable-length value modifiers and possible values, then creates the sysfs attribute group. `current_value_show()` re-queries the WMI instance to read the current value. `validate_enumeration_input()` accepts case-insensitive matches against semicolon-delimited possible values. The generated `current_value_store()` calls `set_attribute()` after validation.

Control flow: `sysman.c` enumerates each WMI instance, creates a kobject named after `ATTR_NAME`, then calls `populate_enum_data()`. Reads of static metadata use cached strings. Reads of `current_value` fetch fresh firmware state. Writes validate against cached possible values and invoke the BIOS attributes WMI setter.

State and persistence: cached metadata lives in `wmi_priv.enumeration_data` until module exit. The firmware setting persists in BIOS only after a successful `set_attribute()` call and may require reboot; sysman marks pending changes globally.

Dependencies and integration: relies on `dell-wmi-sysman.h` macros, WMI object parsing from `sysman.c`, sysfs kobject groups, and BIOS write interface.

Risks: value-count extraction casts `integer` objects through `string.pointer` via the shared macro pattern, which is suspicious and dependent on ACPI union layout. `possible_values` truncation is avoided by `append_enum_string()` bounds checks, but long firmware lists fail population. Test signals include valid/invalid values, case-insensitive writes, variable-length possible-values packages, malformed ACPI types/counts, duplicate names, and exit cleanup removing groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/enum-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/int-attributes.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/int-attributes.c

Purpose: implements Dell BIOS integer attributes in the sysman firmware-attributes interface.

Important APIs/functions: `alloc_int_data()` allocates the per-instance metadata array. `populate_int_data()` validates package fields for name, display strings, default value, modifier, min/max, and scalar increment, caches them, and creates a sysfs group. `current_value_show()` re-queries the integer WMI instance and emits the current integer. `validate_integer_input()` parses user input with `kstrtoint()`, enforces cached min/max bounds, and strips a leading `+` to work around a BIOS bug that would otherwise set zero.

Control flow: `sysman.c` creates a kobject for each integer attribute and delegates population. Metadata reads return cached values via macros. `current_value_store()` is generated by `attribute_property_store()`: it copies input, strips newline, maps kobject to instance, validates, then calls `set_attribute()`.

State and persistence: metadata is cached in `wmi_priv.integer_data`. Writes persist through firmware and set global pending-change state through the BIOS attributes interface. No current value is cached; reads fetch firmware state.

Dependencies and integration: shared sysman header/macros, WMI package enumeration, sysfs attributes with `current_value` mode `0600`, and Dell BIOS attributes setter.

Risks: integer metadata extraction uses `(uintptr_t)obj.string.pointer` for integer elements, inherited from the macro style and potentially fragile. Scalar increment is exposed but not enforced during validation, so firmware may reject values that pass min/max. Test signals include boundary values, leading plus sign, non-numeric input, scalar-increment mismatch, malformed WMI packages, and secure write behavior when admin password is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/int-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passobj-attributes.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passobj-attributes.c

Purpose: implements password-object attributes under the sysman `authentication` kset. It exposes password status/limits and write-only files for current and new password handling.

Important APIs/functions: `alloc_po_data()` allocates password-object metadata. `populate_po_data()` caches attribute name and min/max password length, then creates sysfs files. `is_enabled_show()` re-queries firmware to report whether a password is set. `current_password_store()` copies user-provided current password into either `wmi_priv.current_admin_password` or `current_system_password` based on kobject name. `new_password_store()` strips a newline, bounds input, and calls `set_new_password()`. `role_show()` maps `Admin` to `bios-admin` and `System` to `power-on`.

Control flow: `sysman.c` enumerates password-object WMI instances into the `authentication` kset. Users first write the current password into a write-only buffer, then write the desired new password. Password interface code builds the WMI command and updates cached current password on success.

State and persistence: current passwords are stored in plaintext global buffers for the module lifetime. New passwords persist in firmware after a successful WMI call. The current-password sysfs file is write-only and does not validate against firmware at write time.

Dependencies and integration: sysfs kobject groups, shared sysman metadata, and `passwordattr-interface.c` for the actual WMI method.

Risks: plaintext password retention in kernel memory and lack of explicit clearing on module exit are security-sensitive. Length validation here only checks `MAX_BUFF`; firmware enforces min/max for actual password rules. Test signals include Admin/System role detection, unknown password-object names, current password newline trimming, maximum-length rejection, firmware unsupported/access-denied paths, and cleanup of authentication kobjects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passobj-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passwordattr-interface.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passwordattr-interface.c

Purpose: implements the Dell WMI password interface used by sysman password-object sysfs files to set Admin or System passwords.

Important APIs/functions: `call_password_interface()` evaluates WMI method 1 on `DELL_WMI_BIOS_PASSWORD_INTERFACE_GUID`, extracts integer status, sends a `KOBJ_CHANGE` uevent, and maps firmware status through `map_wmi_error()`. `set_new_password()` validates password type, selects the cached current password buffer, builds a command containing admin security area, password type, current password, and new password as UTF-16 length-prefixed strings, then calls the WMI method. Probe/remove callbacks update `wmi_priv.password_attr_wdev`.

Control flow: `new_password_store()` in `passobj-attributes.c` invokes `set_new_password()`. The function locks `wmi_priv.mutex`, builds all buffers, calls firmware, and on success copies the new value into the selected current password cache. On specific failures it logs missing admin password or invalid password hints.

State and persistence: password changes persist in firmware. Current Admin/System passwords are cached in plaintext global buffers, with the selected buffer updated after successful password change. The WMI device pointer is global and mutex-protected.

Dependencies and integration: WMI, sysman string/security buffer helpers, firmware-attributes class uevents, and password-object sysfs handlers.

Risks: the command uses the current admin password as the security area even when changing System password, which matches the intended firmware contract but must be documented. Plaintext buffers remain in memory. Output object type mismatches become generic `-EIO`. Test signals include Admin and System password changes, wrong-current-password failures, missing-admin-password firmware responses, uevent delivery for `is_enabled`, unknown password type, and concurrent password writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/passwordattr-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/string-attributes.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/string-attributes.c

Purpose: implements Dell BIOS string attributes for sysman firmware-attributes.

Important APIs/functions: `alloc_str_data()` allocates cached string metadata. `populate_str_data()` validates package fields, caches name/display/default/modifier plus min/max length, and creates the sysfs group. `current_value_show()` re-queries firmware for current string value. `validate_str_input()` enforces cached minimum and maximum string lengths. Generated metadata show handlers expose language code, display name, default value, modifier, min/max length, and type.

Control flow: `sysman.c` enumerates string WMI instances and creates one kobject per attribute. Static metadata reads come from `wmi_priv.str_data`; current value reads fetch WMI. Writes pass through the generic generated store function, which strips newline, validates length, and calls `set_attribute()`.

State and persistence: cached metadata persists for the module lifetime. Successful writes persist to BIOS firmware and set global pending-change state via the BIOS attributes interface. Current values are intentionally not cached.

Dependencies and integration: sysman WMI enumeration, sysfs groups, BIOS attributes setter, shared `MAX_BUFF` bounds, and UTF-16 conversion in `set_attribute()`.

Risks: validation counts bytes from `strlen()` rather than user-visible characters, while the setter later converts to UTF-16, so non-ASCII length semantics can differ. Max-length metadata extraction follows the same ACPI union casting pattern as integer attributes. Test signals include min/max boundary writes, empty strings when permitted, malformed WMI packages, long firmware-provided metadata, non-ASCII input if supported by policy, and firmware write failures due to password requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/string-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/sysman.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/sysman.c

Purpose: top-level Dell WMI System Management driver. It creates `/sys/class/firmware-attributes/dell-wmi-sysman`, enumerates BIOS attribute WMI instances, builds per-attribute sysfs kobjects, and coordinates reset/pending-reboot/global state.

Important APIs/functions: global `wmi_priv` holds all shared state. `populate_string_buffer()`, `calculate_string_buffer()`, `calculate_security_buffer()`, and `populate_security_buffer()` build firmware command buffers. `map_wmi_error()` maps Dell firmware status to errno. `reset_bios_show/store()` and `pending_reboot_show()` implement top-level sysfs attributes. `get_wmiobj_pointer()` and `get_instance_count()` enumerate WMI blocks. `init_bios_attributes()` is the core enumerator: validates ACPI packages, skips empty/duplicate names, creates kobjects, and delegates population by type. `release_attributes_data()` tears down sysfs and metadata.

Control flow: module init verifies a Dell/Alienware OEM string, registers BIOS attribute and password WMI interface drivers, creates the firmware-attributes class device and `attributes`/`authentication` ksets, adds top-level files, then initializes enum, integer, string, and password-object attributes in order. Exit reverses the process.

State and persistence: global metadata arrays, password buffers, ksets, WMI device pointers, and `pending_changes` persist while the module is loaded. Firmware attribute changes and BIOS reset operations persist in BIOS and may require reboot; `pending_reboot` exposes the module's pending-change flag.

Dependencies and integration: WMI, DMI OEM-string detection, sysfs/kobject/kset APIs, NLS UTF-8 to UTF-16 conversion, firmware-attributes class, and the per-type attribute objects.

Risks: initialization has many partial-failure paths; cleanup must match created ksets/files. Duplicate attribute names are skipped. Password/security data is kept globally. Test signals include non-Dell rejection, missing WMI set/pass interfaces, malformed packages by type, duplicate names, reset modes, pending-reboot uevents, and complete module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/sysman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell_rbu.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell_rbu.c

Purpose: legacy Dell Remote BIOS Update driver. It creates a platform device with binary sysfs attributes that let userspace stage a BIOS image in memory for firmware to consume after reboot. It supports monolithic (`mono`) and packetized (`packet`) modes, plus `init` to recreate firmware loader entries.

Important APIs/types/functions: global `rbu_data` tracks mono buffer, packet list, sizes, read cursor, and spinlock. `struct packet_data` represents one packet with allocated pages. `img_update_realloc()` allocates contiguous DMA32 pages for mono images. `packetize_data()` and `create_packet()` allocate packet pages above `allocation_floor`, mark them uncached with `set_memory_uc()`, copy image chunks, and append to `packet_data_list`. `packet_read_list()` and `read_packet_data()` expose staged packet data through `data` bin attribute. `callbackfn_rbu()` receives firmware from `request_firmware_nowait()`.

Control flow: module init registers platform device `dell_rbu` and sysfs binary attributes `data`, `image_type`, and `packet_size`. Users set image type and packet size, then trigger firmware loading externally. Firmware callback fills mono or packet storage. Reads expose the staged image. Changing image type or packet size frees previous allocations.

State and persistence: all staged BIOS image bytes live in kernel memory until freed, overwritten, or module exit. Cleanup zeroes image/packet memory before freeing and restores packet memory writeback caching. Firmware update itself depends on external userspace setting CMOS/reboot state, not this driver alone.

Dependencies and integration: platform device/sysfs binary attributes, firmware loader, page allocator, DMA32 allocation, spinlocks, list API, `set_memory_uc/wb`, and Dell BIOS update conventions.

Risks: large allocations can fail or fragment memory. Packet allocation loops can allocate temporary below-floor pages. `image_type_write()` modifies the sysfs write buffer in place and uses substring matching. Some paths return raw or confusing errors. Test signals include mono and packet staging/readback, packet size validation, allocation-floor behavior, memory zeroing on mode switch/exit, firmware callback with zero size, and concurrent sysfs access under spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell_rbu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dual_accel_detect.h -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/dual_accel_detect.h

Purpose: header-only helper for platform x86 drivers to detect convertible systems with two accelerometers. Such systems often report unreliable firmware tablet-mode events unless Windows-specific hinge-angle methods are called, so drivers can suppress broken `SW_TABLET_MODE` reporting and let userspace infer posture from accelerometers.

Important APIs/functions: `dual_accel_detect_bosc0200()` finds the first ACPI `BOSC0200` device and uses `i2c_acpi_client_count()` to confirm it models two I2C clients. `dual_accel_detect()` returns true when either `KIOX010A` plus `KIOX020A`, `DUAL250E`, or the two-client `BOSC0200` pattern is present.

Control flow: consuming drivers call `dual_accel_detect()` during probe or quirk setup. The helper performs ACPI presence checks and, for BOSC0200, balances the ACPI device reference with `acpi_dev_put()`.

State and persistence: none. It performs live ACPI namespace/I2C enumeration checks and returns a boolean.

Dependencies and integration: ACPI device matching and I2C ACPI client counting. It is included directly in drivers, so functions are `static` and compiled into each consumer.

Risks: detection is heuristic and may miss new dual-accelerometer IDs or falsely identify systems where tablet-mode firmware is still valid. Since this is a header with function bodies, changes affect all include sites. Test signals include ACPI namespace fixtures or hardware with Kionix pair, DUAL250E, BOSC0200 with one client, BOSC0200 with two clients, and no accelerometer IDs. Consumers should test that tablet-mode input is disabled only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/dual_accel_detect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-laptop.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-laptop.c

Purpose: legacy ASUS Eee PC ACPI extras driver for HID `ASUS010`. It exposes hotkeys, vendor backlight, sysfs control methods, hwmon fan controls, touchpad LED, rfkill devices, and optional WLAN PCI hotplug.

Important APIs/types/functions: `struct eeepc_laptop` stores ACPI handle, supported control-method bitmask, platform/backlight/input/rfkill objects, hotplug slot, LED workqueue, and event counters. `get_acpi()`/`set_acpi()` call model-specific ACPI methods from `cm_getv`/`cm_setv`. Sysfs helpers expose camera, card reader, display switch, CPU frequency control, and cpufv disabled state. EC fan helpers read/write fan PWM/RPM/control registers. Backlight ops read/write `PBLG/PBLS`. Input uses `eeepc_keymap`. Rfkill setup creates WLAN/Bluetooth/WWAN/WiMAX rfkill devices and can rescan/remove PCI WLAN devices.

Control flow: module registers a generic platform PM driver and the ACPI platform driver. Probe allocates state, applies DMI quirks, calls `INIT` and `CMSG`, creates the fixed `eeepc` platform device, optionally registers vendor backlight, input, hwmon, LED, rfkill/hotplug, and ACPI notify handler. Notify sends netlink events, handles brightness specially, and reports sparse keymap events.

State and persistence: ACPI control methods change firmware device state. Driver state includes event counters, rfkill state, cpufv/hotplug DMI flags, LED workqueue state, and platform sysfs exposure. Resume restores rfkill/hotplug and LED-related WLAN state.

Dependencies and integration: ACPI video, ACPI EC, input sparse-keymap, backlight, hwmon, rfkill, PCI hotplug, DMI, LED class, platform device/driver APIs.

Risks: broad hardware control in one driver creates complex unwind ordering. WLAN hotplug has DMI blacklists due to model-specific breakage. Direct EC fan access lacks detailed error handling. Test signals include probe on ASUS010 systems, DMI quirk paths, brightness notifications with/without ACPI video, sysfs controls, rfkill toggles, PCI hotplug consistency checks, fan hwmon values, suspend/thaw/restore, and module unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-wmi.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-wmi.c

Purpose: Eee PC WMI hotkey driver built on the shared `asus-wmi` framework. It covers WMI event GUID `ABBC0F72-8EA1-11D1-00A0-C90629100000` and avoids binding when the legacy ASUS010 ATKD ACPI device is also active.

Important APIs/functions: `eeepc_wmi_keymap` maps ASUS WMI brightness, volume, WLAN, touchpad, camera, display, and special keys. DMI quirks configure wireless hotplug and ET2012 backlight behavior through `struct quirk_entry`. `et2012_quirks()` inspects OEM strings to choose panel-brightness quirks. `eeepc_wmi_key_filter()` converts T101MT Home press/release scancodes into non-autoreleased key transitions and suppresses hold events. `eeepc_wmi_probe()` rejects systems with legacy ATKD present. `eeepc_wmi_quirks()` initializes the asus-wmi driver quirk pointer and panel power defaults.

Control flow: module init calls `asus_wmi_register_driver()` with a populated `struct asus_wmi_driver`; exit unregisters it. The asus-wmi core owns platform device creation, input registration, WMI notification dispatch, and most hardware operations, while this file supplies keymap/filter/probe/quirk callbacks.

State and persistence: only static quirk pointers and module parameter `hotplug_wireless` are stored here. Firmware state is managed by asus-wmi.

Dependencies and integration: `asus-wmi.h`, DMI/OEM string matching, ACPI legacy-device detection, backlight constants, input sparse-keymap through the asus-wmi core.

Risks: quirk selection mutates a global `quirks` pointer and then writes fields before registration; shared static quirk objects must not be unexpectedly reused across devices. Legacy ATKD detection is important to avoid duplicate hotkey handling. Test signals include WMI-only systems, ATKD conflict path, ET2012 OEM string variants, Home press/hold/release behavior, `hotplug_wireless` parameter, and keymap coverage through asus-wmi events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/eeepc-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.c

Purpose: defines and registers a shared kernel class named `firmware-attributes`, used by platform firmware-setting drivers such as Dell WMI sysman to publish firmware configuration attributes under a common sysfs class.

Important APIs/functions: `const struct class firmware_attributes_class` contains only `.name = "firmware-attributes"` and is exported with `EXPORT_SYMBOL_GPL()`. `fw_attributes_class_init()` calls `class_register()`. `fw_attributes_class_exit()` calls `class_unregister()`.

Control flow: module init registers the class before consumers create devices under it. Consumers call `device_create(&firmware_attributes_class, ...)` and then build their own ksets/attributes below the class device. Exit unregisters the class.

State and persistence: the class object is global static state for the module lifetime. It does not store firmware attributes itself; all per-vendor data is owned by consumers. Sysfs devices disappear when consumers unregister and when the class unregisters.

Dependencies and integration: Linux device class core and module infrastructure. Export is GPL-only, so consumer modules must be GPL-compatible.

Risks: consumers must ensure class lifetime through Kconfig/module dependencies; creating devices before class registration would fail. The class has no dev_groups or release behavior, so consumers must manage their own devices and cleanup. Test signals include class presence in sysfs, consumer device creation/removal, module build as built-in or module, symbol resolution for consumers, and unload ordering when no consumers remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.h -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.h

Purpose: declares the shared `firmware_attributes_class` exported by `firmware_attributes_class.c`.

Important APIs/types: includes `<linux/device/class.h>` and declares `extern const struct class firmware_attributes_class;`. The class name and registration are implemented in the companion C file.

Control flow and integration: platform drivers include this header when they need to create a device in `/sys/class/firmware-attributes`. For example, Dell sysman calls `device_create(&firmware_attributes_class, ...)` and then creates driver-specific ksets under that class device.

State and persistence: no state in the header. The declared class is global runtime state owned by the class helper module.

Dependencies: depends on the Linux device class type definition and correct linkage against the helper object/module.

Risks and test signals: this header is intentionally tiny, so risk is mostly build/configuration coupling. Consumers need Kconfig dependencies or selects to ensure the class symbol exists. Build tests should cover each consumer as built-in and module where supported. Runtime tests should verify that consumer class devices appear under the expected class and are removed cleanly when the consumer unloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/firmware_attributes_class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-laptop.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-laptop.c

Purpose: Fujitsu Lifebook platform driver for ACPI brightness device `FUJ02B1` and hotkey/feature device `FUJ02E3`. It supports vendor backlight, input hotkeys, LED controls, platform status attributes, and battery charge-control extension.

Important APIs/types/functions: `call_fext_func()` evaluates the Fujitsu `FUNC` ACPI method with four integer arguments. `struct fujitsu_bl` owns brightness input/backlight state. `struct fujitsu_laptop` owns hotkey input, platform device, FIFO, flags, and battery charge-control status. Backlight code uses `GBLL/RBLL/SBLL/SBL2` plus `FUNC_BACKLIGHT` power control. Hotkey code reads `FUNC_BUTTONS` GIRB values and `FUNC_FLAGS` status/soft-key bits. LED classdevs implement logolamp, keyboard lamps, radio LED, and eco LED through `FUNC_LEDS` or `FUNC_FLAGS`. Battery hook exposes `charge_control_end_threshold`.

Control flow: init registers the brightness driver, platform status driver, and laptop driver. FUJ02B1 probe registers brightness input/backlight and notify handler when vendor backlight is selected. FUJ02E3 probe initializes FIFO, discards stale button entries, reads supported flags, syncs backlight power, registers input/LEDs/platform sysfs, installs notify handler, and optionally registers battery hook. Notify drains button events, tracks press/release using FIFO, updates flags, and reports soft keys.

State and persistence: brightness level and backlight power affect firmware. LED settings and charge thresholds persist according to firmware behavior. Runtime state includes FIFO of pressed scancodes, supported/current flags, global `fext`, and global `fujitsu_bl`.

Dependencies and integration: ACPI platform devices, input sparse-keymap, backlight, LED class, platform sysfs, kfifo, battery hook/power supply, DMI keymap overrides, ACPI video.

Risks: globals assume at most one FUJ02E3/FUJ02B1 pairing. FIFO overflow or missed release events can leave keys logically pressed. Charge-control validation clamps low values to 50. Test signals include DMI keymaps, brightness notifications, soft keys, LED set/get, lid/dock/radio attributes, battery threshold read/write, unsupported FUNC responses, and multi-device warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-tablet.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-tablet.c

Purpose: supports older Fujitsu tablet PC hardware exposing ACPI IDs `FUJ02BD` or `FUJ02BF`. It uses ACPI resources to obtain an I/O port range and IRQ, then reports tablet buttons plus dock/tablet-mode switches through the input subsystem.

Important APIs/types/functions: global `fujitsu` holds input device, DMI-selected `struct fujitsu_config`, previous keymask, IRQ, and I/O range. Low-level helpers `fujitsu_ack()`, `fujitsu_status()`, and `fujitsu_read_register()` access controller ports. `fujitsu_send_state()` reads register `0xdd` and reports `SW_DOCK` and `SW_TABLET_MODE` with DMI quirks. `fujitsu_interrupt()` checks interrupt status, sends switch state, reads keymask registers `0xde/0xdf`, computes changed bits, emits MSC scan and key events, then acknowledges. DMI callbacks select keymaps and invert/force switch quirks.

Control flow: module init applies DMI keymap/quirk selection and registers the ACPI platform driver. Probe walks `_CRS` resources for IRQ and I/O, sets ACPI name/class, registers input, reserves I/O region, resets controller, and requests shared IRQ. Remove frees IRQ, releases I/O region, and unregisters input. Resume resets controller and resends state.

State and persistence: runtime state is global and single-device. `prev_keymask` tracks pressed buttons. Hardware state is read from I/O registers and acknowledged; no persistent firmware settings are changed.

Dependencies and integration: ACPI resource walking, raw port I/O, IRQ handling, DMI matching, input key/switch events, platform driver PM.

Risks: raw I/O and shared IRQ require exact resource parsing. The default catch-all DMI entry may apply generic Lifebook mapping to unknown systems. Switch-state quirks are model-sensitive. Test signals include resource parse failures, request-region conflicts, shared IRQ behavior, key press/release transitions, dock/tablet switch inversion, resume reset, and unknown hardware with fallback keymap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-tablet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/gigabyte-wmi.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/gigabyte-wmi.c

Purpose: exposes Gigabyte motherboard temperature sensors through hwmon using WMI GUID `DEADBEEF-2001-0000-00A0-C90629100000`.

Important APIs/functions: `enum gigabyte_wmi_commandtype` includes firmware information queries and the implemented `GIGABYTE_WMI_TEMPERATURE_QUERY`. `struct gigabyte_wmi_args` carries one `u32 arg1`, used as the sensor index. `gigabyte_wmi_perform_query()` wraps `wmidev_evaluate_method()`. `gigabyte_wmi_query_integer()` validates integer ACPI results. `gigabyte_wmi_temperature()` queries a sensor, treats zero as absent, and converts the signed 8-bit value to millidegrees Celsius. HWMON ops use `gigabyte_wmi_hwmon_read()` and `gigabyte_wmi_hwmon_is_visible()`.

Control flow: probe detects usable sensors by querying all six possible channels and setting `usable_sensors_mask`. If no sensors work, probe returns `-ENODEV`; otherwise it registers hwmon device `gigabyte_wmi` with six possible temp inputs and visibility controlled by the mask.

State and persistence: module-global `usable_sensors_mask` records channels usable for the probed device. Sensor values are read live from firmware; no settings are written or persisted.

Dependencies and integration: WMI device driver API, ACPI object parsing, hwmon channel-info macros, and module WMI device table.

Risks: `usable_sensors_mask` is global even though WMI driver infrastructure could theoretically probe multiple devices. Temperature is cast to `s8`, so firmware values outside signed 8-bit semantics would be misread. Zero temperature is treated as absent, which may hide a legitimate 0 C reading but is likely a firmware sentinel. Test signals include systems with no sensors, partial channel availability, negative temperatures, WMI ACPI type mismatch, repeated hwmon reads, and multi-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/gigabyte-wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/gpd-pocket-fan.c -->
## sources/distributed-fs/ceph-client/drivers/platform/x86/gpd-pocket-fan.c

Purpose: controls the GPD Pocket fan through two GPIO lines, using CPU thermal zones and AC-power status to choose a fan speed from 0 to 3.

Important APIs/types/functions: `struct gpd_pocket_fan_data` stores device, two thermal zones (`soc_dts0`, `soc_dts1`), two GPIO descriptors, delayed work, and last speed. Module parameters `temp_limits`, `hysteresis`, and `speed_on_ac` tune thresholds. `gpd_pocket_fan_worker()` reads both thermal zones, uses the maximum temperature, enforces minimum speed on AC power, applies hysteresis before lowering speed, kick-starts from off by briefly selecting max speed, sets GPIO outputs, and reschedules itself with a speed-dependent interval. PM callbacks stop work and set minimum speed on suspend, then force update on resume.

Control flow: ACPI platform probe validates module parameters, allocates state, creates autocancel delayed work, obtains thermal zones by name, gets two GPIOs, forces an immediate update, and stores driver data. The worker then runs continuously on `system_percpu_wq`.

State and persistence: fan speed is tracked only in `last_speed`; hardware GPIO state reflects the last selected speed. Module parameters are read-only at runtime. No firmware settings are persisted.

Dependencies and integration: ACPI platform matching for `FAN02501`, thermal zone API, GPIO descriptor API, power-supply `power_supply_is_system_supplied()`, delayed work, and PM sleep callbacks.

Risks: missing thermal zones defer probe; temperature read failures force max speed for safety. Threshold arrays are validated for range but not monotonic order. GPIO direction is set on every speed change. Test signals include invalid parameter normalization, AC vs battery minimum speed, hysteresis lowering, kick-start from off, thermal read failure, suspend/resume behavior, GPIO bit patterns for speeds 0..3, and probe deferral until thermal zones exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/gpd-pocket-fan.c -->
