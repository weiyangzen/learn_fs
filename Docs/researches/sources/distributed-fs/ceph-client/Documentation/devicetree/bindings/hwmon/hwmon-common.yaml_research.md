<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` defines the hardware-monitor binding titled `Hardware Monitoring Devices Common Properties`. It constrains devicetree nodes through compatible strings, required resources, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. This is a reusable common schema fragment rather than a directly matched device compatible; other bindings include it through `$ref` to share fan or hwmon property definitions. Top-level properties are `label`, `shunt-resistor-micro-ohms`. Required top-level properties are none declared. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Guenter Roeck <linux@roeck-us.net>. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/hwmon-common.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/hwmon-common.yaml -->
