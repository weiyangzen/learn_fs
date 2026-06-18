# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-mpp.c

## Purpose
This file implements the older Qualcomm PM8xxx SSBI MPP pin controller driver. It supports multi-purpose PMIC pins with digital, analog, current-sink, DTEST, and paired modes, exposing them through Linux pinctrl, pinmux, generic/custom pinconf, gpiolib, debugfs, and hierarchical IRQ infrastructure.

## Important APIs, Types, and Functions
- `struct pm8xxx_pin_data` caches the single-register MPP encoding as logical fields: register address, mode, input/output/high-Z/paired flags, output value, power source, DTEST selector, AMUX route, analog output level, current sink drive strength, and pull-up.
- `struct pm8xxx_mpp` owns device, parent regmap, pinctrl device, gpiochip, pinctrl descriptor, and pin count.
- `pm8xxx_mpp_update()` converts cached logical state to the hardware byte encoding `(type << 5) | (level << 2) | ctrl` and writes it through regmap.
- Pinctrl operations expose one group per pin from `pm8xxx_groups`.
- Pinmux functions are `digital`, `analog`, and `sink`.
- Pinconf functions handle generic pull-up, high impedance, input enable, level, power source, drive strength and custom `qcom,amux-route`, `qcom,dtest`, `qcom,analog-level`, and `qcom,paired`.
- GPIO operations provide direction, get/set, one-based OF translation, and debug display.
- IRQ support uses `pm8xxx_mpp_irq_chip`, child translate/offset helpers, and two possible parent hwirq offsets: `+ 24` for `qcom,pm8821-mpp` and `+ 0x80` for other supported PMICs.
- `pm8xxx_pin_populate()` decodes the current hardware byte into the cached logical representation.
- `pm8xxx_mpp_probe()` allocates and registers pinctrl/gpiochip and hierarchical IRQ support.

## Control Flow
Probe obtains match-data pin count, parent regmap, allocates pin descriptors and state, assigns MPP registers starting at `SSBI_REG_ADDR_MPP_BASE`, and calls `pm8xxx_pin_populate()` for each pin. After descriptor setup, it registers pinctrl, configures gpiochip metadata, locates the parent IRQ domain, selects the child-to-parent hwirq mapping callback based on PM8821 compatibility, registers the gpiochip, and adds a pin range.

Runtime state changes converge through `pm8xxx_mpp_update()`. Pinmux changes set `pin->mode` and update hardware. Pinconf changes mutate one or more cached fields and update hardware. GPIO direction adapts behavior by mode: digital input enables input; analog input sets both input and output; sink input is rejected; output enables output in digital/analog/sink modes. GPIO get returns cached output for non-input pins or reads parent IRQ line level for input pins.

## State and Persistence
State is cached per pin and initialized from the single SSBI MPP register. There is no dedicated suspend/resume or restore path in this file. Configuration writes are immediate and overwrite the whole MPP register based on cached fields, making cache correctness important.

## Dependencies and Integration Points
The driver depends on the parent PMIC regmap, Linux pinctrl, pinmux, generic pinconf, gpiolib, hierarchical IRQ domains, DT bindings from `qcom,pmic-mpp.h`, and pinctrl helper utilities. Device tree compatibility controls pin count and the PM8821-specific IRQ parent offset. GPIO and IRQ consumers use one-based PMIC MPP numbering.

## Risks and Edge Cases
- The source snapshot contains apparent duplicate declarations/lines, including duplicate `return ARRAY_SIZE(pm8xxx_mpp_functions);` and duplicate `unsigned gpio = chip->base;`, which would create compile diagnostics or errors.
- `pm8xxx_pinmux_set_mux()` and `pm8xxx_pin_config_set()` ignore `pm8xxx_mpp_update()` return values, masking regmap write failures.
- `pm8xxx_mpp_direction_output()` accepts a `value` parameter but does not assign it to `pin->output_value` before updating hardware, so direction-output may not drive the requested level.
- Current sink drive strength is encoded as `(drive_strength / 5) - 1`; a zero or non-multiple-of-5 value can underflow or encode an unintended level because there is no validation in config set.
- Pull-up value `600` is mapped to the `1KOHM` hardware selector, reflecting a binding/hardware naming mismatch that callers must understand.
- GPIO input reads depend on IRQ line-level state rather than a direct MPP input register.

## Test Signals
Compile coverage should catch the duplicate local declaration in debugfs. Runtime testing should cover register encode/decode round trips for all MPP types, DTEST and paired modes, PM8821 versus non-PM8821 IRQ parent offsets, GPIO direction output level behavior, drive-strength validation, and input reads through IRQ state. Debugfs output exercises most cached fields.
