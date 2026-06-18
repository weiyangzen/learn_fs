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
