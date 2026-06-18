<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **ADC attached resistor ladder buttons**. The file describes the devicetree contract for the ADC attached resistor ladder buttons. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `io-channels`, `io-channel-names`, `keyup-threshold-microvolt`.
- Maintainers: Alexandre Belloni <alexandre.belloni@bootlin.com>.
- Top-level properties: `compatible`, `io-channels`, `io-channel-names`, `keyup-threshold-microvolt`, `poll-interval`, `autorepeat`.
- `compatible`: const `adc-keys`.
- `io-channels`: maxItems 1.
- `poll-interval`.
- `io-channel-names`: const `buttons`.
- `keyup-threshold-microvolt`: Voltage above or equal to which all the keys are considered up..
- `autorepeat`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^button-` child nodes with required `linux,code`, `press-threshold-microvolt` and properties `label`, `linux,code`, `press-threshold-microvolt`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `io-channels`, `io-channel-names`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adc-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 103-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-keys.yaml -->
