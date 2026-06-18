<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: GPIO controlled regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.txt, can also be used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/gpio-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>.
- Compatible contract: `regulator-gpio`
- Top-level required properties: `compatible`, `regulator-name`, `gpios`, `states`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`, `gpios`, `states`
- Top-level declared properties (11): `compatible`, `regulator-name`, `enable-gpios`, `gpios`, `gpios-states`, `states`, `startup-delay-us`, `enable-active-high`, `gpio-open-drain`, `regulator-type`, `vin-supply`
- Regulator/vendor integration properties: `regulator-name`, `enable-gpios`, `gpios`, `states`, `startup-delay-us`, `regulator-type`, `vin-supply`
- Property detail signals:
  - `compatible` (const `regulator-gpio`)
  - `regulator-name` (boolean schema True)
  - `enable-gpios` (maxItems 1; GPIO to use to enable/disable the regulator. Warning, the GPIO phandle flags are ignored and the GPIO polarity is contro...)
  - `gpios` (minItems 1; maxItems 8; Array of one or more GPIO pins used to select the regulator voltage/current listed in "states".)
  - `gpios-states` (ref /schemas/types.yaml#/definitions/uint32-array; items enum 2 values; minItems 1; maxItems 8)
  - `states` (ref /schemas/types.yaml#/definitions/uint32-matrix; minItems 2; maxItems 256; Selection of available voltages/currents provided by this regulator and matching GPIO configurations to achieve them. If...)
  - `startup-delay-us` (startup time in microseconds)
  - `enable-active-high` (type boolean; Polarity of "enable-gpio" GPIO is active HIGH. Default is active LOW.)
  - `gpio-open-drain` (type boolean; GPIO is open drain type. If this property is missing then default assumption is false.)
  - `regulator-type` (ref /schemas/types.yaml#/definitions/string; enum `voltage`, `current`; default voltage; Specifies what is being regulated.)
  - `vin-supply` (Input supply phandle.)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`; `/schemas/types.yaml#/definitions/string`
- Textual schema references: `/schemas/regulator/gpio-regulator.yaml`; `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/uint32-array`; `/schemas/types.yaml#/definitions/uint32-matrix`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulator-name, gpios, states) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `gpio-regulator {; compatible = "regulator-gpio";; regulator-name = "mmci-gpio-supply";; regulator-min-microvolt = <1800000>;; regulator-max-microvolt = <2600000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/gpio-regulator.yaml -->
