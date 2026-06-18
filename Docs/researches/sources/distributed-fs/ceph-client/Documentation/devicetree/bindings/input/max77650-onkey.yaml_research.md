<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Onkey driver for MAX77650 PMIC from Maxim Integrated.**. This module is part of the MAX77650 MFD device. For more details see Documentation/devicetree/bindings/mfd/max77650.yaml. The onkey controller is represented as a sub-node of the PMIC node on the device tree. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `maxim,max77650-onkey`.
- Required top-level fields: `compatible`.
- Maintainers: Bartosz Golaszewski <bgolaszewski@baylibre.com>.
- Top-level properties: `compatible`, `linux,code`, `maxim,onkey-slide`.
- `compatible`: const `maxim,max77650-onkey`.
- `linux,code`.
- `maxim,onkey-slide`: ref `/schemas/types.yaml#/definitions/flag`; The system's button is a slide switch, not the default push button..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/flag`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/max77650-onkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 38-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/max77650-onkey.yaml -->
