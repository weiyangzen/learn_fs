<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm RPM regulator. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The Qualcomm RPM regulator is modelled as a subdevice of the RPM. Please refer to Documentation/devicetree/bindings/soc/qcom/qcom,rpm.yaml for information regarding the RPM node. The regulator node houses sub-nodes for each regulator within the device. Each sub-node is identified using the node's name, with valid values listed for each of the pmics below. For pm8058 l0, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14, l15, l16, l17, l18, l19, l20, l21, l22, l23, l24, l25, s0, s1, s2, s3, s4, lvs0, lvs1, ncp For pm8901 l0, l1, l2, l3, l4, l5, l6, s0, s1, s2, s3, s4, lvs0, lvs1, lvs2, lvs3, mvs For pm8921 s1, s2, s3, s4, s7, s8, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l1...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,rpm-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bjorn Andersson <andersson@kernel.org>.
- Compatible contract: `qcom,rpm-pm8058-regulators`, `qcom,rpm-pm8901-regulators`, `qcom,rpm-pm8921-regulators`, `qcom,rpm-pm8018-regulators`, `qcom,rpm-smb208-regulators`
- Top-level required properties: `compatible`
- Required keys across top-level and child schemas: `compatible`
- Top-level declared properties (1): `compatible`
- Property detail signals:
  - `compatible` (enum `qcom,rpm-pm8058-regulators`, `qcom,rpm-pm8901-regulators`, `qcom,rpm-pm8921-regulators`, `qcom,rpm-pm8018-regulators`, `qcom,rpm-smb208-regulators`)
- Child-node or pattern API:
  - pattern child/property `.*-supply$`
  - pattern child/property `^((s|l|lvs)[0-9]*|s[1-2][a-b]|ncp|mvs|usb-switch|hdmi-switch)$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`; `/schemas/types.yaml#/definitions/uint32`
- Textual schema references: `/schemas/regulator/qcom,rpm-regulator.yaml`; `/schemas/types.yaml#/definitions/uint32`
- Header/example integration: `dt-bindings/mfd/qcom-rpm.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/mfd/qcom-rpm.h>; regulators {; compatible = "qcom,rpm-pm8921-regulators";; vdd_l1_l2_l12_l18-supply = <&pm8921_s4>;; s1 {`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpm-regulator.yaml -->
