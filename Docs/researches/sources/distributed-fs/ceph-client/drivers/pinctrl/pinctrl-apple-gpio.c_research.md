# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-apple-gpio.c

Purpose: Implements Apple SoC pinctrl, GPIO, pinmux, and external IRQ support. It dynamically creates one group per pin and four functions (`gpio`, `periph1`, `periph2`, `periph3`) using the `apple,npins` DT property.

Important APIs and functions: Register helpers are `apple_gpio_set_reg()` and `apple_gpio_get_reg()` over a flat regmap. DT map parsing is `apple_gpio_dt_node_to_map()`. Pinmux uses `apple_gpio_pinmux_func_is_gpio()` and `apple_gpio_pinmux_set()`. GPIO methods handle direction, get, set, input, and output. IRQ methods are ack, mask, unmask, startup, type selection, and chained `apple_gpio_irq_handler()`. Probe and registration are `apple_gpio_pinctrl_probe()` and `apple_gpio_register()`.

Control flow: Probe reads interrupt-controller status and parent IRQ count, allocates flexible-array driver state, reads `apple,npins`, builds pin descriptors/names/numbers, maps MMIO, initializes regmap, registers pinctrl, adds generic one-pin groups and functions, then registers gpiochip and optional hierarchical parent IRQ data. DT pinmux parsing reads each packed `pinmux` cell, extracts `APPLE_PIN()` and `APPLE_FUNC()`, validates function index, and emits mux maps. IRQ handling receives a parent group pointer, recovers the controller via the `irqgrps` flexible array, reads pending bits per 32-pin block for that group, and dispatches child IRQs.

State and persistence: `struct apple_gpio_pinctrl` owns the MMIO base, regmap cache, pinctrl descriptor, gpiochip, and IRQ group mapping. Register fields persist mode, data, peripheral selection, input enable, pull, drive, Schmitt, group, and lock status. No suspend state is explicitly saved in this file.

Dependencies and integration points: Uses `dt-bindings/pinctrl/apple.h`, OF, regmap MMIO, generic pinctrl/pinmux helper registries, gpiolib, and IRQ core. Compatible strings are `apple,t8103-pinctrl` and `apple,pinctrl`.

Risks: `apple_gpio_get_reg()` returns 0 on regmap read failure, which can look like a valid low/input state. `apple_gpio_register()` allocates parent IRQ arrays manually, passes them to `devm_gpiochip_add_data()`, then frees them; this relies on gpiolib copying needed data during registration. The IRQ group recovery pointer arithmetic is compact and depends on `irqgrps[i] == i`.

Test signals: DT pinmux parsing for valid/invalid functions, GPIO direction/value changes, input reads using uncached MMIO, IRQ startup/type/mask/unmask for all trigger types, multiple parent IRQ groups, and probe without interrupt-controller validate the driver.
