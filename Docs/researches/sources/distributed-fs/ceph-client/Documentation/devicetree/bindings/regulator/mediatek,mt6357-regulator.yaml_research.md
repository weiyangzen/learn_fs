<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MediaTek MT6357 Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The MT6357 PMIC provides 5 BUCK and 29 LDO. Regulators and nodes are named according to the regulator type: - buck-<name> - ldo-<name>. MT6357 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mediatek,mt6357-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Chen Zhong <chen.zhong@mediatek.com>, Fabien Parent <fabien.parent@linaro.org>, Alexandre Mergnat <amergnat@baylibre.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`, `regulator-min-microvolt`, `regulator-max-microvolt`
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^buck-v(core|modem|pa|proc|s1)$`
  - pattern child/property `^ldo-v(camio18|aud28|aux18|io18|io28|rf12|rf18|cn18|cn28|fe28)$`
  - pattern child/property `^ldo-v(efuse|ibr|ldo28|mch|cama|camd|cn33-bt|cn33-wifi)$`
  - pattern child/property `^ldo-v(xo22|emc|mc|sim1|sim2|sram-others|sram-proc|dram|usb33)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mediatek,mt6357-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6357_vproc_reg: buck-vproc {; regulator-name = "vproc";; regulator-min-microvolt = <518750>;; regulator-max-microvolt = <1312500>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mediatek,mt6357-regulator.yaml -->
