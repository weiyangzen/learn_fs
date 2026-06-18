<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **GPIO attached keys**. The file describes the devicetree contract for the GPIO attached keys. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: none.
- Maintainers: Rob Herring <robh@kernel.org>.
- Top-level properties: `compatible`, `autorepeat`, `label`, `poll-interval`.
- `compatible`: enum `gpio-keys`, `gpio-keys-polled`.
- `poll-interval`.
- `autorepeat`.
- `label`: Name of entire device.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^(button|event|key|switch|(button|event|key|switch)-[a-z0-9-]+|[a-z0-9-]+-(button|event|key|switch))$` child nodes with required `linux,code` and properties `gpios`, `interrupts`, `interrupt-names`, `label`, `linux,code`, `linux,input-type`, `linux,input-value`, `debounce-interval`, `wakeup-source`, `wakeup-event-action`, `linux,can-disable`
- Conditional validation: if `interrupts`: require `interrupt-names` / constrain `interrupt-names`; if `gpio-keys-polled`: require `poll-interval` / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/gpio-keys.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 181-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/gpio-keys.yaml -->
