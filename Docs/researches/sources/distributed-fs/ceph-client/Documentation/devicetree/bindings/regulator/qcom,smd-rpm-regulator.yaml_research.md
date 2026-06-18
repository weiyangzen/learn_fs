<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: QCOM SMD RPM REGULATOR. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Qualcomm RPM over SMD regulator is modelled as a subdevice of the RPM. Because SMD is used as the communication transport mechanism, the RPM resides as a subnode of the SMD. As such, the SMD-RPM regulator requires that the SMD and RPM nodes be present. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,smd.yaml for information pertaining to the SMD node. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,smd-rpm.yaml for information regarding the RPM node. The regulator node houses sub-nodes for each regulator within the device. Each sub-node is identified using the node's name, with valid values listed for each of the pmics below. For mp5496, s1, s2, l2, l5 For...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,smd-rpm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Andy Gross <agross@kernel.org>, Bjorn Andersson <bjorn.andersson@linaro.org>.
- Compatible contract: `qcom,rpm-mp5496-regulators`, `qcom,rpm-pm2250-regulators`, `qcom,rpm-pm6125-regulators`, `qcom,rpm-pm660-regulators`, `qcom,rpm-pm660l-regulators`, `qcom,rpm-pm8226-regulators`, `qcom,rpm-pm8841-regulators`, `qcom,rpm-pm8909-regulators`, `qcom,rpm-pm8916-regulators`, `qcom,rpm-pm8937-regulators`, `qcom,rpm-pm8941-regulators`, `qcom,rpm-pm8950-regulators`, ... (20 total)
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (enum `qcom,rpm-mp5496-regulators`, `qcom,rpm-pm2250-regulators`, `qcom,rpm-pm6125-regulators`, `qcom,rpm-pm660-regulators`, `qcom,rpm-pm660l-regulators`, `qcom,rpm-pm8226-regulators`, `qcom,rpm-pm8841-regulators`, `qcom,rpm-pm8909-regulators`, ... (20 total))
- Child-node or pattern API:
  - pattern child/property `.*-supply$`
  - pattern child/property `^((s|l|lvs|5vs)[0-9]*)|(boost-bypass)|(bob)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,smd-rpm-regulator.yaml`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `pm8941-regulators {; compatible = "qcom,rpm-pm8941-regulators";; vdd_l13_l20_l23_l24-supply = <&pm8941_boost>;; pm8941_s3: s3 {; regulator-min-microvolt = <1800000>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,smd-rpm-regulator.yaml -->
