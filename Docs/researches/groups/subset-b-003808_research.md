# Research group subset-b-003808

Grouped research for HID driver sources under `sources/distributed-fs/ceph-client/drivers/hid`. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-thrustmaster.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-thrustmaster.c

Purpose: initializes Thrustmaster wheels that enumerate as the generic USB HID `Thrustmaster FFB Wheel`. The driver identifies the real wheel model with a vendor control read and sends the model-specific control request that switches the wheel into its full-capability mode.

Important APIs, types, and functions: `struct tm_wheel_info` maps model IDs to switch values and names; `struct tm_wheel_response` describes the vendor response packet; `struct tm_wheel` owns the USB device, one URB, two copied `usb_ctrlrequest` objects, and the model response buffer. `thrustmaster_probe()` parses and starts HID without FF, allocates state, sends safety interrupt packets through `thrustmaster_interrupts()`, then submits a control URB. `thrustmaster_model_handler()` decodes packet type `0x49` or `0x47`, chooses a `tm_wheel_info`, fills `change_request->wValue`, and reuses the URB for the switch request. `thrustmaster_change_handler()` treats normal completion and some protocol failures as likely success because the wheel disconnects/re-enumerates.

Control flow: probe rejects non-USB HID devices, starts HID, allocates all request/response resources, performs the T300RS interrupt prelude, submits a model request, then returns while completion handlers drive the mode switch asynchronously. Remove kills the URB, frees all heap-owned state, and stops HID hardware.

State and persistence: no persistent configuration is stored. Runtime state is the `tm_wheel` drvdata and an in-flight URB; successful mode switching likely causes device reset/re-enumeration. The setup packet arrays and known model table are static constants.

Dependencies and integration: depends on HID core, USB control/interrupt messaging, `hid_is_usb()`, `hid_hw_start()`, and kernel allocation helpers. It registers one USB VID/PID in a `hid_driver` named `hid-thrustmaster`.

Risks: asynchronous URB reuse makes lifetime handling critical; remove must kill the URB before freeing request buffers. Model parsing is based on reverse-engineered packet shapes, and unknown model IDs fail closed. Endpoint assumptions in `thrustmaster_interrupts()` are guarded but still device-specific. Force feedback is deliberately not connected during initial generic HID startup.

Test signals: no KUnit tests. Useful validation is hardware-driven: connect supported wheels, confirm the model log, observe re-enumeration/full mode, and check that removal during an in-flight request does not fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-thrustmaster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-tivo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-tivo.c

Purpose: supplies key mapping overrides for TiVo Slide Bluetooth and USB remotes whose vendor and consumer usages do not map to the desired Linux input keys through generic HID.

Important APIs, types, and functions: `tivo_input_mapping()` is the only behavior hook. It uses `hid_map_usage_clear()` through `tivo_map_key_clear()` to remap TiVo vendor page usages and selected consumer page usages to `KEY_MEDIA`, `KEY_TV`, keypad plus/minus, `KEY_ENTER`, and `KEY_INFO`. `tivo_devices[]` matches Bluetooth and USB TiVo Slide variants.

Control flow: HID input mapping calls the driver for each usage. If the usage page is TiVo vendor or consumer and the usage code is recognized, the function maps and returns `1`, preventing generic mapping. Unknown usages return `0` so generic HID mapping can proceed.

State and persistence: stateless; no drvdata, allocations, probe, remove, or persistent data.

Dependencies and integration: integrates with HID input mapping and Linux input key codes. Device IDs come from `hid-ids.h`, and the module registers a `hid_driver` named `tivo_slide`.

Risks: mappings are exact constants; new remote firmware or alternate usage codes fall through to generic behavior. Because the function overrides consumer usages that already have defaults, regressions would be user-visible key semantics rather than crashes.

Test signals: no in-tree tests. Validation is by pairing/connecting the listed remotes and checking evtest/libinput events for TiVo, Live TV, thumbs up/down, Enter/Last, and Info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-tivo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-tmff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-tmff.c

Purpose: adds force feedback support for older ThrustMaster HID devices, mainly rumble gamepads and force-feedback wheels, by finding a vendor output field and registering memless input FF playback.

Important APIs, types, and functions: `ff_rumble[]` and `ff_joystick[]` are per-device FF capability lists stored in `id->driver_data`. Under `CONFIG_THRUSTMASTER_FF`, `struct tmff_device` keeps the output report and force field. `tmff_scale_u16()` and `tmff_scale_s8()` map input effect ranges to the HID field logical range. `tmff_play()` handles `FF_CONSTANT` and `FF_RUMBLE`, writes two values into the output field, and sends `HID_REQ_SET_REPORT`. `tmff_init()` locates the output field with usage `HID_UP_GENDESK | 0xbb`, sets input FF bits, and calls `input_ff_create_memless()`.

Control flow: `tm_probe()` parses and starts HID with normal FF connection masked out, then calls `tmff_init()` with the matched effect list. If FF support is not compiled, `tmff_init()` is an inline no-op and the device remains a normal HID input device.

State and persistence: the only allocated runtime object is `tmff_device`, owned by the input FF subsystem as memless callback data after successful setup. No persistent storage exists. Device-specific behavior is captured by static ID table entries and the special motor swap for product `0xb320`.

Dependencies and integration: depends on HID report enumeration, input force-feedback APIs, HID output requests, and `hid-ids.h`. It registers a `hid_driver` named `thrustmaster`.

Risks: `tm_probe()` ignores the return value from `tmff_init()`, so FF setup failures do not fail device probing. Output report parsing is strict about duplicate fields and field size but logs unknown output usages. Range conversion assumes two field values and correct descriptor logical min/max.

Test signals: no KUnit tests. Validation should inspect input FF capabilities and exercise rumble/constant effects with tools such as `fftest`, while checking report writes on real listed hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-tmff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-topre.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-topre.c

Purpose: fixes report descriptors for Topre REALFORCE R2/R3S keyboard non-boot interfaces that claim array input but actually send variable input.

Important APIs, types, and functions: `topre_report_fixup()` is the driver hook. It checks for two known descriptor layouts by size and byte pattern, logs a fixup message, and changes the input item flag from `0x00` to `0x02`. `topre_id_table[]` matches REALFORCE R2 108-key, R2 87-key, and R3S 87-key USB IDs.

Control flow: HID core calls `report_fixup` before parsing. If a known descriptor byte sequence is present at the expected offset, the descriptor is modified in place and returned. Otherwise the original descriptor is returned unchanged.

State and persistence: stateless; no allocations, drvdata, probe, or remove. The only state is the modified in-memory descriptor during HID enumeration.

Dependencies and integration: integrates with HID report fixup and USB device ID matching from `hid-ids.h`.

Risks: offset-based descriptor patching is intentionally narrow; descriptor revisions with shifted bytes may not be fixed. Incorrectly matching a descriptor could change keyboard semantics, but the byte-pattern guards reduce that risk.

Test signals: no automated tests. Hardware validation should confirm the affected keyboard interface emits key events correctly after descriptor parsing and that unaffected descriptors are not patched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-topre.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-topseed.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-topseed.c

Purpose: provides vendor-page key mappings for TopSeed Cyberlink, BTC/Emprex, Conceptronic/TopSeed2, and Chicony media-center remotes.

Important APIs, types, and functions: `ts_input_mapping()` maps `HID_UP_LOGIVENDOR` usages to Linux media/TV/color/application keys using `hid_map_usage_clear()`. `ts_devices[]` matches USB and Bluetooth variants from several vendors.

Control flow: input mapping exits early unless the usage page is Logitech vendor. Recognized usage IDs are remapped and return `1`; unknown usage IDs return `0` for generic handling.

State and persistence: stateless. The file contains only mapping logic and device tables.

Dependencies and integration: depends on HID input mapping, input key codes, and `hid-ids.h`. The module registers the `topseed` HID driver.

Risks: device behavior is entirely table-driven; vendor-page collisions or new remote layouts could produce missing or wrong keys. Because unknown usages fall through, the main risk is incomplete mapping rather than device failure.

Test signals: no in-tree tests. Validate by checking evtest output for WLAN/media/TV/color keys on each listed remote family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-topseed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-twinhan.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-twinhan.c

Purpose: remaps the TwinHan IR remote control keyboard-page usages into media remote keys and suppresses modifier usages used as parts of multi-key remote-button encodings.

Important APIs, types, and functions: `twinhan_input_mapping()` handles `HID_UP_KEYBOARD` usages. It maps fixed usage IDs to keys such as `KEY_TEXT`, `KEY_RESTART`, `KEY_EPG`, numeric keys, playback keys, channel/volume controls, and `KEY_POWER2`. Modifier usages `0x0e0` through `0x0e7` and unknown usages return `-1`, which stops generic mapping and prevents stray modifier events.

Control flow: HID calls the mapping hook per usage. Non-keyboard pages return `0`; listed usages map and return `1`; modifier or unrecognized keyboard usages return `-1`.

State and persistence: stateless; no allocations or drvdata.

Dependencies and integration: integrates with HID input mapping and input key codes. `twinhan_devices[]` matches the TwinHan IR remote USB ID.

Risks: returning `-1` for all unrecognized keyboard-page usages intentionally drops events, which is correct for the known remote but can hide new buttons if the same VID/PID appears with a revised layout. The comments document multi-key encodings for power and volume where suppressing modifier components matters.

Test signals: no automated tests. Validate with the physical remote, checking that power/volume do not leave Ctrl/Alt/Meta states stuck and that all documented keys emit the expected input codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-twinhan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-u2fzero.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-u2fzero.c

Purpose: exposes U2F Zero and Nitrokey U2F auxiliary functionality as Linux LED and hardware RNG devices while keeping HIDRAW access for U2F operations.

Important APIs, types, and functions: `struct hw_revision_config` provides per-revision RNG and wink commands. `struct u2f_hid_msg` and `struct u2f_hid_report` model 64-byte U2F HID reports using broadcast CID. `struct u2fzero_device` owns HID/USB pointers, URB, LED classdev, hwrng, buffers, mutex, presence flag, and revision. `u2fzero_send()` serializes output reports. `u2fzero_recv()` submits the interrupt-in URB, sends a command, waits with timeout, and copies the response. `u2fzero_brightness_set()` triggers wink on nonzero brightness. `u2fzero_rng_read()` sends the RNG command and returns bounded response data. `u2fzero_fill_in_urb()` builds a dedicated interrupt URB from usbhid endpoints.

Control flow: probe rejects non-USB, devm-allocates state and buffers, parses HID, starts HIDRAW, prepares the URB, marks the device present, derives names from the hidraw minor, then registers LED and hwrng devices. Remove marks the device absent under lock, stops HID, poisons, and frees the URB.

State and persistence: runtime state is devm-managed except the explicit URB. The mutex serializes command/response buffers and URB use. `present` prevents RNG reads after disconnect. No persistent storage exists.

Dependencies and integration: depends on HIDRAW, hwrng, LED classdev, USB interrupt URBs, and usbhid internals. Matches Cygnal U2F Zero and Clay Logic Nitrokey U2F IDs.

Risks: `u2fzero_fill_in_urb()` return is ignored in probe, so failures could leave `dev->urb` unset before RNG use. Command serialization relies on one shared URB and buffers. Response validation is minimal but bounds copies by actual length, message length, and caller max.

Test signals: no KUnit tests. Validate `/sys/class/leds/u2fzero*`, `/dev/hwrng` registration, RNG reads, LED blink, disconnect during read, and Nitrokey command differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-u2fzero.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core-test.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core-test.c

Purpose: KUnit coverage for UC-Logic raw event hook matching, compiled into `hid-uclogic-core.c` when `CONFIG_HID_KUNIT_TEST` is enabled.

Important APIs, types, and functions: `struct uclogic_raw_event_hook_test` describes a byte event, its size, and expected match result. `hook_events[]` are the registered hooks; `test_events[]` cover exact matches and mismatches by size, trailing bytes, and ordering. `fake_work()` is a no-op scheduled work target. `hid_test_uclogic_exec_event_hook_test()` allocates a synthetic `uclogic_params.event_hooks` list with KUnit memory, initializes each `uclogic_raw_event_hook`, then calls the otherwise-static `uclogic_exec_event_hook()`.

Control flow: test setup creates the hook list, appends two work items, then iterates over test events and asserts that the boolean return equals expectation. The work item can be scheduled for matching events, but no behavior is asserted beyond match detection.

State and persistence: all state is KUnit-managed heap data scoped to the test. Work structs use a no-op function, so persistent effects are absent.

Dependencies and integration: depends on KUnit and `hid-uclogic-params.h`; included directly from the core C file to access static symbols.

Risks: the test validates exact byte/size matching but not work completion, cancellation, or cleanup interactions. It is useful for preventing accidental prefix/substring matching regressions.

Test signals: this file is itself the test signal. Run the `hid_uclogic_core_test` KUnit suite with HID KUnit enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core.c

Purpose: main HID driver for UC-Logic, Huion, UGEE, XP-PEN, Trust, and related tablets whose descriptors or raw reports require correction. It orchestrates parameter discovery, descriptor replacement, input-device naming, raw-event normalization, in-range emulation, and cleanup.

Important APIs, types, and functions: `uclogic_probe()` sets `HID_QUIRK_MULTI_INPUT` and `HID_QUIRK_HIDINPUT_FORCE`, allocates `struct uclogic_drvdata`, initializes timer/rotary state, calls `uclogic_params_init()`, generates a replacement descriptor with `uclogic_params_get_desc()`, parses, and starts HID. `uclogic_report_fixup()` returns the generated descriptor. `uclogic_input_mapping()` remaps keypad frame buttons through `uclogic_extra_input_mapping[]` and can discard invalid pen usages. `uclogic_input_configured()` names input devices by report ID/application and clears `EV_MSC` for touch controls. `uclogic_raw_event()` dispatches input reports through event hooks, pen subreport remapping, pen tweaks, and frame tweaks.

Control flow: probe builds declarative parameters before HID parsing so report fixup can supply corrected descriptors. Runtime raw events first check hook patterns, then possibly convert pen subreports into synthetic report IDs, then mutate pen or frame report bytes in place. Resume re-runs parameter initialization only to re-enable hardware state, discarding the temporary parameters.

State and persistence: `uclogic_drvdata` holds parameters, generated descriptor memory, pen input pointer, in-range timer, rotary encoder previous state, and match-table quirks. The in-range timer synthesizes pen-up events for hardware without out-of-range reporting. No persistent storage exists.

Dependencies and integration: depends on HID core, input core, timers, usbhid, `hid-uclogic-params.h`, and `hid-ids.h`. The device table supplies model quirks for selected UGEE tablets.

Risks: report mutation is offset-sensitive and assumes sizes checked before access. Timer-driven pen-up needs `timer_delete_sync()` on remove. Event hooks schedule work from raw-event context and rely on parameter cleanup to cancel. Generated descriptor lifetime must outlive HID parsing and runtime use.

Test signals: includes `hid-uclogic-core-test.c` under `CONFIG_HID_KUNIT_TEST`. Hardware tests should cover multi-input naming, pen in-range emulation, frame dial/touch transforms, resume, and disconnect while hooks/timers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params-test.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params-test.c

Purpose: KUnit tests for UC-Logic parameter parsing and event-hook cleanup helpers compiled into `hid-uclogic-params.c` with HID KUnit enabled.

Important APIs, types, and functions: `struct uclogic_parse_ugee_v2_desc_case` parameterizes expected parse result, string descriptor bytes, descriptor parameters, and frame type. `hid_test_uclogic_parse_ugee_v2_desc()` calls `uclogic_params_parse_ugee_v2_desc()` and checks X/Y logical maxima, physical maxima, pressure max, button count, and frame type. `hid_test_uclogic_params_cleanup_event_hooks()` uses a fake HID device/drvdata to initialize UGEE v2 event hooks, then calls `uclogic_params_cleanup_event_hooks()` repeatedly to assert idempotence.

Control flow: KUnit array params run invalid, zero-resolution, buttons, dial, and mouse cases. The cleanup test allocates fake state, invokes the real hook initializer, then verifies repeated cleanup leaves `p.event_hooks == NULL`.

State and persistence: all allocations are KUnit-scoped except the production helper allocations, which the cleanup path frees. No persistent data.

Dependencies and integration: depends on KUnit, `hid-uclogic-params.h`, and `hid-uclogic-rdesc.h`; included directly from the params C file to access static helpers.

Risks: parse tests cover the 12-byte form but not the 14-byte XP-PEN Pro extension except indirectly through production code. Cleanup idempotence is tested, but allocation-failure paths and work cancellation timing are not deeply exercised.

Test signals: run the `hid_uclogic_params_test` KUnit suite. Failures indicate descriptor parsing, frame classification, or hook cleanup regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.c

Purpose: discovers, constructs, logs, and cleans UC-Logic-family tablet interface parameters. It is the model-specific decision table behind the UC-Logic core driver, translating USB IDs, interface numbers, string descriptors, magic probe sequences, and quirks into declarative pen/frame/battery/event-hook configuration.

Important APIs, types, and functions: exported helpers are `uclogic_params_init()`, `uclogic_params_get_desc()`, `uclogic_params_cleanup()`, and `uclogic_params_hid_dbg()`. Internal paths include `uclogic_params_get_str_desc()` for raw USB string descriptors, `uclogic_params_pen_init_v1()` and `_v2()` for Huion-style pen descriptors, `uclogic_params_frame_init_with_desc()` and `_v1()` for frame descriptors, `uclogic_params_parse_ugee_v2_desc()` for UGEE v2 descriptor parsing, `uclogic_probe_interface()` for magic interrupt probing, UGEE v2 frame/battery/event-hook helpers, and `uclogic_params_init_ugee_xppen_pro()` for Artist 22R/24 Pro special handling.

Control flow: `uclogic_params_init()` validates USB HID, extracts device and interface metadata, then switches on VID/PID. Some devices receive static descriptor replacements guarded by original descriptor size. Others probe pen parameters from string descriptors, mark non-useful interfaces invalid, or initialize UGEE v2 devices by sending magic data before reading descriptor 100. Output is copied from a temporary `struct uclogic_params` into the caller, with cleanup on errors.

State and persistence: all descriptor parts are kmalloc-owned and later freed by `uclogic_params_cleanup()`. Event hooks own event byte copies and work structs; cleanup cancels work and is idempotent. Firmware strings may populate `hdev->uniq`, and battery devices rewrite `hdev->uniq` to vendor-product form for hwmon safety. No disk persistence.

Dependencies and integration: depends on USB control/interrupt messaging, unaligned access helpers, `hid-uclogic-rdesc` descriptor templates, and `hid-ids.h`. The core driver consumes the resulting parameter structure for report fixup and raw-event transforms.

Risks: this file is heavily hardware-protocol dependent. Incorrect descriptor sizes, interface assumptions, or string parsing can disable interfaces or build wrong descriptors. Several paths return invalid/noop intentionally, so error handling must distinguish unsupported hardware from real failures. Event-hook initialization has multi-allocation cleanup risk; KUnit covers repeated cleanup.

Test signals: includes `hid-uclogic-params-test.c` under HID KUnit. Additional validation needs real tablets across static descriptor, Huion v1/v2, UGEE v2, battery, wireless reconnect, and XP-PEN Pro paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.h

Purpose: declares the UC-Logic parameter model shared by the core driver and parameter discovery implementation.

Important APIs, types, and functions: defines quirk bits `UCLOGIC_MOUSE_FRAME_QUIRK` and `UCLOGIC_BATTERY_QUIRK`; enums for pen in-range behavior and frame type; `struct uclogic_params_pen_subreport` for subreport-to-report-ID rewriting; `struct uclogic_params_pen` for pen descriptor, report ID, subreports, in-range mode, fragmented high-resolution coordinate flags, and tilt correction; `struct uclogic_params_frame` for frame descriptor, report ID, input suffix, rotary encoder, Wacom-compatible device ID byte, touch controls, and bitmap dial transforms; `struct uclogic_raw_event_hook` for raw-event-triggered work; `struct uclogic_params` for whole-interface validity, common descriptor, pen, frame list, and hooks; and `struct uclogic_drvdata` for runtime core state.

Control flow: the header itself has no control flow, but its structures define the contract: parameter discovery fills declarative fields, the core concatenates descriptor parts and applies report-time transformations based on those fields.

State and persistence: describes ownership expectations for kmalloc descriptor pointers and event-hook lists. `uclogic_drvdata` persists for the HID device lifetime and includes transient timer, pen input pointer, rotary state, and quirks.

Dependencies and integration: includes USB, HID, and list headers. Exports `uclogic_params_init()`, `uclogic_params_get_desc()`, `uclogic_params_cleanup()`, and `uclogic_params_hid_dbg()` to `hid-uclogic-core.c`.

Risks: because fields are offset and report-ID sensitive, comments are part of the safety contract. Zero-filled structures are defined as noop, so future fields should preserve that invariant. Ownership mistakes around `desc_ptr` and `event_hooks` can cause leaks or use-after-free.

Test signals: exercised indirectly by UC-Logic KUnit suites and by all UC-Logic hardware paths. ABI is internal to this driver, not userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc-test.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc-test.c

Purpose: KUnit tests for UC-Logic report descriptor template substitution, focused on `uclogic_rdesc_template_apply()`.

Important APIs, types, and functions: `struct uclogic_template_case` defines a template buffer, size, parameter list, and expected result. Test data covers empty/small templates, templates without placeholders, incomplete placeholders at the end, pen placeholders for all or some parameters, frame button placeholders, and missing parameter IDs. `hid_test_uclogic_template()` calls `uclogic_rdesc_template_apply()`, asserts allocation success, compares the full result buffer, then frees it.

Control flow: a KUnit array parameter generator runs all template cases. The test validates that pen placeholders become little-endian 32-bit values and frame button placeholders become HID Usage Maximum items with little-endian 16-bit values.

State and persistence: only temporary KUnit/test allocations and the returned kmalloc descriptor copy exist.

Dependencies and integration: imports the `EXPORTED_FOR_KUNIT_TESTING` namespace and includes `hid-uclogic-rdesc.h`. The production function is exported only for KUnit visibility.

Risks: tests verify substitution mechanics but not semantic validity of the large static descriptors. Boundary cases around placeholder heads at buffer end are covered.

Test signals: run the `hid_uclogic_rdesc_test` KUnit suite. Failures indicate descriptor template replacement regressions that would affect parameter-derived tablet descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.c

Purpose: stores static fixed HID report descriptors and parameterized descriptor templates for UC-Logic-family tablets, and implements the template substitution engine used by parameter discovery.

Important APIs, types, and functions: exports many `uclogic_rdesc_*_arr` and matching `*_size` symbols for WP4030U/WP5540U/WP8060U/WP1062/PF1209/TWHL850/TWHA60 fixed descriptors, v1/v2 pen templates, v1/v2 frame button/touch/dial descriptors, UGEE v2 probe data and pen/frame/battery templates, Ugee EX07/G5 frame descriptors, XP-PEN Deco01 and Artist 22R/24 Pro descriptors, and `uclogic_rdesc_template_apply()`. The template function copies a template and replaces pen placeholder heads (`0xFE,0xED,0x1D,index`) with little-endian 32-bit parameter values, or frame button placeholder heads (`0xFE,0xED,index`) with a HID Usage Maximum item.

Control flow: most of the file is declarative byte arrays. Runtime work happens only in `uclogic_rdesc_template_apply()`, which scans linearly through the copied descriptor, checks placeholder heads and index bounds, writes substituted values, and returns the kmalloc copy.

State and persistence: static descriptor arrays are immutable. Template application allocates a new descriptor owned by the caller. No persistent state.

Dependencies and integration: consumed by `hid-uclogic-params.c` and declared in `hid-uclogic-rdesc.h`. Uses allocation, unaligned writes, endian helpers, and KUnit visibility export.

Risks: descriptor bytes are dense and hardware-specific; mistakes can break HID parsing or userspace axis/button semantics. Template substitution preserves template size, so placeholders must be designed to occupy exactly the final item width. Array/size symbol consistency is critical.

Test signals: includes `hid-uclogic-rdesc-test.c` under HID KUnit. Hardware validation should cover descriptor parsing and input reports for each static/template descriptor family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.h

Purpose: declares UC-Logic fixed descriptor arrays, descriptor template arrays, original descriptor size constants, report IDs, placeholder IDs, and the template application API.

Important APIs, types, and functions: defines original descriptor sizes such as `UCLOGIC_RDESC_WPXXXXU_ORIG_SIZE`, `UCLOGIC_RDESC_WP5540U_V2_ORIG_SIZE`, and TWHL850/TWHA60 interface sizes. Declares fixed descriptor arrays and sizes for legacy tablets, placeholder heads and macros `UCLOGIC_RDESC_PEN_PH()` and `UCLOGIC_RDESC_FRAME_PH_BTN`, enum `uclogic_rdesc_ph_id`, v1/v2 report IDs, frame/touch/dial device ID offsets, UGEE v2 probe data, battery report ID, Ugee G5 frame constants, XP-PEN Artist descriptors, and `uclogic_rdesc_template_apply()`.

Control flow: none. The header defines constants and extern contracts that parameter discovery uses to select descriptor replacements and raw-event transforms.

State and persistence: no runtime state. It documents immutable descriptor symbols and caller-owned kmalloc results from template application.

Dependencies and integration: included by params, rdesc implementation, and rdesc KUnit tests. It includes `linux/usb.h` for fixed-width USB/HID types used in declarations.

Risks: constants couple tightly to report-byte offsets in `hid-uclogic-core.c` and model logic in `hid-uclogic-params.c`. Changing report IDs or offsets without updating raw-event handling will cause misrouted input. Original descriptor size guards must match real hardware descriptors.

Test signals: used by KUnit tests for template substitution and by compile-time linkage of all descriptor symbols. Real hardware remains the main validation for descriptor semantic correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-udraw-ps3.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-udraw-ps3.c

Purpose: implements a custom input driver for the THQ PS3 uDraw tablet, splitting one 27-byte raw HID report into four Linux input devices: joypad, touchpad, pen tablet, and accelerometer.

Important APIs, types, and functions: `struct udraw` stores four `input_dev` pointers, the HID device, and touch-position history for two-finger smoothing. `udraw_raw_event()` decodes button bits, d-pad direction, touch type, coordinates, pen pressure, and accelerometer axes. `allocate_and_setup()` creates common input devices with open/close callbacks. `udraw_setup_touch()`, `_pen()`, `_accel()`, and `_joypad()` define capabilities and ranges. `udraw_probe()` allocates state, parses HID, creates/registers input devices, and starts HID with HIDRAW plus driver connection.

Control flow: probe sets up all input nodes before `hid_hw_start()`. Each raw report of length 27 updates and syncs all four input devices, then returns `0` to leave HIDRAW/HIDDEV handling available. Open/close proxy to `hid_hw_open()` and `hid_hw_close()`.

State and persistence: state is devm-managed for device lifetime. Last one-finger and two-finger coordinates smooth unreliable two-finger reports. No persistent storage.

Dependencies and integration: depends on HID raw-event callbacks and input core. The ID table matches the THQ PS3 uDraw USB device.

Risks: `clamp_accel()` appears to divide by `(range * 0xFF)`, producing a very small normalized value; this may be intentional legacy behavior or a scaling bug. Input registration combines calls with `||`, so later registration errors collapse to boolean `1`. Report parsing is hard-coded to byte offsets and ignores other lengths.

Test signals: no automated tests. Validate with hardware by monitoring four input devices, checking pen pressure offset, touch transitions, d-pad/buttons, accelerometer motion, and HIDRAW availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-udraw-ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-universal-pidff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-universal-pidff.c

Purpose: generic wrapper for USB PID force-feedback devices, adding broader button mapping and initializing `hid-pidff` with per-device quirks for modern wheels, bases, pedals, and joysticks.

Important APIs, types, and functions: `universal_pidff_input_mapping()` remaps joystick button-page usages beyond the normal joystick range into later key ranges, using `KEY_RESERVED` for overflow so scans are still visible. `universal_pidff_probe()` parses and starts HID without default FF, checks collections for `HID_UP_PID`, then calls `hid_pidff_init_with_quirks()` with `id->driver_data`. `universal_pidff_input_configured()` reduces fuzz/deadzone on axes and special-cases FFBeast joystick ABS_Y.

Control flow: probe exits successfully without FF if no PID usage page exists, allowing multi-interface devices with non-FF sibling interfaces to bind cleanly. If PID exists, pidff initialization errors fail probe. Mapping/configuration hooks run during HID input setup.

State and persistence: no private drvdata. Device-specific behavior is stored in the static ID table through PIDFF quirk bits. Axis settings mutate input device abs parameters.

Dependencies and integration: depends on `usbhid/hid-pidff.h`, HID collection metadata, input mapping/configuration, and a broad device ID table for MOZA, CAMMUS, VRS, FFBeast, PXN/Lite Star, and Asetek devices.

Risks: button remapping spans non-joystick key ranges and may surprise userspace, but preserves events. Probe uses a function pointer assigned to `hid_pidff_init_with_quirks`; the null check is defensive but normally redundant. Collection scanning only detects descriptors that expose the PID usage page.

Test signals: no KUnit tests. Validate with `evtest` for high-number buttons, FF effect upload/playback for each quirk family, and axis fuzz/deadzone behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-universal-pidff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-viewsonic.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-viewsonic.c

Purpose: replaces the bad report descriptor of ViewSonic/signotec PD1011 signature pads with a fixed digitizer descriptor.

Important APIs, types, and functions: `PD1011_RDESC_ORIG_SIZE` guards replacement. `pd1011_rdesc_fixed[]` describes stylus X/Y, in-range, tip switch, and pressure fields with corrected logical/physical ranges. `viewsonic_report_fixup()` selects the fixed descriptor for ViewSonic and signotec PD1011 product IDs only when the original descriptor size matches.

Control flow: HID core invokes `report_fixup`; matching devices with expected descriptor size receive the static fixed descriptor and updated size, otherwise the original descriptor is returned unchanged.

State and persistence: stateless; static descriptor only.

Dependencies and integration: depends on HID report fixup and device IDs from `hid-ids.h`. Registers a `viewsonic` HID driver.

Risks: replacement is all-or-nothing by size and product. Firmware with the same ID but different descriptor size will not be fixed; firmware with same size but different semantics could be misdescribed, though the product guard narrows this.

Test signals: no automated tests. Validate HID parsing and signature input events for both ViewSonic and signotec branded PD1011 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-viewsonic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.c

Purpose: shared helpers for ChromeOS Vivaldi keyboards that expose the physical function-row map through HID feature reports and sysfs.

Important APIs, types, and functions: `vivaldi_feature_mapping()` parses Google vendor function-row physical-map usages. It assumes `hid_get_drvdata(hdev)` begins with `struct vivaldi_data`, fetches the feature report with `hid_hw_raw_request()`, feeds it back through `hid_report_raw_event()` so field values are decoded, and stores each ordinal value in `data->function_row_physmap`. `function_row_physmap_show()` delegates formatting to `vivaldi_function_row_physmap_show()`. `vivaldi_is_visible()` hides the sysfs file until at least one function-row key was discovered. `vivaldi_attribute_groups` exports the sysfs attribute group.

Control flow: during feature mapping, only fields whose logical usage is the Google function-row physical map and whose usage page is ordinal are processed. The helper handles unnumbered reports by accounting for the report-ID byte behavior of `hid_hw_raw_request()`.

State and persistence: updates `struct vivaldi_data` in HID drvdata with `num_function_row_keys` and physical map entries. Sysfs exposes current in-memory data; no persistent storage.

Dependencies and integration: depends on HID feature reports, `input/vivaldi-fmap.h`, sysfs attribute groups, and exported symbols for use by Vivaldi-specific HID drivers.

Risks: drvdata layout is a documented assumption; embedding drivers must place `struct vivaldi_data` first. Feature report fetching can fail and only warns. Incorrect report-ID length handling would cause `-EOVERFLOW` or bad field values.

Test signals: no KUnit tests. Validate by binding Vivaldi keyboards and reading `function_row_physmap` sysfs, including unnumbered feature-report devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.h

Purpose: small public header for the shared ChromeOS Vivaldi HID keyboard helpers.

Important APIs, types, and functions: forward-declares `struct hid_device`, `struct hid_field`, and `struct hid_usage`; declares `vivaldi_feature_mapping()` for use as a HID `feature_mapping` callback; declares exported `vivaldi_attribute_groups[]` for drivers that want the function-row sysfs attribute.

Control flow: none.

State and persistence: none directly. The declarations imply that callers provide HID drvdata compatible with `struct vivaldi_data` as required by the C implementation.

Dependencies and integration: included by `hid-vivaldi.c` and any other driver sharing Vivaldi function-row support. Keeps consumers from depending on implementation internals.

Risks: the header does not include `vivaldi-fmap.h`, so the drvdata layout requirement is not type-enforced here. Misuse by a driver with incompatible drvdata can corrupt reads in the common implementation.

Test signals: compile/link coverage through consumers. Runtime validation is reading the exported sysfs attribute on Vivaldi devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi.c

Purpose: HID driver for ChromeOS Vivaldi keyboards, wiring the common function-row mapping helper and sysfs attribute group into HID devices in `HID_GROUP_VIVALDI`.

Important APIs, types, and functions: `vivaldi_probe()` devm-allocates `struct vivaldi_data`, attaches it as drvdata, parses HID, and starts hardware with default connections. `vivaldi_table[]` matches any bus/vendor/product in the Vivaldi HID group. The `hid_driver` sets `.feature_mapping = vivaldi_feature_mapping` and `.driver.dev_groups = vivaldi_attribute_groups`.

Control flow: probe only allocates state and starts HID; feature parsing and sysfs visibility are handled by common helpers during HID setup.

State and persistence: per-device `vivaldi_data` is devm-managed and persists for the HID device lifetime. It backs the function-row sysfs output. No persistent storage.

Dependencies and integration: depends on HID core, `input/vivaldi-fmap.h`, and `hid-vivaldi-common`. The match is group-based rather than VID/PID-specific.

Risks: because common code assumes drvdata begins with `struct vivaldi_data`, this driver must keep drvdata exactly that type or a struct embedding it first. Probe has no custom remove because devm and HID core handle resources.

Test signals: no automated tests. Validate by enumerating a Vivaldi keyboard, confirming HID parse/start, and reading the function row physical map sysfs file when the feature exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vrc2.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-vrc2.c

Purpose: fixes and binds the VRC-2 two-axis car controller, replacing its descriptor with a simple joystick descriptor and ignoring a bogus sibling endpoint/interface.

Important APIs, types, and functions: local VID/PID constants are kept out of `hid-ids.h` because they may be borrowed. `vrc2_rdesc_fixed[]` describes a joystick with X/Y 16-bit absolute axes and trailing constants. `vrc2_report_fixup()` always returns the fixed descriptor. `vrc2_probe()` rejects interfaces whose original report descriptor size is 23, then parses and starts HID normally.

Control flow: on matched device, probe first filters the bogus endpoint by `hdev->dev_rsize`. For the real interface, HID parsing invokes descriptor fixup, then `hid_hw_start()` connects default input handling.

State and persistence: stateless; no private data or allocations.

Dependencies and integration: depends on HID report fixup and generic input handling. Registers a `hid_driver` named `vrc2` for the local USB IDs.

Risks: descriptor fixup is unconditional for non-rejected interfaces. If hardware with the borrowed VID/PID differs, it may receive an incorrect joystick descriptor. The bogus endpoint filter is based only on descriptor size.

Test signals: no automated tests. Validate by plugging the controller, confirming only the useful interface binds, and checking ABS_X/ABS_Y ranges in evtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-vrc2.c -->
