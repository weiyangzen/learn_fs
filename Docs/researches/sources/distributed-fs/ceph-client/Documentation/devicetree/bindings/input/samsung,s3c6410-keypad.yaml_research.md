<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Samsung SoC series Keypad Controller**. Samsung SoC Keypad controller is used to interface a SoC with a matrix-type keypad device. The keypad controller supports multiple row and column lines. A key can be placed at each intersection of a unique row and a unique column. The keypad controller can... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `samsung,s3c6410-keypad`, `samsung,s5pv210-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `samsung,keypad-num-columns`, `samsung,keypad-num-rows`.
- Maintainers: Krzysztof Kozlowski <krzk@kernel.org>.
- Top-level properties: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `wakeup-source`, `linux,input-no-autorepeat`, `linux,input-wakeup`, `samsung,keypad-num-columns`, `samsung,keypad-num-rows`.
- `compatible`: enum `samsung,s3c6410-keypad`, `samsung,s5pv210-keypad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `clocks`: maxItems 1.
- `clock-names`.
- `linux,input-no-autorepeat`: type `boolean`; Do no enable autorepeat feature..
- `linux,input-wakeup`: type `boolean`.
- `samsung,keypad-num-columns`: ref `/schemas/types.yaml#/definitions/uint32`; Number of column lines connected to the keypad controller..
- `samsung,keypad-num-rows`: ref `/schemas/types.yaml#/definitions/uint32`; Number of row lines connected to the keypad controller..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^key-[0-9a-z]+$` child nodes with required `keypad,column`, `keypad,row`, `linux,code` and properties `keypad,column`, `keypad,row`, `linux,code`
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `clocks`, `clock-names`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 121-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/samsung,s3c6410-keypad.yaml -->
