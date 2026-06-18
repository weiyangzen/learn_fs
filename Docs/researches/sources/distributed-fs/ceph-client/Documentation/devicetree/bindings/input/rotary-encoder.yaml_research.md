<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml` is a Linux devicetree YAML schema for a input binding schema: **Rotary encoder**. See Documentation/input/devices/rotary-encoder.rst for more information. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `gpios`.
- Maintainers: Frank Li <Frank.Li@nxp.com>.
- Top-level properties: `compatible`, `gpios`, `linux,axis`, `rotary-encoder,steps`, `rotary-encoder,relative-axis`, `rotary-encoder,rollover`, `rotary-encoder,steps-per-period`, `wakeup-source`, `rotary-encoder,encoding`, `rotary-encoder,half-period`.
- `compatible`: const `rotary-encoder`.
- `gpios`: minItems 2.
- `wakeup-source`.
- `linux,axis`: the input subsystem axis to map to this rotary encoder. Defaults to 0 (ABS_X / REL_X).
- `rotary-encoder,steps`: ref `/schemas/types.yaml#/definitions/uint32`; Number of steps in a full turnaround of the encoder. Only relevant for absolute axis. Defaults to 24 which is a typical value for such devices..
- `rotary-encoder,relative-axis`: ref `/schemas/types.yaml#/definitions/flag`; register a relative axis rather than an absolute one. Relative axis will only generate +1/-1 events on the input device, hence no steps need to be passed..
- `rotary-encoder,rollover`: ref `/schemas/types.yaml#/definitions/flag`; Automatic rollover when the rotary value becomes greater than the specified steps or smaller than 0. For absolute axis only..
- `rotary-encoder,steps-per-period`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`, `4`; Number of steps (stable states) per period. The values have the following meaning: 1: Full-period mode (default) 2: Half-period mode 4: Quarter-period mode.
- `rotary-encoder,encoding`: ref `/schemas/types.yaml#/definitions/string`; enum `gray`, `binary`; the method used to encode steps..
- `rotary-encoder,half-period`: ref `/schemas/types.yaml#/definitions/flag`; Makes the driver work on half-period mode. This property is deprecated. Instead, a 'steps-per-period ' value should be used, such as "rotary-encoder,steps-per-period = <2>"..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `gpios`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/rotary-encoder.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 90-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/rotary-encoder.yaml -->
