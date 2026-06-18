<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Generic PWM Regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Currently supports 2 modes of operation: Voltage Table: When in this mode, a voltage table (See below) of predefined voltage <=> duty-cycle values must be provided via DT. Limitations are that the regulator can only operate at the voltages supplied in the table. Intermediary duty-cycle values which would normally allow finer grained voltage selection are ignored and rendered useless. Although more control is given to the user if the assumptions made in continuous-voltage mode do not reign true. Continuous Voltage: This mode uses the regulator's maximum and minimum supplied voltages specified in the regulator-{min,max}-microvolt properties to calculate appropriate duty-cycle values. This allo...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/pwm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Brian Norris <briannorris@chromium.org>, Lee Jones <lee@kernel.org>, Alexandre Courbot <acourbot@nvidia.com>.
- Compatible contract: `pwm-regulator`
- Top-level required properties: `compatible`, `pwms`
- Required keys across top-level and child schemas: `compatible`, `pwms`
- Top-level declared properties (6): `compatible`, `pwms`, `voltage-table`, `enable-gpios`, `pwm-dutycycle-unit`, `pwm-dutycycle-range`
- Regulator/vendor integration properties: `enable-gpios`
- Property detail signals:
  - `compatible` (const `pwm-regulator`)
  - `pwms` (maxItems 1)
  - `voltage-table` (ref /schemas/types.yaml#/definitions/uint32-matrix; Voltage and Duty-Cycle table.)
  - `enable-gpios` (maxItems 1; Regulator enable GPIO)
  - `pwm-dutycycle-unit` (ref /schemas/types.yaml#/definitions/uint32; default 100; Integer value encoding the duty cycle unit. If not defined, <100> is assumed, meaning that pwm-dutycycle-range contains ...)
  - `pwm-dutycycle-range` (ref /schemas/types.yaml#/definitions/uint32-array; 2 fixed item schema(s); default ['0 100']; Should contain 2 entries. The first entry is encoding the dutycycle for regulator-min-microvolt and the second one the d...)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-matrix`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`
- Textual schema references: `/schemas/regulator/pwm-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.
- PWM integration is explicit; the PWM provider and voltage table/state mapping control the regulator output model.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, pwms) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; // Continuous Voltage With Enable GPIO Example:; regulator {; compatible = "pwm-regulator";; pwms = <&pwm1 0 8448 0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/pwm-regulator.yaml -->
