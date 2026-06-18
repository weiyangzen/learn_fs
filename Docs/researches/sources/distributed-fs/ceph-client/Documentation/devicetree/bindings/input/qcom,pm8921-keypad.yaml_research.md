<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Qualcomm PM8921 PMIC KeyPad**. The file describes the devicetree contract for the Qualcomm PM8921 PMIC KeyPad. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8058-keypad`, `qcom,pm8921-keypad`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `linux,keymap`.
- Maintainers: Dmitry Baryshkov <dmitry.baryshkov@linaro.org>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `wakeup-source`, `linux,keypad-wakeup`, `debounce`, `scan-delay`, `row-hold`.
- `compatible`: enum `qcom,pm8058-keypad`, `qcom,pm8921-keypad`.
- `reg`: maxItems 1.
- `interrupts`.
- `wakeup-source`: type `boolean`; use any event on keypad as wakeup event.
- `linux,keypad-wakeup`: type `boolean`; legacy version of the wakeup-source property.
- `debounce`: ref `/schemas/types.yaml#/definitions/uint32`; Time in microseconds that key must be pressed or released for state change interrupt to trigger..
- `scan-delay`: ref `/schemas/types.yaml#/definitions/uint32`; time in microseconds to pause between successive scans of the matrix array.
- `row-hold`: ref `/schemas/types.yaml#/definitions/uint32`; time in nanoseconds to pause between scans of each row in the matrix array..
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 89-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8921-keypad.yaml -->
