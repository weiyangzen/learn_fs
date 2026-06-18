<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: NXP PF8100/PF8121A/PF8200 PMIC regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: PF8100/PF8121A/PF8200 is a PMIC designed for highperformance consumer applications. It features seven high efficiency buck converters, four linear and one vsnvs regulators. It has built-in one time programmable fuse bank for device configurations.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/nxp,pf8x00-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Jagan Teki <jagan@amarulasolutions.com>, Troy Kisky <troy.kisky@boundarydevices.com>.
- Compatible contract: `nxp,pf8100`, `nxp,pf8121a`, `nxp,pf8200`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (3): `compatible`, `reg`, `regulators`
- Property detail signals:
  - `compatible` (enum `nxp,pf8100`, `nxp,pf8121a`, `nxp,pf8200`)
  - `reg` (maxItems 1)
  - `regulators` (type object; list of regulators provided by this controller)
- Child-node or pattern API:
  - `regulators` child object with properties vsnvs

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/nxp,pf8x00-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@8 {; compatible = "nxp,pf8100";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/nxp,pf8x00-regulator.yaml -->
