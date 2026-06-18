<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c

## Purpose
`gpio-logicvc.c` provides output-only GPIO support for Xylon LogiCVC display-controller GPIO registers. It exposes nine virtual outputs split across the main control register and power-control register.

## Important APIs, types, and functions
`struct logicvc_gpio` stores the gpiochip and regmap. `logicvc_gpio_offset()` maps offsets 0-4 into `LOGICVC_CTRL_REG` bits 11-15 and offsets 5-8 into `LOGICVC_POWER_CTRL_REG` bits 0-3. `logicvc_gpio_get()`, `logicvc_gpio_set()`, and `logicvc_gpio_direction_output()` implement the GPIO callbacks. Probe can reuse a parent syscon regmap or create an MMIO regmap for the node.

## Control flow
Probe allocates driver state, first tries `syscon_node_to_regmap()` on the parent, and falls back to mapping resource 0 plus `devm_regmap_init_mmio()`. It then fills a dynamic-base gpiochip with nine lines, get/set callbacks, and output-direction callback, and registers it with `devm_gpiochip_add_data()`. Direction output simply writes the value because the pins are always configured as outputs.

## State and persistence behavior
Line levels live in LogiCVC registers; direction is fixed output-only by hardware/driver contract. The driver keeps no shadow state and no persistent configuration outside the regmap-backed hardware registers.

## Dependencies and integration points
It binds to `xylon,logicvc-3.02.a-gpio`, integrates with parent syscon/regmap when available, and otherwise owns an MMIO regmap for the GPIO register block. Gpiolib consumers see it as a small output-only gpiochip.

## Risks and edge cases
The offset split between the two registers is correctness-critical; off-by-one errors would drive power-control bits instead of main-control bits or the reverse. Parent syscon fallback must match DT layout, and the local regmap `max_register` calculation depends on resource size and stride. No input-direction callback is provided.

## Test signals
Test all nine offsets, especially the transition from offset 4 to 5, parent syscon and standalone MMIO-regmap probe paths, output set/readback through regmap, and rejection of input-direction requests by gpiolib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-logicvc.c -->
