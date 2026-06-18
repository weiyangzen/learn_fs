<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml` is a Linux devicetree YAML schema for a joystick binding: **ADC attached joystick**. Bindings for joystick devices connected to ADC controllers supporting the Industrial I/O subsystem. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `io-channels`, `#address-cells`, `#size-cells`.
- Maintainers: Artur Rojek <contact@artur-rojek.eu>.
- Top-level properties: `compatible`, `io-channels`, `poll-interval`, `#address-cells`, `#size-cells`.
- `compatible`: const `adc-joystick`.
- `io-channels`: maxItems 1024; minItems 1; List of phandle and IIO specifier pairs. Each pair defines one ADC channel to which a joystick axis is connected. See https://github.com/devicetree-org/dt-schema/blob/master/schemas/iio/iio-consumer.yaml for details..
- `poll-interval`.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^axis@[0-9a-f]+$` child nodes with required `reg`, `linux,code`, `abs-range` and properties `reg`, `linux,code`, `abs-range`, `abs-fuzz`, `abs-flat`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `io-channels`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/adc-joystick.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 127-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/adc-joystick.yaml -->
