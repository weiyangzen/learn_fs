# sources/distributed-fs/ceph-client/include/linux/led-class-multicolor.h

Purpose: declares the LED multicolor class extension for RGB or other compound LEDs made from multiple color channels.

Important APIs and types: `struct mc_subled` describes color index, current brightness, intensity, and hardware channel. `struct led_classdev_mc` embeds `led_classdev`, a color count, and sub-LED array. Helpers convert base class devices to multicolor devices, register/unregister regular or devm devices, and compute per-channel components via `led_mc_calc_color_components()`.

Control flow: a driver populates subled metadata and registers through the multicolor class; brightness changes are decomposed into component intensities before the driver's base brightness callback writes hardware.

State and persistence: component intensities and brightness are in-memory class state and mirrored to device registers by the driver. No durable state is owned here.

Dependencies and integration points: depends on `leds.h` and DT LED color bindings; integrates compound LEDs with the generic LED sysfs and trigger model.

Risks and test signals: risks include mismatched `num_colors`, invalid color/channel mapping, and inconsistency between aggregate brightness and per-channel intensities. Test RGB and non-RGB devices, devm cleanup, brightness/color calculations, trigger updates, and invalid subled arrays.
