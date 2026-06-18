<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` defines the PMBus hardware-monitor binding titled `MPS MP2975 Synchronous Buck Regulator`. Description from the schema: The MPS MP2971, MP2973 & MP2975 is a multi-phase voltage regulator designed for use in high-performance computing and server applications. It supports I2C/PMBus for control and monitoring. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 3 tokens: `mps,mp2971`, `mps,mp2973`, `mps,mp2975`. Top-level properties are `compatible`, `reg`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. The highest-risk API details are I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Naresh Solanki <naresh.solanki@9elements.com>. Dependencies include `/schemas/regulator/regulator.yaml#`. Integration points include the PMBus and hwmon subsystems, I2C device instantiation, regulator/power-rail telemetry, alert lines, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to I2C address constraints, compatible aliases, PMBus chip variants, regulator child nodes, and alert/interrupt wiring, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/pmbus/mps,mp2975.yaml -->
