<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Azoteq IQS620A/621/622/624/625 Keys and Switches**. The Azoteq IQS620A, IQS621, IQS622, IQS624 and IQS625 multi-function sensors feature a variety of self-capacitive, mutual-inductive and Hall-effect sens- ing capabilities that can facilitate a variety of contactless key and switch applications. These... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs620a-keys`, `azoteq,iqs621-keys`, `azoteq,iqs622-keys`, `azoteq,iqs624-keys`, `azoteq,iqs625-keys`.
- Required top-level fields: `compatible`, `linux,keycodes`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `linux,keycodes`.
- `compatible`: enum `azoteq,iqs620a-keys`, `azoteq,iqs621-keys`, `azoteq,iqs622-keys`, `azoteq,iqs624-keys`, `azoteq,iqs625-keys`.
- `linux,keycodes`: maxItems 16; minItems 1; Specifies the numeric keycodes associated with each available touch or proximity event according to the following table. An 'x' indicates the event is supported for a given device. Specify 0 for unused events.....
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^hall-switch-(north|south)$` child nodes with required `linux,code` and properties `linux,code`, `azoteq,use-prox`
- Conditional validation: if `azoteq,iqs624-keys`, `azoteq,iqs625-keys`: require none / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs62x-keys.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 132-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs62x-keys.yaml -->
