# subset-b-003797 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_usages.h -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_usages.h

## Purpose

`hid_usages.h` is a generated, BPF-program-facing HID usage catalog. It gives HID-BPF programs stable C preprocessor names for HID usage pages and page-local usage IDs without pulling in the larger kernel HID parser headers. The file is data-only: it contains no executable code, no structs, and no inline helpers. Its value is the generated mapping between readable names such as `HidUsagePage_Digitizers` or `HidUsage_Dig_PadType` and the numeric values defined by the HID Usage Tables.

The header currently covers common HID pages used by input, sensors, lighting, barcode/scales, power, braille, monitor, camera, arcade, FIDO, haptics, and related device classes. A local consumer visible in this tree is `drivers/hid/bpf/progs/Generic__touchpad.bpf.c`, which includes this header and checks parsed report fields by comparing `field->usage_page` and `field->usage_id` against the generated constants.

## Important APIs, Types, and Definitions

- `#pragma once` is the only include guard.
- `HidUsagePage_*` macros define top-level HID usage pages. Examples include Generic Desktop `0x01`, Keyboard/Keypad `0x07`, Digitizers `0x0d`, Sensors `0x20`, Lighting and Illumination `0x59`, Power `0x84`, and FIDO Alliance `0xf1d0`.
- `HidUsage_GD_*`, `HidUsage_KK_*`, `HidUsage_LED_*`, `HidUsage_Con_*`, `HidUsage_Dig_*`, `HidUsage_Sen_*`, and many other prefix groups define page-local usage IDs.
- The prefix namespace is generated for readability, not for runtime dispatch. A BPF program must still pair a usage ID with the correct usage page because numeric usage IDs are only unique within their page.
- No kernel APIs are called directly. The public contract is the macro names and their numeric values.

## Control Flow

There is no runtime control flow in this file. Build control flow is limited to textual inclusion by HID-BPF programs. At compile time the C preprocessor substitutes the constants into BPF C source, and the BPF compiler emits immediate constants used in verifier-checked comparisons or assignments.

The typical consumer flow is: include `hid_usages.h`, read fields exposed by the HID-BPF context or HID-BPF helper structures, compare `usage_page` and `usage_id` to the generated macros, and modify report-descriptor or event behavior based on those matches. Because the file is generated, source changes should normally come from regenerating the usage table rather than hand editing one macro.

## State and Persistence Behavior

The header has no mutable state and no persistence behavior. Its persistence is source-level: the macro set becomes part of each compiled BPF object that includes it. If the generated constants drift from the HID Usage Tables, the compiled BPF programs will continue using the stale values until rebuilt.

## Dependencies and Integration Points

- The SPDX and generated-file comments identify it as a Linux kernel source artifact and warn against manual edits.
- It integrates with HID-BPF programs under `drivers/hid/bpf/progs/`, especially descriptor fixup or event-rewrite programs that need symbolic HID usage names.
- The constants mirror external HID Usage Table semantics, so the generator and upstream HID table version are an implicit dependency even though no generator script is referenced inside the header.
- It intentionally avoids kernel-only data structures so it can be consumed by restricted BPF C compilation.

## Risks and Edge Cases

- The file is generated and should not be manually edited. Local changes are likely to be lost and may also leave the generator output inconsistent.
- Macro names live in the global preprocessor namespace. Prefixes reduce collisions, but broad inclusion can still conflict with other generated or vendor headers if they choose the same names.
- Several prefixes are compact abbreviations, and some page initials are reused conceptually across the HID specification. Consumers must compare both page and usage rather than assuming a usage macro alone is globally meaningful.
- The file has no version macro or provenance pointer to the exact HID Usage Tables revision used for generation. Reviewers need external process evidence to know whether new HID usages are current.
- Generated spelling is part of the API for BPF source. Fixing a typo-like macro name can break existing BPF programs unless compatibility aliases are provided.

## Test Signals

- BPF build tests should compile all programs under `drivers/hid/bpf/progs/` after regeneration.
- A small compile-only test should include this header in BPF C and compare representative page and usage constants, including `HidUsagePage_Digitizers` and `HidUsage_Dig_PadType`.
- Regeneration tests should diff generated output against the checked-in file and flag manual drift.
- Verifier/load tests for HID-BPF programs should confirm constants are accepted as immediate comparisons and do not require unsupported relocations.
- HID behavior tests should exercise at least one consumer path, such as the generic touchpad descriptor logic, to show the symbolic constants still match parsed usage pages and IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_usages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-a4tech.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-a4tech.c

## Purpose

`hid-a4tech.c` is a small HID quirk driver for A4Tech mice whose second wheel or horizontal wheel is not described in a standard HID-compatible way. It intercepts HID input mapping and event delivery so these devices expose normal Linux input events for vertical and horizontal high-resolution wheel movement.

The driver handles two quirk families. `A4_2WHEEL_MOUSE_HACK_7` treats usage `0x00090007` as an orientation selector for a later wheel event. `A4_2WHEEL_MOUSE_HACK_B8` treats the vendor-like Generic Desktop usage `0x000000b8` as a wheel-orientation report that follows a delayed wheel value.

## Important APIs, Types, and Functions

- `struct a4tech_sc` stores per-device quirk bits, current horizontal-wheel selector state, and a delayed wheel value for devices whose orientation arrives in a separate report.
- `a4_input_mapping()` suppresses direct mapping of the nonstandard `A4_WHEEL_ORIENTATION` usage for B8 devices.
- `a4_input_mapped()` adds `REL_HWHEEL` and `REL_HWHEEL_HI_RES` capabilities whenever the generic HID layer mapped `REL_WHEEL_HI_RES`, and suppresses the `0x00090007` selector usage for hack-7 devices.
- `a4_event()` is the main event translator. It consumes selector reports, delays or redirects wheel events, and emits horizontal or vertical wheel events through `input_event()`.
- `a4_probe()` allocates devres-backed state, stores `id->driver_data` quirks, parses the HID descriptor, and starts HID hardware with `HID_CONNECT_DEFAULT`.
- `a4_devices[]` maps four A4Tech USB product IDs to the two quirk modes.

## Control Flow

Probe is conventional: allocate `struct a4tech_sc`, copy quirk flags from the match table, attach it with `hid_set_drvdata()`, call `hid_parse()`, and call `hid_hw_start()`.

During input setup, `a4_input_mapping()` prevents the B8 orientation usage from becoming an input event of its own. After standard mapping, `a4_input_mapped()` makes sure the input device advertises horizontal wheel event bits if it has a high-resolution wheel and hides the hack-7 selector usage.

Runtime event control depends on the quirk. For B8 devices, a `REL_WHEEL_HI_RES` event is stored in `delayed_value` and consumed. When the subsequent `A4_WHEEL_ORIENTATION` event arrives, the driver emits either vertical `REL_WHEEL` and `REL_WHEEL_HI_RES` or horizontal `REL_HWHEEL` and `REL_HWHEEL_HI_RES` depending on the selector value. For hack-7 devices, the `0x00090007` usage sets `hw_wheel`; later `REL_WHEEL_HI_RES` events are rerouted to horizontal wheel events while that flag is set.

## State and Persistence Behavior

All state is per HID device and devm-owned for the device lifetime. `quirks` is fixed after probe. `hw_wheel` and `delayed_value` are mutable event-stream state used to correlate separate HID reports. There is no persistent storage, no sysfs configuration, and no cross-device state.

## Dependencies and Integration Points

- Uses the HID driver hooks `input_mapping`, `input_mapped`, `event`, and `probe`.
- Uses Linux input relative axes `REL_WHEEL`, `REL_WHEEL_HI_RES`, `REL_HWHEEL`, and `REL_HWHEEL_HI_RES`.
- Relies on vendor/product constants from `hid-ids.h`.
- Integrates with the generic HID input path by returning `1` for consumed events, `-1` for usages that should not be mapped, and `0` for default handling.

## Risks and Edge Cases

- B8 event pairing assumes the wheel delta arrives before the orientation usage. Reordered, dropped, or duplicated reports could cause stale `delayed_value` to be applied to the wrong orientation.
- `delayed_value * 120` assumes the delayed value is a low-resolution wheel unit. If the underlying value is already high-resolution on a future device, scaling would be wrong.
- Hack-7 `hw_wheel` is set from a selector value and not automatically cleared except by later selector events, so malformed streams can leave wheel events in horizontal mode.
- The driver adds horizontal capability bits whenever a high-resolution wheel is mapped, even if a future matched device does not actually report horizontal movement.
- There is no explicit locking around `a4tech_sc` event state. This relies on HID input event delivery ordering for a device.

## Test Signals

- Descriptor/input tests should confirm the nonstandard selector usages do not appear as user-visible input events.
- Event tests should feed B8 report sequences and verify vertical versus horizontal wheel output, including high-resolution scaling.
- Hack-7 tests should toggle usage `0x00090007` and confirm subsequent wheel deltas are rerouted only while selected.
- `evtest` or kernel HID selftests on matched device IDs should show `REL_HWHEEL` and `REL_HWHEEL_HI_RES` capabilities.
- Regression tests should verify unmatched HID usages still pass through default mapping and event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-a4tech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-accutouch.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-accutouch.c

## Purpose

`hid-accutouch.c` is a minimal HID driver for Elo Accutouch touchscreens. Its only behavior is to remap any HID Button-page usage to `BTN_TOUCH`, making the touchscreen contact state visible through the Linux input touchscreen button convention.

## Important APIs, Types, and Functions

- `accutouch_input_mapping()` checks `usage->hid & HID_USAGE_PAGE` and maps all Button-page usages to `EV_KEY/BTN_TOUCH` with `hid_map_usage()`.
- `accutouch_devices[]` matches the Elo Accutouch 2216 USB device ID.
- `accutouch_driver` installs only the `input_mapping` hook; parsing, hardware start, input registration, and event handling are left to the HID core.

## Control Flow

When a matching device is bound, the generic HID core performs standard driver setup because this driver has no custom probe. During HID input mapping, each usage is passed to `accutouch_input_mapping()`. Button-page usages are consumed and mapped to `BTN_TOUCH`; all other usages return `0` so the generic HID mapping path handles them normally.

At runtime, events follow the standard HID input path. Since button usages were mapped to `BTN_TOUCH`, presses and releases are reported as touchscreen contact changes instead of generic mouse or button events.

## State and Persistence Behavior

The file defines no private state and stores no persistent data. All runtime state is maintained by the HID core and input subsystem. The behavior is entirely static based on the device ID and usage page.

## Dependencies and Integration Points

- Depends on Linux HID and module infrastructure.
- Uses `hid_map_usage()` and input event constants `EV_KEY` and `BTN_TOUCH`.
- Uses Elo vendor and product IDs from `hid-ids.h`.
- Integrates with generic HID through the `input_mapping` callback and `module_hid_driver()`.

## Risks and Edge Cases

- Mapping every Button-page usage to `BTN_TOUCH` is intentionally broad. If a future Accutouch descriptor exposes more than one button with distinct meanings, they will all collapse to the same key.
- The driver assumes the generic HID core already maps axes and other touch metadata adequately.
- There is no custom validation of report shape, so unusual firmware descriptors rely entirely on HID core behavior.
- The `MODULE_AUTHOR` string is missing a closing angle bracket in the email text; this is cosmetic but visible in module metadata.

## Test Signals

- A descriptor-level test should verify Button-page usages become `BTN_TOUCH`.
- Runtime testing with an Accutouch 2216 should show contact press/release events on `BTN_TOUCH` with expected absolute position events from generic HID.
- Regression tests should confirm non-button usages still use generic HID mappings.
- Build/module tests should confirm the device ID table exports through `MODULE_DEVICE_TABLE(hid, ...)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-accutouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-alps.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-alps.c

## Purpose

`hid-alps.c` is an ALPS HID touchpad and DualPoint driver. It bypasses generic HID input mapping, initializes ALPS-specific register modes through HID feature reports, decodes raw touch reports, and optionally registers a second input device for a pointing stick. It supports U1-family devices and T4 buttonless devices, each with different register protocols and report layouts.

## Important APIs, Types, and Functions

- `struct alps_dev` stores the primary input device, optional stick input device, HID device, detected ALPS family, max finger count, stick support, button metadata, active dimensions, coordinate ranges, and button counts.
- `struct t4_contact_data` and `struct t4_input_report` model the packed T4 input report used by `t4_raw_event()`.
- `t4_calc_check_sum()` computes the T4 command/report checksum over bounded feature-report ranges.
- `t4_read_write_register()` and `u1_read_write_register()` implement family-specific register read/write commands over HID feature reports via `hid_hw_raw_request()`.
- `T4_init()` and `u1_init()` switch devices into absolute reporting modes, read geometry and button configuration, and populate `struct alps_dev`.
- `t4_raw_event()` decodes T4 multitouch contacts, inverts Y into the configured coordinate range, reports pressure, button state, and MT slots.
- `u1_raw_event()` handles U1 touch reports, feature/mouse report IDs, and stick absolute reports converted into relative `REL_X` and `REL_Y`.
- `alps_input_configured()` opens the low-level device, starts HID I/O, initializes hardware, configures input axes/buttons/MT slots, and registers the optional stick input device.
- `alps_post_reset()` and `alps_post_resume()` restore absolute reporting modes after reset or resume.

## Control Flow

Probe allocates `struct alps_dev`, stores it as HID driver data, sets `HID_QUIRK_NO_INIT_REPORTS`, parses the HID descriptor, classifies the product as T4, U1, or unknown, and starts hardware with `HID_CONNECT_DEFAULT`.

The driver returns `-1` from `alps_input_mapping()` so generic HID usages are not mapped into ordinary input events. Instead, `alps_input_configured()` takes over after the HID input device exists. It opens the HID hardware, calls `hid_device_io_start()` to permit report traffic, runs `T4_init()` or `u1_init()`, then configures the primary input device with multitouch axes, pressure, button capabilities, resolution if known, and `INPUT_MT_POINTER` slots. If U1 initialization detected stick support, it allocates and registers a second input device named `DualPoint Stick` with relative axes, stick properties, and button bits. Finally it stops temporary I/O and closes the HID hardware; normal input open/close later controls the device.

Raw report flow is centralized in `alps_raw_event()`. It ignores reports unless HID input is claimed and the primary input device is ready. T4 products dispatch to `t4_raw_event()`; all others dispatch to `u1_raw_event()`. Each decoder reports MT slot state and synchronizes the input device, returning `1` when it consumed a report and `0` for ignored report IDs.

## State and Persistence Behavior

`struct alps_dev` persists for the HID device lifetime and is devm-managed. Geometry, button counts, family type, and stick presence are read during input configuration and reused by the raw event path. Hardware reporting mode is persistent device state: initialization writes registers to enable absolute touchpad mode and, for supported U1 devices, stick absolute mode. Resume and reset paths rewrite those mode bits because firmware or power transitions can clear them.

The optional stick input device is manually allocated with `input_allocate_device()` and registered through the input core. Once registered, the input subsystem owns it; on registration failure it is freed locally. The primary device is owned by the HID input path.

## Dependencies and Integration Points

- Depends on HID core parsing, raw feature requests, report open/close, PM hooks, and `hid-ids.h` ALPS IDs.
- Depends on the input subsystem for multitouch slots, absolute axes, pressure, relative stick movement, button bits, and input properties.
- Uses unaligned helpers for U1 register addresses and report fields; T4 verification currently reads some fields through casts.
- Integrates with power management through `.resume = pm_ptr(alps_post_resume)` and `.reset_resume = pm_ptr(alps_post_reset)`.
- Uses `HID_QUIRK_NO_INIT_REPORTS` to avoid generic initialization reports that may disturb device state.

## Risks and Edge Cases

- T4 readback validation uses direct casts such as `*(u32 *)&readbuf[6]` and `*(u16 *)&readbuf[10]`, which can be unaligned and endian-sensitive. U1 uses `put_unaligned_le32()` for writes, but T4 validation does not use `get_unaligned_le*()`.
- `t4_calc_check_sum()` rejects `offset + length >= 50`, so exactly boundary-sized checks return zero. That may be intentional for report limits but should be validated against the hardware protocol.
- `t4_raw_event()` casts raw report bytes directly to `struct t4_input_report`; layout padding assumptions matter even though the field order is byte-heavy with a trailing `u16`.
- Raw event decoders do limited `size` validation. They assume report lengths match the selected family before indexing contact arrays and fixed offsets.
- Unknown products still start hardware and dispatch to U1 raw decoding by default in `alps_raw_event()`, although the match table only lists known IDs.
- `input_mt_init_slots()` return value is not checked. Allocation failure could leave later MT reporting misconfigured.
- The second stick device has a fixed `BUS_I2C` bustype even though the HID transport may be broader because IDs match `HID_BUS_ANY`.

## Test Signals

- Feature-report tests should verify U1 and T4 register read/write framing, checksum generation, readback validation, and error handling on bad checksum/address/size.
- Initialization tests should check that U1 absolute mode, U1 stick mode, and T4 advanced absolute mode are written during configuration and restored after resume/reset.
- Raw report tests should feed U1 multitouch, U1 stick, and T4 reports with active and inactive contacts and verify MT slot state, pressure, button events, coordinate inversion for T4, and input synchronization.
- Device capability tests should confirm coordinate min/max/resolution, pressure range, buttonpad property, button count, and optional stick input registration.
- Robustness tests should fuzz short reports and malformed report IDs to catch out-of-bounds access in raw event handlers.
- Manual testing on supported ALPS hardware should verify touch movement, click buttons, suspend/resume recovery, and DualPoint stick open/close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-alps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-apple.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appleir.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-appleir.c

## Purpose

`hid-appleir.c` is a HID driver for Apple infrared remote receivers. Apple remotes send short vendor-specific raw HID packets rather than a normal keyboard-like report descriptor, so this driver decodes the raw packet patterns into Linux input key events for menu, play/pause, forward, back, volume up/down, enter, and repeats.

## Important APIs, Types, and Functions

- `appleir_key_table[]` maps decoded key indices to Linux key codes.
- `struct appleir` stores the input device, HID device, mutable keymap, key-up timer, spinlock, current pressed key, and the first key index for two-packet commands.
- `get_key()` extracts a key index from bits 2..9 of the command byte and returns negative indices for two-packet command prefixes.
- `key_down()`, `key_up()`, and `battery_flat()` wrap input reporting and diagnostics.
- `key_up_tick()` releases the current key after a timeout because the remote does not send ordinary key-up packets.
- `appleir_raw_event()` decodes keydown, repeat, and flat-battery packet prefixes and emits input events while leaving reports visible to hidraw and hiddev.
- `appleir_input_configured()` installs the keymap and input capabilities.
- `appleir_input_mapping()` returns `-1` to suppress generic HID mappings.
- `appleir_probe()` forces HID input registration, initializes state and timer, parses the device, and starts hardware with HIDDEV forced.

## Control Flow

Probe allocates `struct appleir`, stores the HID pointer, sets `HID_QUIRK_HIDINPUT_FORCE`, initializes the spinlock and timer, parses the descriptor, and starts hardware with `HID_CONNECT_DEFAULT | HID_CONNECT_HIDDEV_FORCE`.

When the input device is configured, the driver assigns its keymap storage, enables `EV_KEY` and `EV_REP`, copies the default key table, marks all mapped keys as supported, and clears `KEY_RESERVED`.

Raw event flow only handles 5-byte packets while HID input is claimed. Packets starting `25 87 ee` are keydown packets. The driver releases any previously pressed key, handles pending two-packet state, decodes the current key, reports it down, schedules a key-up timer for one eighth of a second, and clears two-packet state. If `get_key()` returns a negative value, the index is stored as `prev_key_idx` and the next keydown packet completes the command. Packets starting `26` are repeats: they re-report the current key and extend the release timer. Packets starting `25 87 e0` log a possible flat battery message and then fall through to the normal return path.

## State and Persistence Behavior

All persistent runtime state is per device. `current_key` tracks the key currently considered pressed, and the timer releases it if no repeat extends the timeout. `prev_key_idx` carries state between the two packets used by some remote generations to distinguish middle versus play/pause commands. Access to `current_key` in timer and raw-event paths is protected by `spinlock_t lock` for keydown handling and timer release. There is no storage beyond the device lifetime.

## Dependencies and Integration Points

- Depends on HID raw event, input configured, input mapping, probe, and remove hooks.
- Uses the input subsystem keymap fields so userspace can inspect or change key codes.
- Uses kernel timers and spinlocks to synthesize key releases safely.
- Forces HID input and HIDDEV paths while returning `0` from raw event so hidraw/hiddev still receive the underlying reports.
- Matches five Apple IR receiver USB device IDs from `hid-ids.h`.

## Risks and Edge Cases

- The repeat packet path reads and reports `current_key` without taking the spinlock, while the timer can clear it under lock. This may be benign for an int-sized field but is a concurrency edge.
- If a repeat packet arrives before any keydown, `current_key` is zero and `key_down()` can report key code `0`, which maps to `KEY_RESERVED`.
- `prev_key_idx` is reset outside the spinlock on non-keydown paths, while keydown handling updates it under lock.
- The decoder hard-codes 5-byte packets and prefix bytes from known remotes. Newer remotes with different packet lengths or prefixes will pass through without input events.
- The timeout-based key release can create short releases during long holds if repeat packets are delayed beyond `HZ / 8`.

## Test Signals

- Raw packet tests should feed known packet sequences for old and newer remotes and verify decoded key codes.
- Two-packet tests should verify `0x5c/0x5d` plus follow-up maps to `KEY_ENTER` and `0x5e/0x5f` plus follow-up maps to play/pause.
- Repeat tests should verify repeat packets extend the timer and do not emit unexpected keys when no current key exists.
- Timer tests should confirm keys are released after one eighth of a second without repeat.
- Input configuration tests should verify keymap size, `EV_KEY`, `EV_REP`, supported key bits, and generic HID mapping suppression.
- Remove tests should verify `timer_delete_sync()` prevents timer callbacks after `hid_hw_stop()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appleir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-bl.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-bl.c

## Purpose

`hid-appletb-bl.c` is a backlight driver for the Touch Bar backlight endpoint on T2-era MacBook Pro systems. It binds to the Apple Touch Bar backlight HID device, locates the required HID feature report fields, and exposes brightness control through the Linux backlight subsystem.

## Important APIs, Types, and Functions

- Module parameter `brightness` sets default startup brightness: off, dim, or full. Values above 2 are clamped to full brightness during probe.
- `struct appletb_bl` stores the auxiliary field, brightness field, registered `backlight_device`, and whether the HID device is currently powered full-on.
- `appletb_bl_brightness_map[]` maps backlight core levels `0..2` to device protocol values `APPLETB_BL_OFF`, `APPLETB_BL_DIM`, and `APPLETB_BL_ON`.
- `appletb_bl_set_brightness()` sets the auxiliary field to `1`, writes the brightness field, powers the HID device to `PM_HINT_FULLON` when needed, sends the feature report, and drops back to `PM_HINT_NORMAL` when brightness is off.
- `appletb_bl_update_status()` translates backlight blanking and brightness into device protocol values.
- `appletb_bl_probe()` parses the HID descriptor, finds the required feature fields, starts and opens HID hardware, sets default brightness, and registers a raw backlight device.
- `appletb_bl_remove()` turns the Touch Bar backlight off, closes hardware, and stops HID hardware.

## Control Flow

Probe starts by parsing the HID descriptor. It searches feature reports on vendor page `0xff120001` for usages `0xff120020` and `0xff120021`, corresponding to the auxiliary and brightness controls. Both fields must exist and belong to the same report. After allocating state, the driver starts HID hardware in `HID_CONNECT_DRIVER` mode, opens it, writes the default brightness through `appletb_bl_set_brightness()`, and registers `appletb_backlight` with `BACKLIGHT_RAW` type and maximum brightness `2`.

Backlight core calls `appletb_bl_update_status()` whenever brightness or blanking changes. Blanking forces the device brightness protocol value to off; otherwise the core brightness index selects off, dim, or full from the map. Report transmission is synchronous enough to return errors from field setting and power-on, but `hid_hw_request()` itself is fire-and-forget in this code path.

Remove turns brightness off using the same report path, then closes and stops HID hardware.

## State and Persistence Behavior

The private state is devm-managed for the HID device lifetime. `full_on` tracks whether the driver has requested full power; it avoids redundant `PM_HINT_FULLON` calls and is cleared after setting brightness off and requesting normal power. The backlight device persists until devres cleanup. There is no persistent brightness storage in this file; startup brightness comes from the read-only module parameter.

## Dependencies and Integration Points

- Uses HID descriptor parsing, `hid_find_field()`, `hid_set_field()`, `hid_hw_power()`, `hid_hw_request()`, `hid_hw_start()`, `hid_hw_open()`, close, and stop.
- Integrates with the Linux backlight subsystem through `devm_backlight_device_register()` and `backlight_ops`.
- Uses power-management hints to keep the HID endpoint awake while nonzero brightness is active.
- Matches `USB_DEVICE_ID_APPLE_TOUCHBAR_BACKLIGHT` from `hid-ids.h`.
- Provides `BL_CORE_SUSPENDRESUME` so the backlight core calls update paths across suspend/resume.

## Risks and Edge Cases

- The module parameter is an `int`; negative values are not clamped before indexing `appletb_bl_brightness_map`, so a negative `brightness` parameter could index before the array during probe.
- The driver validates that both fields share a report but does not validate field logical ranges. Unexpected descriptors could accept `hid_set_field()` but not behave as intended.
- `hid_hw_request()` has no return value here, so transport failures after field staging are not reported to the backlight core.
- Remove calls `appletb_bl_set_brightness()` and ignores errors, which is reasonable for teardown but can leave hardware lit if the device stops responding.
- Power-state tracking relies on this driver being the only actor controlling the endpoint power hint.

## Test Signals

- Probe tests should verify missing fields, split reports, HID start/open failures, default brightness writes, and backlight registration.
- Parameter tests should cover brightness values 0, 1, 2, values greater than 2, and negative values to expose the lower-bound indexing risk.
- Backlight tests should verify blanking maps to off and normal updates map indices to off/dim/on protocol values.
- Power-management tests should confirm nonzero brightness requests `PM_HINT_FULLON`, off requests `PM_HINT_NORMAL`, and suspend/resume invokes update status.
- Device tests on supported MacBook Pro hardware should observe `/sys/class/backlight/appletb_backlight` brightness changes reflected on the Touch Bar backlight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-bl.c -->
