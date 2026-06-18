# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-gpio.c

Purpose: platform-independent bit-banged I2C adapter using GPIO descriptors. It wires SDA/SCL GPIOs into `i2c-algo-bit`, supports firmware/platform-data timing and open-drain properties, and optionally exposes debugfs fault-injection controls.

Important APIs/types/functions: `struct i2c_gpio_private_data` stores SDA/SCL descriptors, `i2c_adapter`, `i2c_algo_bit_data`, platform data, and optional SCL IRQ completion state. Key functions are `i2c_gpio_setsda_val()`, `i2c_gpio_setscl_val()`, `i2c_gpio_getsda()`, `i2c_gpio_getscl()`, `i2c_gpio_get_properties()`, `i2c_gpio_get_desc()`, `i2c_gpio_probe()`, and `i2c_gpio_remove()`. Fault-injector entry points create debugfs attributes for line forcing, incomplete transfers, arbitration loss, and induced panic.

Control flow: probe reads firmware properties or platform data, requests SDA and SCL as open-drain/high GPIOs unless board data says external handling is present, configures callbacks and default timing, and registers the numbered bit-bang adapter with `i2c_bit_add_numbered_bus()`. If both GPIOs are fast, atomic bit-bang transfers are enabled. Fault injection locks the root adapter before directly toggling lines or temporarily making SCL an IRQ input.

State and persistence: persistent state is the GPIO descriptors, bit algorithm timing, adapter number/name, and optional fault-injection completion data. No hardware state is stored beyond GPIO output direction/value and debugfs files under the adapter.

Dependencies and integration: depends on gpiod consumer APIs, firmware property APIs, platform data ABI, `i2c-algo-bit`, debugfs, IRQ support for optional tests, OF compatible `i2c-gpio`, and ACPI ID `LOON0005`. It is registered at `subsys_initcall` so GPIO I2C buses appear early.

Risks: GPIOs that sleep can distort bus timing. Output-only SCL disables clock-stretch detection and defaults to slower timing. Properties such as `*-has-no-pullup` use push-pull-style flags and rely on external electrical correctness. Fault injection can intentionally wedge the bus or panic the system, so it must stay behind `CONFIG_I2C_GPIO_FAULT_INJECTOR`.

Test signals: adapter creation, correct line names and descriptor acquisition, `i2cdetect`/SMBus emulation over GPIO, clock stretching when `getscl` is present, atomic transfer availability for non-sleeping GPIOs, debugfs fault-injection behavior, and clean adapter removal.
