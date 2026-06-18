<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml` is a Linux devicetree YAML schema for a keypad binding: **ChromeOS EC Keyboard**. Google's ChromeOS EC Keyboard is a simple matrix keyboard implemented on a separate EC (Embedded Controller) device. It provides a message for reading key scans from the EC. These are then converted into keycodes for processing by the kernel. This device... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `google,cros-ec-keyb-switches`, `google,cros-ec-keyb`.
- Required top-level fields: `compatible`.
- Maintainers: Simon Glass <sjg@chromium.org>, Benson Leung <bleung@chromium.org>.
- Top-level properties: `compatible`, `google,needs-ghost-filter`, `function-row-physmap`.
- `compatible`.
- `google,needs-ghost-filter`: type `boolean`; Enable a ghost filter for the matrix keyboard. This is recommended if the EC does not have its own logic or hardware for this..
- `function-row-physmap`: ref `/schemas/types.yaml#/definitions/uint32-array`; maxItems 15; minItems 1; An ordered u32 array describing the rows/columns (in the scan matrix) of top row keys from physical left (KEY_F1) to right. Each entry encodes the row/column as: (((row) & 0xFF) << 24) | (((column) & 0xFF) << 16) where the lower 16 bits are reserved. This....
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `google,cros-ec-keyb`: require `keypad,num-rows`, `keypad,num-columns`, `linux,keymap` / constrain none
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 140-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/google,cros-ec-keyb.yaml -->
