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
