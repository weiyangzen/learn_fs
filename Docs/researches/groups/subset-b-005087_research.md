# subset-b-005087 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-gpio.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-mpp.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-spmi-mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-gpio.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-mpp.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ssbi-mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-x1e80100.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-x1e80100.c

## Purpose
This file is the Qualcomm X1E80100 TLMM SoC pin controller descriptor. It supplies the `pinctrl-msm` common driver with SoC-specific pins, groups, functions, register offsets, GPIO/interrupt bit positions, special SDC/UFS groups, and a PDC wake IRQ map. The procedural logic is intentionally minimal: the file defines data and registers a platform driver for `qcom,x1e80100-tlmm`.

## Important APIs, Types, and Functions
- `PINGROUP()` expands a GPIO pin into `struct msm_pingroup` data with group name, mux function array, register offsets based on `REG_SIZE * id`, pull/drive/mux bits, GPIO input/output bits, interrupt bits, EGPIO bits, and target fields.
- `SDC_QDSD_PINGROUP()` describes SDC/QDSD-style non-GPIO groups with pull/drive bits but no GPIO or interrupt fields.
- `UFS_RESET()` describes the UFS reset pin with output and pull/drive control but no interrupt support.
- `x1e80100_pins[]` lists 238 GPIO pins plus UFS reset and SDC2 pins.
- `DECLARE_MSM_GPIO_PINS()` creates one-pin group arrays for GPIO pins; separate arrays exist for `ufs_reset`, `sdc2_clk`, `sdc2_cmd`, and `sdc2_data`.
- `enum x1e80100_functions` enumerates all mux IDs consumed by `PINGROUP()` and `MSM_PIN_FUNCTION()`.
- `x1e80100_functions[]` maps mux IDs to function names and supported groups.
- `x1e80100_groups[]` maps each group index to pin-specific mux alternatives and register layout.
- `x1e80100_pdc_map[]` maps GPIO numbers to PDC wake IRQ numbers, although it is currently disabled in the SoC data.
- `x1e80100_pinctrl` is the `struct msm_pinctrl_soc_data` passed to `msm_pinctrl_probe()`.
- `x1e80100_pinctrl_probe()` is the only real function and delegates to `msm_pinctrl_probe()`.

## Control Flow
Module/driver initialization uses `arch_initcall()` to register a platform driver named `x1e80100-tlmm`. On probe, compatible `qcom,x1e80100-tlmm` binds and `x1e80100_pinctrl_probe()` calls the shared Qualcomm TLMM engine with `x1e80100_pinctrl`. The common driver then uses the static descriptor data to implement pinctrl, pinmux, pinconf, GPIO, and interrupt behavior.

There is no per-pin runtime logic in this file. Runtime control flow occurs inside `pinctrl-msm`, which interprets the arrays in this file. GPIO groups use uniform 0x1000 register spacing. UFS reset and SDC2 groups use special fixed offsets and disabled fields for unsupported operations.

## State and Persistence
This file defines immutable static descriptors. Runtime state lives in the shared `pinctrl-msm` driver and MMIO hardware registers. The descriptor does not implement suspend/resume or save/restore itself. `x1e80100_pinctrl` sets `.ngpios = 239`, includes a wakeirq map, but sets `.nwakeirq_map = 0` due to a TODO noting that enabling PDC currently breaks GPIO interrupts.

## Dependencies and Integration Points
The descriptor depends on `pinctrl-msm.h` types/macros and the common Qualcomm TLMM driver. It integrates with device tree through compatible `qcom,x1e80100-tlmm`, with the platform bus through `platform_driver_register()`, and with pinctrl consumers through function/group names matching DT pinctrl states. It also integrates with GPIO interrupt support through the register bit definitions in each group and with future PDC wake support through `x1e80100_pdc_map`.

## Risks and Edge Cases
- The source snapshot includes duplicate data entries, such as two `PINCTRL_PIN(26, "GPIO_26")` lines and a duplicated `msm_mux_cri_trng` enum entry. These can desynchronize pin numbers, enum values, function tables, or group counts.
- The descriptor is large and table-driven; copy/paste errors in mux alternatives, register offsets, bit positions, or group names can create board-specific failures that are hard to see in generic tests.
- `.ngpios = 239` while the pin array includes special non-GPIO pins through index 241; consumers must treat only the first GPIO range as normal GPIO.
- PDC wake map data exists but is disabled with `.nwakeirq_map = 0`, so wake IRQ functionality is intentionally absent despite the table.
- `egpio_func = 9` depends on the ordering in `PINGROUP()` function arrays; changing mux ordering can break EGPIO behavior.

## Test Signals
Compile-time checks should cover array sizes, duplicate enum/name issues, and macro expansion with `pinctrl-msm`. DT binding validation should verify function and group names used by X1E80100 boards. Runtime smoke tests should request representative QUP, CCI, QSPI, SDC2, UFS reset, audio, USB, display, and GPIO interrupt functions. The separate `tlmm-test.c` file in this subset specifically exercises TLMM GPIO interrupt behavior on `qcom,x1e80100-tlmm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-x1e80100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/tlmm-test.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/tlmm-test.c

## Purpose
This file is a KUnit-based hardware-oriented test module for Qualcomm TLMM interrupt behavior. It validates that the common TLMM/pinctrl-msm driver delivers the expected number of interrupts when an otherwise unused, non-connected GPIO pin is driven by changing the TLMM pull configuration directly in MMIO. It currently allow-lists `qcom,sc8280xp-tlmm` and `qcom,x1e80100-tlmm`.

## Important APIs, Types, and Functions
- Module parameters `gpio` and `name` select the GPIO number under test and the TLMM register region name. `gpio` is mandatory.
- `tlmm_suite` stores shared suite state: mapped TLMM base, selected GPIO config register, mapped IRQ, and precomputed pull-down/pull-up register values.
- `struct tlmm_test_priv` stores per-test atomic interrupt counters and operation masks for hard IRQ and threaded IRQ handlers.
- Operation flags include `TLMM_TEST_COUNT`, `TLMM_TEST_OUTPUT_LOW`, `TLMM_TEST_OUTPUT_HIGH`, `TLMM_TEST_THEN_HIGH`, `TLMM_TEST_THEN_LOW`, and `TLMM_TEST_WAKE_THREAD`.
- `tlmm_output_low()` and `tlmm_output_high()` directly write pull-down or pull-up values to the selected TLMM GPIO register and read back to flush.
- `tlmm_test_intr_fn()` and `tlmm_test_intr_thread_fn()` implement configurable hard and threaded handler behavior.
- `tlmm_test_request_hard_irq()` and `tlmm_test_request_threaded_irq()` request the mapped IRQ for each test.
- Test cases cover silent lines, rising/falling edges, high/low level interrupts, retriggering from the hard handler, threaded IRQ delivery, retriggering from threaded handlers, and edge delivery while disabled.
- `tlmm_reg_base()` chooses the MMIO resource from `reg-names` and `name` parameter.
- `tlmm_test_init_suite()` discovers the TLMM node, maps registers, creates an IRQ mapping, and computes register values.
- `kunit_test_suites()` registers the test suite.

## Control Flow
Suite initialization requires `tlmm-test.gpio` to be set. It finds a matching TLMM node, resolves the requested register resource, maps it with `ioremap()`, creates an IRQ mapping using a two-cell OF phandle argument with the selected GPIO and flags 0, selects the pin's MMIO register as `base + gpio * TLMM_REG_SIZE`, and computes low/high pull values by preserving all bits except the pull mask.

Each test allocates a fresh `tlmm_test_priv`, configures handler operation masks, sets the initial pin level by writing pull state, requests a hard or threaded IRQ with a trigger mode, generates transitions through direct MMIO writes and sleeps, frees the IRQ, and asserts exact interrupt counts. Handler-driven tests simulate retriggering by changing pull state in the interrupt handler after short delays.

Suite exit disposes the IRQ mapping and unmaps TLMM MMIO.

## State and Persistence
Shared suite state persists for the whole KUnit suite in `tlmm_suite`. Per-test counters and operations are allocated with KUnit-managed memory and reset for each test. The test intentionally modifies live TLMM pull configuration for the selected GPIO and does not restore the original pull value at suite exit beyond preserving unrelated bits when computing low/high values.

## Dependencies and Integration Points
The test depends on KUnit, OF address/IRQ helpers, direct MMIO access, Linux IRQ APIs, and a real TLMM node with compatible in `tlmm_of_match`. It assumes TLMM register layout uses `TLMM_REG_SIZE` spacing and pull values `MSM_PULL_DOWN`/`MSM_PULL_UP`. It integrates with the same X1E80100 TLMM descriptor researched in this subset and with the common `pinctrl-msm` IRQ handling.

## Risks and Edge Cases
- This is not a pure unit test; it requires real hardware or an equivalent environment, a safe unused non-connected GPIO, and correct module parameters.
- The source snapshot contains an extra `}` in `tlmm_test_falling()`, which would break compilation.
- Direct MMIO writes bypass pinctrl/gpiolib locking and state tracking, so tests can interfere with active board functions if the chosen GPIO is wrong.
- Timing uses `msleep()` and `udelay()` with exact interrupt counts; marginal hardware or scheduler delays may cause flaky results.
- Suite initialization requires `reg-names`; TLMM nodes lacking that property fail even when resource 0 would otherwise be usable.
- The original pin pull state is not restored after tests.

## Test Signals
The file itself is the test signal for TLMM interrupt behavior. Passing KUnit cases indicate correct edge/level interrupt handling, hard/threaded delivery, retrigger behavior, and disabled-then-enabled edge delivery for the chosen GPIO. Build tests with `CONFIG_KUNIT` and the target TLMM driver are also necessary because the source snapshot has a visible syntax-risk marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/tlmm-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Kconfig

## Purpose
This Kconfig file defines build-time configuration symbols for the Realtek DHC pin controller family. It provides a core driver option and SoC-specific options for RTD1619B, RTD1319D, RTD1315E, and RTD1625.

## Important APIs, Types, and Functions
This file has no C APIs. Its important symbols are:
- `PINCTRL_RTD`: tristate core Realtek DHC pin controller driver, depending on `ARCH_REALTEK`, defaulting to `y`, and selecting `PINMUX`, `GENERIC_PINCONF`, and `REGMAP_MMIO`.
- `PINCTRL_RTD1619B`: SoC-specific RTD1619B driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1319D`: SoC-specific RTD1319D driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1315E`: SoC-specific RTD1315E driver depending on `PINCTRL_RTD`, default `y`.
- `PINCTRL_RTD1625`: SoC-specific RTD1625 driver depending on `PINCTRL_RTD`, default `y`, with help text describing muxing/GPIO enabling and generic pinconf electrical properties.

## Control Flow
Kconfig evaluation makes the core symbol available only on Realtek architectures. Selecting `PINCTRL_RTD` ensures the common pinmux, pinconf, and regmap-mmio infrastructure is built. Enabling each SoC-specific symbol causes Makefile entries in the same directory to compile the matching data driver, while those drivers call the exported core `rtd_pinctrl_probe()`.

## State and Persistence
The file defines build configuration only. It persists as kernel `.config` selections and has no runtime state.

## Dependencies and Integration Points
The file integrates with the kernel build system and the Realtek pinctrl Makefile. It ties the Realtek pinctrl family to architecture gating and required subsystems. The SoC symbols correspond to `pinctrl-rtd1619b.o`, `pinctrl-rtd1319d.o`, `pinctrl-rtd1315e.o`, and `pinctrl-rtd1625.o`.

## Risks and Edge Cases
- All symbols default to `y`, which can increase default build surface for `ARCH_REALTEK`.
- SoC-specific symbols depend only on `PINCTRL_RTD`; they do not independently gate on finer SoC/DT options.
- The RTD1625 help text lacks a final period/newline polish in this snapshot, but that is cosmetic.

## Test Signals
Build-system validation should check `all{yes,mod,no}config` behavior for `ARCH_REALTEK`, dependency selection of `PINMUX`, `GENERIC_PINCONF`, and `REGMAP_MMIO`, and that each symbol produces the expected object listed in the Makefile. Kconfig linting can catch formatting issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Makefile

## Purpose
This Makefile maps Realtek DHC pinctrl Kconfig symbols to the object files compiled by kbuild. It builds the shared core and each supported SoC-specific data driver.

## Important APIs, Types, and Functions
This file has no runtime APIs. Its object mappings are:
- `CONFIG_PINCTRL_RTD` -> `pinctrl-rtd.o`
- `CONFIG_PINCTRL_RTD1619B` -> `pinctrl-rtd1619b.o`
- `CONFIG_PINCTRL_RTD1319D` -> `pinctrl-rtd1319d.o`
- `CONFIG_PINCTRL_RTD1315E` -> `pinctrl-rtd1315e.o`
- `CONFIG_PINCTRL_RTD1625` -> `pinctrl-rtd1625.o`

## Control Flow
During kbuild, each `obj-$(CONFIG_...)` line expands to either built-in, module, or nothing depending on Kconfig state. The core object provides `rtd_pinctrl_probe()` and `realtek_pinctrl_pm_ops`; SoC objects provide static descriptors and platform drivers that depend on the core symbol.

## State and Persistence
No runtime state exists. The persistent effect is the build artifact set selected by `.config`.

## Dependencies and Integration Points
The Makefile integrates directly with `drivers/pinctrl/realtek/Kconfig`. It assumes the SoC-specific source files exist beside `pinctrl-rtd.c` and use the shared header/core interfaces.

## Risks and Edge Cases
- If a SoC-specific symbol is enabled as built-in while the core is modular, kbuild dependency handling must keep link ordering coherent through the Kconfig dependency.
- Missing source files for any enabled symbol would produce build failures.
- There is no composite module aggregation; each object is controlled independently.

## Test Signals
Build `ARCH_REALTEK` configurations with each symbol as built-in and module where legal. Verify `modules.order`/built-in linkage contains the expected Realtek pinctrl objects and that SoC drivers resolve exported symbols from `pinctrl-rtd.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.c

## Purpose
This file implements the shared Realtek DHC SoC pinctrl core. SoC-specific Realtek pinctrl drivers provide static pin/group/function/mux/config descriptor tables; this core registers a pinctrl device, handles mux selection and GPIO muxing, applies generic and custom pinconf settings through MMIO regmap updates, and optionally saves/restores configured register ranges across system sleep.

## Important APIs, Types, and Functions
- `struct rtd_pinctrl` is runtime state: device, pinctrl device, MMIO base, pinctrl descriptor, pointer to SoC descriptor, regmap, and optional saved register arrays.
- Custom pinconf parameters are `realtek,drive-strength-p`, `realtek,drive-strength-n`, `realtek,duty-cycle`, and `realtek,high-vil-microvolt`.
- Pinctrl ops: `rtd_pinctrl_get_groups_count()`, `rtd_pinctrl_get_group_name()`, `rtd_pinctrl_get_group_pins()`, and `rtd_pinctrl_dbg_show()`.
- Pinmux ops: `rtd_pinctrl_get_functions_count()`, `rtd_pinctrl_get_function_name()`, `rtd_pinctrl_get_function_groups()`, `rtd_pinctrl_set_mux()`, and `rtd_pinctrl_gpio_request_enable()`.
- Lookup helpers: `rtd_pinctrl_find_mux()`, `rtd_pinctrl_set_one_mux()`, `rtd_pinctrl_get_pin_by_number()`, `rtd_pinctrl_find_config()`, and `rtd_pinctrl_find_sconfig()`.
- Pinconf core: `rtd_pconf_parse_conf()` maps generic/custom pin configs into register offset/mask/value updates; `rtd_pin_config_set()` and `rtd_pin_config_group_set()` apply configs to one pin or a group.
- `rtd_pinctrl_probe()` is exported for SoC-specific drivers and performs MMIO mapping, regmap creation, pinctrl registration, platform drvdata setup, and optional PM save-buffer allocation.
- `realtek_pinctrl_suspend()` and `realtek_pinctrl_resume()` save/restore descriptor-specified register ranges.
- `realtek_pinctrl_pm_ops` is exported for SoC drivers to attach to their platform drivers.

## Control Flow
SoC-specific probe calls `rtd_pinctrl_probe(pdev, desc)`. The core allocates runtime state, maps MMIO resource 0, stores the SoC descriptor, fills a `struct pinctrl_desc` with SoC pins and shared ops, initializes an MMIO regmap, registers pinctrl, stores drvdata, and allocates save buffers if `desc->pin_range` exists.

Pinctrl group/function queries return descriptor data directly. Mux setting gets the selected function name, fetches group pins, and calls `rtd_pinctrl_set_one_mux()` for each pin. That helper finds the pin mux descriptor, scans its function table for the requested name, and applies the function's mux value with `regmap_update_bits()`. GPIO request enable is implemented by selecting the `gpio` function for the requested pin.

Pinconf setting flows through `rtd_pconf_parse_conf()`. For each config it finds the pin's electrical config descriptor, computes absolute bit positions from `base_bit` plus feature-specific offsets, handles special cases where offsets cross a 32-bit register boundary, then updates the regmap. It supports Schmitt input, push-pull/bias disable, pull-up/down, drive strength, power source, slew rate, input voltage, high VIL, P/N drive strength, and duty cycle. Group config applies the same configs to each pin in the selected group.

Suspend iterates descriptor-provided register ranges, reading every 32-bit entry into `saved_regs`. Resume writes the saved values back in the same order.

## State and Persistence
Runtime state is in `struct rtd_pinctrl`; static hardware description remains in SoC descriptors from the header. Register state is persistent in hardware until changed. If `pin_range` is supplied, suspend/resume preserve selected pinctrl register ranges in `saved_regs`; otherwise suspend/resume are no-ops. The driver does not cache arbitrary pinconf state beyond optional saved registers.

## Dependencies and Integration Points
The core depends on Linux pinctrl, pinmux, generic pinconf, regmap MMIO, platform resources, OF, and descriptor definitions from `pinctrl-rtd.h`. It is exported to SoC files in the same Realtek family. Device tree pinctrl states are parsed by `pinconf_generic_dt_node_to_map_all`, so DT nodes can combine mux and pinconf properties. GPIO integration is through pinctrl's `gpio_request_enable`, not through a gpiochip in this core.

## Risks and Edge Cases
- `rtd_pconf_parse_conf()` sets `set_val` for slew rate but computes `val = arg << sr_off` instead of `set_val << sr_off`; this appears to write literal 10/20/30 into a 2-bit field and should be reviewed.
- `RTD_HIGH_VIL` computes `val = 1` rather than `BIT(hvil_off)`, so nonzero `hvil_off` likely writes the wrong bit.
- `RTD_DUTY_CYCLE` uses `config_desc->reg_offset` instead of `sconfig_desc->reg_offset`, unlike P/N drive strength; this may target the wrong register for special configs.
- `rtd_pinctrl_find_config()` indexes `configs[pin]` directly, assuming config arrays are indexed by pin number and large enough.
- `rtd_pinctrl_find_mux()` indexes `muxes[pin]` directly, with the same descriptor-size assumption.
- `rtd_pin_config_get()` returns `-ENOTSUPP` for all params, so readback of applied pinconf is not supported.
- The core has no gpiochip; GPIO electrical or mux requests rely on other Realtek GPIO support plus pinctrl muxing.

## Test Signals
Build tests should cover the exported symbols and each SoC descriptor driver. Runtime tests should apply representative DT pinctrl states for muxing, pull-up/down, Schmitt, drive strength, voltage, slew, high-VIL, P/N drive, and duty cycle, then verify register bits. Suspend/resume tests should confirm descriptor ranges are restored. Static analysis should focus on descriptor index bounds and the bit-value concerns noted above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.h

## Purpose
This header defines the descriptor contract between Realtek DHC SoC-specific pinctrl data files and the shared core in `pinctrl-rtd.c`. It provides structures for groups, functions, mux alternatives, electrical config metadata, special config metadata, suspend register ranges, and the top-level SoC descriptor, plus macros that make large static SoC tables concise.

## Important APIs, Types, and Functions
- `NA` is the sentinel value for unsupported offsets or current type.
- `PADDRI_4_8` and `PADDRI_2_4` encode two supported drive-strength selector models.
- `struct rtd_pin_group_desc` describes a named group and its pin list.
- `struct rtd_pin_func_desc` describes a named mux function and groups that support it.
- `struct rtd_pin_mux_desc` describes one mux function name and register value for a pin.
- `struct rtd_pin_config_desc` describes per-pin electrical config register offset, base bit, pull enable/select offsets, current, Schmitt, power, input voltage, slew rate, and high-VIL offsets.
- `struct rtd_pin_sconfig_desc` describes special per-pin/group fields such as duty cycle and separate N/P drive strengths.
- `struct rtd_reg_range` and `struct rtd_pin_range` describe register ranges saved/restored by PM hooks.
- `struct rtd_pin_desc` describes a pin's mux register offset, mask, and possible functions.
- `struct rtd_pin_reg_list` is a register/value pair for SoC data use.
- `RTK_PIN_MUX`, `RTK_PIN_CONFIG`, `RTK_PIN_CONFIG_V2`, `RTK_PIN_CONFIG_I2C`, `RTK_PIN_SCONFIG`, and `RTK_PIN_FUNC` generate descriptor initializers.
- `struct rtd_pinctrl_desc` is the top-level SoC descriptor passed to `rtd_pinctrl_probe()`.
- The header declares `rtd_pinctrl_probe()` and `realtek_pinctrl_pm_ops`.

## Control Flow
There is no executable control flow in the header. SoC-specific source files use the macros to build static arrays, then pass an `rtd_pinctrl_desc` to the core probe. The core indexes these arrays to answer pinctrl queries, set mux registers, apply pinconf register updates, and optionally save/restore PM ranges.

## State and Persistence
The header defines static descriptor state and the PM range schema. Runtime state is allocated in `pinctrl-rtd.c`. `struct rtd_pin_range` and `struct rtd_reg_range` are the persistence contract for suspend/resume register save/restore.

## Dependencies and Integration Points
The header is intended for Realtek pinctrl core and SoC descriptor files. It relies on kernel integer types, pinctrl descriptors from including C files, and platform-device declarations for `rtd_pinctrl_probe()`. The exported PM ops declaration lets SoC platform drivers attach the common suspend/resume handlers.

## Risks and Edge Cases
- There is no include guard in this snapshot, so multiple inclusion in one translation unit would redeclare structures/macros.
- Descriptor arrays are assumed by the core to be indexed by pin number for muxes and configs; SoC files must size and order them carefully.
- `NA` is `0xffffffff`; fields using unsigned offsets must compare against it before arithmetic, or overflow can produce invalid bit positions.
- The macros use compound literals for function arrays inside static initializers. This is valid in GNU C kernel style but makes lifetime and section placement dependent on compiler behavior accepted by the kernel.
- `SHIFT_LEFT()` does no masking and can overflow if caller values exceed field width.

## Test Signals
Compile all Realtek SoC descriptor files that include this header. Descriptor-focused tests should verify array sizes against pin numbers, that unsupported fields are `NA`, that mux masks include every `RTK_PIN_FUNC()` value, and that PM register ranges are 4-byte aligned because the core saves/restores `len / 4` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/realtek/pinctrl-rtd.h -->
