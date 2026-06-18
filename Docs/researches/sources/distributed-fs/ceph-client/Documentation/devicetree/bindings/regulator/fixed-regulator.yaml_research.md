<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Fixed Voltage regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.yaml, can also be used. However a fixed voltage regulator is expected to have the regulator-min-microvolt and regulator-max-microvolt to be the same.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/fixed-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>.
- Compatible contract: `regulator-fixed`, `regulator-fixed-clock`, `regulator-fixed-domain`
- Top-level required properties: `compatible`, `regulator-name`
- Required keys across top-level and child schemas: `compatible`, `regulator-name`, `clocks`, `power-domains`, `required-opps`, `gpio`, `gpios`
- Top-level declared properties (15): `$nodename`, `compatible`, `regulator-name`, `gpio`, `gpios`, `clocks`, `power-domains`, `required-opps`, `startup-delay-us`, `off-on-delay-us`, `enable-active-high`, `gpio-open-drain`, `vin-supply`, `interrupts`, `system-critical-regulator`
- Regulator/vendor integration properties: `regulator-name`, `gpios`, `startup-delay-us`, `off-on-delay-us`, `vin-supply`, `system-critical-regulator`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `regulator-fixed`, `regulator-fixed-clock`, `regulator-fixed-domain`)
  - `regulator-name` (boolean schema True)
  - `gpio` (maxItems 1; gpio to use for enable control)
  - `gpios` (maxItems 1)
  - `clocks` (maxItems 1; clock to use for enable control. This binding is only available if the compatible is chosen to regulator-fixed-clock. Th...)
  - `power-domains` (maxItems 1; Power domain to use for enable control. This binding is only available if the compatible is chosen to regulator-fixed-do...)
  - `required-opps` (maxItems 1; Performance state to use for enable control. This binding is only available if the compatible is chosen to regulator-fix...)
  - `startup-delay-us` (startup time in microseconds)
  - `off-on-delay-us` (off delay time in microseconds)
  - `enable-active-high` (type boolean; Polarity of GPIO is Active high. If this property is missing, the default assumed is Active low.)
  - `gpio-open-drain` (type boolean; GPIO is open drain type. If this property is missing then default assumption is false.)
  - `vin-supply` (Input supply phandle.)
  - `interrupts` (maxItems 1; Interrupt signaling a critical under-voltage event.)
  - `system-critical-regulator` (boolean schema True)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 2 `if` block(s), 2 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/fixed-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- GPIO integration is explicit; polarity, open-drain behavior, and enable timing have to agree with board wiring.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulator-name) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- GPIO polarity and enable-delay mistakes can pass syntax checks while causing rails to be enabled at the wrong time or wrong level.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `reg_1v8: regulator-1v8 {; compatible = "regulator-fixed";; regulator-name = "1v8";; regulator-min-microvolt = <1800000>;; regulator-max-microvolt = <1800000>;; gpio = <&gpio1 16 0>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/fixed-regulator.yaml -->
