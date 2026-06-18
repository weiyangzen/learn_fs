# sources/distributed-fs/ceph-client/drivers/leds/leds-upboard.c

Purpose: platform LED driver for UP Board FPGA-managed status LEDs. It exposes board-specific LED profiles through regmap fields in the parent FPGA MFD.

Important APIs, types, and functions: `struct upboard_led` stores one regmap field and LED class device. `struct upboard_led_profile` maps LED names to bit positions. `upboard_led_brightness_get()` reads the bit, and `upboard_led_brightness_set()` writes boolean brightness. `upboard_led_probe()` chooses the UP or UP2 profile from parent FPGA type and registers one LED per profile entry.

Control flow: probe gets the parent `struct upboard_fpga`, selects the static profile array, allocates each LED, creates a field for `UPBOARD_REG_FUNC_EN0` bit `bit`, assigns get/set callbacks and name, and registers each LED with devm.

State and persistence: state is the FPGA register bit. The driver has no aggregate private state and relies on devm allocations. Brightness max is `LED_ON`, so LEDs are binary.

Dependencies and integration points: UP Board FPGA MFD, regmap fields, platform devices, LED class, and two board type profiles.

Risks and test signals: test unknown FPGA type rejection, per-bit field allocation, read failure returning off, binary brightness writes, and correct LED naming/profile for UP versus UP2 hardware.
