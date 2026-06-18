<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` defines the hardware-monitor binding titled `NTC thermistor temperature sensors`. Description from the schema: Thermistors with negative temperature coefficient (NTC) are resistors that vary in resistance in an often non-linear way in relation to temperature. The negative temperature coefficient means that the resistance decreases as the temperature rises. Since the relationship between resistance and temperature is non-linear, software drivers most often need to use a look up table and interpolation to get from resistance... It is a Linux devicetree YAML schema used to validate hardware description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties, not callable functions. `compatible` uses `oneOf` with 16 branches with 16 tokens: `epcos,b57330v2103`, `epcos,b57891s0103`, `murata,ncp15wb473`, `murata,ncp18wb473`, `murata,ncp21wb473`, `murata,ncp03wb473`, `murata,ncp15wl333`, `murata,ncp03wf104`, `murata,ncp15xh103`, `murata,ncp18wm474`, `samsung,1404-001221`, `ntc,ncp15wb473`, `ntc,ncp18wb473`, `ntc,ncp21wb473`, and 2 more. Top-level properties are `$nodename`, `compatible`, `#thermal-sensor-cells`, `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, `connected-positive`, `io-channels`. Required top-level properties are `compatible`, `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, `io-channels`. Pattern properties are none. The highest-risk API details are sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, matches a devicetree node by `compatible`, `$nodename`, or referenced fragment use, checks required properties, applies `$ref` schemas, evaluates no top-level conditionals, and finally enforces `additionalProperties` or `unevaluatedProperties`. At runtime the corresponding kernel subsystem binds a driver from the compatible table and consumes the validated resources; the YAML itself executes no code.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including sensor cache updates, fan PWM duty state, alarm/limit registers, thermal-zone readings, or PMBus telemetry.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the hwmon subsystem, I2C/platform/MFD parents, thermal zones, fan/pwm/tach consumers, regulators, and board monitor nodes. The binding also integrates with `make dt_binding_check`, `make dtbs_check`, schema example extraction, and the in-tree DTS files that instantiate the documented nodes.

## Risks
Primary risks are incompatible ABI changes to sensor channel modelling, I2C address constraints, GPIO/PWM/tach phandles, thermal-sensor cells, and vendor calibration properties, mismatches between documented compatibles and driver match tables, and resource ordering changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: large compatible catalogues are prone to missing fallback ordering; examples can drift from the schema and give false confidence if not validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation should be part of the signal. Also compare the listed compatible strings with kernel driver `of_match_table` entries and keep DTS users building with `W=1` so property spelling, cell counts, and phandle references regress visibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/hwmon/ntc-thermistor.yaml -->
