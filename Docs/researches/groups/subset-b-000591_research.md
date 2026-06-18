# Research Group subset-b-000591

This grouped report covers Linux devicetree binding YAML schemas for MFD, MIPS platform, misc platform, and MMC/SD/SDHCI hardware under the Ceph client source tree. Each source file was read and parsed as YAML; each section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,twl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,twl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,twl.yaml` defines the MFD parent or mixed-function device binding titled `Texas Instruments TWL family`. The TWLs are Integrated Power Management Chips. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 3 tokens: `ti,twl4030`, `ti,twl6030`, `ti,twl6032`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-controller`, `system-power-controller`, `#interrupt-cells`, `#clock-cells`, `clocks`, `clock-names`, `charger`, `rtc`, `madc`, `pwrbutton`, `watchdog`, `audio`, `keypad`, `twl4030-usb`, `gpio`, `power`, `gpadc`, `usb-comparator`, `pwm`, `pwmled`. Required top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`. Pattern properties are `^regulator-`. Nested required-property signals include `compatible`, `#pwm-cells`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Andreas Kemnade <andreas@kemnade.info>. Direct schema dependencies include `/schemas/iio/adc/ti,twl4030-madc.yaml`, `/schemas/iio/adc/ti,twl6030-gpadc.yaml`, `/schemas/power/supply/ti,twl6030-charger.yaml`, `/schemas/power/supply/twl4030-charger.yaml`, `/schemas/pwm/pwm.yaml#`, `/schemas/regulator/regulator.yaml`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ti,twl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ti,twl.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ti,twl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/wlf,arizona.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/wlf,arizona.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/wlf,arizona.yaml` defines the MFD parent or mixed-function device binding titled `Cirrus Logic/Wolfson Microelectronics Arizona class audio SoCs`. These devices are audio SoCs with extensive digital capabilities and a range of analogue I/O. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 8 tokens: `cirrus,cs47l24`, `wlf,wm1814`, `wlf,wm1831`, `wlf,wm5102`, `wlf,wm5110`, `wlf,wm8280`, `wlf,wm8997`, `wlf,wm8998`. Top-level properties are `compatible`, `reg`, `AVDD-supply`, `CPVDD-supply`, `DBVDD1-supply`, `DCVDD-supply`, `MICVDD-supply`, `gpio-controller`, `#gpio-cells`, `wlf,gpio-defaults`, `interrupt-controller`, `#interrupt-cells`, `interrupts`, `clocks`, `clock-names`, `reset-gpios`, `wlf,reset`. Required top-level properties are `compatible`, `AVDD-supply`, `CPVDD-supply`, `DBVDD1-supply`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`. Pattern properties are none. Nested required-property signals include `DCVDD-supply`, `MICVDD-supply`, `DBVDD2-supply`, `DBVDD3-supply`, `SPKVDD-supply`, `SPKVDDL-supply`, `SPKVDDR-supply`, `compatible`, `AVDD-supply`, `CPVDD-supply`, `DBVDD1-supply`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`, `interrupts`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Direct schema dependencies include `/schemas/extcon/wlf,arizona.yaml#`, `/schemas/regulator/wlf,arizona.yaml#`, `/schemas/sound/wlf,arizona.yaml#`, `/schemas/spi/spi-peripheral-props.yaml`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/wlf,arizona.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/wlf,arizona.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/wlf,arizona.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml` defines the MFD parent or mixed-function device binding titled `X-Powers AC100`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `x-powers,ac100`. Top-level properties are `compatible`, `reg`, `codec`, `rtc`. Required top-level properties are `compatible`, `reg`, `codec`, `rtc`. Pattern properties are none. Nested required-property signals include `#clock-cells`, `compatible`, `interrupts`, `clock-output-names`, `clocks`, `reg`, `codec`, `rtc`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,ac100.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml` defines the MFD parent or mixed-function device binding titled `X-Powers AXP PMIC`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 5 branches with 18 tokens: `x-powers,axp152`, `x-powers,axp192`, `x-powers,axp202`, `x-powers,axp209`, `x-powers,axp221`, `x-powers,axp223`, `x-powers,axp313a`, `x-powers,axp323`, `x-powers,axp717`, `x-powers,axp803`, `x-powers,axp806`, `x-powers,axp809`, `x-powers,axp813`, `x-powers,axp15060`, `x-powers,axp228`, `x-powers,axp805`, and 2 more. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `x-powers,drive-vbus-en`, `x-powers,self-working-mode`, `x-powers,master-mode`, `vin1-supply`, `vin2-supply`, `vin3-supply`, `vin4-supply`, `vin5-supply`, `vin6-supply`, `vin7-supply`, `vina-supply`, `vinb-supply`, `vinc-supply`, `vind-supply`, `vine-supply`, `acin-supply`, `ldo24in-supply`, `ldo3in-supply`, `ldo5in-supply`, `aldoin-supply`, `bldoin-supply`, `cldoin-supply`, `dldoin-supply`, and 11 more. Required top-level properties are `compatible`, `reg`, `#interrupt-cells`, `interrupt-controller`. Pattern properties are none. Nested required-property signals include `interrupts`, `compatible`, `reg`, `#interrupt-cells`, `interrupt-controller`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>. Direct schema dependencies include `/schemas/gpio/x-powers,axp209-gpio.yaml#`, `/schemas/iio/adc/x-powers,axp209-adc.yaml#`, `/schemas/power/supply/x-powers,axp20x-ac-power-supply.yaml#`, `/schemas/power/supply/x-powers,axp20x-battery-power-supply.yaml#`, `/schemas/power/supply/x-powers,axp20x-usb-power-supply.yaml#`, `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/x-powers,axp152.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` defines the MFD parent or mixed-function device binding titled `Xylon LogiCVC multi-function device`. The LogiCVC is a display controller that also contains a GPIO controller. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 3 tokens: `xylon,logicvc-3.02.a`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^gpio@[0-9a-f]+$`, `^display@[0-9a-f]+$`. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Paul Kocialkowski <paul.kocialkowski@bootlin.com>. Direct schema dependencies include `/schemas/display/xylon,logicvc-display.yaml#`, `/schemas/gpio/xylon,logicvc-gpio.yaml#`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/xylon,logicvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml` defines the MFD parent or mixed-function device binding titled `Zodiac Inflight Innovations RAVE Supervisory Processor`. RAVE Supervisory Processor communicates with SoC over UART. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 5 tokens: `zii,rave-sp-niu`, `zii,rave-sp-mezz`, `zii,rave-sp-esb`, `zii,rave-sp-rdu1`, `zii,rave-sp-rdu2`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`, `watchdog`, `backlight`, `pwrbutton`. Required top-level properties are `compatible`. Pattern properties are `^eeprom@[0-9a-f]+$`. Nested required-property signals include `compatible`. The highest-risk API details are child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including MFD runtime state such as regmap access, IRQ chip registration, child-device population, and parent-controlled power/reset sequencing.

## Dependencies and Integration Points
Maintainers listed: Frank Li <Frank.Li@nxp.com>. Direct schema dependencies include `/schemas/input/zii,rave-sp-pwrbutton.yaml`, `/schemas/leds/backlight/zii,rave-sp-backlight.yaml`, `/schemas/nvmem/zii,rave-sp-eeprom.yaml`, `/schemas/serial/serial-peripheral-props.yaml`, `/schemas/watchdog/zii,rave-sp-wdt.yaml`. Integration points include the MFD core, regmap-backed child devices, IRQ domains, I2C/SPI/platform probing, regulators, RTC, GPIO, pinctrl, codec, display, or power-management child nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to child-node naming, address-cell layout, interrupt-controller cells, child compatible strings, regmap range boundaries, and whether unknown children are rejected, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/zii,rave-sp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml` defines the MIPS platform or SoC binding titled `Broadcom cable/DSL/settop platforms`. Boards Broadcom cable/DSL/settop SoC shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 18 tokens: `brcm,bcm3368`, `brcm,bcm3384`, `brcm,bcm33843`, `brcm,bcm3384-viper`, `brcm,bcm33843-viper`, `brcm,bcm6328`, `brcm,bcm6358`, `brcm,bcm6362`, `brcm,bcm6368`, `brcm,bcm63168`, `brcm,bcm63268`, `brcm,bcm7125`, `brcm,bcm7346`, `brcm,bcm7358`, `brcm,bcm7360`, `brcm,bcm7362`, and 2 more. Top-level properties are `$nodename`, `compatible`, `cpus`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include `mips-hpt-frequency`, `brcm,bmips-cbr-reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `if`, `then`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Florian Fainelli <f.fainelli@gmail.com>. Direct schema dependencies include `/schemas/mips/cpus.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/brcm/soc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/brcm/soc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml` defines the MIPS platform or SoC binding titled `MIPS CPUs`. The device tree allows to describe the layout of CPUs in a system through the "cpus" node, which in turn contains a number of subnodes (ie "cpu") defining properties for every CPU. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 23 tokens: `brcm,bmips3300`, `brcm,bmips4350`, `brcm,bmips4380`, `brcm,bmips5000`, `brcm,bmips5200`, `img,i6500`, `ingenic,xburst-fpu1.0-mxu1.1`, `ingenic,xburst-fpu2.0-mxu2.0`, `ingenic,xburst-mxu1.0`, `ingenic,xburst2-fpu2.1-mxu2.1-smt`, `loongson,gs264`, `mips,m14Kc`, `mips,mips1004Kc`, `mips,mips24KEc`, `mips,mips24Kc`, `mips,mips34Kc`, and 7 more. Top-level properties are `compatible`, `reg`, `clocks`, `device_type`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `device_type`, `clocks`, `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Thomas Bogendoerfer <tsbogend@alpha.franken.de>, 周琰杰 (Zhou Yanjie) <zhouyanjie@wanyeetech.com>. Direct schema dependencies include `/schemas/opp/opp-v1.yaml#`. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/cpus.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/cpus.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/econet.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/econet.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/econet.yaml` defines the MIPS platform or SoC binding titled `EcoNet MIPS SoCs`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 1 branch with 2 tokens: `smartfiber,xp8421-b`, `econet,en751221`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Caleb James DeLisle <cjd@cjdns.fr>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/econet.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/econet.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/econet.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ingenic/devices.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ingenic/devices.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ingenic/devices.yaml` defines the MIPS platform or SoC binding titled `Ingenic XBurst based Platforms`. Devices with a Ingenic XBurst CPU shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 7 branches with 14 tokens: `qi,lb60`, `ingenic,jz4740`, `ylm,rs90`, `ingenic,jz4725b`, `gcw,zero`, `ingenic,jz4770`, `img,ci20`, `ingenic,jz4780`, `yna,cu1000-neo`, `ingenic,x1000e`, `yna,cu1830-neo`, `ingenic,x1830`, `yna,cu2000-neo`, `ingenic,x2000e`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: 周琰杰 (Zhou Yanjie) <zhouyanjie@wanyeetech.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: large compatible catalogues are prone to missing fallback ordering or stale driver matches; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ingenic/devices.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ingenic/devices.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ingenic/devices.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml` defines the MIPS platform or SoC binding titled `Lantiq Xway SoC series Clock Generation Unit (CGU)`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `lantiq,cgu-xway`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: John Crispin <john@phrozen.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,cgu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml` defines the MIPS platform or SoC binding titled `Lantiq Xway SoCs DMA Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `lantiq,dma-xway`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: John Crispin <john@phrozen.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,dma-xway.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml` defines the MIPS platform or SoC binding titled `Lantiq Xway SoC series External Bus Unit (EBU)`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `lantiq,ebu-xway`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: John Crispin <john@phrozen.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,ebu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml` defines the MIPS platform or SoC binding titled `Lantiq Xway SoC series Power Management Unit (PMU)`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `lantiq,pmu-xway`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: John Crispin <john@phrozen.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/lantiq/lantiq,pmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/devices.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/devices.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/devices.yaml` defines the MIPS platform or SoC binding titled `Loongson based Platforms`. Devices with a Loongson CPU shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 7 branches with 11 tokens: `loongson,loongson64c-4core-ls7a`, `loongson,loongson64c-4core-rs780e`, `loongson,loongson64c-8core-rs780e`, `loongson,loongson64g-4core-ls7a`, `loongson,loongson64v-4core-virtio`, `loongson,ls1b-demo`, `loongson,lsgz-1b-dev`, `loongson,ls1b`, `loongmasses,smartloong-1c`, `loongson,cq-t300b`, `loongson,ls1c`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Jiaxun Yang <jiaxun.yang@flygoat.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: large compatible catalogues are prone to missing fallback ordering or stale driver matches; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/devices.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/devices.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/devices.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml` defines the MIPS platform or SoC binding titled `Loongson 2K1000 PM Controller`. This controller can be found in Loongson-2K1000 Soc systems. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `loongson,ls2k-pm`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Qing Zhang <zhangqing@loongson.cn>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/ls2k-reset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml` defines the MIPS platform or SoC binding titled `Loongson RS780E PCH ACPI Controller`. This controller can be found in Loongson-3 systems with RS780E PCH. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `loongson,rs780e-acpi`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Jiaxun Yang <jiaxun.yang@flygoat.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/loongson/rs780e-acpi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mobileye.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mobileye.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mobileye.yaml` defines the MIPS platform or SoC binding titled `Mobileye SoC series`. Boards with a Mobileye SoC shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 6 tokens: `mobileye,eyeq5-epm5`, `mobileye,eyeq5`, `mobileye,eyeq6h-epm6`, `mobileye,eyeq6h`, `mobileye,eyeq6lplus-epm6`, `mobileye,eyeq6lplus`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Vladimir Kondratiev <vladimir.kondratiev@intel.com>, Gregory CLEMENT <gregory.clement@bootlin.com>, Théo Lebrun <theo.lebrun@bootlin.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mobileye.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mobileye.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mobileye.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` defines the MIPS platform or SoC binding titled `MIPS Coherence Manager`. The Coherence Manager (CM) is responsible for establishing the global ordering of requests from all elements of the system and sending the correct data back to the requester. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `mti,mips-cm`, `mobileye,eyeq6-cm`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`. Pattern properties are none. Nested required-property signals include `compatible`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Jiaxun Yang <jiaxun.yang@flygoat.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml` defines the MIPS platform or SoC binding titled `Ralink SoC based Platforms`. Boards with a Ralink SoC shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 12 branches with 21 tokens: `ralink,rt2880-eval-board`, `ralink,rt2880-soc`, `ralink,rt3050-soc`, `ralink,rt3052-eval-board`, `ralink,rt3052-soc`, `ralink,rt3350-soc`, `ralink,rt3352-soc`, `ralink,rt3883-eval-board`, `ralink,rt3383-soc`, `ralink,rt5350-soc`, `ralink,mt7620a-eval-board`, `ralink,mt7620a-soc`, `ralink,mt7620n-soc`, `onion,omega2+`, `vocore,vocore2`, `ralink,mt7628a-soc`, and 5 more. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Sergio Paracuellos <sergio.paracuellos@gmail.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: large compatible catalogues are prone to missing fallback ordering or stale driver matches; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ralink.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ralink.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/realtek-rtl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/realtek-rtl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/realtek-rtl.yaml` defines the MIPS platform or SoC binding titled `Realtek RTL83xx/93xx SoC series`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 4 tokens: `cisco,sg220-26`, `realtek,rtl8382-soc`, `cameo,rtl9302c-2x-rtl8224-2xge`, `realtek,rtl9302-soc`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Bert Vermeulen <bert@biot.com>, Sander Vanheule <sander@svanheule.net>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/realtek-rtl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/realtek-rtl.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/realtek-rtl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml` defines the miscellaneous platform device binding titled `Aspeed Coprocessor Vectored Interrupt Controller`. The Aspeed AST2400 and AST2500 SoCs have a controller that provides interrupts to the ColdFire coprocessor. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 3 tokens: `aspeed,ast2400-cvic`, `aspeed,ast2500-cvic`, `aspeed,cvic`. Top-level properties are `compatible`, `reg`, `valid-sources`, `copro-sw-interrupts`. Required top-level properties are `compatible`, `reg`, `valid-sources`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `valid-sources`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Andrew Jeffery <andrew@codeconstruct.com.au>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/aspeed,ast2400-cvic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml` defines the miscellaneous platform device binding titled `DPAA2 console support`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `fsl,dpaa2-console`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Laurentiu Tudor <laurentiu.tudor@nxp.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,dpaa2-console.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml` defines the miscellaneous platform device binding titled `Freescale Management Complex`. The Freescale Management Complex (fsl-mc) is a hardware resource manager that manages specialized hardware objects used in network-oriented packet processing applications. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 1 token: `fsl,qoriq-mc`. Top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `iommu-map`, `msi-map`, `msi-parent`, `dma-coherent`, `dpmacs`. Required top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Frank Li <Frank.Li@nxp.com>. Direct schema dependencies include `/schemas/net/fsl,qoriq-mc-dpmac.yaml`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/fsl,qoriq-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ge-achc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ge-achc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ge-achc.yaml` defines the miscellaneous platform device binding titled `GE Healthcare USB Management Controller`. A device which handles data acquisition from compatible USB based peripherals. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 2 tokens: `ge,achc`, `nxp,kinetis-k20`. Top-level properties are `compatible`, `clocks`, `vdd-supply`, `vdda-supply`, `reg`, `reset-gpios`. Required top-level properties are `compatible`, `clocks`, `reg`, `reset-gpios`. Pattern properties are none. Nested required-property signals include `compatible`, `clocks`, `reg`, `reset-gpios`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Sebastian Reichel <sre@kernel.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ge-achc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ge-achc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ge-achc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/google,android-pipe.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/google,android-pipe.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/google,android-pipe.yaml` defines the miscellaneous platform device binding titled `Android Goldfish QEMU Pipe`. Android QEMU pipe virtual device generated by Android emulator. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `google,android-pipe`. Top-level properties are `compatible`, `reg`, `interrupts`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Kuan-Wei Chiu <visitorckw@gmail.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/google,android-pipe.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/google,android-pipe.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/google,android-pipe.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/idt,89hpesx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/idt,89hpesx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/idt,89hpesx.yaml` defines the miscellaneous platform device binding titled `EEPROM / CSR SMBus-slave interface of IDT 89HPESx devices`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 4 branches with 0 tokens: no explicit compatible constants. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^eeprom@`. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Serge Semin <fancer.lancer@gmail.com>. Direct schema dependencies include `/schemas/eeprom/at24.yaml#`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/idt,89hpesx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/idt,89hpesx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/idt,89hpesx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml` defines the miscellaneous platform device binding titled `Intel IXP4xx AHB Queue Manager`. The IXP4xx AHB Queue Manager maintains queues as circular buffers in an 8KB embedded SRAM along with hardware pointers. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `intel,ixp4xx-ahb-queue-manager`. Top-level properties are `compatible`, `reg`, `interrupts`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/intel,ixp4xx-ahb-queue-manager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml` defines the miscellaneous platform device binding titled `Liebherr's BK4 external SPI controller`. Liebherr's BK4 external SPI controller is a device which handles data acquisition from compatible industrial peripherals. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `lwn,bk4-spi`. Top-level properties are `compatible`, `reg`, `spi-max-frequency`, `fsl,spi-cs-sck-delay`, `fsl,spi-sck-cs-delay`. Required top-level properties are `compatible`, `spi-max-frequency`. Pattern properties are none. Nested required-property signals include `compatible`, `spi-max-frequency`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Lukasz Majewski <lukma@denx.de>. Direct schema dependencies include `/schemas/spi/spi-peripheral-props.yaml#`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/lwn,bk4-spi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml` defines the miscellaneous platform device binding titled `NVIDIA Tegra186 (and later) MISC register block`. The MISC register block found on Tegra186 and later SoCs contains registers that can be used to identify a given chip and various strapping options. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 4 tokens: `nvidia,tegra186-misc`, `nvidia,tegra194-misc`, `nvidia,tegra234-misc`, `nvidia,tegra264-misc`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra186-misc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml` defines the miscellaneous platform device binding titled `NVIDIA Tegra APBMISC block`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 5 tokens: `nvidia,tegra210-apbmisc`, `nvidia,tegra124-apbmisc`, `nvidia,tegra114-apbmisc`, `nvidia,tegra30-apbmisc`, `nvidia,tegra20-apbmisc`. Top-level properties are `compatible`, `reg`, `nvidia,long-ram-code`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/nvidia,tegra20-apbmisc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml` defines the miscellaneous platform device binding titled `OLPC XO-1.75 Embedded Controller`. This binding describes the Embedded Controller acting as a SPI bus master on a OLPC XO-1.75 laptop computer. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `olpc,xo1.75-ec`. Top-level properties are `compatible`, `cmd-gpios`, `spi-cpha`. Required top-level properties are `compatible`, `cmd-gpios`. Pattern properties are none. Nested required-property signals include `compatible`, `cmd-gpios`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Lubomir Rintel <lkundrak@v3.sk>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/olpc,xo1.75-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/pci1de4,1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/pci1de4,1.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/pci1de4,1.yaml` defines the miscellaneous platform device binding titled `RaspberryPi RP1 MFD PCI device`. The RaspberryPi RP1 is a PCI multi function device containing peripherals ranging from Ethernet to USB controller, I2C, SPI and others. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 1 token: `pci1de4,1`. Top-level properties are `compatible`, `reg`, `#interrupt-cells`, `interrupt-controller`. Required top-level properties are `compatible`, `reg`, `#interrupt-cells`, `interrupt-controller`, `pci-ep-bus@1`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `#interrupt-cells`, `interrupt-controller`, `pci-ep-bus@1`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: A. della Porta <andrea.porta@suse.com>. Direct schema dependencies include `/schemas/pci/pci-ep-bus.yaml`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/pci1de4,1.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/pci1de4,1.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/pci1de4,1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` defines the miscellaneous platform device binding titled `Qualcomm FastRPC Driver`. The FastRPC implements an IPC (Inter-Processor Communication) mechanism that allows for clients to transparently make remote method invocations across DSP and APPS boundaries. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `qcom,kaanapali-fastrpc`, `qcom,fastrpc`, `qcom,glymur-fastrpc`. Top-level properties are `compatible`, `label`, `memory-region`, `qcom,glink-channels`, `qcom,non-secure-domain`, `qcom,smd-channels`, `qcom,vmids`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `label`, `#address-cells`, `#size-cells`. Pattern properties are `(compute-)?cb@[0-9]*$`. Nested required-property signals include `compatible`, `reg`, `label`, `#address-cells`, `#size-cells`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Srinivas Kandagatla <srinivas.kandagatla@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qcom,fastrpc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml` defines the miscellaneous platform device binding titled `VCPU stall detector`. This binding describes a CPU stall detector mechanism for virtual CPUs which is accessed through MMIO. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 1 token: `qemu,vcpu-stall-detector`. Top-level properties are `compatible`, `reg`, `clock-frequency`, `interrupts`, `timeout-sec`. Required top-level properties are `compatible`. Pattern properties are none. Nested required-property signals include `compatible`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Sebastian Ene <sebastianene@google.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/qemu,vcpu-stall-detector.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml` defines the miscellaneous platform device binding titled `TI FPC202 dual port controller with expanded IOs`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `ti,fpc202`. Top-level properties are `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `enable-gpios`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `#address-cells`, `#size-cells`. Pattern properties are `^i2c@[0-1]$`, `^led@1[4-b]$`. Nested required-property signals include `#address-cells`, `#size-cells`, `reg`, `compatible`, `gpio-controller`, `#gpio-cells`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Romain Gantois <romain.gantois@bootlin.com>. Direct schema dependencies include `/schemas/i2c/i2c-atr.yaml#`, `/schemas/i2c/i2c-controller.yaml#`, `/schemas/leds/common.yaml#`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,fpc202.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,fpc202.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,fpc202.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml` defines the miscellaneous platform device binding titled `Texas Instruments K3 ESM`. The ESM (Error Signaling Module) is an IP block on TI K3 devices that allows handling of safety events somewhat similar to what interrupt controller would do. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `ti,j721e-esm`. Top-level properties are `compatible`, `reg`, `ti,esm-pins`. Required top-level properties are `compatible`, `reg`, `ti,esm-pins`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `ti,esm-pins`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Neha Malcom Francis <n-francis@ti.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/ti,j721e-esm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml` defines the miscellaneous platform device binding titled `Xilinx SDFEC(16nm) IP`. The Soft Decision Forward Error Correction (SDFEC) Engine is a Hard IP block which provides high-throughput LDPC and Turbo Code implementations. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `xlnx,sd-fec-1.1`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `xlnx,sdfec-code`, `xlnx,sdfec-din-width`, `xlnx,sdfec-din-words`, `xlnx,sdfec-dout-width`, `xlnx,sdfec-dout-words`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `xlnx,sdfec-code`, `xlnx,sdfec-din-width`, `xlnx,sdfec-din-words`, `xlnx,sdfec-dout-width`, `xlnx,sdfec-dout-words`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `clocks`, `clock-names`, `xlnx,sdfec-code`, `xlnx,sdfec-din-width`, `xlnx,sdfec-din-words`, `xlnx,sdfec-dout-width`, `xlnx,sdfec-dout-words`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Cvetic, Dragan <dragan.cvetic@amd.com>, Erim, Salih <salih.erim@amd.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,sd-fec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml` defines the miscellaneous platform device binding titled `Xilinx Triple Modular Redundancy(TMR) Inject IP`. The Triple Modular Redundancy(TMR) Inject core provides functional fault injection by changing selected MicroBlaze instructions, which provides the possibility to verify that the TMR subsystem error detection and fault recovery logic is working properly. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 1 token: `xlnx,tmr-inject-1.0`. Top-level properties are `compatible`, `reg`, `xlnx,magic`. Required top-level properties are `compatible`, `reg`, `xlnx,magic`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `xlnx,magic`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Appana Durga Kedareswara rao <appana.durga.kedareswara.rao@amd.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-inject.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml` defines the miscellaneous platform device binding titled `Xilinx Triple Modular Redundancy(TMR) Manager IP`. The Triple Modular Redundancy(TMR) Manager is responsible for handling the TMR subsystem state, including fault detection and error recovery. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 1 token: `xlnx,tmr-manager-1.0`. Top-level properties are `compatible`, `reg`, `xlnx,magic1`. Required top-level properties are `compatible`, `reg`, `xlnx,magic1`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `xlnx,magic1`. The highest-risk API details are driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including device probe state, mailbox/session state, service-processor communication, error-reporting status, or accelerator control state owned by the matched driver.

## Dependencies and Integration Points
Maintainers listed: Appana Durga Kedareswara rao <appana.durga.kedareswara.rao@amd.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include misc, firmware, remoteproc/RPMsg, PCI/queue-manager, service-processor, management-controller, accelerator, error-signalling, and platform helper drivers. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to driver-specific resource order, mailbox/interrupt semantics, child-node contracts, DMA/IOMMU attachment, firmware channel naming, and ABI-stable vendor properties, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/misc/xlnx,tmr-manager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Allwinner A10 MMC Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 16 branches with 23 tokens: `allwinner,sun4i-a10-mmc`, `allwinner,sun5i-a13-mmc`, `allwinner,sun7i-a20-mmc`, `allwinner,sun8i-a83t-emmc`, `allwinner,sun9i-a80-mmc`, `allwinner,sun20i-d1-mmc`, `allwinner,sun50i-a64-emmc`, `allwinner,sun50i-a64-mmc`, `allwinner,sun50i-a100-emmc`, `allwinner,sun50i-a100-mmc`, `allwinner,sun8i-a83t-mmc`, `allwinner,suniv-f1c100s-mmc`, `allwinner,sun8i-r40-emmc`, `allwinner,sun50i-h5-emmc`, `allwinner,sun50i-h6-emmc`, `allwinner,sun8i-r40-mmc`, and 7 more. Top-level properties are `#address-cells`, `#size-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/allwinner,sun4i-a10-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Amlogic SD / eMMC controller for S905/GXBB family SoCs`. The MMC 5.1 compliant host controller on Amlogic provides the interface for SD, eMMC and SDIO devices It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 4 tokens: `amlogic,t7-mmc`, `amlogic,meson-axg-mmc`, `amlogic,meson-gx-mmc`, `amlogic,meson-gxbb-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `amlogic,dram-access-quirk`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-gx-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Amlogic Meson SDHC controller`. The SDHC MMC host controller on Amlogic SoCs provides an eMMC and MMC card interface with 1/4/8-bit bus width. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 4 tokens: `amlogic,meson8-sdhc`, `amlogic,meson8b-sdhc`, `amlogic,meson8m2-sdhc`, `amlogic,meson-mx-sdhc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Martin Blumenstingl <martin.blumenstingl@googlemail.com>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdhc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Amlogic Meson6, Meson8 and Meson8b SDIO/MMC controller`. The highspeed MMC host controller on Amlogic SoCs provides an interface for MMC, SD, SDIO and SDHC types of memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 3 tokens: `amlogic,meson8-sdio`, `amlogic,meson8b-sdio`, `amlogic,meson-mx-sdio`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Pattern properties are `slot@[0-2]$`. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>. Direct schema dependencies include `mmc-slot.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/amlogic,meson-mx-sdio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Arasan SDHCI Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 14 branches with 15 tokens: `arasan,sdhci-8.9a`, `arasan,sdhci-4.9a`, `arasan,sdhci-5.1`, `renesas,r9a06g032-sdhci`, `renesas,rzn1-sdhci`, `rockchip,rk3399-sdhci-5.1`, `xlnx,zynqmp-8.9a`, `xlnx,versal-8.9a`, `xlnx,versal-net-emmc`, `intel,lgm-sdhci-5.1-emmc`, `intel,lgm-sdhci-5.1-sdxc`, `intel,keembay-sdhci-5.1-emmc`, `intel,keembay-sdhci-5.1-sd`, `intel,keembay-sdhci-5.1-sdio`, `axiado,ax3000-sdhci-5.1-emmc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `dma-coherent`, `interrupts`, `interrupt-names`, `phys`, `phy-names`, `resets`, `arasan,soc-ctl-syscon`, `clock-output-names`, `#clock-cells`, `xlnx,fails-without-test-cd`, `xlnx,int-clock-stable-broken`, `xlnx,mio-bank`, `iommus`, `power-domains`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `phys`, `phy-names`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, `dependencies`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Adrian Hunter <adrian.hunter@intel.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml` against representative board DTBs. The schema has 9 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arasan,sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arm,pl18x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arm,pl18x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arm,pl18x.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `ARM PrimeCell MultiMedia Card Interface (MMCI) PL180 and PL181`. The ARM PrimeCell MMCI PL180 and PL181 provides an interface for reading and writing to MultiMedia and SD cards alike. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 4 branches with 6 tokens: `arm,pl180`, `arm,primecell`, `arm,pl181`, `arm,pl18x`, `st,stm32-sdmmc2`, `st,stm32mp25-sdmmc2`. Top-level properties are `compatible`, `clocks`, `dmas`, `dma-names`, `access-controllers`, `power-domains`, `resets`, `reg`, `interrupts`, `st,sig-dir-dat0`, `st,sig-dir-dat2`, `st,sig-dir-dat31`, `st,sig-dir-dat74`, `st,sig-dir-cmd`, `st,sig-pin-fbclk`, `st,sig-dir`, `st,neg-edge`, `st,use-ckin`, `st,cmd-gpios`, `st,ck-gpios`, `st,ckin-gpios`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, `dependencies`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>, Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/arm/primecell.yaml#`, `/schemas/types.yaml#/definitions/flag`, `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/arm,pl18x.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/arm,pl18x.yaml` against representative board DTBs. The schema has 4 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/arm,pl18x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `ASPEED SD/SDIO/MMC Controller`. The ASPEED SD/SDIO/eMMC controller exposes two slots implementing the SDIO Host Specification v2.00, with 1 or 4 bit data buses, or an 8 bit data bus if only a single slot is enabled. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 4 tokens: `aspeed,ast2400-sd-controller`, `aspeed,ast2500-sd-controller`, `aspeed,ast2600-sd-controller`, `aspeed,ast2700-sd-controller`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `resets`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `clocks`. Pattern properties are `^sdhci@[0-9a-f]+$`. Nested required-property signals include `compatible`, `reg`, `clocks`, `interrupts`, `#address-cells`, `#size-cells`, `ranges`, `resets`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `if`, `then`, `else`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Andrew Jeffery <andrew@aj.id.au>, Ryan Chen <ryanchen.aspeed@gmail.com>. Direct schema dependencies include `sdhci-common.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/aspeed,sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Atmel High-Speed MultiMedia Card Interface (HSMCI)`. The Atmel HSMCI controller provides an interface for MMC, SD, and SDIO memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `atmel,hsmci`. Top-level properties are `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Pattern properties are `slot@[0-2]$`. Nested required-property signals include `reg`, `bus-width`, `compatible`, `interrupts`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`, `slot@0`, `slot@1`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, `anyOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>, Aubin Constans <aubin.constans@microchip.com>. Direct schema dependencies include `mmc-controller.yaml`, `mmc-slot.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,hsmci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Atmel SDHCI controller`. Bindings for the SDHCI controller found in Atmel/Microchip SoCs. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 5 tokens: `atmel,sama5d2-sdhci`, `microchip,sam9x60-sdhci`, `microchip,sam9x7-sdhci`, `microchip,sama7d65-sdhci`, `microchip,sama7g5-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `microchip,sdcal-inverted`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Aubin Constans <aubin.constans@microchip.com>, Nicolas Ferre <nicolas.ferre@microchip.com>. Direct schema dependencies include `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/atmel,sama5d2-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Broadcom BCM2835 SDHOST controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `brcm,bcm2835-sdhost`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Stefan Wahren <stefan.wahren@i2se.com>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,bcm2835-sdhost.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Broadcom IPROC SDHCI controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 5 tokens: `brcm,bcm2835-sdhci`, `brcm,bcm2711-emmc2`, `brcm,sdhci-iproc-cygnus`, `brcm,sdhci-iproc`, `brcm,bcm7211a0-sdhci`. Top-level properties are `compatible`, `reg`, `dma-coherent`, `interrupts`, `iommus`, `clocks`, `sdhci,auto-cmd12`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ray Jui <ray.jui@broadcom.com>, Scott Branden <scott.branden@broadcom.com>, Nicolas Saenz Julienne <nsaenz@kernel.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,iproc-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Broadcom Kona family SDHCI controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `brcm,kona-sdhci`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`. Required top-level properties are `compatible`, `reg`, `clocks`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `clocks`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Florian Fainelli <f.fainelli@gmail.com>. Direct schema dependencies include `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,kona-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Broadcom BRCMSTB/BMIPS SDHCI Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 8 tokens: `brcm,bcm7216-sdhci`, `brcm,bcm7445-sdhci`, `brcm,sdhci-brcmstb`, `brcm,bcm2712-sdhci`, `brcm,bcm72116-sdhci`, `brcm,bcm74165b0-sdhci`, `brcm,bcm7425-sdhci`, `brcm,bcm74371-sdhci`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `clock-frequency`, `sdhci,auto-cmd12`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `clock-frequency`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Al Cooper <alcooperx@gmail.com>, Florian Fainelli <f.fainelli@gmail.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/brcm,sdhci-brcmstb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Black Sesame Technologies DWCMSHC SDHCI Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `bst,c1200-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `memory-region`, `dma-coherent`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ge Gordon <gordon.ge@bst.ai>. Direct schema dependencies include `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/bst,c1200-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Cadence SD/SDIO/eMMC Host Controller (SD4HC)`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 6 tokens: `amd,pensando-elba-sd4hc`, `microchip,mpfs-sd4hc`, `microchip,pic64gx-sd4hc`, `mobileye,eyeq-sd4hc`, `socionext,uniphier-sd4hc`, `cdns,sd4hc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `cdns,phy-input-delay-sd-highspeed`, `cdns,phy-input-delay-legacy`, `cdns,phy-input-delay-sd-uhs-sdr12`, `cdns,phy-input-delay-sd-uhs-sdr25`, `cdns,phy-input-delay-sd-uhs-sdr50`, `cdns,phy-input-delay-sd-uhs-ddr50`, `cdns,phy-input-delay-mmc-highspeed`, `cdns,phy-input-delay-mmc-ddr`, `cdns,phy-dll-delay-sdclk`, `cdns,phy-dll-delay-sdclk-hsmmc`, `cdns,phy-dll-delay-strobe`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Masahiro Yamada <yamada.masahiro@socionext.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `sdhci-common.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/cdns,sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Freescale Enhanced Secure Digital Host Controller (eSDHC)`. The Enhanced Secure Digital Host Controller provides an interface for MMC, SD, and SDIO types of memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 14 tokens: `fsl,mpc8536-esdhc`, `fsl,mpc8378-esdhc`, `fsl,p2020-esdhc`, `fsl,p4080-esdhc`, `fsl,t1040-esdhc`, `fsl,t4240-esdhc`, `fsl,ls1012a-esdhc`, `fsl,ls1021a-esdhc`, `fsl,ls1028a-esdhc`, `fsl,ls1088a-esdhc`, `fsl,ls1043a-esdhc`, `fsl,ls1046a-esdhc`, `fsl,ls2080a-esdhc`, `fsl,esdhc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-frequency`, `sdhci,wp-inverted`, `sdhci,1-bit-only`, `sdhci,auto-cmd12`, `voltage-ranges`, `dma-coherent`, `little-endian`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Frank Li <Frank.Li@nxp.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`, `mmc-controller-common.yaml#`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl,esdhc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Freescale Enhanced Secure Digital Host Controller (eSDHC) for i.MX`. The Enhanced Secure Digital Host Controller on Freescale i.MX family provides an interface for MMC, SD, and SDIO types of memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 12 branches with 29 tokens: `fsl,imx25-esdhc`, `fsl,imx35-esdhc`, `fsl,imx51-esdhc`, `fsl,imx53-esdhc`, `fsl,imx6q-usdhc`, `fsl,imx6sl-usdhc`, `fsl,imx6sx-usdhc`, `fsl,imx7d-usdhc`, `fsl,imx7ulp-usdhc`, `fsl,imx8mm-usdhc`, `fsl,imxrt1050-usdhc`, `nxp,s32g2-usdhc`, `nxp,s32n79-usdhc`, `fsl,imx50-esdhc`, `fsl,imx6sll-usdhc`, `fsl,imx6ull-usdhc`, and 13 more. Top-level properties are `compatible`, `reg`, `interrupts`, `fsl,wp-controller`, `fsl,delay-line`, `voltage-ranges`, `fsl,tuning-start-tap`, `fsl,tuning-step`, `fsl,strobe-dll-delay-target`, `clocks`, `clock-names`, `iommus`, `power-domains`, `pinctrl-names`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-esdhc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Freescale Secure Digital Host Controller for i.MX2/3 series`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 3 tokens: `fsl,imx21-mmc`, `fsl,imx31-mmc`, `fsl,imx27-mmc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `dmas`, `dma-names`. Required top-level properties are `clocks`, `clock-names`, `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `clocks`, `clock-names`, `compatible`, `reg`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Markus Pargmann <mpa@pengutronix.de>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fsl-imx-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Fujitsu/Socionext SDHCI controller (F_SDH30)`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `socionext,synquacer-sdhci`, `fujitsu,mb86s70-sdhci-3.0`, `socionext,f-sdh30-e51-mmc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `dma-coherent`, `interrupts`, `resets`, `fujitsu,cmd-dat-delay-select`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/fujitsu,sdhci-fujitsu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Hisilicon specific extensions to the Synopsys Designware Mobile Storage Host Controller`. The Synopsys designware mobile storage host controller is used to interface a SoC with storage medium such as eMMC or SD/MMC cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 4 tokens: `hisilicon,hi3660-dw-mshc`, `hisilicon,hi4511-dw-mshc`, `hisilicon,hi6220-dw-mshc`, `hisilicon,hi3670-dw-mshc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `hisilicon,peripheral-syscon`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Zhangfei Gao <zhangfei.gao@linaro.org>. Direct schema dependencies include `/schemas/mmc/synopsys-dw-mshc-common.yaml#`, `/schemas/types.yaml#/definitions/phandle`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3660-dw-mshc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Hisilicon HiSTB SoCs specific extensions to the Synopsys DWMMC controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 2 tokens: `hisilicon,hi3798cv200-dw-mshc`, `hisilicon,hi3798mv200-dw-mshc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `hisilicon,sap-dll-reg`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `hisilicon,sap-dll-reg`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Yang Xiwen <forbidden405@outlook.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/phandle-array`, `synopsys-dw-mshc-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/hisilicon,hi3798cv200-dw-mshc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Ingenic SoCs MMC Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 7 tokens: `ingenic,jz4740-mmc`, `ingenic,jz4725b-mmc`, `ingenic,jz4760-mmc`, `ingenic,jz4775-mmc`, `ingenic,jz4780-mmc`, `ingenic,x1000-mmc`, `ingenic,jz4770-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Paul Cercueil <paul@crapouillou.net>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/ingenic,mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/litex,mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/litex,mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/litex,mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `LiteX LiteSDCard device`. LiteSDCard is a small footprint, configurable SDCard core for FPGA based system on chips. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `litex,mmc`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `vmmc-supply`, `interrupts`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `vmmc-supply`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `reg-names`, `clocks`, `vmmc-supply`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Gabriel Somlo <gsomlo@gmail.com>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/litex,mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/litex,mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/litex,mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `The SD/SDIO/eMMC host controller for Loongson-2K family SoCs`. The MMC host controller on the Loongson-2K0500/2K1000 (using an externally shared apbdma controller) provides the SD and SDIO device interfaces. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 4 tokens: `loongson,ls2k0300-mmc`, `loongson,ls2k0500-mmc`, `loongson,ls2k1000-mmc`, `loongson,ls2k2000-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, `if`, `then`, `else`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Binbin Zhou <zhoubinbin@loongson.cn>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/loongson,ls2k0500-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Marvell sdhci-dove controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `marvell,dove-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Required top-level properties are `compatible`, `reg`, `interrupts`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Adrian Hunter <adrian.hunter@intel.com>, Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,dove-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Marvell orion-sdio controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `marvell,orion-sdio`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Nicolas Pitre <nico@fluxnic.net>, Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,orion-sdio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Marvell Xenon SDHCI Controller`. This file documents differences between the core MMC properties described by mmc-controller.yaml and the properties used by the Xenon implementation. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 6 tokens: `marvell,armada-cp110-sdhci`, `marvell,armada-ap806-sdhci`, `marvell,armada-ap807-sdhci`, `marvell,ac5-sdhci`, `marvell,armada-3700-sdhci`, `marvell,sdhci-xenon`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `dma-coherent`, `interrupts`, `iommus`, `marvell,pad-type`, `marvell,xenon-sdhc-id`, `marvell,xenon-phy-type`, `marvell,xenon-phy-znr`, `marvell,xenon-phy-zpr`, `marvell,xenon-phy-nr-success-tun`, `marvell,xenon-phy-tun-step-divider`, `marvell,xenon-phy-slow-mode`, `marvell,xenon-tun-count`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `marvell,pad-type`, `compatible`, `reg`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml` against representative board DTBs. The schema has 4 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/marvell,xenon-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Microchip Sparx5 Mobile Storage Host Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `microchip,dw-sparx5-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `microchip,clock-delay`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Lars Povlsen <lars.povlsen@microchip.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,dw-sparx5-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Microchip PIC32 SDHI Controller`. The Microchip PIC32 family of microcontrollers (MCUs) includes models with Secure Digital Host Controller Interface (SDHCI) controllers, allowing them to interface with Secure Digital (SD) cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `microchip,pic32mzda-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `pinctrl-names`, `pinctrl-0`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `pinctrl-names`, `pinctrl-0`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/microchip,sdhci-pic32.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-card.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-card.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MMC Card / eMMC Generic`. This documents describes the devicetree bindings for a mmc-host controller child node describing a mmc-card / an eMMC. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `mmc-card`. Top-level properties are `compatible`, `reg`, `broken-hpi`. Required top-level properties are `compatible`, `reg`. Pattern properties are `^partitions(-boot[12]|-gp[14])?$`. Nested required-property signals include `compatible`, `reg`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern-property regexes can over-match or under-match child nodes; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-card.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-card.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MMC Controller & Slots Common Properties`. These properties are common to multiple MMC host controllers and the possible slots or ports for multi-slot controllers. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. This is a reusable common schema fragment rather than a directly probed device binding; other MMC or SDHCI bindings include it with `$ref` to share controller, slot, or host-controller properties. Top-level properties are `#address-cells`, `#size-cells`, `broken-cd`, `cd-gpios`, `non-removable`, `wp-inverted`, `cd-inverted`, `bus-width`, `max-frequency`, `max-sd-hs-hz`, `disable-wp`, `wp-gpios`, `cd-debounce-delay-ms`, `no-1-8-v`, `cap-sd-highspeed`, `cap-mmc-highspeed`, `sd-uhs-sdr12`, `sd-uhs-sdr25`, `sd-uhs-sdr50`, `sd-uhs-sdr104`, `sd-uhs-ddr50`, `cap-power-off-card`, `cap-mmc-hw-reset`, `cap-sdio-irq`, `full-pwr-cycle`, `full-pwr-cycle-in-suspend`, `mmc-ddr-1_2v`, `mmc-ddr-1_8v`, and 20 more. Required top-level properties are none declared. Pattern properties are `^.*@[0-9]+$`, `^clk-phase-(legacy|sd-hs|mmc-(hs|hs[24]00|ddr52)|uhs-(sdr(12|25|50|104)|ddr50))$`. Nested required-property signals include `reg`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `dependencies`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MMC Controller Common Properties`. These properties are common to multiple MMC host controllers. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a composed compatible schema with 0 tokens: no explicit compatible constants. Top-level properties are `$nodename`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `mmc-controller-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: examples can drift from the schema and must stay validated; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-controller.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-controller.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Simple eMMC hardware reset provider`. The purpose of this driver is to perform standard eMMC hw reset procedure, as described by Jedec 4.4 specification. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `mmc-pwrseq-emmc`. Top-level properties are `compatible`, `reset-gpios`. Required top-level properties are `compatible`, `reset-gpios`. Pattern properties are none. Nested required-property signals include `compatible`, `reset-gpios`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-emmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Marvell SD8787 power sequence provider`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 2 tokens: `mmc-pwrseq-sd8787`, `mmc-pwrseq-wilc1000`. Top-level properties are `compatible`, `powerdown-gpios`, `reset-gpios`. Required top-level properties are `compatible`, `powerdown-gpios`, `reset-gpios`. Pattern properties are none. Nested required-property signals include `compatible`, `powerdown-gpios`, `reset-gpios`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-sd8787.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Simple MMC power sequence provider`. The purpose of the simple MMC power sequence provider is to supports a set of common properties between various SOC designs. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `mmc-pwrseq-simple`. Top-level properties are `compatible`, `reset-gpios`, `clocks`, `clock-names`, `post-power-on-delay-ms`, `power-off-delay-us`. Required top-level properties are `compatible`. Pattern properties are none. Nested required-property signals include `compatible`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-pwrseq-simple.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-slot.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-slot.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-slot.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MMC slot properties`. These properties defines slot properties for MMC controlers that have multiple slots or ports provided by the same controller and sharing the same resources. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. This is a reusable common schema fragment rather than a directly probed device binding; other MMC or SDHCI bindings include it with `$ref` to share controller, slot, or host-controller properties. Top-level properties are `$nodename`, `compatible`, `reg`. Required top-level properties are `reg`. Pattern properties are none. Nested required-property signals include `reg`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `mmc-controller-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-slot.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-slot.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-slot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MMC/SD/SDIO slot directly connected to a SPI bus`. The extra properties used by an mmc connected via SPI. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses a single `const` with 1 token: `mmc-spi-slot`. Top-level properties are `compatible`, `reg`, `interrupts`, `voltage-ranges`, `gpios`. Required top-level properties are `compatible`, `reg`, `spi-max-frequency`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `spi-max-frequency`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/spi/spi-peripheral-props.yaml`, `/schemas/types.yaml#/definitions/uint32-matrix`, `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mmc-spi-slot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mtk-sd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mtk-sd.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mtk-sd.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `MTK MSDC Storage Host Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 21 tokens: `mediatek,mt2701-mmc`, `mediatek,mt2712-mmc`, `mediatek,mt6779-mmc`, `mediatek,mt6795-mmc`, `mediatek,mt7620-mmc`, `mediatek,mt7622-mmc`, `mediatek,mt7986-mmc`, `mediatek,mt7988-mmc`, `mediatek,mt8135-mmc`, `mediatek,mt8173-mmc`, `mediatek,mt8183-mmc`, `mediatek,mt8189-mmc`, `mediatek,mt8196-mmc`, `mediatek,mt8516-mmc`, `mediatek,mt7623-mmc`, `mediatek,mt6893-mmc`, and 5 more. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `pinctrl-2`, `hs400-ds-delay`, `mediatek,hs200-cmd-int-delay`, `mediatek,hs400-cmd-int-delay`, `mediatek,hs400-cmd-resp-sel-rising`, `mediatek,hs400-ds-dly3`, `mediatek,latch-ck`, `mediatek,tuning-step`, `resets`, `reset-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `vmmc-supply`, `vqmmc-supply`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `vmmc-supply`, `vqmmc-supply`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Chaotian Jing <chaotian.jing@mediatek.com>, Wenbin Mei <wenbin.mei@mediatek.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mtk-sd.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mtk-sd.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mtk-sd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mxs-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mxs-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mxs-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Freescale MXS MMC controller`. The Freescale MXS Synchronous Serial Ports (SSP) can act as a MMC controller to support MMC, SD, and SDIO types of memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 2 tokens: `fsl,imx23-mmc`, `fsl,imx28-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `dmas`, `dma-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>. Direct schema dependencies include `mmc-controller-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mxs-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/mxs-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/mxs-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `NPCM SDHCI Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 2 tokens: `nuvoton,npcm750-sdhci`, `nuvoton,npcm845-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Tomer Maimon <tmaimon77@gmail.com>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/npcm,sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Nuvoton MA35D1 SD/SDIO/MMC Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 1 token: `nuvoton,ma35d1-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `resets`, `nuvoton,sys`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `pinctrl-names`, `pinctrl-0`, `resets`, `nuvoton,sys`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `pinctrl-names`, `pinctrl-0`, `resets`, `nuvoton,sys`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Shan-Chun Hung <shanchun1218@gmail.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nuvoton,ma35d1-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `NVIDIA Tegra Secure Digital Host Controller`. This controller on Tegra family SoCs provides an interface for MMC, SD, and SDIO types of memory cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 9 tokens: `nvidia,tegra20-sdhci`, `nvidia,tegra30-sdhci`, `nvidia,tegra114-sdhci`, `nvidia,tegra124-sdhci`, `nvidia,tegra210-sdhci`, `nvidia,tegra186-sdhci`, `nvidia,tegra194-sdhci`, `nvidia,tegra132-sdhci`, `nvidia,tegra234-sdhci`. Top-level properties are `compatible`, `reg`, `interrupts`, `assigned-clocks`, `assigned-clock-parents`, `assigned-clock-rates`, `clocks`, `clock-names`, `resets`, `reset-names`, `power-gpios`, `interconnects`, `interconnect-names`, `iommus`, `operating-points-v2`, `power-domains`, `nvidia,default-tap`, `nvidia,default-trim`, `nvidia,dqs-trim`, `nvidia,pad-autocal-pull-down-offset-1v8`, `nvidia,pad-autocal-pull-down-offset-1v8-timeout`, `nvidia,pad-autocal-pull-down-offset-3v3`, `nvidia,pad-autocal-pull-down-offset-3v3-timeout`, `nvidia,pad-autocal-pull-down-offset-sdr104`, `nvidia,pad-autocal-pull-down-offset-hs400`, `nvidia,pad-autocal-pull-up-offset-1v8`, `nvidia,pad-autocal-pull-up-offset-1v8-timeout`, `nvidia,pad-autocal-pull-up-offset-3v3`, and 4 more. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `reset-names`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/nvidia,tegra20-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/owl-mmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/owl-mmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/owl-mmc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Actions Semi Owl SoCs SD/MMC/SDIO controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `actions,owl-mmc`, `actions,s500-mmc`, `actions,s700-mmc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `dmas`, `dma-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `resets`, `dmas`, `dma-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/owl-mmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/owl-mmc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/owl-mmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Renesas Multi Media Card Interface (MMCIF) Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an ordered fallback `items` sequence with 14 tokens: `renesas,mmcif-r7s72100`, `renesas,mmcif-r8a73a4`, `renesas,mmcif-r8a7740`, `renesas,mmcif-r8a7742`, `renesas,mmcif-r8a7743`, `renesas,mmcif-r8a7744`, `renesas,mmcif-r8a7745`, `renesas,mmcif-r8a7778`, `renesas,mmcif-r8a7790`, `renesas,mmcif-r8a7791`, `renesas,mmcif-r8a7793`, `renesas,mmcif-r8a7794`, `renesas,mmcif-sh73a0`, `renesas,sh-mmcif`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, `resets`, `dmas`, `dma-names`, `max-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`, `resets`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, `if`, `then`, `else`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Wolfram Sang <wsa+renesas@sang-engineering.com>. Direct schema dependencies include `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,mmcif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Renesas SDHI SD/MMC controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 7 branches with 49 tokens: `renesas,sdhi-mmc-r8a77470`, `renesas,sdhi-r7s72100`, `renesas,sdhi-r7s9210`, `renesas,sdhi-r8a73a4`, `renesas,sdhi-r8a7740`, `renesas,sdhi-r9a09g057`, `renesas,sdhi-sh73a0`, `renesas,sdhi-r8a7778`, `renesas,sdhi-r8a7779`, `renesas,rcar-gen1-sdhi`, `renesas,sdhi-r8a7742`, `renesas,sdhi-r8a7743`, `renesas,sdhi-r8a7744`, `renesas,sdhi-r8a7745`, `renesas,sdhi-r8a77470`, `renesas,sdhi-r8a7790`, and 33 more. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `iommus`, `mux-states`, `power-domains`, `resets`, `pinctrl-0`, `pinctrl-1`, `pinctrl-names`, `max-frequency`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`. Pattern properties are none. Nested required-property signals include `clock-names`, `resets`, `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Wolfram Sang <wsa+renesas@sang-engineering.com>. Direct schema dependencies include `/schemas/regulator/regulator.yaml#`, `mmc-controller.yaml`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/renesas,sdhi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Rockchip designware mobile storage host controller`. Rockchip uses the Synopsys designware mobile storage host controller to interface a SoC with storage medium such as eMMC or SD/MMC cards. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 5 branches with 20 tokens: `rockchip,rk2928-dw-mshc`, `rockchip,rk3288-dw-mshc`, `rockchip,px30-dw-mshc`, `rockchip,rk1808-dw-mshc`, `rockchip,rk3036-dw-mshc`, `rockchip,rk3128-dw-mshc`, `rockchip,rk3228-dw-mshc`, `rockchip,rk3308-dw-mshc`, `rockchip,rk3328-dw-mshc`, `rockchip,rk3368-dw-mshc`, `rockchip,rk3399-dw-mshc`, `rockchip,rk3506-dw-mshc`, `rockchip,rk3528-dw-mshc`, `rockchip,rk3562-dw-mshc`, `rockchip,rk3568-dw-mshc`, `rockchip,rk3588-dw-mshc`, and 4 more. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `rockchip,default-sample-phase`, `rockchip,desired-num-phases`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Heiko Stuebner <heiko@sntech.de>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `synopsys-dw-mshc-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/rockchip-dw-mshc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Samsung Exynos SoC specific extensions to the Synopsys Designware Mobile Storage Host Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 15 tokens: `axis,artpec8-dw-mshc`, `samsung,exynos4210-dw-mshc`, `samsung,exynos4412-dw-mshc`, `samsung,exynos5250-dw-mshc`, `samsung,exynos5420-dw-mshc`, `samsung,exynos5420-dw-mshc-smu`, `samsung,exynos7-dw-mshc`, `samsung,exynos7-dw-mshc-smu`, `samsung,exynos7870-dw-mshc`, `samsung,exynos7870-dw-mshc-smu`, `samsung,exynos5433-dw-mshc-smu`, `samsung,exynos7885-dw-mshc-smu`, `samsung,exynos850-dw-mshc-smu`, `samsung,exynos8890-dw-mshc-smu`, `samsung,exynos8895-dw-mshc-smu`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `samsung,dw-mshc-ciu-div`, `samsung,dw-mshc-ddr-timing`, `samsung,dw-mshc-hs400-timing`, `samsung,dw-mshc-sdr-timing`, `samsung,read-strobe-delay`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `samsung,dw-mshc-ddr-timing`, `samsung,dw-mshc-sdr-timing`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `samsung,dw-mshc-ddr-timing`, `samsung,dw-mshc-sdr-timing`, `samsung,dw-mshc-ciu-div`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Jaehoon Chung <jh80.chung@samsung.com>, Krzysztof Kozlowski <krzk@kernel.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `synopsys-dw-mshc-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,exynos-dw-mshc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Samsung SoC SDHCI Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 2 tokens: `samsung,s3c6410-sdhci`, `samsung,exynos4210-sdhci`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Jaehoon Chung <jh80.chung@samsung.com>, Krzysztof Kozlowski <krzk@kernel.org>. Direct schema dependencies include `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/samsung,s3c6410-sdhci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-am654.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-am654.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-am654.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `TI AM654 MMC Controller`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 8 tokens: `ti,am62-sdhci`, `ti,am64-sdhci-4bit`, `ti,am64-sdhci-8bit`, `ti,am654-sdhci-5.1`, `ti,j721e-sdhci-4bit`, `ti,j721e-sdhci-8bit`, `ti,j7200-sdhci-8bit`, `ti,j7200-sdhci-4bit`. Top-level properties are `compatible`, `reg`, `interrupts`, `power-domains`, `clocks`, `clock-names`, `dma-coherent`, `ti,otap-del-sel-legacy`, `ti,otap-del-sel-mmc-hs`, `ti,otap-del-sel-sd-hs`, `ti,otap-del-sel-sdr12`, `ti,otap-del-sel-sdr25`, `ti,otap-del-sel-sdr50`, `ti,otap-del-sel-sdr104`, `ti,otap-del-sel-ddr50`, `ti,otap-del-sel-ddr52`, `ti,otap-del-sel-hs200`, `ti,otap-del-sel-hs400`, `ti,itap-del-sel-legacy`, `ti,itap-del-sel-mmc-hs`, `ti,itap-del-sel-sd-hs`, `ti,itap-del-sel-sdr12`, `ti,itap-del-sel-sdr25`, `ti,itap-del-sel-ddr50`, `ti,itap-del-sel-ddr52`, `ti,trm-icp`, `ti,driver-strength-ohm`, `ti,strobe-sel`, and 2 more. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ti,otap-del-sel-legacy`. Pattern properties are none. Nested required-property signals include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ti,otap-del-sel-legacy`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-am654.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-am654.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-am654.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-common.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `SDHCI Controller Common Properties`. Common properties present on Secure Digital Host Controller Interface (SDHCI) devices. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. This is a reusable common schema fragment rather than a directly probed device binding; other MMC or SDHCI bindings include it with `$ref` to share controller, slot, or host-controller properties. Top-level properties are `sdhci-caps`, `sdhci-caps-mask`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Adrian Hunter <adrian.hunter@intel.com>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint64`, `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-common.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-msm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-msm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-msm.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Qualcomm SDHCI controller (sdhci-msm)`. Secure Digital Host Controller Interface (SDHCI) present on Qualcomm SOCs supports SD/MMC/SDIO devices. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 3 branches with 52 tokens: `qcom,sdhci-msm-v4`, `qcom,apq8084-sdhci`, `qcom,ipq4019-sdhci`, `qcom,ipq8074-sdhci`, `qcom,msm8226-sdhci`, `qcom,msm8953-sdhci`, `qcom,msm8974-sdhci`, `qcom,msm8976-sdhci`, `qcom,msm8916-sdhci`, `qcom,msm8992-sdhci`, `qcom,msm8994-sdhci`, `qcom,msm8996-sdhci`, `qcom,msm8998-sdhci`, `qcom,ipq5018-sdhci`, `qcom,ipq5210-sdhci`, `qcom,ipq5332-sdhci`, and 36 more. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `dma-coherent`, `interrupts`, `interrupt-names`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `resets`, `qcom,ddr-config`, `qcom,dll-config`, `iommus`, `interconnects`, `interconnect-names`, `power-domains`, `operating-points-v2`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Pattern properties are `^opp-table(-[a-z0-9]+)?$`. Nested required-property signals include `required-opps`, `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Bjorn Andersson <andersson@kernel.org>, Konrad Dybcio <konradybcio@kernel.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `sdhci-common.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; pattern-property regexes can over-match or under-match child nodes; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-msm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-msm.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-msm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml` defines the MMC, SD, SDHCI, or power-sequence binding titled `Marvell PXA SDHCI v1/v2/v3`. It constrains devicetree nodes through compatible strings, required resources, child-node contracts, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 4 tokens: `mrvl,pxav1-mmc`, `mrvl,pxav2-mmc`, `mrvl,pxav3-mmc`, `marvell,armada-380-sdhci`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `pinctrl-names`, `pinctrl-0`, `pinctrl-1`, `mrvl,clk-delay-cycles`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Pattern properties are none. Nested required-property signals include `reg-names`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. The highest-risk API details are compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including host-controller registration, card-detect state, power sequencing, regulator enablement, clock/tuning state, and runtime PM owned by MMC host drivers.

## Dependencies and Integration Points
Maintainers listed: Ulf Hansson <ulf.hansson@linaro.org>. Direct schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `mmc-controller.yaml#`. Integration points include the MMC core, SDHCI and DesignWare host drivers, GPIO card-detect/write-protect lines, regulators, clocks, resets, power sequencing, CQE/tuning, and board storage nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, `reg` and interrupt resource order, clock/reset names, bus-width and timing flags, voltage regulator phandles, power-sequence links, and common MMC/SDHCI schema references, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mmc/sdhci-pxa.yaml -->
