# sources/distributed-fs/ceph-client/drivers/leds/leds-lp5562.c

Purpose: LP5562 four-channel RGBW LED engine driver using LP55xx common framework with chip-specific RGB/W engine muxing and predefined pattern support.

Important APIs/types/functions: `lp5562_cfg` provides LP55xx common register hooks and chip callbacks. `lp5562_post_init_device()` sets direct mode, clock config, clears PWM, and maps LEDs to register PWM. `lp5562_led_brightness()` and `lp5562_multicolor_brightness()` write channel PWM registers. `lp5562_run_predef_led_pattern()` loads predefined RGB programs and runs engines. Sysfs stores `led_pattern` and `engine_mux`.

Control flow: common `lp55xx_probe` performs device setup. Brightness uses direct PWM registers under the common lock. Pattern sysfs mode 0 stops engines; nonzero modes load common platform pattern arrays into three engine memories, map RGB to engines, and start engines. `engine_mux` maps RGB fixed engines or W to the currently selected engine.

State and persistence: common LP55xx chip state stores engine index, lock, LED/current data, and platform patterns. Hardware stores program memory, engine selection, PWM/current, and enable/opmode.

Dependencies/integration: LP55xx common framework, firmware/platform predefined patterns, I2C, LED multicolor support, sysfs device attributes.

Risks: predefined pattern pointer arithmetic assumes `mode <= num_patterns` and valid pattern data; program size must be below page size. `engine_mux` for W depends on current `chip->engine_idx`, which is set by other sysfs engine controls. Pattern loading is RGB-only, with W handled separately by mux.

Test signals: RGBW brightness writes, pattern off/on modes, program-size overflow rejection, engine mux strings `RGB` and `W`, engine timing waits, firmware loading, and common remove cleanup.
