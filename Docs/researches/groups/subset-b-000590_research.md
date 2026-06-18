# subset-b-000590 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk805.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk805.yaml

Purpose: Devicetree schema for the Rockchip RK805 I2C PMIC MFD, describing the top-level PMIC node, its regulator children, GPIO role, clock output, wakeup capability, and power-controller flags.

Important schema surface and control flow: `compatible` is limited to `rockchip,rk805`; `reg`, `interrupts`, and `#clock-cells` are required. The schema exposes `gpio-controller` with two-cell GPIO specifiers, the deprecated `rockchip,system-power-controller`, generic `system-power-controller`, `wakeup-source`, six input supplies, and a `regulators` object whose children must be `DCDC_REG1` through `DCDC_REG4` or `LDO_REG1` through `LDO_REG3` and must satisfy the common regulator schema. An `allOf` branch changes `clock-output-names` cardinality: one name when `#clock-cells` is 0, otherwise two.

State, dependencies, and integration: persistent state is the board DT description consumed by the RK8xx MFD, regulator, GPIO, clock, interrupt, and power-management drivers. Dependencies include the core DT meta-schema, common regulator binding, Rockchip clock IDs in `dt-bindings/clock/rockchip,rk808.h`, and interrupt/pinctrl bindings used by board examples. Risks are incorrect regulator child casing, stale use of the deprecated Rockchip power-controller flag, and clock name count mismatches. Test signals are `dt_binding_check`, example validation, and boot-time probe of RK805 regulators, GPIOs, wake IRQ, and optional 32 kHz output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk805.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk806.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk806.yaml

Purpose: Schema for the Rockchip RK806 PMIC MFD, which may sit on SPI or I2C and provides many switchable regulators, GPIOs, reset behavior, and PWRCTRL pin muxing.

Important schema surface and control flow: the top-level node requires `compatible = "rockchip,rk806"`, `reg`, and one interrupt. It allows GPIO controller registration, `system-power-controller`, `rockchip,reset-mode` values 0, 1, or 2, supplies `vcc1` through `vcc14` plus `vcca`, and a `regulators` object containing `dcdc-reg1` through `dcdc-reg10`, `pldo-reg1` through `pldo-reg6`, and `nldo-reg1` through `nldo-reg5`. Top-level `*-pins` nodes reference the pinmux-node schema and restrict `function` to `pin_fun0` through `pin_fun5` and `pins` to the three `gpio_pwrctrl` pins. `allOf` pulls in SPI peripheral properties so chip-select style nodes validate.

State, dependencies, and integration: DT state configures regulator rails, reset policy, GPIO controller exposure, and optional PWRCTRL pin muxing used by the RK806 MFD/regulator/gpio/pinctrl drivers. Dependencies include `/schemas/spi/spi-peripheral-props.yaml`, `/schemas/regulator/regulator.yaml`, and `/schemas/pinctrl/pinmux-node.yaml`. Risks include mixing SPI and I2C conventions, wrong lowercase regulator child names, and reset-mode values that can briefly interrupt rails. Test signals are schema validation, example compile, and runtime probe of regulator names, GPIO cells, reset path, and SPI/I2C bus properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk806.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk808.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk808.yaml

Purpose: Binding for the Rockchip RK808 I2C PMIC MFD, covering regulators, RTC, power button, clock outputs, DVS GPIOs, wakeup support, and system power-off integration.

Important schema surface and control flow: `compatible`, `reg`, `interrupts`, and `#clock-cells` are required; `#clock-cells` is fixed at 1 and `clock-output-names` may contain two entries. The schema permits the deprecated Rockchip-specific power-controller flag and the generic replacement, `wakeup-source`, `dvs-gpios` with up to two host GPIO specifiers for buck DVS, regulator input supplies from `vcc1-supply` through `vcc12-supply` plus `vddio-supply`, and a `regulators` object limited to `DCDC_REG1-4`, `LDO_REG1-8`, and `SWITCH_REG1-2`.

State, dependencies, and integration: the DT node persists all board-specific rail topology and optional DVS behavior consumed by RK808 MFD, regulator, RTC, input, and clock drivers. Dependencies are the common regulator schema, Rockchip clock binding, GPIO/pinctrl/interrupt bindings, and PMIC-specific Linux drivers. Risks include forgetting `#clock-cells`, using deprecated power-controller spelling, DVS GPIO polarity errors, and missing input supplies that can cause regulator registration failures on real boards. Test signals are `dt_binding_check`, the example, regulator registration with expected child names, clock provider registration, RTC/power-key interrupts, and suspend/resume DVS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk808.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk816.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk816.yaml

Purpose: Schema for the Rockchip RK816 I2C PMIC MFD, describing regulators, RTC, power button, GPIO controller capability, clock output, wakeup, and system power control.

Important schema surface and control flow: it requires `compatible = "rockchip,rk816"`, `reg`, `interrupts`, and fixed `#clock-cells = 1`. It accepts `clock-output-names`, `gpio-controller` with `#gpio-cells = 2`, `system-power-controller`, `wakeup-source`, supplies `vcc1` through `vcc8`, and a regulator namespace using lowercase child names such as `dcdc1` through `dcdc4`, `ldo1` through `ldo6`, and switch/boost-style rails allowed by the schema. Pattern properties also allow `*-pins` pinmux nodes with constrained RK816 pin names and functions.

State, dependencies, and integration: the node is persistent board configuration for the RK816 MFD, regulator, GPIO, clock, input, and RTC paths. It depends on the common regulator and pinmux schemas, Rockchip pinctrl constants, and interrupt bindings. Risks are regulator child-name mismatch with other RK8xx variants, power sequencing mistakes in suspend regulator states, and exposing GPIO controller cells without matching driver support on a board. Test signals are binding validation, example validation, successful regulator and GPIO provider registration, and suspend/resume rail checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk816.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk817.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk817.yaml

Purpose: Binding for the RK809/RK817 PMIC family, an I2C MFD with regulators, RTC, power button, audio codec, clocking, and RK817-specific charger support.

Important schema surface and control flow: `compatible` is `rockchip,rk809` or `rockchip,rk817`; `reg`, `interrupts`, and `#clock-cells` are required. The schema covers optional MCLK input (`clocks` and `clock-names = "mclk"`), `#sound-dai-cells = 0`, generic and deprecated power-controller flags, wakeup, nine supply inputs, a `codec` child with microphone differential mode, and a `charger` child that references power-supply semantics and requires a monitored battery plus Rockchip sense and sleep-current calibration properties. `allOf` includes the DAI common schema, adjusts `clock-output-names` count based on `#clock-cells`, and prevents RK817-only `BOOST`/`OTG_SWITCH` rails from being used on RK809 while preventing RK809-only `DCDC_REG5` and `SWITCH_REG1-2` on RK817.

State, dependencies, and integration: board DT drives MFD cell creation for regulator, RTC, input, codec/DAI, clock, and charger/power-supply drivers. Dependencies include regulator, sound DAI, power-supply, battery, clock, GPIO, and interrupt bindings. Risks cluster around variant-specific regulator names, mandatory charger calibration when the charger node is present, and codec clock wiring. Test signals are schema branch validation for both compatibles, audio DAI registration, charger power-supply probe with battery phandle, and runtime regulator map checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk817.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk818.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk818.yaml

Purpose: Schema for the Rockchip RK818 I2C PMIC MFD, covering regulators, RTC, power button, two clock outputs, wakeup behavior, and system power-off use.

Important schema surface and control flow: the binding requires `compatible = "rockchip,rk818"`, `reg`, `interrupts`, and `#clock-cells = 1`. It allows `clock-output-names` with up to two entries, deprecated and generic power-controller flags, `wakeup-source`, input supplies for four DCDC rails, boost, LDO groups, digital I/O, HDMI switch, and USB switch. The `regulators` object permits `DCDC_REG1-4`, `DCDC_BOOST`, `LDO_REG1-9`, `SWITCH_REG`, `HDMI_SWITCH`, and `OTG_SWITCH`, each validated by the common regulator schema.

State, dependencies, and integration: the DT node persists the board's RK818 rail topology and optional switch rails for HDMI/USB, consumed by RK818 MFD, regulator, RTC, input, and clock drivers. Dependencies include regulator schema, clock IDs from the RK808 family, and GPIO/interrupt/pinctrl bindings. Risks include omitting switch supplies, wrong regulator child names, retaining deprecated power-controller syntax, and suspend-state definitions that keep or cut critical rails incorrectly. Test signals are `dt_binding_check`, example validation, successful clock provider setup, regulator registration for boost/switch rails, and wakeup IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rockchip,rk818.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71815-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71815-pmic.yaml

Purpose: Devicetree schema for the ROHM BD71815 PMIC MFD, used to describe regulators, GPIOs/GPOs, charger sense resistor configuration, interrupt wiring, and a fixed 32 kHz clock output.

Important schema surface and control flow: `compatible = "rohm,bd71815"`, `reg`, `interrupts`, and `regulators` are required. The schema exposes `gpio-controller` with two cells, `clocks`/`#clock-cells = 0`, `clock-output-names = "bd71815-32k-out"`, `rohm,clkout-open-drain`, `rohm,charger-sense-resistor-micro-ohms`, `gpio-reserved-ranges`, and `rohm,enable-hidden-gpo`. The regulator child schema is delegated to `/schemas/regulator/rohm,bd71815-regulator.yaml`, so rail details stay aligned with the dedicated regulator binding.

State, dependencies, and integration: DT state controls PMIC I2C probe, IRQ routing, clock provider exposure, GPIO/GPO registration, charger calibration, and regulator initialization. Dependencies include the ROHM regulator schema, common clock/GPIO/interrupt bindings, and MFD/regulator/clock/GPIO drivers. Risks include using hidden GPOs without reserving unavailable GPIO lines, selecting an incorrect current-sense resistor value, and mismatching the fixed clock-output name. Test signals are `dt_binding_check`, regulator child validation through the referenced schema, GPIO range checks, and runtime clock/regulator/GPIO probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71815-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71828-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71828-pmic.yaml

Purpose: Binding for the ROHM BD71828 PMIC MFD, describing regulators, GPIOs, LEDs, charger sense resistor, 32 kHz clock output, interrupts, and optional system power control.

Important schema surface and control flow: the top-level node requires compatible, register address, interrupt, and `regulators`. It supports GPIO controller cells, `clocks`/`#clock-cells = 0`, fixed `clock-output-names`, open-drain clock output, charger sense resistor selection, `gpio-reserved-ranges`, `system-power-controller`, a regulator subtree referenced through the ROHM BD71828 regulator schema, and an `leds` child referenced through the BD71828 LED schema. Additional properties are closed.

State, dependencies, and integration: the persistent DT node feeds the BD71828 MFD core and its regulator, GPIO, LED, clock, power-off, charger, and interrupt subdevices. Dependencies include ROHM regulator and LED schemas, common GPIO/clock/interrupt definitions, and Linux MFD cell drivers. Risks are incorrect LED child compatibles, forgetting to reserve unavailable GPIO lines, mismatched charger sense value, and using power-off control on a board where the PMIC does not own system power. Test signals are schema validation, LED and regulator child validation, and runtime registration of GPIO, clock, LED, and regulator devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71828-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71837-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71837-pmic.yaml

Purpose: Schema for ROHM BD71837 PMICs used with NXP i.MX platforms, modeling regulator setup, interrupt wiring, external oscillator input, clock output, and reset/power-button timing options.

Important schema surface and control flow: `compatible = "rohm,bd71837"`, `reg`, `interrupts`, `#clock-cells`, and `regulators` are required. Optional clock input uses `clocks` and `clock-names = "osc"`, clock output naming is fixed to `pmic_clk`, and ROHM-specific properties describe SNVS reset power retention and short/long press timing using enumerated millisecond values. The regulator subtree is validated by the BD71837 regulator binding.

State, dependencies, and integration: board DT determines how the BD71837 MFD provides regulators and clock output and how reset and button-timing policy is programmed. Dependencies include the ROHM regulator schema, clock provider/consumer bindings, interrupt bindings, and PMIC MFD/regulator drivers. Risks include choosing unsupported press durations, mismatching external oscillator wiring, and relying on reset-SNVS behavior without matching board power topology. Test signals are binding checks, example validation, regulator child schema coverage, and boot-time confirmation of clock output and PMIC reset-button behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71837-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71847-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71847-pmic.yaml

Purpose: Binding for ROHM BD71847 and BD71850 PMICs, primarily capturing regulator topology, reset/button timing, optional external clock input, and clock output behavior.

Important schema surface and control flow: `compatible` is either `rohm,bd71847` or `rohm,bd71850`; `reg`, `interrupts`, `#clock-cells`, and `regulators` are required. Optional `clocks` may feed the PMIC oscillator, `clock-output-names` names the PMIC clock output, and dependency rules tie `#clock-cells` and `clocks` together. ROHM properties describe SNVS retention on reset and enumerated short/long power-button press times. Regulators are delegated to the BD71847 regulator schema and top-level additional properties are rejected.

State, dependencies, and integration: persistent DT configures the PMIC MFD, regulators, interrupt line, and optional clock provider/consumer relationship. Dependencies include the ROHM regulator binding, clock bindings, interrupt bindings, and PMIC drivers. Risks include incompatible clock-cell/clock combinations, wrong variant compatible for board silicon, and unsupported button timing values. Test signals are `dt_binding_check`, regulator child validation, dependency-rule failures for incomplete clock descriptions, and runtime regulator/clock probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd71847-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd72720-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd72720-pmic.yaml

Purpose: Schema for ROHM BD72720 and BD73900 PMIC families, capturing regulator, LED, GPIO, clock, charger, interrupt, and pin function configuration for automotive or safety-oriented power systems.

Important schema surface and control flow: compatible values distinguish supported PMIC variants; `reg`, `interrupts`, and `regulators` are required. The schema allows GPIO controller cells, clock output control, charger sense resistor configuration, optional LEDs, and `rohm,pin-fault_b` to select FAULT_B pin behavior from enumerated functions. Top-level pattern properties model PMIC pin configuration nodes with constrained pin and function enumerations. Regulator and LED subtrees are delegated to dedicated ROHM schemas.

State, dependencies, and integration: DT state drives MFD cell creation for regulators, LEDs, GPIOs, clock output, charger calibration, and fault pin behavior. Dependencies include ROHM regulator/LED schemas, common GPIO/clock/interrupt and pinctrl concepts, and the PMIC drivers. Risks include misprogramming FAULT_B behavior, invalid pin-function combinations, charger sense resistor mismatch, and variant-specific regulator assumptions hidden in delegated schemas. Test signals are binding validation, pin function enum coverage, regulator/LED child schema checks, and runtime verification of fault, GPIO, regulator, and LED registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd72720-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9571mwv.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9571mwv.yaml

Purpose: Devicetree binding for ROHM BD9571MWV and BD9574MWF PMICs, describing their I2C node, interrupt and GPIO controllers, DDR backup power mask, reset-button mode, and regulator children.

Important schema surface and control flow: compatible is `rohm,bd9571mwv` or `rohm,bd9574mwf`; `reg`, `interrupts`, interrupt-controller cells, GPIO controller cells, and one reset-mode property are required. `rohm,ddr-backup-power` is a 4-bit mask for DDR rails kept alive in backup mode. `oneOf` requires exactly a level-mode or pulse-mode RSTB description. `regulators` accepts only `vd09`, `vd18`, `vd25`, `vd33`, and `dvfs`, each using the common regulator schema and a matching `regulator-name` pattern.

State, dependencies, and integration: DT persists PMIC reset-mode straps, backup rail policy, regulator constraints, and provider roles for GPIO and interrupts. Dependencies include common regulator, GPIO, interrupt, and types schemas plus the BD957x MFD/regulator/GPIO drivers. Risks include specifying both or neither reset mode, using regulator names that do not match hardware rails, and setting an incorrect DDR backup mask. Test signals are `dt_binding_check`, `oneOf` validation, regulator-name pattern failures, and runtime interrupt/GPIO/regulator provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9571mwv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9576-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9576-pmic.yaml

Purpose: Binding for ROHM BD9576MUF and BD9573MUF PMICs, focused on R-Car style regulator sequencing, watchdog GPIOs, DDR voltage selection, and VOUT1 external enable wiring.

Important schema surface and control flow: `compatible` is `rohm,bd9576` or `rohm,bd9573`; `reg` and `regulators` are required while `interrupts` is optional. Board-specific controls include `rohm,vout1-en-low`, `rohm,vout1-en-gpios`, `rohm,ddr-sel-low`, watchdog enable and ping GPIOs, and `rohm,hw-timeout-ms` with one or two values for normal or windowed watchdog mode. Regulators are delegated to `/schemas/regulator/rohm,bd9576-regulator.yaml`.

State, dependencies, and integration: DT configures watchdog control wiring, startup strap interpretation, DDR voltage selection, and regulator child setup used by MFD, regulator, and watchdog-related logic. Dependencies include GPIO and regulator schemas and ROHM PMIC drivers. Risks include describing a VOUT1 GPIO when the startup strap does not enable pin control, unsafe watchdog timeout windows, and incorrect DDR strap assumptions. Test signals are schema validation, referenced regulator schema validation, GPIO phandle resolution, and hardware watchdog/regulator behavior during boot and watchdog ping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9576-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96801-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96801-pmic.yaml

Purpose: Schema for ROHM BD96801 and BD96805 scalable automotive PMICs, modeling regulators, safety interrupts, watchdog settings, and watchdog failure action.

Important schema surface and control flow: compatible is `rohm,bd96801` or `rohm,bd96805`; `reg`, `interrupts`, `interrupt-names`, and `regulators` are required. `interrupts` may describe `intb` and optional fatal `errb`; `interrupt-names` enforces the first name as `intb` or `errb` and the second as `errb`. Watchdog properties include `rohm,hw-timeout-ms`, `rohm,wdg-action` (`prstb` or `intb-only`), and generic `timeout-sec` through an `allOf` reference to `/schemas/watchdog/watchdog.yaml`. Regulators are delegated to the BD96801 regulator schema.

State, dependencies, and integration: the DT node defines safety IRQ topology, watchdog policy, and regulator limits including safety warning/error settings in child nodes. Dependencies include watchdog and ROHM regulator schemas plus interrupt and I2C bindings. Risks include omitting `errb` on systems that need fatal event handling, reversed interrupt names, and watchdog action that unexpectedly powers down rails. Test signals are `dt_binding_check`, watchdog schema validation, interrupt-name ordering checks, and runtime regulator/watchdog/IRQ registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96801-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96802-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96802-pmic.yaml

Purpose: Binding for ROHM BD96802 and BD96806 configurable automotive PMICs, describing their I2C node, safety interrupt lines, and regulator child tree.

Important schema surface and control flow: compatible is `rohm,bd96802` or `rohm,bd96806`; `reg`, one or two interrupts, matching `interrupt-names`, and `regulators` are required. The interrupt model mirrors BD96801: `intb` is the normal interrupt, optional `errb` reports fatal faults that can shut down power outputs. The regulator subtree references `../regulator/rohm,bd96802-regulator.yaml`, and additional top-level properties are rejected.

State, dependencies, and integration: DT state sets PMIC address, IRQ wiring, and regulator safety/voltage constraints for the BD96802 MFD and regulator drivers. Dependencies include the ROHM BD96802 regulator schema and common interrupt/regulator infrastructure. Risks include not connecting `errb` on systems that need fatal fault capture, misspelled interrupt names, and regulator child properties accepted only by the delegated schema. Test signals are binding validation, example validation, regulator child validation, and runtime IRQ/regulator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96802-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,exynos5433-lpass.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,exynos5433-lpass.yaml

Purpose: Schema for the Samsung Exynos5433 Low Power Audio Subsystem MFD-style bus node, grouping audio DMA, I2S, and UART child devices under the LPASS register ranges and power domain.

Important schema surface and control flow: the node requires `compatible = "samsung,exynos5433-lpass"`, one clock named `sfr0_ctrl`, two `reg` ranges, `#address-cells = 1`, `#size-cells = 1`, and `ranges`. Optional `power-domains` ties the subsystem to the audio power domain. Child pattern properties reference PL330 DMA, Samsung I2S, and Samsung UART schemas based on unit-addressed node names.

State, dependencies, and integration: persistent DT defines LPASS MMIO windows, bus address translation, clocking, power domain membership, and child device layout. Dependencies include Exynos clock IDs, ARM GIC interrupt bindings, `/schemas/dma/arm,pl330.yaml`, `/schemas/sound/samsung-i2s.yaml`, and `/schemas/serial/samsung_uart.yaml`. Risks include missing `ranges`, incomplete child power-domain or clock definitions, and address/size cell mismatches that prevent child resources from translating. Test signals are `dt_binding_check`, child schema validation, and runtime probe of audio DMA, I2S DAI, and audio UART under the LPASS domain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,exynos5433-lpass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2dos05.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2dos05.yaml

Purpose: Binding for the Samsung S2DOS05 PMIC, a panel/touchscreen companion PMIC with four LDOs, one buck, and ADC-related power measurement functions.

Important schema surface and control flow: `compatible = "samsung,s2dos05"`, `reg`, and `regulators` are required. The `regulators` object allows `buck` and `ldo1` through `ldo4`; each child must use the common regulator schema and include `regulator-name`. Additional top-level and regulator-child properties outside the schema are rejected.

State, dependencies, and integration: DT persists the I2C address and regulator constraints for panel and touchscreen rails consumed by the S2DOS05 MFD/regulator support. Dependencies include the common regulator schema and I2C bus binding. Risks include the loose regex shape for regulator names if future rail names are added, missing `regulator-name`, and voltage ranges that do not match attached display hardware. Test signals are `dt_binding_check`, example validation, and runtime regulator registration for `buck` and `ldo1-4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2dos05.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpa01.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpa01.yaml

Purpose: Schema for the Samsung S2MPA01 PMIC, part of the S2M/S5M family with regulators, RTC, clock outputs, interrupts, and wakeup capability.

Important schema surface and control flow: the required properties are `compatible = "samsung,s2mpa01-pmic"`, `reg`, and `regulators`; `interrupts` and `wakeup-source` are optional. The regulator subtree is delegated to `/schemas/regulator/samsung,s2mpa01.yaml`, which owns the valid LDO/BUCK child names and regulator-specific constraints. Additional top-level properties are closed.

State, dependencies, and integration: persistent DT sets the PMIC I2C address and regulator initialization data and may wire an interrupt for RTC, power, or fault events. Dependencies include the Samsung S2MPA01 regulator schema, common interrupt and regulator infrastructure, and the S2M/S5M MFD drivers. Risks include omitting an interrupt when wake events are expected, using regulator names not covered by the referenced schema, and confusing S2MPA01 with adjacent S2MPS variants. Test signals are binding validation, delegated regulator validation, and boot-time registration of regulators and optional wake IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpa01.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg10-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg10-pmic.yaml

Purpose: Binding for the Samsung S2MPG10 main PMIC, which provides buck and LDO regulators, power meters, RTC clock outputs, GPIO interfaces, wakeup, and optional system power control.

Important schema surface and control flow: `compatible = "samsung,s2mpg10-pmic"`, `interrupts`, and `regulators` are required. Optional `clocks` references the Samsung S2MPS11 clock-provider schema, while `system-power-controller` and `wakeup-source` expose power-management roles. Pattern properties document supply phandles for `vinb1m` through `vinb10m` and `vinl1m` through `vinl15m`, including detailed rail sharing for LDO inputs. Regulators are validated by `/schemas/regulator/samsung,s2mpg10-regulator.yaml`.

State, dependencies, and integration: DT state describes main-PMIC interrupt wiring, regulator input supply topology, clock outputs, and PMIC ownership of system shutdown. Dependencies include Samsung clock and regulator schemas, GPIO/interrupt bindings, and S2MPG10 MFD/regulator/clock drivers. Risks include wrong main/sub PMIC rail suffixes, incomplete input supplies for shared LDO groups, and misuse of external-control regulator constants. Test signals are schema validation, referenced regulator and clock child validation, and runtime regulator/clock/wakeup registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg10-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg11-pmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg11-pmic.yaml

Purpose: Schema for the Samsung S2MPG11 sub-PMIC, complementing S2MPG10 with buck, buck-boost, LDO, NTC, power meter, GPIO, and wakeup-related resources.

Important schema surface and control flow: required properties are `compatible = "samsung,s2mpg11-pmic"`, `interrupts`, and `regulators`. `wakeup-source` is optional. Pattern properties define buck input supplies for numbered `vinbNs`, special `vinba`, `vinbb`, and `vinbd`, plus `vinl1s` through `vinl6s` shared LDO supplies. Regulators are delegated to `/schemas/regulator/samsung,s2mpg11-regulator.yaml`.

State, dependencies, and integration: DT persists the sub-PMIC IRQ, rail input topology, and regulator constraints consumed by the S2MPG11 MFD/regulator code. Dependencies include the Samsung regulator schema, GPIO/interrupt bindings, and shared Samsung PMIC infrastructure. Risks include confusing `m` and `s` suffixes between main and sub PMIC rails, incomplete shared-LDO supply descriptions, and external-control constants that must match regulator child capabilities. Test signals are `dt_binding_check`, regulator child schema validation, and runtime probe of regulators and wake-capable interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mpg11-pmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mps11.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mps11.yaml

Purpose: Family binding for Samsung S2MPS11/13/14/15 and S2MPU02/05 PMICs, covering regulators, RTC/clock outputs, interrupts, wakeup behavior, and variant-specific power-off quirks.

Important schema surface and control flow: `compatible`, `reg`, and `regulators` are required. Supported compatibles select variant-specific regulator schemas through `allOf` branches. Optional `clocks` references the S2MPS11 clock binding, `interrupts` wires PMIC events, and `wakeup-source` enables wake handling. `samsung,s2mps11-acokb-ground` and `samsung,s2mps11-wrstbi-ground` are quirk flags, but `allOf` disables them for incompatible variants.

State, dependencies, and integration: DT state selects the exact regulator child contract and provides PMIC clock and wake/interrupt integration for S2M/S5M drivers. Dependencies include multiple Samsung regulator schemas, the Samsung PMIC clock schema, and interrupt bindings. Risks include using S2MPS11-only quirk properties on other variants, wrong regulator child set for the selected compatible, and missing clock child cells when clock outputs are consumed. Test signals are schema branch validation per compatible, quirk rejection on nonmatching variants, delegated regulator checks, and runtime regulator/clock/RTC interrupt probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s2mps11.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s5m8767.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s5m8767.yaml

Purpose: Binding for the Samsung S5M8767 PMIC, describing regulators, clock outputs, interrupts, wakeup, input supplies, and buck DVS GPIO configuration.

Important schema surface and control flow: `compatible = "samsung,s5m8767-pmic"`, `reg`, and `regulators` are required. Optional `clocks` references the Samsung S2MPS11-style clock provider schema. The binding has detailed DVS properties for buck2, buck3, and buck4 voltage tables, DVS GPIOs, dynamic scaling enable flags, default DVS index, discharge GPIOs, and input supplies `vinb1-9` and `vinl1-9`. Dependency rules require DVS GPIOs when DVS voltage arrays or per-buck GPIO-DVS flags are present. Regulator details are delegated to the S5M8767 regulator schema.

State, dependencies, and integration: DT persists power-rail constraints and dynamic voltage scaling wiring used by Samsung PMIC regulator and clock drivers. Dependencies include the Samsung clock and regulator schemas, GPIO bindings, and interrupt bindings. Risks include incomplete DVS dependency sets, wrong default DVS index, GPIO polarity mistakes, and supply phandle omissions for enabled rails. Test signals are `dt_binding_check`, dependency failures for partial DVS descriptions, delegated regulator validation, and runtime DVS/regulator/clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/samsung,s5m8767.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/silergy,sy7636a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/silergy,sy7636a.yaml

Purpose: Schema for the Silergy SY7636A PMIC used by e-paper displays, combining a regulator, thermal sensor, and GPIO-controlled power-good/enable/VCOM behavior.

Important schema surface and control flow: `compatible = "silergy,sy7636a"`, `reg`, `#thermal-sensor-cells = 0`, `vin-supply`, and `regulators` are required. The binding also defines clock/address cell constants used by its child layout, `epd-pwr-good-gpios`, `enable-gpios`, and `vcom-en-gpios`. The regulator child is constrained to the expected SY7636A output and uses the common regulator schema with additional properties closed.

State, dependencies, and integration: DT state configures the I2C address, input supply, display power GPIOs, thermal sensor provider, and VCOM/regulator constraints for e-paper display stacks. Dependencies include regulator, thermal-sensor, GPIO, and I2C bindings plus the SY7636A MFD/regulator/thermal drivers. Risks include incorrect GPIO polarity delaying panel power sequencing, missing `vin-supply`, and treating the thermal sensor as multi-cell. Test signals are binding validation, thermal zone phandle resolution, regulator registration, and display power sequencing tests with power-good GPIO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/silergy,sy7636a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/spacemit,p1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/spacemit,p1.yaml

Purpose: Binding for the SpacemiT P1 PMIC, defining the I2C PMIC node, interrupt line, regulator input supplies, and regulator child tree.

Important schema surface and control flow: `compatible = "spacemit,p1"`, `reg`, `interrupts`, and `regulators` are required. The top-level supply properties identify six VIN inputs plus analog and digital LDO input groups (`aldoin`, `dldoin1`, `dldoin2`). The `regulators` object delegates valid rail names and properties to the SpacemiT P1 regulator schema and closes unevaluated properties.

State, dependencies, and integration: persistent DT records PMIC address, IRQ, input-supply topology, and regulator constraints for the P1 MFD/regulator driver. Dependencies include the SpacemiT regulator binding, common regulator/interrupt/I2C bindings, and board-level supply providers. Risks include missing parent supply phandles for enabled rails, using regulator child names outside the delegated schema, and interrupt polarity mistakes. Test signals are `dt_binding_check`, referenced regulator schema validation, and runtime regulator probe with input supply resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/spacemit,p1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,sc2731.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,sc2731.yaml

Purpose: Schema for Spreadtrum/Unisoc SC27xx PMICs connected over SPI, describing the PMIC interrupt controller, addressable child space, regulators, RTC, ADC, EIC, charger, and other MFD subblocks.

Important schema surface and control flow: `compatible` enumerates supported SC27xx variants; `reg`, `interrupts`, `interrupt-controller`, `spi-max-frequency`, `#address-cells = 1`, `#size-cells = 0`, and `#interrupt-cells = 1` are part of the top-level contract. The `regulators` subtree is delegated to the Spreadtrum regulator schema. Pattern properties allow child nodes at register offsets, with compatible-specific references for MFD subdevices such as ADC, RTC, charger, and EIC-style controllers.

State, dependencies, and integration: DT persists SPI addressing, IRQ demultiplexing, PMIC child register layout, and regulator configuration for Spreadtrum MFD child drivers. Dependencies include SPI peripheral semantics, regulator, IIO, RTC, power-supply, and interrupt-controller schemas. Risks include incorrect `#interrupt-cells` for PMIC child interrupts, SPI frequency mismatch, and variant-specific child blocks described with the wrong compatible. Test signals are schema validation, SPI child resource translation, interrupt-domain registration, and runtime probe of regulator and PMIC subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,sc2731.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,ums512-glbreg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,ums512-glbreg.yaml

Purpose: Binding for Unisoc UMS512 global register/syscon blocks that expose miscellaneous system control registers and child simple-MFD devices.

Important schema surface and control flow: `compatible` is an ordered list ending in `syscon` and `simple-mfd`; `reg`, `#address-cells = 1`, `#size-cells = 1`, and `ranges` are required. Pattern properties permit child nodes by unit address and rely on their own schemas for specific functionality. Additional properties are closed around the syscon/simple-MFD bus contract.

State, dependencies, and integration: DT state describes a memory-mapped global register window used as a regmap-backed syscon and as a parent bus for child devices. Dependencies include syscon conventions, simple-mfd child probing, address translation via `ranges`, and child-specific schemas. Risks include using an incomplete compatible list, omitting `ranges` so child registers cannot translate, and letting unrelated register fields leak into ad hoc child nodes. Test signals are binding checks, child node schema validation, syscon regmap lookup, and runtime child device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/sprd,ums512-glbreg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-lptimer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-lptimer.yaml

Purpose: Schema for STM32 low-power timer blocks, an MFD-style timer node that can expose PWM, counter, trigger/timer, and encoder-related child functions.

Important schema surface and control flow: the node requires `compatible`, `reg`, `clocks`, and `clock-names = "mux"`. Optional properties include one interrupt, DMA-style address/size cells, `wakeup-source`, access controllers, power domains, and child nodes `pwm`, `counter`, and `timer`. Child nodes reference PWM, counter, and timer-trigger semantics with required compatibles and cell counts. Pattern properties cover encoder child nodes with unit addresses.

State, dependencies, and integration: DT state configures a low-power timer MMIO block, clock input, optional wake IRQ, and child-function registration for STM32 timer drivers. Dependencies include clock, interrupt, power-domain, access-controller, PWM, counter, and timer-trigger bindings. Risks include missing child address cells when timer subnodes use `reg`, exposing unsupported child functions on a given SoC instance, and wakeup-source without a valid interrupt. Test signals are `dt_binding_check`, child schema validation, and runtime probe of PWM/counter/timer-trigger devices under the LPTIM parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-lptimer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-timers.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-timers.yaml

Purpose: Binding for STM32 general-purpose and low-power timer MFD nodes that may provide PWM, counter, timer-trigger, DMA, reset, interrupt, and power-domain integration.

Important schema surface and control flow: compatible values cover `st,stm32-timers` and `st,stm32-lptimer`; `reg`, `clocks`, and `clock-names = "int"` are required. Optional properties include reset, power domain, DMA channels and names, interrupt names, access controllers, and child nodes for `pwm`, `counter`, and `timer@N`. The `pwm` child validates `st,breakinput`, PWM cells, and compatible; the counter and timer-trigger children use their own constrained properties. Pattern properties allow timer trigger child nodes with unit addresses.

State, dependencies, and integration: the DT node represents a timer register block and advertises child devices that share the same hardware. Dependencies include STM32 clock/reset/power-domain bindings, DMA mappings, PWM/counter bindings, and interrupt definitions. Risks include DMA name/channel order mismatches, incorrect break-input tuples, missing reset controls on reset-gated timers, and invalid child `reg` values. Test signals are binding validation, example validation with DMA and PWM, runtime child creation, PWM output tests, counter reads, and trigger IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stm32-timers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmfx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmfx.yaml

Purpose: Schema for the ST STMFX I2C multi-function expander, covering GPIO expansion, optional IDD/touchscreen pin availability, open-drain behavior, supply, interrupt line, and pinctrl child configuration.

Important schema surface and control flow: top-level `compatible = "st,stmfx-0300"`, I2C `reg` of 0x42 or 0x43, and `interrupts` are required. Optional properties include `drive-open-drain` and `vdd-supply`. The `pinctrl` child requires `compatible = "st,stmfx-0300-pinctrl"`, GPIO and interrupt controller cells, `gpio-ranges`, and allows `*-pins` groups using pinmux-node semantics plus bias, drive, and output configuration properties.

State, dependencies, and integration: DT state configures the STMFX MFD and its pinctrl/GPIO/IRQ providers, including which pins are available when touchscreen or IDD functions consume analog GPIOs. Dependencies include I2C, interrupt, regulator supply, GPIO, and pinctrl bindings. Risks include incorrect `gpio-ranges` when some analog pins are unavailable, using an unsupported I2C address, and missing interrupt-controller cells in the pinctrl child. Test signals are schema validation, pin group validation, GPIO range sanity, and runtime GPIO/IRQ/pinctrl provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmfx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmpe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmpe.yaml

Purpose: Binding for ST STMPE port expanders over I2C or SPI, describing a parent MFD with optional GPIO, keypad, ADC, PWM, touchscreen, reset, supplies, wakeup, and ADC timing controls.

Important schema surface and control flow: compatible enumerates STMPE601/801/811/1600/1601/2401/2403; `reg` and `interrupts` are required. `allOf` imports SPI peripheral properties. Optional top-level controls include `vcc-supply`, `vio-supply`, reset GPIO, wakeup, autosleep timeout, sample time, ADC bit mode, reference select, and ADC frequency. Child nodes reference dedicated schemas for ADC and GPIO, matrix-keymap for keypad, PWM schema for PWM, and touchscreen schema for touch input while constraining STMPE-specific timing/current properties.

State, dependencies, and integration: DT persists bus identity, interrupt wiring, power supplies, low-power timing, and enabled child functions for STMPE MFD child drivers. Dependencies include SPI/I2C, GPIO, IIO ADC, PWM, input matrix-keymap, touchscreen, regulator, and interrupt bindings. Risks include enabling child functions unsupported by a specific chip variant, invalid ADC timing enum values, and incomplete keypad `linux,keymap`. Test signals are binding validation, child schema validation, SPI property validation when used on SPI, and runtime probe of GPIO/ADC/keypad/PWM/touchscreen children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stmpe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stpmic1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stpmic1.yaml

Purpose: Schema for the ST STPMIC1 PMIC MFD, covering PMIC interrupt controller, onkey input, watchdog, and a rich regulator subtree with over-current interrupts and reset-mask behavior.

Important schema surface and control flow: `compatible = "st,stpmic1"`, `reg = 0x33`, `interrupts`, `#interrupt-cells = 2`, and `interrupt-controller` are required. Optional `onkey` references input semantics and requires falling/rising interrupts and names, with power-off timing and ST-specific flags. Optional `watchdog` references watchdog semantics. The `regulators` child requires `compatible = "st,stpmic1-regulators"` and defines buck, LDO, vref, boost, and power-switch children, with supply pattern properties, per-rail allowed regulator properties, optional current-limit interrupts, and `st,mask-reset` on selected rails.

State, dependencies, and integration: DT configures PMIC IRQ demultiplexing, onkey behavior, watchdog, regulator constraints, supply inputs, and fault handling for STPMIC1 drivers. Dependencies include input, watchdog, regulator, interrupt, and STPMIC1 IRQ constant bindings. Risks include wrong interrupt IDs/names for onkey or regulator current limits, using disallowed regulator properties on fixed switches, and masking reset on rails that should reset with the PMIC. Test signals are `dt_binding_check`, per-rail additional-property rejection, example validation, and runtime registration of interrupt, onkey, watchdog, and regulator cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/st,stpmic1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,ab8500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,ab8500.yaml

Purpose: Large MFD schema for the ST-Ericsson AB8500 and AB8505 analog baseband PMIC used with U8500 platforms, covering power, ADC, battery, charger, fuel gauge, RTC, USB PHY, GPIO, clock, PWM, codec, key, thermal, and regulator subblocks.

Important schema surface and control flow: top-level compatible is `stericsson,ab8500` or `stericsson,ab8505`; the node is also an interrupt controller with one-cell address space for children. Required child blocks include `clock-controller`, `gpio`, `rtc`, `adc`, `thermal`, `ab8500_fg`, `ab8500_btemp`, `ab8500_charger`, `ab8500_chargalg`, `phy`, `key`, and `regulator`. Many child schemas are inline, while battery and charger blocks reference dedicated power-supply schemas. Regulator children enumerate internal and external rails, including AB8505-only rails, and PWM blocks are matched by `pwm@N` pattern properties.

State, dependencies, and integration: DT represents the AB8500 as a PRCMU child with many MFD cells and a shared interrupt domain. Dependencies include regulator, IIO ADC, power-supply, USB PHY, input, clock, PWM, GPIO, RTC, thermal, and interrupt-controller bindings. Risks include missing one of the many required child blocks, describing AB8505-only rails on AB8500 boards, interrupt-name order mistakes, and old U8500 platform coupling through PRCMU. Test signals are full `dt_binding_check`, child schema validation, interrupt-domain creation, and runtime probe of battery/charger/regulator/USB/RTC/GPIO/clock children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,ab8500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,db8500-prcmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,db8500-prcmu.yaml

Purpose: Binding for the ST-Ericsson DB8500 PRCMU, an always-on power/reset/control microcontroller that exposes syscon registers, regulators, clocks, reset, interrupt control, and nested AB8500 analog-baseband integration.

Important schema surface and control flow: compatible must be `stericsson,db8500-prcmu`, then `syscon`. The node requires three register ranges with names `prcmu`, `prcmu-tcpm`, and `prcmu-tcdm`, one interrupt, address/size cells, `ranges`, interrupt-controller cells, and a `db8500-prcmu-regulators` child. The regulator child enumerates many SoC-internal voltage domains and references the common regulator schema. Pattern properties cover clock-controller, reset-controller, and AB8500 child nodes with their own required compatible/resource contracts.

State, dependencies, and integration: DT state models the PRCMU as both syscon/regmap and MFD parent for power, clock, reset, interrupt, and AB8500 control paths. Dependencies include syscon, regulator, clock, reset, interrupt-controller, and AB8500 schemas. Risks include register range ordering mistakes, missing `ranges` for child translation, regulator child omissions that break platform power domains, and overbroad syscon access expectations. Test signals are binding validation, reg-name ordering checks, syscon lookup, regulator provider creation, and runtime child probe of PRCMU clock/reset/AB8500 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/stericsson,db8500-prcmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon-common.yaml

Purpose: Common schema fragment for system-controller register blocks that exposes reusable properties shared by syscon-style bindings.

Important schema surface and control flow: the schema requires `compatible` and includes common property definitions for syscon register regions, notably `reg-io-width` constrained to 1, 2, 4, or 8 bytes. Its `allOf` logic aligns the fragment with the core simple-bus/syscon-style contract and is intended for inclusion by concrete syscon bindings rather than direct board use alone.

State, dependencies, and integration: persistent DT state described through this fragment becomes regmap configuration and compatible matching for system controller drivers and consumers. Dependencies include the DT core schema and concrete bindings that include this common fragment, especially `syscon.yaml`. Risks include concrete bindings forgetting to include this common schema, invalid I/O width values that produce wrong regmap access size, and treating the common file as a complete device binding. Test signals are schema validation of including bindings and `dt_binding_check` failures for unsupported `reg-io-width`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon.yaml

Purpose: Main binding for system-controller (`syscon`) devices, covering many SoC-specific miscellaneous register blocks that expose regmap-backed system control and may act as simple-MFD parents.

Important schema surface and control flow: the schema enumerates many allowed compatible sequences, including vendor-specific compatibles followed by `syscon`, and in some cases `simple-mfd`. `reg` is required, and optional `resets` supports reset-gated syscon blocks. `allOf` includes `syscon-common.yaml` and conditional restrictions for compatible-specific combinations. The binding rejects additional top-level properties outside the syscon contract unless allowed by included schemas.

State, dependencies, and integration: DT syscon nodes persist MMIO register windows accessed by many drivers through syscon/regmap phandles, reset controllers, power/reset children, or simple-MFD child devices. Dependencies include syscon-common, reset bindings, simple-mfd conventions, and many consumer drivers that call syscon lookup APIs. Risks include adding arbitrary register blocks under generic `syscon` without a specific compatible, wrong compatible ordering, exposing unrelated hardware through one regmap, and missing reset controls. Test signals are `dt_binding_check`, compatible sequence validation, syscon lookup by phandle/compatible at runtime, and child-device probe when `simple-mfd` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,am3359-tscadc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,am3359-tscadc.yaml

Purpose: Schema for the TI AM3359 touchscreen controller and ADC MFD, describing the shared TSCADC hardware block and its ADC, touchscreen, or magnetic reader child functions.

Important schema surface and control flow: compatible values identify the AM3359 TSCADC family; `reg`, `interrupts`, `clocks`, `clock-names = "fck"`, and child function nodes are part of the contract. Optional DMA channels are named and ordered, and `power-domains` is allowed for SoCs that gate the block. The `adc`, `tsc`, and `mag` children are referenced through their dedicated schemas.

State, dependencies, and integration: DT state describes one MMIO and IRQ resource shared by multiple MFD children plus optional DMA and power-domain wiring. Dependencies include clock, DMA, power-domain, IIO ADC, input touchscreen, and TI child bindings. Risks include enabling both child functions without matching hardware muxing, DMA name/order mismatches, and missing functional clock names. Test signals are binding validation, child schema validation, runtime probe of `ti_am335x_tscadc` and ADC/touchscreen children, and input/IIO data flow tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,am3359-tscadc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml

Purpose: Binding for the TI BQ25703A charger manager and buck/boost converter, combining power-supply charger configuration with a regulator child output.

Important schema surface and control flow: `allOf` references the generic power-supply schema. `compatible = "ti,bq25703a"`, `reg = 0x6b`, `monitored-battery`, and `regulators` are required; optional properties include `input-current-limit-microamp` and one interrupt. The `regulators` child constrains the charger converter regulator node and uses common regulator properties for voltage/current naming and constraints.

State, dependencies, and integration: DT state provides the I2C address, battery phandle, charger input-current limit, interrupt wiring, and buck/boost regulator setup for charger and regulator drivers. Dependencies include power-supply, battery, regulator, and interrupt bindings. Risks include omitting `monitored-battery`, setting unsafe input-current limits, and treating the converter regulator as a generic PMIC rail without charger constraints. Test signals are `dt_binding_check`, power-supply schema validation, battery phandle resolution, and runtime charger plus regulator registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,bq25703a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp8732.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp8732.yaml

Purpose: Schema for TI LP8732/LP8733 PMICs, describing a compact PMIC with regulators and GPIO provider capability.

Important schema surface and control flow: compatible enumerates LP873x variants; `reg`, GPIO controller declaration, `#gpio-cells = 2`, and `regulators` are required. The regulator subtree references the LP873x regulator schema and supply pattern properties describe input phandles for buck and LDO rails. Additional properties are rejected.

State, dependencies, and integration: persistent DT configures I2C address, GPIO provider cells, rail input supplies, and regulator constraints for LP873x MFD, GPIO, and regulator drivers. Dependencies include TI LP873x regulator schema, GPIO binding, and regulator framework bindings. Risks include missing GPIO provider properties, wrong variant compatible, and supply phandles that do not match enabled regulator children. Test signals are binding validation, delegated regulator validation, GPIO provider registration, and runtime regulator supply resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp8732.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87524-q1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87524-q1.yaml

Purpose: Binding for the TI LP87524-Q1 four 1-phase buck converter PMIC with reset GPIO, GPIO provider support, supply inputs, and regulator children.

Important schema surface and control flow: the node requires `compatible = "ti,lp87524-q1"`, `reg = 0x60`, `gpio-controller`, `#gpio-cells = 2`, and `regulators`. Optional `reset-gpios` describes the PMIC reset line. The regulator subtree delegates rail validation to the LP87524-Q1 regulator schema, while pattern properties capture per-buck input supply phandles.

State, dependencies, and integration: DT state configures the PMIC address, reset line, GPIO provider role, buck input supplies, and regulator constraints consumed by TI PMIC drivers. Dependencies include GPIO and regulator schemas, the TI LP87524 regulator binding, and I2C bus binding. Risks include using this four-phase-compatible schema for other LP8756x topologies, missing reset polarity, and incomplete input supplies. Test signals are `dt_binding_check`, regulator child validation, GPIO provider probe, and regulator enable/voltage checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87524-q1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87561-q1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87561-q1.yaml

Purpose: Schema for TI LP87561-Q1, a single 4-phase buck converter PMIC with GPIO provider support and optional reset line.

Important schema surface and control flow: required properties include `compatible = "ti,lp87561-q1"`, `reg = 0x60`, GPIO controller declaration, `#gpio-cells = 2`, `buck3210-in-supply`, and `regulators`. Optional `reset-gpios` controls PMIC reset. The regulator child is constrained to the single combined multiphase buck topology through the LP87561-Q1 regulator schema.

State, dependencies, and integration: DT persists the combined buck input supply, reset wiring, GPIO provider cells, and regulator constraints for LP87561 drivers. Dependencies include TI LP87561 regulator schema, GPIO and regulator bindings, and I2C. Risks include describing split-buck rails on this single-output topology, omitting the combined input supply, and wrong reset GPIO polarity. Test signals are binding validation, delegated regulator checks, runtime regulator registration for the combined buck, and GPIO provider probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87561-q1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87565-q1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87565-q1.yaml

Purpose: Binding for TI LP87565 and LP87565-Q1 dual 2-phase buck PMICs, describing regulator topology, input supplies, reset GPIO, and GPIO provider role.

Important schema surface and control flow: compatible is `ti,lp87565` or `ti,lp87565-q1`; `reg = 0x60`, GPIO controller declaration, `#gpio-cells = 2`, `buck10-in-supply`, `buck23-in-supply`, and `regulators` are required. Optional `reset-gpios` describes PMIC reset. The regulator subtree is delegated to the LP87565 regulator schema for the two combined buck outputs.

State, dependencies, and integration: persistent DT configures two input supply groups, reset, GPIO cells, and dual buck regulator constraints for TI LP87565 drivers. Dependencies include the TI regulator schema, GPIO and regulator common schemas, and I2C. Risks include using single- or four-phase supply naming from adjacent LP875 variants, missing one of the input groups, and invalid regulator child names. Test signals are schema validation, delegated regulator validation, and runtime probe of GPIO plus two buck regulator outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,lp87565-q1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,nspire-misc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,nspire-misc.yaml

Purpose: Schema for the TI Nspire miscellaneous system controller block, a syscon/simple-MFD register area containing at least a reboot controller child.

Important schema surface and control flow: compatible must be the ordered sequence `ti,nspire-misc`, `syscon`, `simple-mfd`; `reg` and `reboot` are required. The `reboot` child references `/schemas/power/reset/syscon-reboot.yaml`, so offset/value semantics are validated by the generic syscon reboot binding.

State, dependencies, and integration: DT state creates a syscon regmap for the MISC register window and a child reboot device that writes a reset value at a configured offset. Dependencies include syscon, simple-mfd, and syscon-reboot bindings plus reset/power drivers. Risks include wrong compatible order, incorrect reboot offset/value causing failed or unsafe reset, and omitting `simple-mfd` so the reboot child is not populated. Test signals are `dt_binding_check`, syscon-reboot child validation, and runtime reboot path testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,nspire-misc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65086.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65086.yaml

Purpose: Binding for the TI TPS65086 PMIC, describing I2C address, optional interrupt controller, GPIO provider, and regulators including buck-specific step-size and decay options.

Important schema surface and control flow: required properties are `compatible = "ti,tps65086"`, `reg = 0x5e`, `gpio-controller`, `#gpio-cells = 2`, and `regulators`; interrupt-controller properties are optional but defined. The `regulators` child allows `buck1-6`, `ldoa1-3`, `swa1`, `swb1-2`, and `vtt`. Buck nodes accept common regulator properties plus TI-specific `ti,regulator-step-size-25mv` and `ti,regulator-decay`; LDO/switch nodes accept a narrower set.

State, dependencies, and integration: DT persists regulator constraints, buck voltage encoding quirks, GPIO provider cells, and optional interrupt domain configuration for TPS65086 drivers. Dependencies include common regulator/GPIO/interrupt bindings and the TPS65086 MFD/regulator/GPIO drivers. Risks include applying buck-only TI properties to non-buck rails, omitting GPIO provider fields, and wrong fixed I2C address. Test signals are binding validation, per-regulator additional-property rejection, GPIO provider registration, and runtime buck voltage/decay behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65086.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65910.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65910.yaml

Purpose: Binding for TI TPS65910 and TPS65911 PMICs, covering regulators, GPIO, RTC/interrupt controller behavior, sleep policy, battery comparator thresholds, 32 kHz oscillator, and input supplies.

Important schema surface and control flow: compatible selects `ti,tps65910` or `ti,tps65911`; `reg`, `gpio-controller`, `#gpio-cells`, and `regulators` are required. Optional interrupt-controller fields, battery threshold enums, sleep-control booleans, 9-element `ti,en-gpio-sleep`, and `ti,system-power-controller` tune PMIC behavior. Regulator pattern properties accept multiple rail name sets with `ti,regulator-ext-sleep-control`. Supply pattern properties document `vcc1-7` and `vccio` mappings. `allOf` disables TPS65911-only LDO/vddctrl rails on TPS65910 and disables TPS65910-only rails on TPS65911.

State, dependencies, and integration: DT configures variant-specific rail maps, GPIO/IRQ providers, sleep behavior, oscillator policy, and system power-off ownership. Dependencies include regulator, GPIO, interrupt, and types schemas plus TPS65910 MFD/regulator drivers. Risks include wrong variant rail names, invalid sleep-control arrays, missing input supplies for enabled regulators, and legacy `ti,system-power-controller` semantics. Test signals are binding validation for both variants, `allOf` rail rejection, GPIO/IRQ provider probe, and regulator sleep-state behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps65910.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps6594.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps6594.yaml

Purpose: Schema for TI TPS6594-family PMICs, including TPS6594-Q1, TPS6593-Q1, LP8764-Q1, TPS65224-Q1, and TPS652G1, with regulators, GPIOs, RTC/watchdog/ESM/PFSM features, and primary-PMIC synchronization role.

Important schema surface and control flow: `compatible`, `reg`, and `interrupts` are required. Optional `ti,primary-pmic` marks the SPMI synchronization controller PMIC, `system-power-controller` enables power-off role, and GPIO provider fields expose PMIC GPIOs. Regulator children allow bucks `buck1-5`, combined rails `buck12`, `buck34`, `buck123`, `buck1234`, and `ldo1-4`; `allOf` disallows incompatible combined buck groupings, such as using `buck123` together with `buck34`. Pattern properties define per-buck and per-LDO input supply phandles.

State, dependencies, and integration: DT state configures PMIC bus address or SPI chip select, IRQ, GPIOs, supply topology, combined buck topology, and system power/synchronization role for TPS6594-family MFD and regulator drivers. Dependencies include regulator, GPIO, interrupt, I2C/SPI bus, and TI PMIC driver support. Risks include invalid combined-buck descriptions, wrong primary PMIC designation in multi-PMIC systems, missing GPIO cells when `gpio-controller` is set, and compatible/rail mismatches across derivatives. Test signals are `dt_binding_check`, `allOf` buck-combination failures, runtime regulator and GPIO provider probe, and multi-PMIC power-state synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,tps6594.yaml -->
