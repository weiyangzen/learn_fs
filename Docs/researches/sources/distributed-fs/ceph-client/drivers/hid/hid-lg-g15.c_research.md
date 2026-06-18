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
