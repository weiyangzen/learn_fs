<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. QCA6390 PMU Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The QCA6390 package contains discrete modules for WLAN and Bluetooth. They are powered by the Power Management Unit (PMU) that takes inputs from the host and provides LDO outputs. This document describes this module.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,qca6390-pmu.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bartosz Golaszewski <bartosz.golaszewski@linaro.org>.
- Compatible contract: No `compatible` property is declared in this schema.
- Top-level required properties: `compatible`, `regulators`
- Required keys across top-level and child schemas: `compatible`, `regulators`, `vddaon-supply`, `vddpmu-supply`, `vddrfa0p95-supply`, `vddrfa1p3-supply`, `vddrfa1p9-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`, `vddasd-supply`, `vddrfa0p8-supply`, `vddrfa1p2-supply`, `vddrfa1p7-supply`, `vddrfa2p2-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vdd-supply`, `vdddig-supply`, `vddrfa1p8-supply`
- Top-level declared properties (26): `compatible`, `vdd-supply`, `vddaon-supply`, `vddasd-supply`, `vdddig-supply`, `vddpmu-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vddio1p2-supply`, `vddrfa0p8-supply`, `vddrfa0p95-supply`, `vddrfa1p2-supply`, `vddrfa1p3-supply`, `vddrfa1p7-supply`, `vddrfa1p8-supply`, `vddrfa1p9-supply`, `vddrfa2p2-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`, `wlan-enable-gpios`, `bt-enable-gpios`, `swctrl-gpios`, `xo-clk-gpios`, ... (26 total)
- Regulator/vendor integration properties: `vdd-supply`, `vddaon-supply`, `vddasd-supply`, `vdddig-supply`, `vddpmu-supply`, `vddpmumx-supply`, `vddpmucx-supply`, `vddio1p2-supply`, `vddrfa0p8-supply`, `vddrfa0p95-supply`, `vddrfa1p2-supply`, `vddrfa1p3-supply`, `vddrfa1p7-supply`, `vddrfa1p8-supply`, `vddrfa1p9-supply`, `vddrfa2p2-supply`, `vddpcie1p3-supply`, `vddpcie1p9-supply`, `vddio-supply`
- Property detail signals:
  - `compatible`
  - `vdd-supply` (VDD supply regulator handle)
  - `vddaon-supply` (VDD_AON supply regulator handle)
  - `vddasd-supply` (VDD_ASD supply regulator handle)
  - `vdddig-supply` (VDD_DIG supply regulator handle)
  - `vddpmu-supply` (VDD_PMU supply regulator handle)
  - `vddpmumx-supply` (VDD_PMU_MX supply regulator handle)
  - `vddpmucx-supply` (VDD_PMU_CX supply regulator handle)
  - `vddio1p2-supply` (VDD_IO_1P2 supply regulator handle)
  - `vddrfa0p8-supply` (VDD_RFA_0P8 supply regulator handle)
  - `vddrfa0p95-supply` (VDD_RFA_0P95 supply regulator handle)
  - `vddrfa1p2-supply` (VDD_RFA_1P2 supply regulator handle)
  - `vddrfa1p3-supply` (VDD_RFA_1P3 supply regulator handle)
  - `vddrfa1p7-supply` (VDD_RFA_1P7 supply regulator handle)
  - `vddrfa1p8-supply` (VDD_RFA_1P8 supply regulator handle)
  - `vddrfa1p9-supply` (VDD_RFA_1P9 supply regulator handle)
  - `vddrfa2p2-supply` (VDD_RFA_2P2 supply regulator handle)
  - `vddpcie1p3-supply` (VDD_PCIE_1P3 supply regulator handle)
  - ... plus 8 more top-level declared propertie(s).
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 1 `allOf` block(s), 1 `oneOf` block(s), 0 `anyOf` block(s), 4 `if` block(s), 4 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,qca6390-pmu.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulators) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Conditional branches and alternatives need negative tests for each compatible variant so later edits do not accidentally widen or narrow a PMIC-specific contract.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; pmu {; compatible = "qcom,qca6390-pmu";; pinctrl-names = "default";; pinctrl-0 = <&bt_en_state>, <&wlan_en_state>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,qca6390-pmu.yaml -->
