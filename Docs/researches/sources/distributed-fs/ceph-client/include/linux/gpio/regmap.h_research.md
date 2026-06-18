<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h

Purpose: This header describes a generic GPIO controller backed by Linux regmap. It lets MFD/regmap devices expose GPIO lines without hand-writing a full `gpio_chip`.

Important APIs/types/functions: `GPIO_REGMAP_ADDR_ZERO` and `GPIO_REGMAP_ADDR()` encode optional register base zero. `struct gpio_regmap_config` supplies parent, regmap, optional firmware node/label/names, GPIO count, data/set/clear/direction register bases, stride, GPIOs per register, optional IRQ domain, optional `fixed_direction_output` bitmap, optional regmap-IRQ chip/line/flags under `CONFIG_REGMAP_IRQ`, `reg_mask_xlate()` for base/offset-to-register/mask translation, `init_valid_mask()`, and `drvdata`. Lifecycle APIs are `gpio_regmap_register()`, `gpio_regmap_unregister()`, `devm_gpio_regmap_register()`, and `gpio_regmap_get_drvdata()`.

Control flow, state, and persistence: Callers describe register layout once, then the implementation creates a `gpio_chip` whose get/set/direction callbacks issue regmap reads/updates. Optional regmap-IRQ support creates a regmap IRQ device and connects its domain to GPIO IRQ handling. Driver-private `drvdata` persists inside the opaque `gpio_regmap`.

Dependencies/integration: It integrates gpiolib, regmap, optional regmap-irq, firmware nodes, and IRQ domains. The documented register-base rules define valid input-only, output-only, and bidirectional configurations.

Risks and test signals: Invalid combinations of register bases lead to nonsensical direction/value behavior. `reg_mask_xlate()` must honor stride and `ngpio_per_reg`, and fixed-output masks must align with `ngpio`. Tests should cover input-only, output-only, split set/clear, direction-in vs direction-out layouts, custom translation, IRQ domain setup, managed unregister, and regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/regmap.h -->
