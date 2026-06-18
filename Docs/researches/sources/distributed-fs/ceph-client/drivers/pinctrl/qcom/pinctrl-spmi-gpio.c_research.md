# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-gpio.c

## Purpose
This file implements the Qualcomm SPMI PMIC GPIO pin controller driver for PMIC GPIO peripheral blocks. It registers a Linux pinctrl provider, pinmux provider, generic/custom pinconf provider, gpiochip, and hierarchical IRQ bridge for SPMI PMIC GPIO pins described by compatible strings such as `qcom,pm8550-gpio`, `qcom,pm8998-gpio`, and many other PMIC variants.

The driver is hardware-state-oriented. At probe it reads each SPMI GPIO peripheral's type/subtype and control registers into a per-pin `struct pmic_gpio_pad`, then later pinctrl, gpio, and IRQ operations update that cached state and write it back to the PMIC register block.

## Important APIs, Types, and Functions
- `struct pmic_gpio_pad` caches per-pin register-derived state: SPMI base address, enable state, output value, buffer capability/type, input/output enables, analog pass-through, LV/MV subtype flag, source count, selected power source, pull, strength, mux function, ATEST, and DTEST buffer.
- `struct pmic_gpio_state` owns driver-wide state: device, parent regmap, registered pinctrl device, gpiochip, SPMI USID, and peripheral ID base for IRQ parent mapping.
- `pmic_gpio_read()` and `pmic_gpio_write()` are thin regmap helpers against `pad->base + addr` with device error logging.
- Pinctrl operations expose one group per pin using `pmic_gpio_get_groups_count()`, `pmic_gpio_get_group_name()`, and `pmic_gpio_get_group_pins()`, with DT parsing via `pinconf_generic_dt_node_to_map_group`.
- Pinmux is implemented by `pmic_gpio_set_mux()`, with function names from `dt-bindings/pinctrl/qcom,pmic-gpio.h` and special handling for LV/MV subtypes versus older subtypes.
- Pinconf is implemented by `pmic_gpio_config_get()` and `pmic_gpio_config_set()`. Generic parameters include drive mode, bias, high impedance, power source, input/output enable, and output level. Custom parameters are `qcom,pull-up-strength`, `qcom,drive-strength`, `qcom,atest`, `qcom,analog-pass`, and `qcom,dtest-buffer`.
- GPIO operations are `pmic_gpio_get_direction()`, `pmic_gpio_direction_input()`, `pmic_gpio_direction_output()`, `pmic_gpio_get()`, `pmic_gpio_set()`, and `pmic_gpio_of_xlate()`.
- IRQ integration uses `spmi_gpio_irq_chip`, `pmic_gpio_domain_translate()`, `pmic_gpio_child_to_parent_hwirq()`, and `pmic_gpio_populate_parent_fwspec()` to connect gpiochip IRQs to the parent SPMI interrupt domain.
- `pmic_gpio_populate()` decodes hardware registers and subtype capabilities during probe.
- `pmic_gpio_probe()` builds the descriptors, registers pinctrl and gpiochip, wires hierarchical IRQs, and optionally adds a legacy pin range when `gpio-ranges` is absent.

## Control Flow
Probe reads the DT `reg` property for the base PMIC peripheral address and obtains the number of pins from OF match data. It allocates dynamic pin descriptors and pads, derives each pad base as `reg + i * PMIC_GPIO_ADDRESS_RANGE`, and calls `pmic_gpio_populate()` for each pin. Population validates `PMIC_GPIO_REG_TYPE`, decodes subtype-specific capabilities, reads direction/function/output registers differently for LV/MV and non-LV/MV subtypes, then reads VIN, pull, DTEST, output strength/type, and ATEST state.

After population, the driver copies a gpiochip template, fills runtime fields, registers pinctrl, locates the parent IRQ domain using `of_irq_find_parent()` and `irq_find_host()`, configures a hierarchical `gpio_irq_chip`, adds the gpiochip, and adds a pin range when the DT has no `gpio-ranges` property.

Runtime configuration flows through pinconf and pinmux. `pmic_gpio_config_set()` first mutates cached `pmic_gpio_pad` fields for all requested configs, then writes VIN, pull, output type/strength, DTEST input routing, mode/function/output selection, and master enable. `pmic_gpio_set_mux()` updates `pad->function` and rewrites mode/function/master-enable fields. GPIO direction and set operations are wrappers that translate to pinconf configs.

IRQ flow is hierarchical: child hwirqs are zero-based gpio offsets, translated from one-based firmware gpio numbers. Parent SPMI interrupt hwirq is `child_hwirq + state->pid_base`; parent fwspec is four-cell with USID, peripheral ID, zero, and trigger type. Mask/unmask call parent IRQ operations and gpiochip IRQ resource helpers.

## State and Persistence
Pin state is cached in memory in `struct pmic_gpio_pad` and is initialized from hardware registers on probe. Later pinconf/gpio/pinmux operations update both the cache and hardware registers. There is no suspend/resume persistence layer in this file; persistence across power management depends on the PMIC retaining register values or other subsystem restore behavior. Remove only unregisters the gpiochip; devm allocations and pinctrl registration are managed by device lifetime.

## Dependencies and Integration Points
The driver depends on Linux pinctrl, pinmux, generic pinconf, gpiolib, hierarchical IRQ domains, regmap, SPMI parent devices, DT binding constants from `qcom,pmic-gpio.h`, and core pinctrl helpers. It requires the parent device to expose a regmap and to be convertible with `to_spmi_device()` so USID can be used in parent IRQ fwspecs. Device tree supplies `reg`, compatible-specific pin count, optional `gpio-ranges`, and GPIO/IRQ phandle cells.

## Risks and Edge Cases
- The source snapshot contains suspicious duplicated/stray lines, including a stray `}` after `pmic_gpio_get_groups_count()` and duplicate ATEST assignment in `pmic_gpio_populate()`. The stray brace would be a compile blocker if present in the real build tree.
- `state->chip.can_sleep = false` even though register operations use regmap to a PMIC parent; this assumes the parent regmap path is safe in gpio contexts.
- `pmic_gpio_config_set()` mutates cached state as it parses configs before all validation and writes complete, so an error partway through can leave cache changed without matching hardware.
- Non-LV/MV function index remapping is subtle: FUNC3/FUNC4 are rejected and DTEST functions are shifted down. Incorrect DT function selection can silently map to different register encodings if not validated carefully.
- `pmic_gpio_get_direction()` returns `-EINVAL` for analog pass-through, disabled, or neither-input-nor-output pins, which consumers may treat differently from a valid direction.
- The OF match data intentionally includes PMICs with holes, but the driver still creates sequential logical gpio groups; board DTs must avoid absent physical pins.

## Test Signals
Useful validation includes compile coverage with `CONFIG_PINCTRL_QCOM_SPMI_GPIO`, DT binding tests for each compatible and `gpio-ranges`, gpio-lib tests for one-based OF translation, pinconf round-trips for bias/drive/source/DTEST/ATEST, interrupt mapping tests that verify USID/peripheral parent fwspec generation, and hardware smoke tests for LV/MV analog-pass-through versus non-LV/MV digital modes. Debugfs pinconf output via `pmic_gpio_config_dbg_show()` provides a practical runtime sanity signal.
