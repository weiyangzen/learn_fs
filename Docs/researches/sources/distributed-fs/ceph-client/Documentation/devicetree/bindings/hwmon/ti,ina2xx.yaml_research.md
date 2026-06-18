<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` defines the hardware-monitor binding titled `Texas Instruments INA209 family of power/voltage monitors`. Description from the schema: The INA209 is a high-side current shunt and power monitor with an I2C interface. Datasheets: https://www.ti.com/product/INA209 It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 16 tokens: `silergy,sq52206`, `silergy,sy24655`, `ti,ina209`, `ti,ina219`, `ti,ina220`, `ti,ina226`, `ti,ina228`, `ti,ina230`, `ti,ina231`, `ti,ina233`, `ti,ina234`, `ti,ina237`, `ti,ina238`, `ti,ina260`, and 2 more. Top-level properties are `compatible`, `reg`, `#io-channel-cells`, `shunt-resistor`, `ti,shunt-gain`, `vs-supply`, `ti,alert-polarity-active-high`, `ti,maximum-expected-current-microamp`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates `allOf`, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `hwmon-common.yaml#`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one SoC variant while rejecting another; large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ti,ina2xx.yaml -->
