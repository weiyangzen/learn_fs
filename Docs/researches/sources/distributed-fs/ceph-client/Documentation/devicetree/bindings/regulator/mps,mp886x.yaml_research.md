<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power Systems MP8867/MP8869 voltage regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mp886x.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Jisheng Zhang <jszhang@kernel.org>.
- Compatible contract: `mps,mp8867`, `mps,mp8869`
- Top-level required properties: `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`
- Required keys across top-level and child schemas: `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`
- Top-level declared properties (5): `compatible`, `reg`, `enable-gpios`, `mps,fb-voltage-divider`, `mps,switch-frequency-hz`
- Regulator/vendor integration properties: `enable-gpios`, `mps,fb-voltage-divider`, `mps,switch-frequency-hz`
- Property detail signals:
  - `compatible` (enum `mps,mp8867`, `mps,mp8869`)
  - `reg` (maxItems 1)
  - `enable-gpios` (maxItems 1; GPIO to enable/disable the regulator.)
  - `mps,fb-voltage-divider` (ref /schemas/types.yaml#/definitions/uint32-array; maxItems 2; An array of two integers containing the resistor values R1 and R2 of the feedback voltage divider in kilo ohms.)
  - `mps,switch-frequency-hz` (enum `500000`, `750000`, `1000000`, `1250000`, `1500000`; The valid switch frequency in Hertz.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-array`
- Textual schema references: `/schemas/regulator/mps,mp886x.yaml`; `/schemas/types.yaml#/definitions/uint32-array`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, enable-gpios, mps,fb-voltage-divider) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; i2c {; #address-cells = <1>;; #size-cells = <0>;; regulator@62 {; compatible = "mps,mp8869";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mp886x.yaml -->
