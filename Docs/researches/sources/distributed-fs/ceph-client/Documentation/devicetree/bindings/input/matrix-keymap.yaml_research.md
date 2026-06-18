<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml` is a Linux devicetree YAML schema for a keypad binding: **Common Key Matrices on Matrix-connected Keyboards**. This common schema defines matrix keypad keymap encoding and row/column dimension properties that concrete keypad controller bindings reference. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: none.
- Maintainers: Olof Johansson <olof@lixom.net>.
- Top-level properties: `linux,keymap`, `keypad,num-rows`, `keypad,num-columns`.
- `linux,keymap`: ref `/schemas/types.yaml#/definitions/uint32-array`; An array of packed 1-cell entries containing the equivalent of row, column and linux key-code. The 32-bit big endian cell is packed as: row << 24 | column << 16 | key-code.
- `keypad,num-rows`: ref `/schemas/types.yaml#/definitions/uint32`; Number of row lines connected to the keypad controller..
- `keypad,num-columns`: ref `/schemas/types.yaml#/definitions/uint32`; Number of column lines connected to the keypad controller..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: True` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.

## Risks and Test Signals
- Primary risks: updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/matrix-keymap.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 48-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/matrix-keymap.yaml -->
