# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-mpp.c

## Purpose
This file implements the Qualcomm SPMI PMIC MPP pin controller driver. PMIC MPPs are multi-purpose pins that can operate as digital GPIO-like pins, analog inputs/outputs, or current sinks. The driver exposes MPPs through Linux pinctrl, pinmux, pinconf, gpiolib, and hierarchical IRQ infrastructure for SPMI PMICs such as `pm8916`, `pm8941`, `pm8994`, and related variants.

## Important APIs, Types, and Functions
- `struct pmic_mpp_pad` caches per-MPP state: SPMI base, enable/output/input flags, paired mode, pull-up capability, number of VIN sources, selected source, AMUX input, analog output level, pull-up, function, sink drive strength, and DTEST selector.
- `struct pmic_mpp_state` holds device, parent regmap, pinctrl device, and gpiochip.
- `pmic_mpp_read()` and `pmic_mpp_write()` wrap regmap accesses to a pin's SPMI peripheral address.
- `pmic_mpp_write_mode_ctl()` converts cached logical state into the mode/function/value fields of `PMIC_MPP_REG_MODE_CTL`.
- Pinctrl and pinmux operations expose one group per pin and three functions: `digital`, `analog`, and `sink`.
- `pmic_mpp_config_get()` and `pmic_mpp_config_set()` implement generic pinconf plus custom `qcom,amux-route`, `qcom,analog-level`, `qcom,dtest`, and `qcom,paired`.
- GPIO operations support direction, get/set, OF translation, and debug display.
- IRQ support uses `pmic_mpp_irq_chip`, `pmic_mpp_domain_translate()`, `pmic_mpp_child_to_parent_hwirq()`, and parent fwspec population through `gpiochip_populate_parent_fwspec_fourcell`.
- `pmic_mpp_populate()` validates each peripheral and decodes initial register state.
- `pmic_mpp_probe()` allocates descriptors, reads hardware state, registers pinctrl/gpiochip, and connects the parent IRQ domain.

## Control Flow
Probe reads `reg`, obtains `npins` from match data, allocates pin descriptors and pads, and computes each pad's base as `reg + i * PMIC_MPP_ADDRESS_RANGE`. `pmic_mpp_populate()` verifies type `PMIC_MPP_TYPE`, decodes subtype to set the number of power sources and whether pull-up is available, reads mode control to set input/output/function/paired/DTEST fields, then reads VIN, pull, AMUX, sink, analog-output, and enable registers.

Pinmux changes call `pmic_mpp_set_mux()`, which updates `pad->function`, rewrites mode control, and writes master enable. Pinconf changes update cached values, write VIN and optional pull-up, write AMUX and analog output level, rewrite mode control, write sink drive strength, and finally write master enable.

GPIO direction operations are simple pinconf wrappers: input enables input; output sets level and enables output. Reads return cached output unless input is enabled, in which case `PMIC_MPP_REG_RT_STS` is sampled. OF GPIO numbers are one-based and translated to zero-based offsets.

IRQ flow translates one-based firmware pin numbers to child offsets and maps child hwirq to parent hwirq with a fixed `+ 0xc0` offset. Mask/unmask operations coordinate parent IRQ masking with gpiochip IRQ resource enable/disable.

## State and Persistence
The driver initializes cache from hardware on probe and treats `struct pmic_mpp_pad` as the source of truth for future register writes. It has no explicit suspend/resume save/restore. Remove unregisters the gpiochip; devm handles the other allocations and registrations.

## Dependencies and Integration Points
Dependencies include SPMI parent regmap, Linux pinctrl/generic pinconf/pinmux, gpiolib, IRQ domain hierarchy, DT bindings from `qcom,pmic-mpp.h`, and pinctrl utility helpers. Device tree supplies compatible-derived pin count, `reg`, GPIO/IRQ phandle cells, and pinconf properties. The driver integrates with the parent SPMI interrupt controller through four-cell parent fwspec allocation.

## Risks and Edge Cases
- The source snapshot contains apparent compile issues: duplicate `unsigned int val;` declarations in `pmic_mpp_write_mode_ctl()` and duplicate `.pin_config_group_dbg_show` initializer in `pmic_mpp_pinconf_ops`.
- `pmic_mpp_populate()` computes DTEST as `sel + 1` when `sel >= PMIC_MPP_SELECTOR_DTEST_FIRST`; because write-side encoding uses `PMIC_MPP_SELECTOR_DTEST_FIRST + pad->dtest - 1`, this read-side expression appears off by the selector base and should be reviewed.
- `BUG_ON(npins > ARRAY_SIZE(pmic_mpp_groups))` can hard-stop boot for bad match data instead of failing probe gracefully.
- `pmic_mpp_config_set()` accepts some values without tight range checks, such as DTEST, analog level, and drive strength, relying on hardware/register width assumptions.
- Cached state can diverge if a multi-write config operation fails after earlier cache mutations.
- Current sink mode through gpiolib is only partially GPIO-like; consumers expecting normal input/output semantics can get surprising behavior.

## Test Signals
Compile coverage with SPMI MPP enabled is essential because of the duplicate declarations/initializers visible in this snapshot. Runtime validation should cover digital input/output/bidirectional modes, analog input/output, current sink drive levels, DTEST and paired selectors, one-based GPIO translation, IRQ parent hwirq mapping at `0xc0`, and debugfs output. DT schema checks should ensure compatible-specific pin counts do not exceed the static group table.
