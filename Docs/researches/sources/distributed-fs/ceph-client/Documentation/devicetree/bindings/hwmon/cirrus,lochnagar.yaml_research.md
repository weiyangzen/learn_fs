<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` defines the hardware-monitor binding titled `Cirrus Logic Lochnagar Audio Development Board`. Description from the schema: Lochnagar is an evaluation and development board for Cirrus Logic Smart CODEC and Amp devices. It allows the connection of most Cirrus Logic devices on mini-cards, as well as allowing connection of various application processor systems to provide a full evaluation platform. Audio system topology, clocking and power can all be controlled through the Lochnagar, allowing the device under test to be used in a variety... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 1 token: `cirrus,lochnagar2-hwmon`. Top-level properties are `compatible`. Required top-level properties are `compatible`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Dependencies include dt-schema core/meta schemas only. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: the main regression mode is DTS ABI drift.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from DTS users and schema-only validation. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/cirrus,lochnagar.yaml -->
