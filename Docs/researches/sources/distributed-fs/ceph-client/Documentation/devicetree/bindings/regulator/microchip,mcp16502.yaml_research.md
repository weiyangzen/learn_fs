<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MCP16502 - High-Performance PMIC. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MCP16502 is an optimally integrated PMIC compatible with Microchip's eMPUs(Embedded Microprocessor Units), requiring Dynamic Voltage Scaling (DVS) with the use of High-Performance mode (HPM).

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/microchip,mcp16502.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Andrei Simion <andrei.simion@microchip.com>.
- Compatible contract: `microchip,mcp16502`
- Top-level required properties: `compatible`, `reg`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `reg`, `regulators`
- Top-level declared properties (9): `compatible`, `lpm-gpios`, `reg`, `lvin-supply`, `pvin1-supply`, `pvin2-supply`, `pvin3-supply`, `pvin4-supply`, `regulators`
- Regulator/vendor integration properties: `lvin-supply`, `pvin1-supply`, `pvin2-supply`, `pvin3-supply`, `pvin4-supply`
- Property detail signals:
  - `compatible` (const `microchip,mcp16502`)
  - `lpm-gpios` (maxItems 1; GPIO for LPM pin. Note that this GPIO must remain high during suspend-to-ram, keeping the PMIC into HIBERNATE mode.)
  - `reg` (maxItems 1)
  - `lvin-supply` (Input supply phandle for LDO1 and LDO2)
  - `pvin1-supply` (Input supply phandle for VDD_IO (BUCK1))
  - `pvin2-supply` (Input supply phandle for VDD_DDR (BUCK2))
  - `pvin3-supply` (Input supply phandle for VDD_CORE (BUCK3))
  - `pvin4-supply` (Input supply phandle for VDD_OTHER (BUCK4))
  - `regulators` (type object; List of regulators and its properties.)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/microchip,mcp16502.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, reg, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `i2c {; #address-cells = <1>;; #size-cells = <0>;; pmic@5b {; compatible = "microchip,mcp16502";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/microchip,mcp16502.yaml -->
