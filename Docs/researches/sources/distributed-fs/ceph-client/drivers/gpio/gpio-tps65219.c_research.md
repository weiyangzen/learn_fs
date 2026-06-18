<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c

Purpose: exposes GPIO/GPO pins on TPS65214/TPS65215/TPS65219 PMICs while respecting different line counts and GPIO0 direction rules.

Important APIs, types, and functions: `struct tps65219_gpio` stores a chip-specific `change_dir` callback, gpiochip, and parent PMIC. There are separate templates and get_direction helpers for TPS65214 and TPS65219. Shared callbacks are `tps65219_gpio_get()`, `tps65219_gpio_set()`, `tps65219_gpio_direction_input()`, and `tps65219_gpio_direction_output()`.

Control flow: probe selects the TPS65214 two-line template or TPS65219 three-line template from the platform ID, installs the appropriate direction-change callback, and registers the chip. Nonzero offsets are output-only GPOs. GPIO0 can be input or output depending on PMIC/NVM state; TPS65219 refuses Linux direction changes because the spec says the bit is NVM/initialize-state controlled, while TPS65214 allows direction changes after validating that the multifunction pin is configured as GPIO rather than VSEL.

State and persistence behavior: PMIC registers hold value and direction. No software cache is maintained.

Dependencies and integration points: depends on `linux/mfd/tps65219.h`, parent regmap, platform IDs for TPS65214/TPS65219, and gpiolib.

Risks and test signals: `tps65219_gpio_get()` calls the TPS65219 get_direction helper even for TPS65214, which deserves regression coverage. GPIO0 status is documented as multifunction and logs a warning. Test chip-ID template selection, output-only errors, TPS65219 NVM direction refusal, TPS65214 VSEL rejection, GPIO0 get behavior, and value bit mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65219.c -->
