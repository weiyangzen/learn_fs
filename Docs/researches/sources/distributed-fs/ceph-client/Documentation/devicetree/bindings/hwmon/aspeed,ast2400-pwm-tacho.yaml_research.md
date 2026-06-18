<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` defines the hardware-monitor binding titled `ASPEED AST2400/AST2500 PWM and Fan Tacho controller`. Description from the schema: The ASPEED PWM controller can support up to 8 PWM outputs. The ASPEED Fan Tacho controller can support up to 16 Fan tachometer inputs. There can be up to 8 fans supported. Each fan can have 1 PWM output and 1-2 Fan tach inputs. It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses an `enum` with 2 tokens: `aspeed,ast2400-pwm-tacho`, `aspeed,ast2500-pwm-tacho`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#cooling-cells`, `clocks`, `resets`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `clocks`, `resets`. Pattern properties are `^fan@[0-7]$`. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Joel Stanley <joel@jms.id.au>, Andrew Jeffery <andrew@codeconstruct.com.au>. Dependencies include `/schemas/types.yaml#/definitions/uint8-array`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: pattern property regexes can over-match or under-match child nodes; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/aspeed,ast2400-pwm-tacho.yaml -->
