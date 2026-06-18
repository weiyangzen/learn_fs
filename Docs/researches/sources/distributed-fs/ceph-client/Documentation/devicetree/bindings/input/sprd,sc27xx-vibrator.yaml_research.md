<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Spreadtrum SC27xx PMIC Vibrator**. The file describes the devicetree contract for the Spreadtrum SC27xx PMIC Vibrator. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, `sprd,sc2731-vibrator`.
- Required top-level fields: `compatible`, `reg`.
- Maintainers: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>.
- Top-level properties: `compatible`, `reg`.
- `compatible`: enum `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, `sprd,sc2731-vibrator`.
- `reg`: maxItems 1.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 31-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/sprd,sc27xx-vibrator.yaml -->
