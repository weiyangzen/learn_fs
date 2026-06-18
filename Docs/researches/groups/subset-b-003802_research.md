# Research Group subset-b-003802

Source-tree-aligned grouped research for subset B work item `subset-b-003802`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo.c

## Purpose

`hid-lenovo.c` is the HID special-driver for IBM/Lenovo keyboards, TrackPoint devices, ScrollPoint mice, tablet keyboards, the ThinkPad Pro Dock, and one Lenovo Yoga Slim 7x I2C keyboard. It fixes malformed descriptors, maps vendor usages to Linux input keys, exposes device-specific sysfs controls, drives mute/micmute/Fn-lock LEDs, and sends vendor reports that put TrackPoint keyboards into useful native modes.

## Important APIs, Types, And Functions

The central private state is `struct lenovo_drvdata`, which stores LED report buffers and mutexes, two `led_classdev` objects, Fn-lock work, TrackPoint tuning fields, Compact keyboard sensitivity and middle-click state, and the owning `hid_device`. Driver entry points are collected in `lenovo_driver`: `lenovo_report_fixup()`, `lenovo_input_mapping()`, `lenovo_raw_event()`, `lenovo_event()`, `lenovo_probe()`, `lenovo_remove()`, `lenovo_input_configured()`, and `lenovo_reset_resume()`. Device-specific setup is split across `lenovo_probe_tpkbd()`, `lenovo_probe_cptkbd()`, and `lenovo_probe_tp10ubkbd()`. Sysfs handlers implement `fn_lock`, Compact keyboard `sensitivity` and `middleclick_workaround`, plus ThinkPad USB keyboard TrackPoint knobs `press_to_select`, `dragging`, `release_to_select`, `select_right`, `sensitivity`, and `press_speed`.

## Control Flow

HID core matches `lenovo_devices`, calls report fixup before parsing, then `lenovo_probe()` parses and starts HID hardware. Product id dispatch decides whether extra setup is needed. The ThinkPad USB keyboard path first relies on `lenovo_input_mapping_tpkbd()` marking the TrackPoint subdevice by temporarily setting drvdata to `1`; `lenovo_probe_tpkbd()` then validates feature/output reports, creates TrackPoint sysfs attributes, allocates real drvdata, registers mute LEDs, and sends report 4 settings. Compact USB/Bluetooth and TrackPoint II keyboards allocate drvdata on the mouse/native interface, set defaults, send vendor commands with `lenovo_features_set_cptkbd()`, and create sysfs controls. Tablet/Ultrabook keyboard setup searches output reports for application `0xffa00001`, allocates drvdata, initializes Fn-lock work and LED mutex, programs default Fn-lock state, creates sysfs, and registers LEDs.

Input mapping rewrites vendor usages into standard key codes for Compact keyboards, TrackPoint II keyboards, X1/X12 tablets, ThinkPad 10 Ultrabook keyboards, and ScrollPoint horizontal wheel reports. `lenovo_raw_event()` rewrites the Compact USB Fn-F12 report and synthesizes X12 tablet hotkey input events from raw report id 3. `lenovo_event()` tracks Fn-Esc toggles and implements the Compact middle-button workaround: a middle-button down followed by wheel movement becomes scrolling, while a down/up with no wheel movement emits a real middle click. Removal unregisters sysfs and LEDs per product and stops HID hardware. USB reset resume re-sends Compact keyboard configuration for USB mouse interfaces.

## State And Persistence Behavior

All runtime state is per-HID-device drvdata and is lost on unplug. Hardware state is explicitly programmed through feature/output reports: TrackPoint selection/sensitivity settings, Compact keyboard native middle-button mode and Fn-lock/sensitivity, and TP10/X1/X12 LED/Fn-lock output report 9. `fn_lock`, sensitivity, and TrackPoint tuning values persist only in kernel memory while the device is bound; the driver re-applies Compact settings on reset resume but does not persist user settings across rebinds. LED state is cached in `led_state`; TP10-style LED output uses `led_report_mutex` because one shared 3-byte output buffer is reused. Fn-lock LED sync for TP10-style devices is deferred through `fn_lock_sync_work`.

## Dependencies And Integration Points

The file integrates with HID parsing/mapping, Linux input events, sysfs attribute groups, LED class triggers `audio-mute` and `audio-micmute`, workqueues, mutexes, USB/Bluetooth/I2C HID ids from `hid-ids.h`, and PM reset-resume through `pm_ptr()`. It intentionally binds only selected generic HID groups for tablet keyboards so other drivers such as `hid-multitouch` can handle touchpad/TrackPoint portions.

## Risks And Test Signals

Risks are concentrated around fixed descriptor offsets and product-specific report assumptions: bad firmware revisions could make report fixups corrupt descriptors, missing reports return `-ENODEV`, and raw-event casts require sufficiently sized reports. The Compact keyboard sysfs setters call `lenovo_features_set_cptkbd()` without rolling back partial vendor-command failures, so user-visible state can diverge from hardware. Test signals include successful HID probe for each id, expected evtest key codes for Fn hotkeys, no duplicate wheel/middle events, functional TrackPoint sysfs writes, LED class brightness changes, X12 raw hotkey synthesis, reset-resume reconfiguration, and clean unbind with no pending work or LED leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-letsketch.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-letsketch.c

## Purpose

`hid-letsketch.c` supports the LetSketch/VSON WP9620N drawing tablet family by switching the USB device into a vendor raw-report mode and exposing clean Linux input devices for the pen tablet and pad buttons. Without this driver, only part of the active area works and buttons are hardwired to keyboard or mouse shortcuts.

## Important APIs, Types, And Functions

`struct letsketch_data` stores the HID device, two input devices, and an in-range timer. `letsketch_probe()` owns the USB-only raw-mode handshake and device registration. `letsketch_setup_input_tablet()` registers the absolute pen device with `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, `BTN_TOOL_PEN`, `BTN_TOUCH`, and stylus buttons. `letsketch_setup_input_tablet_pad()` registers a pad input device with five `BTN_0`-based buttons and dummy ABS axes for udev/libwacom compatibility. `letsketch_raw_event()` decodes 12-byte report id 8 packets. `letsketch_get_string()` wraps the fragile USB string-descriptor reads needed for mode switching.

## Control Flow

Probe rejects non-USB HID devices and all interfaces except interface 0. It then performs the vendor handshake by slowly reading string descriptors `0xc8..0xca`, descriptors `1..250`, descriptor `0x64`, and `0xc8` again, retrying each read up to five times with `usleep_range()` because the firmware fails when polled too quickly. After a final delay, HID parsing runs, drvdata is allocated, the pen and pad input devices are registered, and HID hardware starts with `HID_CONNECT_HIDRAW` rather than normal hid-input. Input device open/close calls directly open/close HID hardware.

Raw reports with header nibble `0x80` update the pen device: in-range is asserted, touch/stylus bits are decoded from `raw_data[1]`, little-endian X/Y/pressure fields are reported, and a 100 ms timer is armed to synthesize out-of-range because firmware never sends an explicit leave event. Header nibble `0xe0` updates the pad device by treating `raw_data[4]` values 1 through 5 as mutually exclusive button presses. Unknown headers are warned and ignored.

## State And Persistence Behavior

State is minimal and devm-managed. The tablet raw-mode state is a firmware mode established by USB descriptor reads during probe and lasts until reset/unplug. Input state is transient event state plus the timer-maintained `BTN_TOOL_PEN` in-range bit. The driver does not expose sysfs or persistent configuration.

## Dependencies And Integration Points

The driver depends on USB HID, `usb_string()`, input core, timers, `get_unaligned_le16()`, and device ids from `hid-ids.h`. It bypasses ordinary parsed HID input by using only hidraw plus custom input devices, which is necessary because the useful data format is vendor-specific and the other USB interfaces become disabled after raw mode is enabled.

## Risks And Test Signals

Risks include the unusual descriptor-read handshake, long probe latency from 250 string reads, strict fixed 12-byte raw packet expectations, no explicit remove callback for deleting the timer, and unknown behavior on rebranded devices with slightly different report formats. Test with interface filtering, successful raw-mode transition, libinput/libwacom detection, full active-area coordinates, pressure range to 8192, both stylus buttons, five pad buttons, in-range timeout behavior when the pen leaves, and suspend/unplug races around the timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-letsketch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg-g15.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg-g15.c

## Purpose

`hid-lg-g15.c` implements special handling for Logitech G13/G15/G15 v2/G510 gaming keyboards and Z-10 speakers. It disables undesirable G-key keyboard emulation, creates dedicated input devices for macro/LCD/menu controls, and registers LED class devices for keyboard backlights, LCD backlights, macro preset LEDs, macro record LEDs, and multicolor backlights.

## Important APIs, Types, And Functions

Model identity is carried in `enum lg_g15_model`; LED slots are defined by `enum lg_g15_led_type`. `struct lg_g15_data` is the main state block: DMA-aligned transfer buffer, mutex, work item, input devices, HID device, model, LED array, game-mode state, and cached hardware backlight toggle state. `struct lg_g15_led` wraps either `led_classdev` or `led_classdev_mc`. Major functions include `lg_g15_probe()`, `lg_g15_raw_event()`, model-specific event decoders `lg_g13_event()`, `lg_g15_event()`, `lg_g15_v2_event()`, `lg_g510_event()`, LED readers/writers for G13/G15/G510, and registration helpers `lg_g15_register_led()`, `lg_g15_setup_led_rgb()`, and input init helpers.

## Control Flow

Probe enables `HID_QUIRK_INPUT_PER_APP`, parses reports, and only takes over interfaces with an input report application of `0xff000000`; other interfaces fall back to generic HID. It allocates model state and custom input devices, chooses a HID connect mask, starts hardware, disables G-key F-key emulation through either output or feature reports, reads initial LED/backlight state, registers model-appropriate input devices, and registers LEDs. G13 gets two input devices, one macropad and one simplified joystick, because the thumbstick should look like a real joystick. G15/G15 v2 use hidraw only because disabling emulated keyboard input makes the built-in emulated keyboard useless. G510 keeps both hid-input and hidraw.

Raw events dispatch by model, report id, and report size. G13 decodes keybits into macro/LCD keys, reports thumbstick buttons and ABS axes on the joystick device, and notices hardware backlight-toggle changes. G15/G15 v2 decode G-keys, M-keys, macro record, LCD menu buttons, and schedule work when the backlight-cycle key changes brightness behind the driver's cache. G510 decodes 18 G-keys, game-mode slider state, M-keys, LCD menu keys, headphone mute, mic mute as `KEY_F20`, and a separate input report for hardware backlight toggle. Work functions either refresh hardware LED brightness and notify LED core or re-sync G510 RGB values after hardware backlight re-enable.

## State And Persistence Behavior

The transfer buffer and LED brightness cache are protected by `g15->mutex`. LED brightness state is partly hardware-readable and partly last-written, depending on model. G13 power-up defaults are not persistent; the driver reads the current RGB/macro state and hardware backlight bit. G15/G15 v2 brightness is read through feature report 2. G510 stores two RGB multicolor LEDs: keyboard brightness and power-on/reset backlight value. Hardware backlight toggle state is represented as `backlight_disabled` and surfaced through `LED_BRIGHT_HW_CHANGED` notifications rather than by rewriting brightness immediately.

## Dependencies And Integration Points

The file integrates with HID raw requests, Linux input, LED class and multicolor LED class, `dt-bindings/leds/common.h` color ids, workqueues, mutexes, and Logitech USB ids. It deliberately reports gaming controls as Linux macro and LCD-menu key codes for userspace daemons. LED names such as `g15::kbd_backlight`, `g13:rgb:kbd_backlight`, and `g15::power_on_backlight_val` are stable userspace integration points.

## Risks And Test Signals

Risks include strict report ids/sizes per model, fallback semantics if disabling G-key emulation fails, missing explicit remove/cancel-work path because devm handles most objects but queued work can still touch hardware, and fragile LED state when hardware buttons change brightness while software writes are in flight. Test by probing each supported model/interface combination, verifying no duplicate F-key events for G-keys, evtest coverage for all macro/LCD/menu controls, G13 joystick recognition, RGB and single-color LED get/set, hardware brightness-change notifications, G510 game-mode logging, Z-10 LCD menu keys, unplug during LED writes, and KVM/error paths where feature GET reports fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg-g15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg.c

## Purpose

`hid-lg.c` is the main Logitech special HID driver for older receivers, keyboards, joysticks, gamepads, 3D controllers, and wheels. It applies descriptor replacements/fixups, remaps vendor usages, adjusts mapped input metadata, forwards wheel raw/input events to `hid-lg4ff`, initializes the appropriate force-feedback backend, and exposes the module parameter controlling automatic wheel native-mode switching.

## Important APIs, Types, And Functions

`struct lg_drv_data` is allocated here and shared with force-feedback modules through `hid-lg.h`; it stores quirk bits and optional device-specific properties. Quirk flags include descriptor fixups (`LG_RDESC`, `LG_RDESC_REL_ABS`), input quirks (`LG_BAD_RELATIVE_KEYS`, `LG_DUPLICATE_USAGES`, `LG_EXPANDED_KEYMAP`, `LG_IGNORE_DOUBLED_WHEEL`, `LG_WIRELESS`, `LG_INVERT_HWHEEL`), transport quirk `LG_NOGET`, and force-feedback selectors `LG_FF`, `LG_FF2`, `LG_FF3`, `LG_FF4`. Main entry points are `lg_report_fixup()`, `lg_input_mapping()`, `lg_input_mapped()`, `lg_event()`, `lg_raw_event()`, `lg_probe()`, and `lg_remove()`.

## Control Flow

Probe requires USB HID, ignores nonzero G29 interfaces, allocates drvdata, applies `HID_QUIRK_NOGET` when requested, parses descriptors, clears `HID_CONNECT_FF` for devices handled by a custom force-feedback backend, and starts HID hardware. The Wii wheel path performs a two-step feature report setup with a small wait and random address bytes. Probe then calls exactly one FF initializer: `lgff_init()`, `lg2ff_init()`, `lg3ff_init()`, or `lg4ff_init()`. If initialization fails, HID hardware is stopped and drvdata is freed.

Report fixup either edits descriptor bytes in place or replaces the full report descriptor for known wheels whose original descriptors hide separate pedal axes or misdescribe controls. Input mapping handles Ultra X remote vendor usages, wireless receiver consumer-page usages, expanded Logitech button maps, and ignored duplicate wheel buttons. `lg_input_mapped()` clears bad relative-key flags, clears duplicate usage bits, and marks Logitech wheel ABS axes as `HID_GD_MULTIAXIS` to avoid generic fuzz/flat values. Runtime `lg_event()` inverts horizontal wheel events when requested and delegates FF4 input adjustment; `lg_raw_event()` delegates FF4 pedal combining.

## State And Persistence Behavior

Persistent driver state is one `lg_drv_data` per bound HID device. For FF4 wheels, `drv_data->device_props` is allocated and freed by `hid-lg4ff.c`. Descriptor fixups are applied only during parse. The Wii wheel feature setup and force-feedback state live in hardware until reset. `lg4ff_no_autoswitch` is a module parameter visible across all devices while the module is loaded.

## Dependencies And Integration Points

The file depends on USB HID, usbhid helpers, random bytes, wait queues, Linux input/HID mapping APIs, Logitech ids, and optional FF modules declared by `hid-lg.h` and `hid-lg4ff.h`. Kconfig controls whether `lgff_init()`, `lg2ff_init()`, `lg3ff_init()`, and `lg4ff_init()` are real functions or stubs returning failure.

## Risks And Test Signals

Risks include descriptor replacements keyed only by product id and original size, quirk interactions that can remove expected input bits, custom FF init failures aborting entire probe, G29 interface filtering, and mode-switching side effects in `lg4ff_init()` that can trigger USB reset. Test with `hid-recorder`/evtest on each quirk family, descriptor size mismatch logging, force-feedback upload/playback, Wii wireless setup, wheel axes with no fuzz/flat, horizontal wheel inversion, duplicate usage suppression, and module parameter `lg4ff_no_autoswitch` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg.h

## Purpose

`hid-lg.h` is the shared internal header for the Logitech special HID driver and its force-feedback helper files. It provides the common per-device state shape and feature-gated initializer declarations.

## Important APIs, Types, And Functions

`struct lg_drv_data` contains `unsigned long quirks` and `void *device_props`. `quirks` is set by `hid-lg.c` device-table driver data and read by event, raw-event, mapping, and FF paths. `device_props` is intentionally untyped so `hid-lg4ff.c` can attach its `struct lg4ff_device_entry` without exposing wheel internals in the main header. The header declares `lgff_init()`, `lg2ff_init()`, and `lg3ff_init()` when their Kconfig symbols are enabled and provides inline stubs returning `-1` otherwise.

## Control Flow

The header has no standalone runtime flow. Compile-time Kconfig decides whether the main driver can call real FF initializers or receives a guaranteed failure from the stub, causing `lg_probe()` to unwind if a device table selects a disabled FF backend.

## State And Persistence Behavior

No state is allocated here. The struct layout is persistent ABI only inside this driver family: `hid-lg.c` allocates and frees `lg_drv_data`, while force-feedback modules read or extend it during probe and remove.

## Dependencies And Integration Points

The prototypes assume `struct hid_device` is visible from including C files. This header is included by `hid-lg.c`, `hid-lgff.c`, `hid-lg2ff.c`, `hid-lg3ff.c`, and `hid-lg4ff.c`, forming the compile-time contract among the Logitech driver pieces.

## Risks And Test Signals

The main risk is config mismatch: a product table entry using `LG_FF`, `LG_FF2`, or `LG_FF3` will fail probe if the corresponding Kconfig option is disabled. Build tests across Logitech FF config combinations and probe tests for FF-enabled devices are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg2ff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg2ff.c

## Purpose

`hid-lg2ff.c` provides memless rumble support for Logitech RumblePad/RumblePad 2 style devices selected by `LG_FF2` in `hid-lg.c`.

## Important APIs, Types, And Functions

`struct lg2ff_device` holds the output `hid_report` used for rumble commands. `lg2ff_init()` validates the first input device and output report 0 field 0 with at least seven values, allocates the private object, sets `FF_RUMBLE`, creates a memless FF device, initializes the report to a stop command, and sends it. `play_effect()` translates Linux `FF_RUMBLE` magnitudes into Logitech report bytes.

## Control Flow

`lg_probe()` starts HID hardware with generic FF disabled, then calls `lg2ff_init()`. Initialization uses the first HID input device as the FF device and stores `lg2ff_device` as memless callback data. On each rumble effect, strong and weak magnitudes are scaled from 16-bit input FF units to 8-bit device units. Nonzero rumble sends command `0x51` with weak in value index 2 and strong in index 4; zero rumble sends command `0xf3` with both magnitudes cleared. Each effect is sent with `hid_hw_request(..., HID_REQ_SET_REPORT)`.

## State And Persistence Behavior

The only private state is the allocated `lg2ff_device` referenced by input FF core. The output report object belongs to HID core. Hardware rumble state persists until another effect command or stop command is sent; initialization explicitly sends a stopped state.

## Dependencies And Integration Points

This file depends on Linux input force-feedback memless support, HID output reports, and the shared Logitech header. It is not a HID driver by itself; it is called by `hid-lg.c` for devices marked `LG_FF2`.

## Risks And Test Signals

Risks include assuming the first HID input is the desired gamepad, accepting only one fixed output report layout, and no explicit cleanup callback beyond input core lifetime. Test by probing RumblePad variants, verifying `FF_RUMBLE` appears in `ffbit`, playing weak/strong/combined effects through `fftest`, stopping effects, and checking malformed descriptors fail cleanly with `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg2ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg3ff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg3ff.c

## Purpose

`hid-lg3ff.c` implements force feedback for the Logitech Flight System G940, selected by `LG_FF3` in the main Logitech driver. It supports constant force and autocenter commands for the stick's X and Y axes.

## Important APIs, Types, And Functions

`lg3ff_init()` validates that an input device exists and output report 0 field 0 has at least 35 values, sets `FF_CONSTANT` and `FF_AUTOCENTER`, creates a memless FF device, and attaches `hid_lg3ff_set_autocenter()` if autocenter is available. `hid_lg3ff_play()` writes constant-force command bytes. `hid_lg3ff_set_autocenter()` writes the discovered autocenter pattern into both X and Y axis command regions.

## Control Flow

The main driver disables generic FF and calls `lg3ff_init()`. Runtime FF playback clears the entire output report value array, handles `FF_CONSTANT`, reads X/Y levels from the ramp fields used by memless force feedback, writes command `0x51`, stores negated two's-complement X at index 1 and Y at index 31, then sends the report. Autocenter writes command `0x51` plus fixed values at indices 1..4 and 31..34 and sends the report. The comments note a hardware deadman's switch must be covered for effects to work.

## State And Persistence Behavior

There is no additional heap state. The driver mutates the HID output report value buffer and relies on HID/input core for FF object lifetime. Hardware force state persists until overwritten by later commands.

## Dependencies And Integration Points

It depends on the first HID input device, Linux input memless FF, and `hid_validate_values()` against the G940 output report shape. It is built only when `CONFIG_LOGIG940_FF` provides the real initializer declared in `hid-lg.h`.

## Risks And Test Signals

Risks include using ramp fields for constant-force X/Y levels, assuming exactly one fixed report layout, sign conventions that differ from other Logitech sticks, and clearing all output fields before each effect. Test by confirming `FF_CONSTANT`/`FF_AUTOCENTER` exposure, positive and negative X/Y force direction, autocenter strength, deadman's switch behavior, and clean failure when reports or inputs are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg3ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.c

## Purpose

`hid-lg4ff.c` is the advanced force-feedback and mode-management layer for Logitech racing wheels. It supports Driving Force/Formula EX, WingMan Formula GP/Force GP, MOMO, DFP, G25, DFGT, G27, G29, MOMO Racing, and Wii Speed Force devices. Beyond FF playback, it handles pedal-combine emulation, steering range control, multimode wheel identification and switching, real-id reporting, alternate-mode sysfs, and optional RPM LEDs.

## Important APIs, Types, And Functions

`struct lg4ff_device_entry` stores a spinlock-protected output report and `struct lg4ff_wheel_data`. `lg4ff_wheel_data` stores current product id, real product id, pedal-combine flag, current/min/max range, range setter, alternate modes, real model strings, and optional LED state. Static tables describe supported wheels, multimode wheels, alternate modes, identification masks, and vendor mode-switch command sequences. External functions used by `hid-lg.c` are `lg4ff_init()`, `lg4ff_deinit()`, `lg4ff_adjust_input_event()`, and `lg4ff_raw_event()`.

## Control Flow

Initialization validates the first input device and seven-byte output report, allocates the device entry, stores it in `lg_drv_data->device_props`, identifies whether the device is a multimode wheel using reported product id plus USB `bcdDevice`, and may automatically switch a wheel from Driving Force emulation to native mode. If switching is triggered, initialization returns after the vendor command because the wheel will reset. Otherwise it selects the matching wheel table entry, advertises FF bits, creates a memless FF device with `lg4ff_play()`, initializes wheel data, sets autocenter handling, creates sysfs files, programs maximum steering range, and registers optional five-segment RPM LEDs for G27/G29.

Runtime FF playback only handles `FF_CONSTANT`: neutral force sends a deactivate command for slot 1, while non-neutral force sends slot 1 command `0x11` with an 8-bit force centered at `0x80`. Autocenter has a default command path and a Formula Force EX-specific path. Range setters use either G25/G27/DFGT/G29 command `0xf8 0x81` or the DFP two-stage coarse/fine limit protocol. Raw-event adjustment optionally rewrites pedal bytes to synthesize combined pedals; input-event adjustment rescales DFP X axis for limited ranges. Sysfs writes can combine pedals, change range, or switch alternate compatibility modes using vendor commands.

## State And Persistence Behavior

Per-device state lives in `lg_drv_data->device_props` until `lg4ff_deinit()`. Report writes are protected by `report_lock` because FF callbacks, LED writes, sysfs writes, and range/autocenter operations reuse the same output report buffer. Sysfs `combine_pedals` and `range` mutate cached wheel data; range also programs hardware if supported. Multimode switch state is mostly hardware state and may cause USB detach/reset. LED state is cached as a five-bit mask and mirrored to hardware with `lg4ff_set_leds()`.

## Dependencies And Integration Points

This file depends on USB descriptors, HID output reports, Linux input FF, sysfs device attributes, optional LED class, shared `lg_drv_data`, `hid-lg4ff.h`, and `lg4ff_no_autoswitch` exported by `hid-lg.c`. It is tightly coupled to the main Logitech driver, which delegates FF4 raw and input events and calls deinit on remove.

## Risks And Test Signals

Risks include many hard-coded vendor commands, multimode identification from `bcdDevice` masks, automatic native-mode switching that intentionally interrupts probe, sysfs parsing via `simple_strtoul()`, unsupported range writes being silently ignored, and concurrent access to shared output reports. Test signals include `fftest` constant force and autocenter, range sysfs bounds and DFP axis rescaling, pedal combine raw reports for every product layout, alternate-mode listing and switching with/without `lg4ff_no_autoswitch`, real-id for multimode wheels, G27/G29 RPM LED registration, clean deinit removing sysfs/LEDs, and no use-after-free during unplug while FF or sysfs operations run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.h -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.h

## Purpose

`hid-lg4ff.h` is the compile-time interface between the main Logitech HID driver and the Logitech wheel force-feedback module.

## Important APIs, Types, And Functions

When `CONFIG_LOGIWHEELS_FF` is enabled, it declares the module parameter storage `lg4ff_no_autoswitch` and four functions: `lg4ff_adjust_input_event()`, `lg4ff_raw_event()`, `lg4ff_init()`, and `lg4ff_deinit()`. The adjustment functions receive `struct lg_drv_data *` so they can access FF4 wheel properties stored by the initializer. When the config is disabled, inline stubs return neutral values: event/raw adjustments return `0`, init/deinit return `-1`.

## Control Flow

The header has no runtime flow. `hid-lg.c` uses it to compile the same delegation calls regardless of Kconfig. With FF4 enabled, wheel products selected by `LG_FF4` enter the real module. With FF4 disabled, a selected FF4 product will fail probe after `lg4ff_init()` returns `-1`.

## State And Persistence Behavior

No state is owned here. The only declared state is the external `lg4ff_no_autoswitch`, which is defined and exposed as a module parameter in `hid-lg.c` when FF4 is built.

## Dependencies And Integration Points

The header assumes the including file has the HID and Logitech private types visible. It is included by both `hid-lg.c` and `hid-lg4ff.c` and is the boundary that allows FF4 support to be optional.

## Risks And Test Signals

Risks are limited to Kconfig behavior and prototype drift. Build with and without `CONFIG_LOGIWHEELS_FF`, then probe an `LG_FF4` wheel to verify enabled builds initialize and disabled builds fail predictably rather than linking missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lg4ff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lgff.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-lgff.c

## Purpose

`hid-lgff.c` provides the older generic Logitech force-feedback backend for WingMan Cordless RumblePad, WingMan Force 3D, and related Logitech devices selected by `LG_FF` in the main driver. It supports rumble, constant force, and optional autocenter depending on product id.

## Important APIs, Types, And Functions

`struct dev_type` maps vendor/product ids to an FF capability list. Static capability arrays describe rumble-only, joystick constant-force, and joystick constant-force plus autocenter devices. `lgff_init()` validates input/report layout, selects capabilities from the table, sets input FF bits, creates a memless FF device, and assigns `hid_lgff_set_autocenter()` when supported. `hid_lgff_play()` writes device reports for `FF_CONSTANT` and `FF_RUMBLE`.

## Control Flow

After `hid-lg.c` starts HID hardware with generic FF disabled, it calls `lgff_init()` for `LG_FF` products. Initialization uses the first input device and output report 0 field 0 requiring at least seven values. If the product is not in the table, it defaults to constant-force joystick behavior. Runtime constant-force effects offset X/Y ramp levels by `0x7f`, clamp to 8-bit values, write command `0x51 0x08 x y`, and send the report. Rumble effects scale weak/strong magnitudes to 8-bit left/right values, write command `0x42`, and send the report. Autocenter writes a seven-byte `0xfe 0x0d` command with a 4-bit magnitude.

## State And Persistence Behavior

This backend does not allocate private per-device state. It writes directly into the first output report's value buffer. Hardware force/rumble/autocenter state persists until another report overwrites it or the device resets.

## Dependencies And Integration Points

It depends on Linux input memless FF, HID output reports, and the main Logitech driver for device matching and lifecycle. It is enabled by `CONFIG_LOGITECH_FF` through the declaration in `hid-lg.h`.

## Risks And Test Signals

Risks include defaulting unknown table matches to joystick constant-force, assuming the first input and first output report are correct, shared report buffer mutation without a private lock, and differing sign/centering conventions from FF3/FF4. Test with product-specific FF bit exposure, `fftest` rumble and constant force, autocenter magnitude changes, malformed report validation, and repeated start/stop effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-lgff.c -->
