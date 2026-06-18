# subset-b-003806 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-quirks.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-quirks.c

## Purpose

`hid-quirks.c` is the HID core quirk registry and lookup implementation. It combines static VID/PID tables, build-config-gated special-driver routing, ignore lists, mouse-interface ignore lists, and runtime module-parameter quirks into the bitmask returned to HID bus drivers. The file decides when a HID device should be ignored, when generic HID should defer to a specialized driver, and when device-specific parser/transport workarounds such as `HID_QUIRK_NOGET`, `HID_QUIRK_MULTI_INPUT`, `HID_QUIRK_ALWAYS_POLL`, or `HID_QUIRK_NO_INIT_REPORTS` should be enabled.

## Important APIs, Types, and Functions

- `hid_quirks[]`: alphabetically sorted static HID quirk table. Each row maps a bus/vendor/product match to a quirk bitmask in `driver_data`.
- `hid_have_special_driver[]`: compile-time conditional table of devices that should be routed to a specialized HID driver when that driver is enabled.
- `hid_ignore_list[]` and `hid_mouse_ignore_list[]`: static device tables for whole-device ignore and mouse-interface-only ignore behavior.
- `hid_ignore(struct hid_device *hdev)`: exported predicate used by HID transports to decide whether generic HID should bind at all.
- `struct quirks_list_struct`, `dquirks_list`, and `dquirks_lock`: runtime quirk list and serialization for module-parameter-provided overrides.
- `hid_modify_dquirk()`, `hid_exists_dquirk()`, `hid_remove_all_dquirks()`: dynamic quirk add/replace, lookup, and cleanup helpers.
- `hid_quirks_init(char **quirks_param, __u16 bus, int count)` and `hid_quirks_exit(__u16 bus)`: exported module lifecycle hooks for parsing `vendor:product:quirks` strings and removing bus-scoped dynamic entries.
- `hid_gets_squirk()` and `hid_lookup_quirk()`: static plus dynamic quirk resolution, with dynamic entries taking precedence.

## Control Flow

Normal lookup starts in `hid_lookup_quirk()`. It first handles special version-sensitive cases that bypass the table path: NCR USB devices always get `HID_QUIRK_NO_INIT_REPORTS`, and older Jabra Speak firmware revisions are ignored. It then locks `dquirks_lock`; if a dynamic quirk matches, its `driver_data` becomes the complete result, otherwise `hid_gets_squirk()` derives static bits from ignore tables, special-driver tables, the generic quirk table, and `hdev->initial_quirks`.

Ignore handling is separate. `hid_ignore()` first honors explicit `HID_QUIRK_NO_IGNORE` and `HID_QUIRK_IGNORE` bits already present on the device. It then evaluates hard-coded vendor/product/name/version ranges that cannot be represented cleanly in static tables, including Code Mercenaries IOWarrior, Logitech Harmony and AudioHub lookalike filtering, SoundGraph iMON ranges, Hanwang tablet ranges, Jess Yurex USBNONE, Velleman comedi devices, an Atmel V-USB radio, ELAN devices handled by elan-i2c, and Jieli devices distinguished by name and serial. It finally checks mouse-interface ignore and the static ignore table.

Runtime quirk setup in `hid_quirks_init()` parses strings as hex `vendor:product:quirks`, fills a `struct hid_device_id` with the caller-supplied bus, and calls `hid_modify_dquirk()`. Replacement builds a temporary `hid_device` and list item, searches for an existing matching item with `hid_match_one_id()`, replaces or appends under `dquirks_lock`, and frees the temporary device.

## State and Persistence Behavior

Static quirk tables are read-only for the kernel image lifetime. Dynamic quirks persist in `dquirks_list` until `hid_quirks_exit()` removes entries for a bus or `HID_BUS_ANY`. Dynamic entries are intentionally stronger than static quirks: if `hid_exists_dquirk()` returns a match, `hid_lookup_quirk()` does not OR in static bits. `hdev->initial_quirks` is preserved only through the static path.

## Dependencies and Integration Points

The file depends on HID matching APIs (`hid_match_id`, `hid_match_one_id`), Linux list/mutex/slab helpers, `hid-ids.h` VID/PID constants, and ELAN ACPI IDs from `linux/input/elan-i2c-ids.h`. Exported functions are consumed by HID transport modules and HID core initialization. Kconfig conditionals in `hid_have_special_driver[]` connect this file to many optional drivers such as Apple, Logitech, RMI, Retrode, Roccat, Sony, and multitouch-related drivers.

## Risks and Edge Cases

- Dynamic quirks replace static lookup rather than merging with it, so a module parameter can accidentally drop important static ignore or special-driver bits.
- `hid_modify_dquirk()` allocates `q_new` before knowing whether a replacement is needed; the ownership is correct, but future changes must keep the replacement/free path balanced.
- The static tables are long and manually sorted; duplicate or unsorted entries can hide maintenance errors.
- `hid_ignore()` contains name/serial string checks for reused USB IDs. Those are necessarily brittle and depend on transport-provided strings being initialized and NUL-terminated.
- The ELAN loop uses `strlen(elan_acpi_id[i].id)` as the sentinel; malformed table entries would affect matching.
- Version-specific bypasses in `hid_lookup_quirk()` return immediately and do not honor dynamic quirks.

## Test Signals

Useful signals include unit-style tests for static table matches, dynamic override precedence, malformed quirk parameter parsing, replacement of an existing dynamic quirk, bus-scoped dynamic cleanup, and explicit `NO_IGNORE`/`IGNORE` precedence. Integration coverage should confirm that devices in `hid_have_special_driver[]` get `HID_QUIRK_HAVE_SPECIAL_DRIVER` only when their Kconfig driver is enabled, ignored devices do not bind to generic HID, and mouse-ignore entries only affect USB mouse interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-rapoo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-rapoo.c

## Purpose

`hid-rapoo.c` adds a small companion input device for Rapoo 2.4 GHz receivers so side-button bits in a vendor-specific raw report are exposed as standard `KEY_BACK` and `KEY_FORWARD` events.

## Important APIs, Types, and Functions

- `rapoo_devices[]`: matches `USB_VENDOR_ID_RAPOO` / `USB_DEVICE_ID_RAPOO_2_4G_RECEIVER`.
- `rapoo_probe()`: parses and starts HID, then allocates/registers a managed input device for USB interface number 1.
- `rapoo_raw_event()`: intercepts report ID 1, reads `data[1]`, maps `0x08` to `KEY_BACK` and `0x10` to `KEY_FORWARD`, syncs the input device, and consumes the report.
- `RAPOO_BTN_BACK` and `RAPOO_BTN_FORWARD`: bit masks for the vendor report byte.

## Control Flow

Probe runs `hid_parse()` and `hid_hw_start()` for every matched receiver. For USB devices, only interface 1 gets the extra input device; other interfaces keep normal HID handling with no driver data. On the active interface, the driver creates an input device named `Rapoo 2.4G Wireless Mouse`, sets bus/vendor/product/version metadata, advertises `EV_KEY`, `KEY_BACK`, and `KEY_FORWARD`, registers it, and stores it as HID driver data.

Raw event processing is intentionally narrow. If no input device was installed, the report is ignored by this driver. If the report ID is 1 and the buffer is at least two bytes, the side-button bits are reported and the function returns 1 so generic HID does not process the same vendor report.

## State and Persistence Behavior

The only persistent state is the devm-managed `struct input_dev` stored in HID driver data. Button state is not cached; each qualifying raw report emits current key states and an input sync. Device teardown relies on devm cleanup and HID core removal.

## Dependencies and Integration Points

The driver integrates with HID parse/start, USB interface metadata, and the Linux input subsystem. It depends on `hid-ids.h` for Rapoo IDs and on input key definitions from `linux/input-event-codes.h`.

## Risks and Edge Cases

- `rapoo_probe()` returns success early for non-interface-1 USB interfaces after `hid_hw_start()`, so those interfaces still rely on HID core lifetime management without driver-private state.
- A failure after `hid_hw_start()` during input allocation or registration returns an error without an explicit `hid_hw_stop()` in this file.
- The raw event assumes `data[1]` semantics for all matched receiver variants.
- Returning 1 consumes report ID 1, which is correct for the side-button vendor report but would be risky if future devices reuse the ID for normal input.

## Test Signals

Test with the matched receiver should show a second input node only on USB interface 1, no duplicate generic events for the side buttons, correct press/release transitions for back/forward, and normal operation of non-side-button interfaces. Error-path testing should cover input allocation/registration failure after `hid_hw_start()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-rapoo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-razer.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-razer.c

## Purpose

`hid-razer.c` supports Razer BlackWidow gaming keyboard macro keys. It optionally remaps keyboard usages `0x68` through `0x6c` to Linux `KEY_MACRO1` through `KEY_MACRO5` and sends a feature report to the mouse-typed interface to enable those macro key reports.

## Important APIs, Types, and Functions

- `macro_key_remapping`: module parameter controlling whether the usage remapping is active.
- `blackwidow_init[]`: 91-byte feature-report payload used to enable macro key reporting.
- `razer_input_mapping()`: maps selected keyboard-page usages with `hid_map_usage_clear()`.
- `razer_probe()`: parses the report descriptor, sends `blackwidow_init` via `hid_hw_raw_request()` when `hdev->type == HID_TYPE_USBMOUSE`, then starts hardware.
- `razer_devices[]`: matches BlackWidow, BlackWidow Classic, and BlackWidow Ultimate USB IDs.

## Control Flow

During probe the driver parses HID first. If the current interface is the BlackWidow interface identified as `HID_TYPE_USBMOUSE`, it duplicates the static initialization payload and sends it as feature report ID 0 with `HID_REQ_SET_REPORT`. A short or failed transfer is logged, but probe continues to `hid_hw_start()` so the device remains usable. During input mapping, when `macro_key_remapping` is enabled, only keyboard usage-page entries in the `0x68`-`0x6c` range are consumed and remapped; all other usages return 0 for normal HID mapping.

## State and Persistence Behavior

The module parameter is global mutable state. No per-device allocation persists after probe. The device-level macro enablement is pushed into keyboard firmware state through the feature report and is not retried after resume in this file.

## Dependencies and Integration Points

This driver uses HID input mapping, raw feature requests, USB-facing HID report semantics, and Linux input macro keycodes. It depends on Razer VID/PID constants from `hid-ids.h`.

## Risks and Edge Cases

- The feature report is only sent on probe for `HID_TYPE_USBMOUSE`; suspend/resume or firmware reset paths may require reinitialization but no PM hooks are present.
- A short successful transfer is logged but does not fail probe; this favors usability but can hide disabled macro keys.
- The usage-page test uses a bitwise expression; future usage encodings should be checked against HID helper idioms before extending it.
- Disabling `macro_key_remapping` leaves any enabled macro reports to generic mapping, which may or may not be meaningful.

## Test Signals

Tests should verify that the macro keys generate `KEY_MACRO1`-`KEY_MACRO5` when remapping is enabled, fall back to generic handling when disabled, and that the 91-byte feature report is sent only to the intended interface. Resume testing should confirm whether macro keys remain enabled after power management transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-razer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-redragon.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-redragon.c

## Purpose

`hid-redragon.c` fixes a malformed Redragon Asura keyboard report descriptor. The keyboard advertises one input item as array data at descriptor bytes 100-101, but the generated key data requires variable input semantics.

## Important APIs, Types, and Functions

- `redragon_report_fixup()`: descriptor fixup hook. If the descriptor is at least 102 bytes and bytes 100-101 are `0x81, 0x00`, it rewrites byte 101 to `0x02`.
- `redragon_devices[]`: matches the Redragon Asura under the Jess vendor ID.
- `redragon_driver`: HID driver with only `.report_fixup` and the ID table.

## Control Flow

HID core invokes `report_fixup` before parsing the descriptor. The function verifies both size and expected byte pattern, logs a device info message when applying the fix, mutates the descriptor in place, and returns the descriptor pointer. No probe override is needed; normal HID core parse/start behavior handles the device after the fixup.

## State and Persistence Behavior

No runtime state is stored. The only mutation is the in-memory report descriptor passed by HID core for the current device instance.

## Dependencies and Integration Points

The driver integrates with HID descriptor parsing through the report-fixup callback. It depends on `hid-ids.h` for the Jess/Redragon IDs and kernel HID module registration.

## Risks and Edge Cases

- The fix is byte-offset-specific. If a firmware variant shifts the item while keeping the same USB ID, the condition will not match.
- If another device with the same ID has valid bytes at that offset, it will be left unchanged because both bytes must match the known malformed pattern.
- The code does not validate surrounding descriptor structure, only the local bytes.

## Test Signals

Descriptor-level tests should feed the known malformed descriptor and confirm byte 101 changes from `0x00` to `0x02`, while shorter or already-correct descriptors are unchanged. Device testing should confirm that key events parse as variable key bits and no parser warnings remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-redragon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-retrode.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-retrode.c

## Purpose

`hid-retrode.c` improves Retrode 2 controller adapter presentation. It forces multi-input splitting and assigns useful names to the input devices for SNES mouse, SNES/N64 ports, and Mega Drive ports based on HID report IDs.

## Important APIs, Types, and Functions

- `retrode_probe()`: sets `HID_QUIRK_MULTI_INPUT`, parses HID, and starts hardware.
- `retrode_input_configured()`: names each `hid_input` according to `hi->report->field[0]->report->id`.
- `retrode_devices[]`: matches `USB_VENDOR_ID_FUTURE_TECHNOLOGY` / `USB_DEVICE_ID_RETRODE2`.
- `CONTROLLER_NAME_BASE`: base string for generated input names.

## Control Flow

Probe sets the multi-input quirk before parsing so HID creates separate input devices for different report IDs. After input devices are configured, the callback inspects the first field's report ID: 0 becomes `Retrode SNES Mouse`, 1 and 2 become `Retrode SNES / N64 #1/#2`, 3 and 4 become `Retrode Mega Drive #1/#2`, and unknown IDs log an error and receive an `Unknown` suffix. Names are allocated with `devm_kasprintf()` and assigned directly to `hi->input->name`.

## State and Persistence Behavior

No private driver state is kept. The only persistent per-device data is devm-managed input-name memory tied to the HID device lifetime and the quirk bit set on the HID device before parse.

## Dependencies and Integration Points

The driver relies on HID multi-input behavior, input device configuration callbacks, and Retrode USB IDs from `hid-ids.h`.

## Risks and Edge Cases

- `retrode_input_configured()` assumes `hi->report->field[0]` is present; malformed descriptors with no fields could crash.
- Unknown report IDs still create input devices, but their names lose port specificity.
- The quirk must be set before `hid_parse()`; moving it later would break input splitting.

## Test Signals

Tests should verify that report IDs 0-4 produce distinct input devices with the expected names, unknown report IDs log an error but still allocate a name, and the SNES mouse path is unaffected by the multi-input quirk. Descriptor fuzzing should cover absent fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-retrode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-rmi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-rmi.c

## Purpose

`hid-rmi.c` implements a HID transport for Synaptics RMI4 devices. It detects HID reports that expose RMI register access, registers an `rmi_transport_dev` with the RMI core, converts HID output/input reports into RMI read/write block operations, and turns HID attention reports into an IRQ-like event path for the RMI function drivers.

## Important APIs, Types, and Functions

- `struct rmi_data`: per-device state for page selection, RMI transport, read wait queue, report buffers, flags, reset work, HID device pointer, device capability flags, and IRQ domain/mapping.
- `rmi_hid_read_block()` and `rmi_hid_write_block()`: RMI transport operations that implement paged register reads and writes using HID reports.
- `rmi_set_page()` and `rmi_set_mode()`: helper operations for RMI page register writes and feature-report mode selection.
- `rmi_raw_event()`, `rmi_read_data_event()`, and `rmi_input_event()`: dispatch incoming HID reports to read-completion or attention handling.
- `rmi_event()`: suppresses generic mouse events from RMI devices and schedules reset-to-RMI-mode work when mouse-emulation reports appear.
- `rmi_input_configured()` and `rmi_input_mapping()`: open HID I/O, switch to attention mode, set page zero, register the RMI transport, and hide normal HID usages for RMI devices.
- `rmi_setup_irq_domain()`: creates a one-entry IRQ domain and maps a virtual IRQ for RMI core attention delivery.
- `rmi_probe()` and `rmi_remove()`: parse/start the HID device, detect RMI report IDs, allocate buffers, configure transport data, and unregister transport on removal.

## Control Flow

Probe allocates `rmi_data`, sets `HID_QUIRK_NO_INIT_REPORTS` and `HID_QUIRK_NO_INPUT_SYNC`, parses reports, and uses `rmi_check_valid_report_id()` to determine whether the device has the RMI feature, attention input, and write output reports. If the reports are missing, probe falls through to `hid_hw_start()` and the device behaves as ordinary HID. If present, it marks `RMI_DEVICE`, allocates a combined output/input buffer, initializes the wait queue and page mutex, creates an IRQ domain, fills `xport` with HID operations and platform data, then starts HID.

After HID input configuration, `rmi_input_configured()` opens HID hardware, starts device I/O, sets attention-report mode, sets RMI page 0, registers the RMI transport, sets `RMI_STARTED`, stops I/O, and closes the device. RMI core calls back into `rmi_hid_read_block()` and `rmi_hid_write_block()` for register access. Reads serialize on `page_mutex`, switch pages when necessary, send a read-address output report, wait up to one second for `RMI_READ_DATA_PENDING`, copy chunks from `readReport`, retry up to five times on timeout, and clear pending flags on exit. Writes serialize similarly, switch pages, fill a write report, and send it.

Incoming raw events are filtered by report ID. Read data reports wake the wait queue if a read is pending. Attention reports call `rmi_set_attn_data()`, then invoke the mapped IRQ with interrupts locally disabled. Generic mouse/pointer events from RMI devices are suppressed; with physical buttons, button usages are allowed and zero X/Y events are filtered. A mouse-emulation event schedules reset work to put firmware back into RMI attention mode.

Suspend calls `rmi_driver_suspend()`. Resume opens the HID device, resets attention mode, calls `rmi_driver_resume()`, and closes HID. Removal clears `RMI_STARTED`, cancels reset work, unregisters the RMI transport, and stops HID hardware.

## State and Persistence Behavior

Persistent state includes the current RMI page, report buffer sizes and pointers, capability flags, pending-read flags, `RMI_STARTED`, the RMI transport registration, and the synthetic IRQ mapping. `page_mutex` serializes page switching and all register I/O. The wait queue and bit flags coordinate asynchronous HID input reports with synchronous RMI register reads. `rmi_hid_pdata` is a static platform-data template; probe mutates its GPIO-disable field for physical-button devices before copying it into `xport.pdata`.

## Dependencies and Integration Points

This file bridges HID core, the Linux RMI4 core (`linux/rmi.h`), input, PM, wait queues, workqueues, IRQ domains, and HID raw report I/O. Device IDs include specific Razer, Lenovo, Primax, Synaptics, and generic `HID_GROUP_RMI` matches. RMI core consumes the `hid_rmi_ops` transport callbacks and receives attention events through the synthetic IRQ.

## Risks and Edge Cases

- `rmi_hid_read_block()` copies `read_input_count` bytes but increments by the unbounded report count even when `min(read_input_count, bytes_needed)` copied less; malformed reports can desynchronize `bytes_read`.
- `rmi_hid_write_block()` copies `len` bytes into `writeReport[4]` without checking that `len + 4 <= output_report_size`.
- `rmi_check_sanity()` reads `data[valid_size - 1]` before checking `valid_size > 0`; a zero-size report would underflow.
- Static `rmi_hid_pdata` is mutated for physical-button devices and then reused for later devices, so `gpio_data.disable` can leak between probes.
- Attention handling calls into generic IRQ handling under `local_irq_save()`, so downstream RMI paths must be IRQ-context safe.
- Missing RMI reports cause a graceful fallback to generic HID, but partial or bogus reports can still allocate buffers and fail later.

## Test Signals

Coverage should include RMI-capable and non-RMI fallback devices, report-ID validation, page switching, successful and timed-out reads, multi-packet reads, oversized write rejection, attention IRQ delivery, physical-button filtering, mouse-emulation reset work, suspend/resume mode restoration, and removal while read/reset work is pending. Static analysis should flag the zero-size sanity check and write-buffer bounds assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-rmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.c

## Purpose

`hid-roccat-arvo.c` is the Roccat Arvo keyboard driver. It exposes Arvo mode-key, key-mask, profile, button, and info feature reports through a class-backed sysfs ABI and forwards three-byte special key reports to the Roccat character device.

## Important APIs, Types, and Functions

- `arvo_sysfs_show/set_mode_key()`, `arvo_sysfs_show/set_key_mask()`, and `arvo_sysfs_show/set_actual_profile()`: text sysfs attributes backed by Roccat feature reports.
- `arvo_sysfs_read()` and `arvo_sysfs_write()`: binary sysfs helpers enforcing full-size, offset-zero transfers.
- `bin_attr_button` and `bin_attr_info`: binary ABI endpoints for write-only button data and read-only info data.
- `arvo_init_specials()` and `arvo_remove_specials()`: allocate/free `struct arvo_device` and connect/disconnect the Roccat char device on the non-keyboard interface.
- `arvo_raw_event()` and `arvo_report_to_chrdev()`: convert special reports into `struct arvo_roccat_report`.

## Control Flow

Probe requires USB, parses HID, starts hardware, then calls `arvo_init_specials()`. The keyboard protocol interface is left to generic HID with no driver data; the other interface allocates state, reads the current profile, and attempts `roccat_connect()`. Sysfs operations retrieve the underlying USB interface through the class-device parent chain, lock `arvo_lock`, and use `roccat_common2_receive()` or `roccat_common2_send()`. Profile writes validate a 1-5 profile range and update the cached profile only after the feature-report write succeeds.

Raw events with size 3 are interpreted as `struct arvo_special_report`. The lower nibble becomes the macro button, the upper nibble selects press/release, and the cached profile is attached before the report is sent to the char device.

## State and Persistence Behavior

Persistent per-device state is `struct arvo_device`: char-device claim/minor, `arvo_lock`, and cached `actual_profile`. The selected profile is persistent in device firmware according to the header. Mode-key and key-mask state are read on demand rather than cached.

## Dependencies and Integration Points

The driver depends on HID/USB, the Roccat common feature-report helpers, `linux/hid-roccat.h` char-device APIs, and Arvo wire structs from `hid-roccat-arvo.h`. It registers a class named `arvo` to provide per-device sysfs files.

## Risks and Edge Cases

- Sysfs binary access requires exact full-size transfers; partial userspace reads/writes fail except EOF.
- `arvo_raw_event()` checks only size, not report ID or fixed marker bytes, before converting special reports.
- Char-device setup failure is tolerated, but code paths must continue to check `roccat_claimed`.
- Text writes convert `unsigned long` to one-byte fields without rejecting values beyond byte range for mode/key-mask.

## Test Signals

Test profile set/get, mode-key and key-mask report round trips, full-size binary ABI behavior, keyboard-interface bypass, non-keyboard char-device creation, special-report press/release translation, and remove paths with and without successful `roccat_connect()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.h

## Purpose

`hid-roccat-arvo.h` defines the Arvo keyboard wire-format structs, command IDs, special-report bit masks, Roccat char-device event format, and per-device state used by `hid-roccat-arvo.c`.

## Important APIs, Types, and Functions

- Packed feature-report structs: `arvo_mode_key`, `arvo_button`, `arvo_info`, `arvo_key_mask`, and `arvo_actual_profile`.
- `enum arvo_commands`: command/report IDs for mode key, button, info, key mask, and actual profile.
- `struct arvo_special_report`: three-byte interrupt report with action/button encoded in `event`.
- `ARVO_SPECIAL_REPORT_EVENT_MASK_ACTION` and `_BUTTON`: masks used to split event action and button index.
- `struct arvo_roccat_report`: user-visible char-device event containing profile, button, and action.
- `struct arvo_device`: cached driver state.

## Control Flow

The header has no executable control flow, but its command IDs and packed layouts are the contract for USB feature-report transactions. The C file fills `command` fields before writes and casts raw interrupt data to `arvo_special_report` before emitting `arvo_roccat_report`.

## State and Persistence Behavior

The `arvo_actual_profile` comment states profile selection is persistent in firmware. `struct arvo_device` caches the actual profile in memory and stores the char-device minor and mutex used by sysfs and event paths.

## Dependencies and Integration Points

The header depends only on Linux fixed-width integer types and mutex visibility from including C files. It is tightly coupled to Roccat common feature-report helpers and `linux/hid-roccat.h` event delivery.

## Risks and Edge Cases

The ABI is byte-size sensitive. Any padding, enum value change, or command mismatch would break userspace tools and device communication. Several fields are documented as unknown, so validation is necessarily limited.

## Test Signals

Build-time layout checks or static assertions for packed sizes would be valuable. Runtime tests should confirm command IDs and report sizes match the values used by sysfs binary attributes and raw-event translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.c

## Purpose

`hid-roccat-common.c` provides shared USB feature-report helpers for second-generation Roccat drivers. It implements receive/send wrappers, write-status polling, common device-state initialization, and reusable sysfs binary read/write helpers.

## Important APIs, Types, and Functions

- `roccat_common2_feature_report()`: converts an 8-bit report ID to HID feature report value `0x300 | report_id`.
- `roccat_common2_receive()` and `roccat_common2_send()`: exported full-size USB control GET_REPORT/SET_REPORT wrappers.
- `roccat_common2_receive_control_status()` and `roccat_common2_send_with_status()`: poll command `ROCCAT_COMMON_COMMAND_CONTROL` until OK, busy retry, or error.
- `roccat_common2_device_init_struct()`: initializes the common device mutex.
- `roccat_common2_sysfs_read()` and `roccat_common2_sysfs_write()`: exported binary sysfs helpers for drivers using `struct roccat_common2_device`.

## Control Flow

Receive allocates a temporary kernel buffer, issues a class/interface/IN `HID_REQ_GET_REPORT` control transfer, copies exactly `size` bytes to the caller buffer, frees the temporary buffer, and returns 0 only when the transfer length equals `size`. Send duplicates caller data, issues a class/interface/OUT `HID_REQ_SET_REPORT`, frees the duplicate, and similarly requires a full-length transfer.

Status writes first send the command payload, sleep 100 ms, then call `roccat_common2_receive_control_status()`. The status loop sleeps 50 ms before each poll, treats OK as success, busy as a 500 ms retry, invalid/critical values as `-EINVAL`, and unknown values as logged `-EINVAL`.

Common sysfs helpers derive the HID and USB device from the sysfs kobject parent chain, reject partial accesses except EOF reads, serialize through `roccat_common2_device.lock`, and perform either a receive or `send_with_status`.

## State and Persistence Behavior

The file owns no global mutable state. Per-device locking and char-device state live in `struct roccat_common2_device` defined by the header and allocated by device-specific drivers. USB transfers mutate device firmware state when used for writes.

## Dependencies and Integration Points

The helpers depend on USB control messaging, HID report request constants, Linux allocation and sleep APIs, and Roccat driver sysfs parent layout. They are exported for multiple Roccat modules including KonePure, Ryos, Savu, and similar simplified drivers.

## Risks and Edge Cases

- `roccat_common2_receive()` copies `size` bytes from the temporary buffer even when the USB transfer returns a short positive length; the allocated buffer is uninitialized beyond `len`.
- The status polling loop can run forever if firmware continuously reports busy.
- The sysfs helpers assume the kobject parent chain maps to a USB interface and common device state.
- Exact-size sysfs access is simple but unfriendly to partial reads used by some tooling.

## Test Signals

Test full, short, and negative USB control transfers; busy-to-OK and busy-forever control polling; invalid/critical status handling; exact-size sysfs read/write rejection; and concurrent sysfs access serialization through the common mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.h

## Purpose

`hid-roccat-common.h` declares the common Roccat command/status structures, exported feature-report helper APIs, common per-device state, and macros that generate binary sysfs attributes for simple Roccat devices.

## Important APIs, Types, and Functions

- `ROCCAT_COMMON_COMMAND_CONTROL`: shared command ID for control/status operations.
- `struct roccat_common2_control`: packed control report with command, value, and request bytes.
- Exported helpers: `roccat_common2_receive`, `roccat_common2_send`, `roccat_common2_send_with_status`, `roccat_common2_device_init_struct`, `roccat_common2_sysfs_read`, and `roccat_common2_sysfs_write`.
- `struct roccat_common2_device`: common char-device claim/minor plus a mutex.
- `ROCCAT_COMMON2_SYSFS_*` and `ROCCAT_COMMON2_BIN_ATTRIBUTE_*` macros: generate typed read/write callback wrappers and static `struct bin_attribute` definitions.

## Control Flow

The macros expand in device-specific drivers to call the common sysfs helpers with fixed command IDs and fixed byte sizes. Read-only, write-only, and read/write variants set file modes `0440`, `0220`, and `0660` respectively.

## State and Persistence Behavior

`struct roccat_common2_device` is embedded or allocated per HID interface. Its mutex is the serialization point for sysfs USB transactions. The header itself has no storage.

## Dependencies and Integration Points

The header depends on USB and Linux types. It is included by most Roccat driver C files and is the shared ABI for simplified drivers that do not need device-specific cached state.

## Risks and Edge Cases

Because the macros define static symbol names such as `bin_attr_<thingy>`, they are intended for one use per translation unit per attribute name. The generated binary attributes inherit the exact-size limitations of the common helpers. Any mismatch between macro `SIZE` values and firmware report sizes causes consistent `-EIO` or rejected userspace access.

## Test Signals

Compilation across all Roccat drivers is the main contract check. Runtime tests should verify each generated bin attribute has the expected mode, size, and command behavior for a representative simple driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.c

## Purpose

`hid-roccat-isku.c` supports Roccat Isku and Isku FX keyboards. It exposes keyboard configuration and macro storage through sysfs binary attributes, tracks the active profile, and forwards button/profile reports to the Roccat char device.

## Important APIs, Types, and Functions

- `isku_get_actual_profile()` and `isku_set_actual_profile()`: feature-report accessors for the active zero-based profile.
- `isku_sysfs_read()` and `isku_sysfs_write()`: Isku-specific binary sysfs helpers allowing reads/writes up to each attribute's real size.
- `ISKU_BIN_ATTR_*` macro uses: generate ABI files for macro, key groups, light, key mask, last set, talk, talkfx, control, reset, and info.
- `isku_init_specials()` and `isku_remove_specials()`: allocate state and connect char device only on `ISKU_USB_INTERFACE_PROTOCOL`.
- `isku_raw_event()`, `isku_keep_values_up_to_date()`, and `isku_report_to_chrdev()`: update cached profile and emit char-device reports.

## Control Flow

Probe parses and starts HID, then initializes only the interface with protocol 0. Initialization reads the active profile and tries to register a class-backed Roccat char device. Text sysfs profile writes validate profile <= 4, send the profile report with status polling, update the cached profile, and synthesize a profile event with one-based profile data for userspace. Binary sysfs reads/writes lock `isku_lock` and send exactly `count` bytes, rejecting nonzero offsets and counts larger than the declared maximum.

Raw events are ignored on non-Isku interfaces or before state allocation. Button reports with event `ISKU_REPORT_BUTTON_EVENT_PROFILE` update the cached zero-based profile from one-based report data. All button reports are forwarded with the cached profile converted to one-based numbering.

## State and Persistence Behavior

`struct isku_device` stores char-device state, a mutex, and cached `actual_profile`. Most configuration is persisted in device firmware and read/written on demand through sysfs. The cached profile is updated from both sysfs writes and interrupt reports.

## Dependencies and Integration Points

The driver depends on Roccat common feature-report helpers, Isku layout constants from `hid-roccat-isku.h`, class-backed sysfs groups, and `linux/hid-roccat.h` for event forwarding.

## Risks and Edge Cases

- Binary sysfs helpers permit short writes/reads up to the declared size, which differs from the stricter common helper pattern and may allow partial firmware payloads.
- `roccat_report_event()` is called after sysfs profile writes without checking `roccat_claimed`; if char-device registration failed, the stored minor may be invalid.
- Raw-event data is cast without checking the report size.
- Profile numbering mixes zero-based firmware state with one-based userspace/event data.

## Test Signals

Tests should cover profile set/get, char-device registration failure, partial binary payload behavior, protocol-interface gating, profile-change interrupt reports, and event payload numbering. Hardware tests should verify large macro payload transfers and light/key group writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.h

## Purpose

`hid-roccat-isku.h` defines the Isku report sizes, command IDs, profile report layout, interrupt button report format, char-device event layout, and per-device state used by the Isku driver.

## Important APIs, Types, and Functions

- Size constants such as `ISKU_SIZE_MACRO`, `ISKU_SIZE_KEYS_EASYZONE`, and `ISKU_SIZE_LIGHT` define sysfs binary ABI lengths.
- `ISKU_USB_INTERFACE_PROTOCOL` selects the keyboard interface handled by the driver.
- `struct isku_actual_profile`: three-byte feature report for active profile.
- `enum isku_commands`: command IDs for key groups, macros, info, light, reset, talk, and firmware operations.
- `struct isku_report_button`, `ISKU_REPORT_NUMBER_BUTTON`, and `ISKU_REPORT_BUTTON_EVENT_PROFILE`: interrupt-report contract.
- `struct isku_roccat_report` and `struct isku_device`: event ABI and cached driver state.

## Control Flow

The C file's generated sysfs callbacks are parameterized by the sizes and command IDs in this header. Raw event handling casts button reports to `struct isku_report_button` and emits `struct isku_roccat_report`.

## State and Persistence Behavior

The header defines only layouts. `actual_profile` is cached in `struct isku_device`, while all key/macro/light data is device firmware state accessed through packed command payloads.

## Dependencies and Integration Points

It depends on fixed-width Linux types and is consumed by `hid-roccat-isku.c`. The command constants are also part of the implicit userspace ABI because bin attribute sizes and meanings are stable.

## Risks and Edge Cases

Changing any size constant or packed layout breaks both firmware communication and userspace tools. Firmware-write command IDs are declared but not used in this C file, so future update paths need careful validation.

## Test Signals

Layout-size checks and sysfs attribute size verification should cover each constant. Event tests should verify profile report parsing and one-based profile publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.c

## Purpose

`hid-roccat-kone.c` supports the original Roccat Kone mouse. It mirrors all five profile payloads and settings in memory, exposes them through sysfs, handles firmware write confirmation and checksum updates, manages TCU calibration and startup profile changes, and forwards special mouse events through the Roccat char device.

## Important APIs, Types, and Functions

- `kone_receive()` and `kone_send()`: Kone-specific USB control transfer wrappers using 16-bit command values rather than the common `0x300 | report_id` helper.
- `kone_get_profile()`, `kone_set_profile()`, `kone_get_settings()`, `kone_set_settings()`, `kone_get_weight()`, and `kone_get_firmware_version()`: device data accessors.
- `kone_check_write()`: polls `kone_command_confirm_write` until success or error after writes.
- `kone_set_settings_checksum()`: recomputes the settings byte-sum checksum.
- Sysfs callbacks for `settings`, `profile1`-`profile5`, `actual_profile`, `actual_dpi`, `weight`, `firmware_version`, `tcu`, and `startup_profile`.
- `kone_init_kone_device_struct()`: reads all profiles, settings, and firmware version during initialization.
- `kone_raw_event()`, `kone_keep_values_up_to_date()`, and `kone_report_to_chrdev()`: filter repeated firmware events, update cached DPI/profile, and emit userspace reports.

## Control Flow

Probe requires USB, parses HID, starts hardware, and initializes only the mouse protocol interface. Initialization reads the five profiles, settings, firmware version, computes the active profile/DPI from the startup profile, and attempts char-device registration.

Sysfs profile and settings reads serve from the cached mirror and allow partial reads. Writes require full object payloads at offset zero. Settings writes validate startup profile, write to the device, replace the cached settings, activate the new startup profile, and emit a profile switch event if it changed. Profile writes avoid device I/O when the payload matches the cached profile. `startup_profile` text writes update the cached settings, recompute checksum, write settings, activate the profile, and emit a report. `tcu` writes run a multi-step calibration sequence with sleeps, reread settings, optionally update the TCU state and checksum, and reactivate the startup profile.

Raw event handling processes 12-byte `struct kone_mouse_event` reports. It suppresses repeated tilt/special-button data introduced by firmware 1.38 by comparing the `wipe` group with the last event. Profile and DPI switch/OSD events update cached state. Relevant profile, DPI, macro, and multimedia events are forwarded to the Roccat char device.

## State and Persistence Behavior

`struct kone_device` caches active profile/DPI, the last mouse event, all five profiles, settings, firmware version, char-device state, and a mutex. Firmware stores profiles/settings persistently; the driver assumes cached values remain valid unless a write or TCU calibration changes them. Weight is read on demand because hardware can change without notification.

## Dependencies and Integration Points

The driver uses HID/USB control transfers, Roccat char-device APIs, class-backed sysfs groups, Kone wire structs from `hid-roccat-kone.h`, and Linux sleep/allocation helpers. It differs from newer Roccat drivers by not using `roccat_common2_*` for core Kone commands.

## Risks and Edge Cases

- `kone_get_profile()` and `kone_set_profile()` use unusual USB requests (`USB_REQ_CLEAR_FEATURE` and `USB_REQ_SET_CONFIGURATION`) for class/interface transfers; this is device-specific but fragile.
- The TCU path logs "couldn't read settings" on the normal success path after setting `retval = size`, because the label is reached unconditionally.
- `kone_tcu_command()` treats the positive byte count returned by `kone_send()` as success/failure directly; a full one-byte write returns 0 from `kone_send()`, but this relies on wrapper behavior.
- Cached profile indexing assumes event values are in range; malformed event values can index outside `profiles`.
- Char-device failure is tolerated, but manual profile-report calls need `roccat_claimed` checks in all paths.
- Full-object writes cast userspace buffers directly to packed structs, so validation is limited.

## Test Signals

Tests should cover initial mirror loading, full and partial sysfs reads, profile/settings no-op writes, checksum recomputation, startup profile switching, TCU activation/deactivation timing, write-confirm status values, raw-event duplicate suppression, out-of-range event handling, and char-device failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.h

## Purpose

`hid-roccat-kone.h` defines the original Kone firmware payloads, command IDs, mouse event format, Roccat event ABI, and cached device state.

## Important APIs, Types, and Functions

- Configuration structs: `kone_keystroke`, `kone_button_info`, `kone_light_info`, `kone_profile`, and `kone_settings`.
- Enumerations for button types, button numbers, keystroke actions, polling rates, mouse events, and command IDs.
- `struct kone_mouse_event`: 12-byte interrupt report with a `struct_group(wipe, ...)` region used for duplicate suppression.
- `struct kone_roccat_report`: three-byte userspace event with event, value, and macro key.
- `struct kone_device`: complete cached state for the driver.

## Control Flow

The C file reads and writes the packed structs as complete firmware payloads. Raw interrupt reports are cast to `kone_mouse_event`; event values select profile/DPI updates or userspace forwarding. Command enum values are passed directly as USB control values.

## State and Persistence Behavior

Profiles and settings represent persistent firmware state. `struct kone_device` mirrors those payloads in RAM and adds volatile active-profile/DPI, firmware version, and duplicate-suppression state.

## Dependencies and Integration Points

The header depends on Linux types and packed layout support. Its structs are exposed indirectly through binary sysfs files, so they are both firmware and userspace ABI.

## Risks and Edge Cases

The large packed profile layout is checksum-sensitive. Field comments document multiple firmware-version-dependent meanings, so validation must consider firmware version. `struct_group(wipe, ...)` is relied on by the duplicate suppression code and should not be rearranged casually.

## Test Signals

Layout-size checks for `kone_profile`, `kone_settings`, and `kone_mouse_event`; checksum tests; command-value tests; and event parsing tests should accompany any changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.c

## Purpose

`hid-roccat-koneplus.c` supports Roccat Kone[+] and Kone XTD mice. It exposes feature-report configuration through sysfs, controls profile selection for profile-specific reads, tracks the active profile, and forwards button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `koneplus_send_control()`: sends common control requests for profile settings/buttons with range validation and status polling.
- `koneplus_get_actual_profile()` and `koneplus_set_actual_profile()`: read/write the zero-based active profile.
- `koneplus_sysfs_read()` and `koneplus_sysfs_write()`: exact-size binary sysfs helpers using `roccat_common2_*`.
- Generated attributes for control, talk, macro, tcu image, info, sensor, tcu, profile settings, and profile buttons.
- `koneplus_sysfs_read_profilex_settings/buttons()`: select a profile through control then read the current profile payload.
- `koneplus_raw_event()`, `koneplus_keep_values_up_to_date()`, and `koneplus_report_to_chrdev()`: update active profile and forward report 3 events.

## Control Flow

Probe initializes only the USB mouse interface. It reads the current active profile, stores it, and connects the char device. Sysfs fixed attributes directly read or write their command payloads. Profile-specific read-only attributes first send a control request selecting profile 0-4 for settings or buttons, then read the shared profile payload command. Text profile writes validate profile <= 4, send the active-profile command with status polling, update cached state, and synthesize a one-based profile event.

Raw events on the mouse interface inspect button report number 3. Profile event type `0x20` updates cached `actual_profile` from one-based report data. Quicklaunch and timer release events are filtered out; other button report fields are copied into `struct koneplus_roccat_report` with the cached profile converted to one-based numbering.

## State and Persistence Behavior

Per-device state is minimal: zero-based `actual_profile`, char-device state, and a mutex. The driver does not cache full profile settings or button payloads; it reads them from firmware on demand. Active profile persists in device firmware when set.

## Dependencies and Integration Points

The driver depends on Roccat common feature-report helpers, `hid-roccat-koneplus.h` layouts, HID/USB mouse-interface selection, class-backed sysfs, and Roccat char-device event delivery.

## Risks and Edge Cases

- Firmware info reads ignore the return value of `roccat_common2_receive()` and may print uninitialized stack data on failure.
- `koneplus_sysfs_set_actual_profile()` reports to the char device without checking `roccat_claimed`.
- Raw-event size is not checked before casting to the button report struct.
- Profile selection is a two-step control/read sequence; concurrent sysfs accesses outside the same lock can select the wrong profile if not serialized. The profilex helpers call `koneplus_send_control()` before entering `koneplus_sysfs_read()`'s lock, so there is a race window.

## Test Signals

Tests should cover profile range validation, profile-specific read serialization, firmware-info failure handling, raw report translation/filtering, char-device unavailable paths, and exact-size sysfs behavior for large macro and TCU image transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.h

## Purpose

`hid-roccat-koneplus.h` defines Kone[+]/XTD report sizes, command IDs, profile-selection control request IDs, info/profile report layouts, button interrupt report format, userspace event payload, and per-device state.

## Important APIs, Types, and Functions

- `KONEPLUS_SIZE_*`: binary sysfs and firmware payload sizes.
- `enum koneplus_control_requests`: profile settings and buttons selection requests.
- `struct koneplus_actual_profile` and `struct koneplus_info`: small feature-report payloads.
- `enum koneplus_commands`: feature command IDs, including shared `0x0c` for TCU and TCU image.
- `struct koneplus_mouse_report_button` and button type/action enums: report 3 event contract.
- `struct koneplus_roccat_report` and `struct koneplus_device`: userspace event and cached state.

## Control Flow

The C file uses the size and command constants to generate sysfs accessors. Button reports are cast according to this header and converted to char-device events.

## State and Persistence Behavior

Only the active zero-based profile is cached in `struct koneplus_device`. Profile data, buttons, macros, sensor, TCU, and talk settings live in firmware and are accessed through fixed-size reports.

## Dependencies and Integration Points

This header is coupled to `hid-roccat-common.h` generated attributes, KonePlus firmware protocol, and userspace Roccat tooling that consumes the binary sysfs files.

## Risks and Edge Cases

Command `KONEPLUS_COMMAND_TCU` and `KONEPLUS_COMMAND_TCU_IMAGE` both use `0x0c`; the driver distinguishes read/write by payload size and attribute. Changing sizes or packed fields breaks userspace and firmware protocol.

## Test Signals

Verify binary attribute sizes, profile report range 0-4, button report parsing for all type enums, and the shared TCU command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-konepure.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-konepure.c

## Purpose

`hid-roccat-konepure.c` is a simplified common-helper driver for Roccat KonePure and KonePure Optical mice. It exposes common feature-report sysfs files and forwards special button reports directly to the Roccat char device.

## Important APIs, Types, and Functions

- `struct konepure_mouse_report_button`: eight-byte report 3 payload layout.
- `ROCCAT_COMMON2_BIN_ATTRIBUTE_*` declarations: generate sysfs ABI for actual profile, control, info, talk, macro, sensor, TCU, TCU image, profile settings, and profile buttons.
- `konepure_init_specials()` and `konepure_remove_specials()`: allocate a `roccat_common2_device` and connect/disconnect char device on mouse interfaces.
- `konepure_raw_event()`: forwards report-number-3 data to userspace without further translation.

## Control Flow

Probe parses and starts HID, then initializes only USB mouse protocol interfaces. The class `konepure` supplies bin attributes through the Roccat char-device class device. Common sysfs callbacks perform exact-size USB feature transfers and status polling for writes. Raw events on the mouse interface are ignored unless `data[0] == 3`; claimed char-device instances receive the raw report bytes.

## State and Persistence Behavior

The driver stores only `struct roccat_common2_device` state: char-device claim/minor and a lock. All profile, macro, sensor, and TCU state remains in firmware and is accessed on demand.

## Dependencies and Integration Points

It depends on `hid-roccat-common.h` macros and common helpers, HID/USB mouse-interface selection, and Roccat char-device APIs.

## Risks and Edge Cases

- `konepure_raw_event()` does not check report size before forwarding.
- The driver forwards raw report bytes in the firmware layout, so userspace must know the report format.
- Common-helper exact-size sysfs limitations and receive short-copy risk apply.

## Test Signals

Tests should verify each bin attribute mode/size, exact-size access behavior, char-device connection, report-3 forwarding, non-mouse-interface bypass, and removal with failed char-device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-konepure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.c

## Purpose

`hid-roccat-kovaplus.c` supports Roccat Kova[+] mice. It caches profile settings/buttons for five profiles, exposes feature-report sysfs files, tracks active profile/CPI/sensitivity, and forwards translated button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `kovaplus_send_control()` and `kovaplus_select_profile()`: select firmware profile payloads for subsequent reads.
- `kovaplus_get_profile_settings/buttons()` and `kovaplus_get_actual_profile()`: initialize cached state.
- `kovaplus_set_actual_profile()`: write the active zero-based profile with status polling.
- Generated sysfs attributes for control, info, profile settings/buttons, and per-profile read-only profile payloads.
- Text attributes for active profile, CPI, X/Y sensitivity, and firmware version.
- `kovaplus_keep_values_up_to_date()` and `kovaplus_report_to_chrdev()`: update cached runtime values and publish userspace events.

## Control Flow

Initialization on the mouse interface reads each profile's settings and buttons with a 70 ms delay between operations because shorter delays can freeze the device, then reads the current active profile and derives runtime CPI/sensitivity from the cached profile settings. Sysfs profile-specific reads select a profile through control and then read the shared payload. Active-profile writes validate `< 5`, send the firmware command, update cached state, and synthesize a profile event.

Raw event handling processes report number 3. Profile type `0x20` updates active profile and derived values, CPI type converts firmware CPI values with `kovaplus_convert_event_cpi()`, and sensitivity type updates X/Y sensitivity. Userspace reports skip profile type `0x30`, attach cached one-based profile, include a button number only for macro/shortcut/quicklaunch/timer events, and normalize CPI values.

## State and Persistence Behavior

`struct kovaplus_device` caches active profile, active CPI, active X/Y sensitivity, char-device state, mutex, and arrays of five profile settings and button payloads. Firmware remains authoritative for writes through sysfs; cached initialization data is used for runtime state derivation.

## Dependencies and Integration Points

The driver uses Roccat common feature-report helpers, `hid-roccat-kovaplus.h` layouts, class-backed sysfs, USB mouse-interface filtering, and Roccat char-device events.

## Risks and Edge Cases

- `kovaplus_send_control()` uses `roccat_common2_send()` without status polling, unlike some sibling drivers.
- Profile-specific read helpers select the profile before entering the common read lock, leaving a possible race with other sysfs operations.
- Firmware-version reads ignore receive errors and may print uninitialized data.
- Raw-event casts do not check size.
- The fixed 70 ms wait is hardware-sensitive and may be insufficient for some devices or unnecessarily slow for others.

## Test Signals

Tests should cover initialization timing, all five profile cache loads, active profile changes, CPI conversion values `4` and `7`, sensitivity updates, firmware-info failure handling, profile-read concurrency, exact-size sysfs behavior, and event filtering for profile type `0x30`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.h

## Purpose

`hid-roccat-kovaplus.h` defines Kova[+] report sizes, control requests, packed profile/info/actual-profile payloads, mouse button report types, Roccat event payload, and cached device state.

## Important APIs, Types, and Functions

- `KOVAPLUS_SIZE_*`: fixed payload sizes for control, info, profile settings, and profile buttons.
- `enum kovaplus_control_requests`: profile settings/buttons selectors.
- `struct kovaplus_actual_profile`, `struct kovaplus_profile_settings`, `struct kovaplus_profile_buttons`, and `struct kovaplus_info`.
- `enum kovaplus_mouse_report_button_types`: profile, macro, shortcut, quicklaunch, timer, CPI, sensitivity, and multimedia event types.
- `struct kovaplus_roccat_report` and `struct kovaplus_device`.

## Control Flow

The C file uses control request IDs to choose which profile data subsequent reads return. Mouse report type constants drive cache updates and char-device event construction.

## State and Persistence Behavior

Profile settings/buttons are cached in `struct kovaplus_device`, along with active profile/CPI/sensitivity. The packed profile structures represent firmware state and are surfaced to userspace.

## Dependencies and Integration Points

The header depends on Linux fixed-width types and is consumed by the Kova[+] driver and Roccat userspace tools via the binary sysfs ABI.

## Risks and Edge Cases

Several type comments describe one-based firmware values while cached profile indices are zero-based. Layout or enum changes would break both firmware interaction and event decoding.

## Test Signals

Size/layout checks, profile index conversion tests, CPI event conversion, and event-type coverage should guard this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.c

## Purpose

`hid-roccat-lua.c` is a minimal Roccat Lua mouse driver exposing a single control binary sysfs file for CPI, button, and light settings.

## Important APIs, Types, and Functions

- `lua_sysfs_read()` and `lua_sysfs_write()`: exact-size feature-report helpers for the Lua sysfs file.
- `LUA_BIN_ATTRIBUTE_RW(control, CONTROL)`: generates the eight-byte `control` binary attribute.
- `lua_create_sysfs_attributes()` and `lua_remove_sysfs_attributes()`: create/remove the attribute directly on the USB interface device.
- `lua_init_specials()` and `lua_remove_specials()`: allocate/free `struct lua_device` and initialize its mutex.
- `lua_probe()` and `lua_remove()`: parse/start/stop HID and install/remove sysfs state.

## Control Flow

Probe requires USB, parses and starts HID, allocates Lua state, initializes the lock, and creates `control` on the USB interface kobject rather than via a Roccat class. Reads and writes require offset zero and count exactly eight bytes; reads use `roccat_common2_receive()` while writes use `roccat_common2_send()` without status polling.

## State and Persistence Behavior

Only a mutex persists in `struct lua_device`. All device configuration is firmware state accessed through the eight-byte control report. No Roccat char device is created and no raw events are handled.

## Dependencies and Integration Points

The file uses HID/USB, Roccat common feature-report receive/send helpers, direct sysfs bin file creation, and Lua constants from `hid-roccat-lua.h`.

## Risks and Edge Cases

- Sysfs files are created directly on the USB interface, so the kobject traversal differs from class-backed Roccat drivers.
- Writes do not use common status polling.
- Failure after `hid_hw_start()` is handled by `hid_hw_stop()`, but sysfs creation failure must ensure allocated state is freed, which this file does.
- Exact-size access may surprise generic sysfs readers.

## Test Signals

Test creation/removal of the interface `control` bin file, exact eight-byte read/write behavior, concurrent accesses through `lua_lock`, write failure propagation, and probe cleanup after sysfs creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.h

## Purpose

`hid-roccat-lua.h` defines the Lua control report size, command ID, and per-device mutex state.

## Important APIs, Types, and Functions

- `LUA_SIZE_CONTROL = 8`: fixed binary sysfs payload size.
- `LUA_COMMAND_CONTROL = 3`: feature report command ID.
- `struct lua_device`: contains `lua_lock` for serialized USB transfers.

## Control Flow

The C file's generated sysfs callbacks use the size and command constants to issue feature-report transfers.

## State and Persistence Behavior

The header defines only the in-memory lock; actual Lua settings persist in device firmware.

## Dependencies and Integration Points

It depends on Linux types and is consumed only by `hid-roccat-lua.c`.

## Risks and Edge Cases

The ABI has no named packed payload fields, so validation and documentation of the eight-byte control report are limited.

## Test Signals

Tests should assert the sysfs file size is eight bytes and that reads/writes use command ID 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-lua.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.c

## Purpose

`hid-roccat-pyra.c` supports Roccat Pyra wired and wireless mice. It exposes settings/profile/info reports through sysfs, caches profile settings for runtime CPI/profile tracking, and forwards selected button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `pyra_send_control()`: selects profile settings/buttons with range validation.
- `pyra_get_settings()`, `pyra_set_settings()`, and `pyra_get_profile_settings()`: firmware accessors.
- `pyra_sysfs_read()` and `pyra_sysfs_write()`: exact-size binary sysfs helpers.
- Generated attributes for control, info, profile settings/buttons, and per-profile read-only settings/buttons.
- `pyra_sysfs_write_settings()`: custom settings writer that updates active profile and emits a profile event.
- `pyra_init_pyra_device_struct()`: reads settings and all five profile settings, then derives cached runtime state.
- `pyra_raw_event()`, `pyra_keep_values_up_to_date()`, and `pyra_report_to_chrdev()`: runtime event handling.

## Control Flow

Probe initializes only mouse protocol interfaces. Initialization reads the three-byte settings report, then each profile's settings, and calls `profile_activated()` using the startup profile. Sysfs profile-specific reads select the profile through a control report before reading the shared payload. Settings writes require exactly `PYRA_SIZE_SETTINGS`, validate the startup profile, send with status polling, update the cached active profile/CPI, and synthesize a profile event.

Raw events process button report number 3. Profile type `PROFILE_2` updates the active zero-based profile from one-based data; CPI type updates the cached CPI. Char-device forwarding emits profile/CPI changes immediately and forwards macro/shortcut/quicklaunch press events with the current one-based profile value.

## State and Persistence Behavior

`struct pyra_device` stores active profile, active CPI, char-device state, mutex, and cached settings for five profiles. Firmware stores the startup profile and profile settings; the driver mirrors enough data to report runtime values without rereading on every interrupt.

## Dependencies and Integration Points

The driver depends on Roccat common helpers, Pyra wire definitions from `hid-roccat-pyra.h`, HID/USB mouse-interface filtering, class-backed sysfs, and Roccat char-device APIs.

## Risks and Edge Cases

- The `PYRA_BIN_ATTRIBUTE_R` macro uses `.size_new`, which is unusual compared with `struct bin_attribute`'s `.size` and may rely on local kernel compatibility or be a typo.
- Profile-specific read helpers select the profile before acquiring the sysfs transfer lock, creating a race with other profile-selection operations.
- `pyra_sysfs_show_actual_profile()` ignores read errors and returns `settings.startup_profile` from an uninitialized stack struct on failure.
- `pyra_sysfs_write_settings()` emits a char-device report without checking `roccat_claimed`.
- Raw-event casts do not check size.

## Test Signals

Tests should cover wired and wireless IDs, initialization cache load, settings writes, startup profile validation, profile/CPI event updates, profile-specific read races, firmware-info/settings read failure paths, bin attribute structure compatibility, and exact-size sysfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.h

## Purpose

`hid-roccat-pyra.h` defines Pyra report sizes, control request values, packed settings/profile/info payloads, mouse/audio report layouts, event type constants, Roccat report payload, and per-device state.

## Important APIs, Types, and Functions

- `PYRA_SIZE_*`: control, info, profile settings/buttons, and settings payload sizes.
- `enum pyra_control_requests`: profile settings/buttons selectors.
- `struct pyra_settings`, `struct pyra_profile_settings`, and `struct pyra_info`: feature-report payload layouts.
- `enum pyra_commands`: report command IDs.
- `struct pyra_mouse_event_button` and audio/button type enums: interrupt report formats.
- `struct pyra_roccat_report` and `struct pyra_device`: userspace event and cached state.

## Control Flow

The C file uses the control request enum to select profile data before reading shared payload commands. Raw button report type constants decide which events update cached values and which are forwarded.

## State and Persistence Behavior

`struct pyra_device` caches active profile/CPI and profile settings. The settings payload's `startup_profile` is zero-based firmware state and persists in the device.

## Dependencies and Integration Points

The header depends on Linux fixed-width types and is part of the binary sysfs and char-device ABI consumed by Roccat tooling.

## Risks and Edge Cases

Profile numbering is mixed: firmware settings use 0-4, several mouse events report 1-5, and userspace reports keep some one-based behavior. Any layout or enum change breaks userspace and firmware protocol.

## Test Signals

Layout-size checks, profile numbering conversion tests, button/audio report parsing, and sysfs attribute size checks should guard this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-ryos.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-ryos.c

## Purpose

`hid-roccat-ryos.c` supports Roccat Ryos MK, Glow, and Pro keyboards. It exposes many keyboard configuration, macro, lighting, and talk feature reports through common Roccat sysfs attributes and forwards special reports to the Roccat char device.

## Important APIs, Types, and Functions

- `struct ryos_report_special`: five-byte report number 3 event payload.
- Generated common attributes for profile, key groups, key mask, light, macro, info, reset, light control, talk, stored lights, custom lights, and light macro.
- `ryos_init_specials()` and `ryos_remove_specials()`: allocate common device state and connect/disconnect char device on protocol 0 interface.
- `ryos_raw_event()`: forwards report 3 to the char device.

## Control Flow

Probe requires USB, parses and starts HID, and initializes only interface protocol 0. Initialization allocates `struct roccat_common2_device`, initializes its lock, and connects a char device sized for `struct ryos_report_special`. Sysfs attributes are supplied by a class named `ryos` and use exact-size common helper transfers. Raw events on other interfaces or non-report-3 data are ignored; report 3 is forwarded as raw bytes if the char device is claimed.

## State and Persistence Behavior

Driver state is limited to common char-device state and a mutex. Keyboard profiles, macros, and lighting state live in firmware and are accessed on demand through sysfs feature reports.

## Dependencies and Integration Points

The driver uses Roccat common helpers, HID/USB, class sysfs groups, and `linux/hid-roccat.h` event forwarding. It does not have a separate header in this work item; report constants and layouts are local.

## Risks and Edge Cases

- `ryos_raw_event()` does not validate `size` before checking and forwarding `data[0]`.
- Large lighting and macro payload sizes make short USB transfer handling important.
- Common-helper status polling can block indefinitely on repeated busy status.

## Test Signals

Tests should verify all bin attribute sizes/modes, protocol-interface gating, report-3 char-device forwarding, large macro/light transfers, failed char-device registration, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-ryos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.c

## Purpose

`hid-roccat-savu.c` supports the Roccat Savu mouse. It exposes profile/general/buttons/macro/info/sensor reports through common Roccat sysfs attributes and translates special report data into compact Roccat char-device events.

## Important APIs, Types, and Functions

- Generated common attributes for control, profile, general, buttons, macro, info, and sensor.
- `savu_init_specials()` and `savu_remove_specials()`: allocate common device state and connect/disconnect char device on mouse interfaces.
- `savu_report_to_chrdev()`: converts `struct savu_mouse_report_special` into `struct savu_roccat_report`.
- `savu_raw_event()`: filters by USB mouse interface and forwards through the conversion helper.

## Control Flow

Probe parses and starts HID, then initializes only the USB mouse protocol interface. Common sysfs attributes use fixed-size Roccat feature reports. Raw events on the mouse interface are passed to `savu_report_to_chrdev()`, which ignores non-special report numbers, copies the type and two data bytes, and emits the smaller Roccat event payload.

## State and Persistence Behavior

Only common char-device state and a lock persist in RAM. Device profile, macro, button, and sensor settings are firmware state accessed through sysfs.

## Dependencies and Integration Points

The driver depends on `hid-roccat-common.h`, Savu layouts from `hid-roccat-savu.h`, HID/USB mouse-interface filtering, and Roccat char-device APIs.

## Risks and Edge Cases

- Raw-event code does not check `size` before reading report fields.
- The driver does not cache active profile or CPI, so userspace must infer changes from forwarded reports or query firmware.
- Common-helper exact-size and status-polling behavior applies.

## Test Signals

Tests should verify sysfs attribute sizes, mouse-interface gating, special report translation, handling of unclaimed char device, large macro transfer behavior, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.h

## Purpose

`hid-roccat-savu.h` defines the Savu special mouse report layout, report number, button-event type constants, and compact Roccat userspace event layout.

## Important APIs, Types, and Functions

- `struct savu_mouse_report_special`: report number, zero byte, event type, and two data bytes.
- `SAVU_MOUSE_REPORT_NUMBER_SPECIAL = 3`: raw-event selector.
- `enum savu_mouse_report_button_types`: profile, quicklaunch, timer, CPI, sensitivity, and multimedia event type values.
- `struct savu_roccat_report`: type plus two data bytes sent to userspace.

## Control Flow

The C file casts report 3 data to `savu_mouse_report_special`, copies the type and data bytes into `savu_roccat_report`, and forwards it through the Roccat char device.

## State and Persistence Behavior

The header defines no persistent driver state. It describes interrupt-event payloads only; profile and button configuration state are handled by feature reports in `hid-roccat-savu.c`.

## Dependencies and Integration Points

It depends on Linux fixed-width types and is consumed by the Savu driver. The event type values are part of the userspace ABI.

## Risks and Edge Cases

The event enum documents data semantics but the C file does not validate them. Layout changes would break char-device consumers.

## Test Signals

Layout-size checks and event-type coverage for report 3 should accompany changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-savu.h -->
