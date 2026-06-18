<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` defines the hardware-monitor binding titled `Analog Devices ADM1075/ADM127x/ADM1281/ADM129x digital power monitors`. Description from the schema: The ADM1293 and ADM1294 are high accuracy integrated digital power monitors that offer digital current, voltage, and power monitoring using an on-chip, 12-bit analog-to-digital converter (ADC), communicated through a PMBus compliant I2C interface. Datasheets: https://www.analog.com/en/products/adm1294.html The SQ24905C is also a Hot-swap controller compatibility to the ADM1278, the PMBUS_MFR_MODEL is MC09C Datashe... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 10 tokens: `adi,adm1075`, `adi,adm1272`, `adi,adm1273`, `adi,adm1275`, `adi,adm1276`, `adi,adm1278`, `adi,adm1281`, `adi,adm1293`, `adi,adm1294`, `silergy,mc09c`. Top-level properties are `compatible`, `reg`, `adi,volt-curr-sample-average`, `adi,power-sample-average`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/uint32`, `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,adm1275.yaml -->
