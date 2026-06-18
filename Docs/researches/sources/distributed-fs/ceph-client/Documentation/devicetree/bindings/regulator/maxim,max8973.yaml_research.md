<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Maxim MAX8973/MAX77621 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/maxim,max8973.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `maxim,max8973`, `maxim,max77621`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (15): `compatible`, `junction-warn-millicelsius`, `maxim,dvs-gpio`, `maxim,dvs-default-state`, `maxim,externally-enable`, `maxim,enable-gpio`, `maxim,enable-remote-sense`, `maxim,enable-falling-slew-rate`, `maxim,enable-active-discharge`, `maxim,enable-frequency-shift`, `maxim,enable-bias-control`, `maxim,enable-etr`, `maxim,enable-high-etr-sensitivity`, `reg`, `interrupts`
- Regulator/vendor integration properties: `maxim,dvs-gpio`, `maxim,dvs-default-state`, `maxim,externally-enable`, `maxim,enable-gpio`, `maxim,enable-remote-sense`, `maxim,enable-falling-slew-rate`, `maxim,enable-active-discharge`, `maxim,enable-frequency-shift`, `maxim,enable-bias-control`, `maxim,enable-etr`, `maxim,enable-high-etr-sensitivity`
- Property detail signals:
  - `compatible` (enum `maxim,max8973`, `maxim,max77621`)
  - `junction-warn-millicelsius` (Junction warning temperature threshold in millicelsius. If die temperature crosses this level then device generates the ...)
  - `maxim,dvs-gpio` (maxItems 1; GPIO which is connected to DVS pin of device.)
  - `maxim,dvs-default-state` (ref /schemas/types.yaml#/definitions/uint32; enum `0`, `1`; Default state of GPIO during initialisation. 1 for HIGH and 0 for LOW.)
  - `maxim,externally-enable` (type boolean; Externally control the regulator output enable/disable.)
  - `maxim,enable-gpio` (maxItems 1; GPIO for enable control. If the valid GPIO is provided then externally enable control will be considered.)
  - `maxim,enable-remote-sense` (type boolean; Enable remote sense.)
  - `maxim,enable-falling-slew-rate` (type boolean; Enable falling slew rate.)
  - `maxim,enable-active-discharge` (type boolean; Eable active discharge.)
  - `maxim,enable-frequency-shift` (type boolean; Enable 9% frequency shift.)
  - `maxim,enable-bias-control` (type boolean; Enable bias control which can reduce the startup delay to 20us from 220us.)
  - `maxim,enable-etr` (type boolean; Enable Enhanced Transient Response.)
  - `maxim,enable-high-etr-sensitivity` (type boolean; Enhanced transient response circuit is enabled and set for high sensitivity. If this property is available then etr will...)
  - `reg` (maxItems 1)
  - `interrupts` (maxItems 1)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/maxim,max8973.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@1b {; compatible = "maxim,max8973";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/maxim,max8973.yaml -->
