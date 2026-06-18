<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Richtek RT4803 Boost Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: RT4803 is a boost regulator that's designed to provide the minimum output voltage, even if the input voltage is lower than the required voltage. It supports boost and auto bypass mode that depends on the difference between the input and output voltage. If the input is lower than the output, mode will transform to boost mode. Otherwise, turn on bypass switch to enter bypass mode. Datasheet is available at https://www.richtek.com/assets/product_file/RT4803/DS4803-03.pdf https://www.richtek.com/assets/product_file/RT4803A/DS4803A-06.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/richtek,rt4803.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: ChiYuan Huang <cy_huang@richtek.com>.
- Compatible contract: `richtek,rt4803`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (4): `compatible`, `reg`, `richtek,vsel-active-high`, `regulator-allowed-modes`
- Regulator/vendor integration properties: `richtek,vsel-active-high`, `regulator-allowed-modes`
- Property detail signals:
  - `compatible` (enum `richtek,rt4803`)
  - `reg` (maxItems 1)
  - `richtek,vsel-active-high` (type boolean; Specify the VSEL register group is using when system is active)
  - `regulator-allowed-modes` (items enum 2 values; Available operating mode 1: Auto PFM/PWM 2: Force PWM)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/richtek,rt4803.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@75 {; compatible = "richtek,rt4803";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/richtek,rt4803.yaml -->
