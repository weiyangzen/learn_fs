# sources/distributed-fs/ceph-client/drivers/leds/leds-lp3952.c

Purpose: TI LP3952 I2C RGB LED-array driver using regmap, ACPI/device properties for LED labels, reset GPIO, and fixed pattern-generator initialization.

Important APIs/types/functions: `lp3952_register_write()` wraps regmap writes with logging. `lp3952_on_off()` updates LED enable bits. `lp3952_set_brightness()` uses four-level current control plus on/off. `lp3952_register_led_classdev()` registers named LEDs only for labels found in device properties. `lp3952_set_pattern_gen_cmd()` writes packed pattern-generator commands. `lp3952_configure()` disables LEDs and initializes pattern/active mode.

Control flow: probe allocates private state, asserts `nrst` GPIO high with a devm action to drive it low on cleanup, initializes regmap, configures the chip, then registers available LED classdevs from labels `blue2`, `green2`, `red2`, `blue1`, `green1`, `red1`.

State and persistence: per-channel classdev state is in `lp3952_led_array`; hardware stores active mode, enable bits, current levels, and pattern generator command.

Dependencies/integration: LP3952 platform header for register and enum definitions, I2C regmap, GPIO descriptor, device properties/ACPI labels, LED class.

Risks: no remove callback beyond devm cleanup; LED outputs are not explicitly disabled except reset GPIO action. Brightness only supports 0-4. Registration returns `-ENODEV` if no labels are found. Pattern generator setup is fixed and not exposed.

Test signals: reset GPIO lifecycle, property-label based registration, brightness value mapping and channel validation, all-labels-missing behavior, and regmap write failure propagation.
