# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-gpio.c

## Purpose
This file implements the older Qualcomm PM8xxx SSBI GPIO pinctrl/gpio driver. It targets PMIC GPIO blocks reached through a parent SSBI regmap and exposes pinmux, pinconf, gpiochip, debugfs, and hierarchical IRQ support for compatibles such as `qcom,pm8058-gpio`, `qcom,pm8917-gpio`, and `qcom,pm8921-gpio`.

Unlike the SPMI GPIO driver, the hardware register model is banked: each GPIO has a single SSBI register address and multiple logical banks selected by writing the bank index, with writes using `PM8XXX_BANK_WRITE`.

## Important APIs, Types, and Functions
- `struct pm8xxx_pin_data` stores dynamic pin state: SSBI register address, power source, mode, open-drain flag, output value, bias/pull-up strength, drive strength, disable/high-Z, mux function, and inversion.
- `struct pm8xxx_gpio` owns device, parent regmap, pinctrl device, gpiochip, pinctrl descriptor, and pin count.
- `pm8xxx_read_bank()` selects and reads one bank from a pin register; `pm8xxx_write_bank()` writes a selected bank.
- Pinctrl operations expose each pin as a group using static `pm8xxx_groups`.
- Pinmux uses `pm8xxx_pinmux_set_mux()` and function names from `qcom,pmic-gpio.h`.
- Pinconf uses `pm8xxx_pin_config_get()` and `pm8xxx_pin_config_set()` with generic bias, direction, level, power source, drive mode, and custom `qcom,drive-strength`/`qcom,pull-up-strength`.
- GPIO operations implement direction, get/set, one-based OF translation, and debugfs state.
- IRQ integration uses `pm8xxx_irq_chip`, `pm8xxx_domain_translate()`, and parent hwirq offset `+ 0xc0`.
- `pm8xxx_pin_populate()` initializes `pm8xxx_pin_data` by reading banks 0 through 5.
- `pm8xxx_gpio_probe()` registers the pinctrl and gpiochip and configures hierarchical IRQs.

## Control Flow
Probe obtains `npins` from OF match data, obtains the parent regmap, clones the static pinctrl descriptor, allocates pin descriptors and per-pin state, assigns each pin's register as `SSBI_REG_ADDR_GPIO(i)`, and populates cached state from hardware. It then registers pinctrl, initializes a gpiochip from the template, locates the parent IRQ domain, fills `gpio_irq_chip`, registers the gpiochip, and adds a pin range when `gpio-ranges` is missing.

Pinconf set operations parse all configs and set a bitmask of bank numbers to write. Banks encode power source/enable, mode/open-drain/output, bias, drive strength/disable, function, and inversion. GPIO direction and set operations write bank 1 directly. GPIO get returns cached output for output mode, otherwise uses the mapped IRQ line and `irq_get_irqchip_state(..., IRQCHIP_STATE_LINE_LEVEL, ...)` to read input level.

## State and Persistence
The driver keeps a per-pin cache initialized from hardware banks. Configuration updates write selected hardware banks and update the cache. There is no explicit suspend/resume path. The state is not persisted outside hardware and driver memory. Remove unregisters the gpiochip.

## Dependencies and Integration Points
The driver depends on a parent regmap, pinctrl/generic pinconf/pinmux, gpiolib, IRQ domains, DT bindings from `qcom,pmic-gpio.h`, and pinctrl utilities. It integrates with parent PMIC IRQ handling through hierarchical gpiochip IRQs, two-cell child firmware specs, and a `+ 0xc0` parent interrupt offset.

## Risks and Edge Cases
- The source snapshot contains suspicious duplicate/stray lines: duplicated `arg = 1;` in `pm8xxx_pin_config_get()` and an extra `};` in the debugfs buffer type block. The extra brace would be a compile blocker.
- `pm8xxx_pinmux_set_mux()` ignores the return value from `pm8xxx_write_bank()` and always returns 0, hiding hardware write failures.
- `pm8xxx_pin_config_set()` similarly ignores individual `pm8xxx_write_bank()` return values, so failed register writes are not propagated.
- The `banks & BIT(4)` and `banks & BIT(5)` write paths exist, but the switch cases in this file do not set those bits, so function and inversion writes mostly occur outside pinconf.
- Input reads depend on IRQ mapping and parent IRQ chip state rather than direct GPIO register reads, so GPIO get may fail if IRQ domain setup is absent or disabled.
- `PM8XXX_QCOM_DRIVE_STRENGH` is misspelled in the macro name, though the DT string is `qcom,drive-strength`.

## Test Signals
Compile coverage is important for the visible debugfs brace issue. Runtime tests should exercise bank read/write sequencing, pinconf write error propagation expectations, GPIO direction/value operations, OF one-based translation, input read via IRQ state, parent hwirq offset mapping, and legacy `gpio-ranges` behavior. Debugfs `pm8xxx_gpio_dbg_show()` is a useful manual inspection signal when `CONFIG_DEBUG_FS` is enabled.
