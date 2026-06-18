<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Regulator Haptic**. The file describes the devicetree contract for the Regulator Haptic. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: none.
- Required top-level fields: `compatible`, `haptic-supply`, `max-microvolt`, `min-microvolt`.
- Maintainers: Jaewon Kim <jaewon02.kim@samsung.com>.
- Top-level properties: `compatible`, `haptic-supply`, `max-microvolt`, `min-microvolt`.
- `compatible`: const `regulator-haptic`.
- `haptic-supply`: Power supply to the haptic motor.
- `max-microvolt`: The maximum voltage value supplied to the haptic motor.
- `min-microvolt`: The minimum voltage value supplied to the haptic motor.
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `haptic-supply`.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/regulator-haptic.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`.
- Research note: this report was generated after reading the full 43-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/regulator-haptic.yaml -->
