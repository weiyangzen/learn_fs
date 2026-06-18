<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. RPMh Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: rpmh-regulator devices support PMIC regulator management via the Voltage Regulator Manager (VRM) and Oscillator Buffer (XOB) RPMh accelerators. The APPS processor communicates with these hardware blocks via a Resource State Coordinator (RSC) using command packets. The VRM allows changing three parameters for a given regulator, enable state, output voltage, and operating mode. The XOB allows changing only a single parameter for a given regulator, its enable state. Despite its name, the XOB is capable of controlling the enable state of any PMIC peripheral. It is used for clock buffers, low-voltage switches, and LDO/SMPS regulators which have a fixed voltage and mode. ======================= Re...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,rpmh-regulator.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bjorn Andersson <bjorn.andersson@linaro.org>, Krzysztof Kozlowski <krzk@kernel.org>.
- Compatible contract: `qcom,pm6150-rpmh-regulators`, `qcom,pm6150l-rpmh-regulators`, `qcom,pm6350-rpmh-regulators`, `qcom,pm660-rpmh-regulators`, `qcom,pm660l-rpmh-regulators`, `qcom,pm7325-rpmh-regulators`, `qcom,pm7550-rpmh-regulators`, `qcom,pm8005-rpmh-regulators`, `qcom,pm8009-rpmh-regulators`, `qcom,pm8009-1-rpmh-regulators`, `qcom,pm8010-rpmh-regulators`, `qcom,pm8150-rpmh-regulators`, ... (37 total)
- Top-level required properties: `compatible`, `qcom,pmic-id`
- Required keys across top-level and child schemas: `compatible`, `qcom,pmic-id`
- Top-level declared properties (6): `compatible`, `qcom,pmic-id`, `qcom,always-wait-for-ack`, `vdd-flash-supply`, `vdd-rgb-supply`, `bob`
- Regulator/vendor integration properties: `qcom,pmic-id`, `qcom,always-wait-for-ack`, `vdd-flash-supply`, `vdd-rgb-supply`
- Property detail signals:
  - `compatible` (enum `qcom,pm6150-rpmh-regulators`, `qcom,pm6150l-rpmh-regulators`, `qcom,pm6350-rpmh-regulators`, `qcom,pm660-rpmh-regulators`, `qcom,pm660l-rpmh-regulators`, `qcom,pm7325-rpmh-regulators`, `qcom,pm7550-rpmh-regulators`, `qcom,pm8005-rpmh-regulators`, ... (37 total))
  - `qcom,pmic-id` (ref /schemas/types.yaml#/definitions/string; RPMh resource name suffix used for the regulators found on this PMIC.)
  - `qcom,always-wait-for-ack` (ref /schemas/types.yaml#/definitions/flag; Boolean flag which indicates that the application processor must wait for an ACK or a NACK from RPMh for every request s...)
  - `vdd-flash-supply` (Input supply phandle of flash.)
  - `vdd-rgb-supply` (Input supply phandle of rgb.)
  - `bob` (ref regulator.yaml#; type object; BOB regulator node.)
- Child-node or pattern API:
  - `bob` child object
  - pattern child/property `^(smps|ldo|lvs|bob)[0-9]+$`

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 28 `if` block(s), 28 `then` block(s). Top-level closure is `unevaluatedProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/string`; `/schemas/types.yaml#/definitions/flag`; `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,rpmh-regulator.yaml`; `/schemas/types.yaml#/definitions/flag`; `/schemas/types.yaml#/definitions/string`
- Header/example integration: `dt-bindings/regulator/qcom,rpmh-regulator.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, qcom,pmic-id) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/regulator/qcom,rpmh-regulator.h>; pm8998-rpmh-regulators {; compatible = "qcom,pm8998-rpmh-regulators";; qcom,pmic-id = "a";`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,rpmh-regulator.yaml -->
