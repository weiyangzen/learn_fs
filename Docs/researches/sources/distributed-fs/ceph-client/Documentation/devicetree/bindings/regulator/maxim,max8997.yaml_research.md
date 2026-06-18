<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8997 Power Management IC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Maxim MAX8997 is a Power Management IC which includes voltage and current regulators, charger controller with fuel gauge, RTC, clock outputs, haptic motor driver, flash LED driver and Micro-USB Interface Controller. The binding here is not complete and describes only regulator and charger controller parts.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max8997.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max8997-pmic`
- Top-level required properties: `compatible`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `reg`, `regulators`, `regulator-name`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`
- Top-level declared properties (14): `compatible`, `charger-supply`, `interrupts`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck125-dvs-gpios`, `max8997,pmic-ignore-gpiodvs-side-effect`, `reg`, `regulators`
- Regulator/vendor integration properties: `charger-supply`, `max8997,pmic-buck1-dvs-voltage`, `max8997,pmic-buck2-dvs-voltage`, `max8997,pmic-buck5-dvs-voltage`, `max8997,pmic-buck1-uses-gpio-dvs`, `max8997,pmic-buck2-uses-gpio-dvs`, `max8997,pmic-buck5-uses-gpio-dvs`, `max8997,pmic-buck125-default-dvs-idx`, `max8997,pmic-buck125-dvs-gpios`, `max8997,pmic-ignore-gpiodvs-side-effect`
- Property detail signals:
  - `compatible` (const `maxim,max8997-pmic`)
  - `charger-supply` (Regulator node for charging current.)
  - `interrupts` (2 fixed item schema(s))
  - `max8997,pmic-buck1-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck1 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck2-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck2 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck5-dvs-voltage` (ref /schemas/types.yaml#/definitions/uint32-array; minItems 1; maxItems 8; A set of 8 voltage values in micro-volt (uV) units for buck5 when changing voltage using GPIO DVS. If none of max8997,pm...)
  - `max8997,pmic-buck1-uses-gpio-dvs` (type boolean; buck1 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck2-uses-gpio-dvs` (type boolean; buck2 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck5-uses-gpio-dvs` (type boolean; buck5 can be controlled by GPIO DVS.)
  - `max8997,pmic-buck125-default-dvs-idx` (ref /schemas/types.yaml#/definitions/uint32; minimum 0; maximum 7; default 0)
  - `max8997,pmic-buck125-dvs-gpios` (minItems 3; maxItems 3; GPIO specifiers for three host gpio's used for DVS.)
  - `max8997,pmic-ignore-gpiodvs-side-effect` (type boolean; When GPIO-DVS mode is used for multiple bucks, changing the voltage value of one of the bucks may affect that of another...)
  - `reg` (maxItems 1)
  - `regulators` (type object; List of child nodes that specify the regulators.)
- Child-node or pattern API:
  - `regulators` child object with properties CHARGER, CHARGER_CV, CHARGER_TOPOFF, ENVICHG, ESAFEOUT1, ESAFEOUT2

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 1 `if` block(s), 1 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/maxim,max8997.yaml`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`
- Header/example integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, max8997,pmic-buck1-dvs-voltage, max8997,pmic-buck2-dvs-voltage, max8997,pmic-buck5-dvs-voltage, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; #include <dt-bindings/interrupt-controller/irq.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8997.yaml -->
