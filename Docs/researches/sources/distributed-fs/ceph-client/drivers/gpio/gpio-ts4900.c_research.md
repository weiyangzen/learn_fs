<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c

Purpose: exposes Technologic Systems I2C FPGA digital I/O lines, including TS-4900 style separate input bits and TS-7970 style input-on-output-bit variants.

Important APIs, types, and functions: `struct ts4900_gpio_priv` stores regmap, gpiochip, and selected input bit. GPIO callbacks are get_direction, direction_input, direction_output, get, and set. The regmap uses 16-bit register addresses and 8-bit values.

Control flow: I2C probe reads optional `ngpios` defaulting to 32, selects the input bit from OF match data, initializes an I2C regmap, and registers a sleeping gpiochip. Direction_input clears OE with a read-modify-write to avoid racing output data. Direction_output preloads the output bit before enabling OE when transitioning from input to output to avoid line glitches.

State and persistence behavior: no software cache. Each GPIO offset is a separate FPGA register containing OE, OUT, and IN/status bits.

Dependencies and integration points: depends on I2C, regmap, OF compatibles `technologic,ts4900-gpio` and `technologic,ts7970-gpio`, optional `ngpios`, and gpiolib.

Risks and test signals: several regmap reads ignore return status before using `reg`, so bus failures can produce undefined decisions. Direction_output writes whole register values rather than masked updates in the final step. Test both compatible input-bit modes, glitchless transition ordering, ngpio override, regmap error injection, and per-offset register addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ts4900.c -->
