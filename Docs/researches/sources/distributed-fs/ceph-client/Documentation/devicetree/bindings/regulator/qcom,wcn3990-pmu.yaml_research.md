<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml

## Purpose
This file is a Linux Devicetree JSON-schema binding for regulator hardware or regulator-framework data: Qualcomm Technologies, Inc. WCN3990 PMU Regulators. It gives `dt-schema` a machine-readable contract for DTS/DTB nodes before Linux regulator, MFD, PMIC, GPIO, PWM, SPMI, RPM/RPMh, or board-specific drivers consume those nodes at probe time.

Description signal: The WCN3990 package contains discrete modules for WLAN and Bluetooth. They are powered by the Power Management Unit (PMU) that takes inputs from the host and provides LDO outputs. This document describes this module.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/regulator/qcom,wcn3990-pmu.yaml#` using meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Maintainers: Bartosz Golaszewski <bartosz.golaszewski@oss.qualcomm.com>.
- Compatible contract: `qcom,wcn3950-pmu`, `qcom,wcn3988-pmu`, `qcom,wcn3990-pmu`, `qcom,wcn3991-pmu`, `qcom,wcn3998-pmu`
- Top-level required properties: `compatible`, `regulators`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`
- Required keys across top-level and child schemas: `compatible`, `regulators`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`
- Top-level declared properties (9): `compatible`, `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`, `vddch1-supply`, `swctrl-gpios`, `clocks`, `regulators`
- Regulator/vendor integration properties: `vddio-supply`, `vddxo-supply`, `vddrf-supply`, `vddch0-supply`, `vddch1-supply`
- Property detail signals:
  - `compatible` (enum `qcom,wcn3950-pmu`, `qcom,wcn3988-pmu`, `qcom,wcn3990-pmu`, `qcom,wcn3991-pmu`, `qcom,wcn3998-pmu`)
  - `vddio-supply` (VDD_IO supply regulator handle)
  - `vddxo-supply` (VDD_XTAL supply regulator handle)
  - `vddrf-supply` (VDD_RF supply regulator handle)
  - `vddch0-supply` (chain 0 supply regulator handle)
  - `vddch1-supply` (chain 1 supply regulator handle)
  - `swctrl-gpios` (maxItems 1; GPIO line indicating the state of the clock supply to the BT module)
  - `clocks` (maxItems 1; Reference clock handle)
  - `regulators` (type object; LDO outputs of the PMU)
- Child-node or pattern API:
  - `regulators` child object

## Control Flow
There is no imperative control flow in this YAML. Validation control flow starts when `dt-schema` selects the binding by `$id` and `compatible`, checks the required lists, expands shared `$ref` schemas, validates scalar constraints, and then descends into child regulator nodes or pattern-matched properties. The binding has 0 `allOf` block(s), 0 `oneOf` block(s), 0 `anyOf` block(s), 0 `if` block(s), 0 `then` block(s). Top-level closure is `additionalProperties: False`, so DTS authors either must stay within the declared property set or rely on referenced schemas that intentionally allow extension.

## State and Persistence Behavior
The file stores no runtime state. Its persistent effect is the source-controlled ABI contract for board firmware descriptions: regulator names, voltage/current limits, boot/always-on policy, supply dependencies, enable GPIOs, PWM or SPMI/RPM resource identifiers, and child regulator node names are encoded in DTS and compiled into DTB. Kernel regulator consumers then use those persisted properties during driver probe and regulator framework registration; later voltage, mode, and enable state changes happen in drivers, not in this schema.

## Dependencies and Integration Points
- Schema references: `regulator.yaml#`
- Textual schema references: `/schemas/regulator/qcom,wcn3990-pmu.yaml`
- Header/example integration: `dt-bindings/gpio/gpio.h`
- Runtime integration starts from the `compatible` value, which selects Linux regulator/MFD/platform drivers and the matching regulator descriptors.
- Child regulator nodes integrate with the regulator core by carrying common `regulator-*` constraints and supply phandles under device-specific names or regex-matched regulator names.

## Risks
- A wrong `compatible` string or child regulator name can keep the binding from matching and can also prevent the intended kernel regulator driver from probing.
- Missing required top-level properties (compatible, regulators, vddio-supply, vddxo-supply, vddrf-supply, vddch0-supply) should be caught by `dt_binding_check`, but the failure often maps to a runtime probe failure or absent regulator registration.
- Child-node schemas are easy to break by renaming rails, omitting `reg`, or placing common regulator constraints at the wrong level.
- Supply phandle mistakes can invert power dependency ordering and produce deferred probes or brown-out behavior that schema validation may only partially detect.
- Property-closure behavior varies by binding and referenced schemas; validation should confirm both typo rejection and intentionally allowed extension points.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml` to validate this YAML, referenced schemas, and inline examples.
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml` against boards using this regulator to verify real DTS nodes, child rails, and supply phandles.
- Useful negative tests remove each required property, use an unsupported `compatible`, add an undeclared property, and alter child regulator names or `reg` values when present.
- Inline example seed observed in the file: `#include <dt-bindings/gpio/gpio.h>; pmu {; compatible = "qcom,wcn3990-pmu";; vddio-supply = <&vreg_io>;; vddxo-supply = <&vreg_xo>;`

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/regulator/qcom,wcn3990-pmu.yaml -->
