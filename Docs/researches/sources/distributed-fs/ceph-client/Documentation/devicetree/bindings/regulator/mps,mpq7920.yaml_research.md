<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Monolithic Power System MPQ7920 PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

No free-form description field is present; purpose is inferred from title and declared properties.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mps,mpq7920.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Saravanan Sekar <sravanhome@gmail.com>.
- Compatible contract: `mps,mpq7920`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (4): `$nodename`, `compatible`, `reg`, `regulators`
- Property detail signals:
  - `$nodename`
  - `compatible` (enum `mps,mpq7920`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller, must be named after their hardware counterparts BUCK[1-4], one LDORTC, a...)
- Child-node or pattern API:
  - `regulators` child object with properties mps,switch-freq, ldortc

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint8`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mps,mpq7920.yaml`; `/schemas/types.yaml#/definitions/uint8`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@69 {; compatible = "mps,mpq7920";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mps,mpq7920.yaml -->
