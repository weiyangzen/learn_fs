<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Pine64 PinePhone keyboard**. A keyboard accessory is available for the Pine64 PinePhone and PinePhone Pro. It connects via I2C, providing a raw scan matrix, a flashing interface, and a subordinate I2C bus for communication with a battery charger IC. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `pine64,pinephone-keyboard`.
- Required top-level fields: `compatible`, `reg`, `interrupts`.
- Maintainers: Samuel Holland <samuel@sholland.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `vbat-supply`, `wakeup-source`, `i2c`.
- `compatible`: const `pine64,pinephone-keyboard`.
- `reg`: const `21`.
- `interrupts`: maxItems 1.
- `wakeup-source`.
- `vbat-supply`: Supply for the keyboard MCU.
- `i2c`: ref `/schemas/i2c/i2c-controller.yaml#`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/i2c/i2c-controller.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `i2c` object node with required none and properties none
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `vbat-supply`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 66-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/pine64,pinephone-keyboard.yaml -->
