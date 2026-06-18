
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-cros-ec.c

Purpose: exposes ChromeOS EC GPIOs to Linux through EC commands, with named lines and read/set/get-direction support but no local direction control.

Important APIs/types/functions: callbacks are `cros_ec_gpio_set()`, `cros_ec_gpio_get()`, `cros_ec_gpio_get_direction()`, `cros_ec_gpio_init_names()`, `cros_ec_gpio_ngpios()`, and `cros_ec_gpio_probe()`. It uses EC command structs `ec_params_gpio_set`, `ec_params_gpio_get`, `ec_params_gpio_get_v1`, and `ec_response_gpio_get_v1`.

Control flow: probe adopts the EC transport device fwnode, queries GPIO count via `EC_GPIO_GET_COUNT`, allocates a gpiochip, queries every GPIO name through `EC_GPIO_GET_INFO`, prefixes names with `EC:`, then registers a can-sleep gpiochip. Get and set strip the prefix and issue name-based EC commands. Direction query uses indexed v1 EC GPIO info and interprets input/output flags.

State and persistence behavior: line names are cached in devm memory; values, direction, lock/unlock policy, and persistence live in EC firmware. There is no IRQ, PM state, or local shadow cache.

Dependencies and integration points: depends on ChromeOS EC core/platform data, EC command protocol, platform child device id `cros-ec-gpio`, gpiolib, and firmware-node propagation from the EC transport.

Risks: set operations are allowed only when system policy/EC firmware permits them; failures propagate from `cros_ec_cmd()`. Name buffers depend on EC-provided names fitting command structs. There is no direction setter, so consumers expecting ordinary bidirectional GPIOs may fail. EC latency makes `can_sleep` mandatory.

Test signals: EC command mocking for count/info/get/set, line-name prefix correctness, direction flag interpretation, locked-system set rejection, and probe behavior when EC count or a single info query fails.
