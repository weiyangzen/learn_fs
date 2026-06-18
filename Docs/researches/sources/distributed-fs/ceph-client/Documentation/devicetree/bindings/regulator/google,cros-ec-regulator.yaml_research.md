<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: ChromeOS EC controlled voltage regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: Any property defined as part of the core regulator binding, defined in regulator.yaml, can also be used.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/google,cros-ec-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Pi-Hsun Shih <pihsun@chromium.org>.
- Compatible contract: `google,cros-ec-regulator`
- Top-level required properties: `compatible`, `reg`
- Required keys across top-level and child schemas: `compatible`, `reg`
- Top-level declared properties (3): `compatible`, `reg`, `vin-supply`
- Regulator/vendor integration properties: `vin-supply`
- Property detail signals:
  - `compatible` (const `google,cros-ec-regulator`)
  - `reg` (maxItems 1; Identifier for the voltage regulator to ChromeOS EC.)
  - `vin-supply` (Input supply phandle)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/google,cros-ec-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `spi {; #address-cells = <1>;; #size-cells = <0>;; cros_ec: ec@0 {; compatible = "google,cros-ec-spi";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/google,cros-ec-regulator.yaml -->
