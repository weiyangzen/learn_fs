<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` defines the hardware-monitor binding titled `Analog Devices LTC4282 I2C High Current Hot Swap Controller over I2C`. Description from the schema: Analog Devices LTC4282 I2C High Current Hot Swap Controller over I2C. https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4282.pdf It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `adi,ltc4282`. Top-level properties are `compatible`, `reg`, `vdd-supply`, `clocks`, `#clock-cells`, `adi,rsense-nano-ohms`, `adi,vin-mode-microvolt`, `adi,fet-bad-timeout-ms`, `adi,overvoltage-dividers`, `adi,undervoltage-dividers`, `adi,current-limit-sense-microvolt`, `adi,overcurrent-retry`, `adi,overvoltage-retry-disable`, `adi,undervoltage-retry-disable`, `adi,fault-log-enable`, `adi,gpio1-mode`, `adi,gpio2-mode`, `adi,gpio3-monitor-enable`. Required top-level properties are `compatible`, `reg`, `adi,rsense-nano-ohms`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Nuno Sa <nuno.sa@analog.com>. Dependencies include `/schemas/types.yaml#/definitions/string`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/adi,ltc4282.yaml -->
