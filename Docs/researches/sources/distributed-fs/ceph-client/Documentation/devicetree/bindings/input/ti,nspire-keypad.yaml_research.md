<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **TI-NSPIRE Keypad**. The file describes the devicetree contract for the TI-NSPIRE Keypad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `ti,nspire-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `scan-interval`, `row-delay`, `linux,keymap`.
- Maintainers: Andrew Davis <afd@ti.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`, `scan-interval`, `row-delay`, `active-low`.
- `compatible`: enum `ti,nspire-keypad`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- `scan-interval`: ref `/schemas/types.yaml#/definitions/uint32`; How often to scan in us. Based on a APB speed of 33MHz, the maximum and minimum delay time is ~2000us and ~500us respectively.
- `row-delay`: ref `/schemas/types.yaml#/definitions/uint32`; How long to wait between scanning each row in us..
- `active-low`: Specify that the keypad is active low..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 74-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/ti,nspire-keypad.yaml -->
