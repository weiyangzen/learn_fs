<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: MT6359 Regulator from MediaTek Integrated. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: List of regulators provided by this controller. It is named according to its regulator type, buck_<name> and ldo_<name>. MT6359 regulators node should be sub node of the MT6397 MFD node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/mt6359-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Hsin-Hsiung Wang <hsin-hsiung.wang@mediatek.com>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: None at top level.
- Required keys across top-level and child schemas: `regulator-name`
- Top-level declared properties (0): none
- Property detail signals:
- Child-node or pattern API:
  - pattern child/property `^buck_v(s1|gpu11|modem|pu|core|s2|pa|proc2|proc1|core_sshub)$`
  - pattern child/property `^ldo_v(ibr|rf12|usb|camio|efuse|xo22)$`
  - pattern child/property `^ldo_v(rfck|emc|a12|a09|ufs|bbck)$`
  - pattern child/property `^ldo_vcn(18|13|33_1_bt|13_1_wifi|33_2_bt|33_2_wifi)$`
  - pattern child/property `^ldo_vsram_(proc2|others|md|proc1|others_sshub)$`
  - pattern child/property `^ldo_v(fe|bif|io)28$`
  - pattern child/property `^ldo_v(aud|io|aux|rf|m)18$`
  - pattern child/property `^ldo_vsim[12]$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/mt6359-regulator.yaml`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pmic {; regulators {; mt6359_vs1_buck_reg: buck_vs1 {; regulator-name = "vs1";; regulator-min-microvolt = <800000>;; regulator-max-microvolt = <2200000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/mt6359-regulator.yaml -->
