<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek DVFSRC-controlled Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Dynamic Voltage and Frequency Scaling Resource Collector Regulators are controlled with votes to the DVFSRC hardware.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6873-dvfsrc-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: AngeloGioacchino Del Regno <angelogioacchino.delregno@collabora.com>.
- Compatible contract: `mediatek,mt6873-dvfsrc-regulator`, `mediatek,mt6893-dvfsrc-regulator`, `mediatek,mt8183-dvfsrc-regulator`, `mediatek,mt8192-dvfsrc-regulator`, `mediatek,mt8195-dvfsrc-regulator`, `mediatek,mt8196-dvfsrc-regulator`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`, `dvfsrc-vcore`, `dvfsrc-vscp`
- Top-level declared properties (3): `compatible`, `dvfsrc-vcore`, `dvfsrc-vscp`
- Property detail signals:
  - `compatible` (enum `mediatek,mt6873-dvfsrc-regulator`, `mediatek,mt6893-dvfsrc-regulator`, `mediatek,mt8183-dvfsrc-regulator`, `mediatek,mt8192-dvfsrc-regulator`, `mediatek,mt8195-dvfsrc-regulator`, `mediatek,mt8196-dvfsrc-regulator`)
  - `dvfsrc-vcore` (ref regulator.yaml#; DVFSRC-controlled SoC Vcore regulator)
  - `dvfsrc-vscp` (ref regulator.yaml#; DVFSRC-controlled System Control Processor regulator)
- Child-node or pattern API:
  - No named child object or `patternProperties` contract is declared at the top level.

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 1 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6873-dvfsrc-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- No inline example body was detected by the parser; validation should still cover the schema itself and any DTS nodes that match it.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6873-dvfsrc-regulator.yaml -->
