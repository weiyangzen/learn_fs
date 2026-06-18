<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **FocalTech FT8112 touchscreen controller**. Supports the FocalTech FT8112 touchscreen controller. This touchscreen controller uses the i2c-hid protocol with a reset GPIO. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `focaltech,ft8112`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `vcc33-supply`.
- Maintainers: Daniel Peng <Daniel_Peng@pegatron.corp-partner.google.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- `compatible`: enum `focaltech,ft8112`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `panel`.
- `vcc33-supply`.
- `vccio-supply`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `panel`, `reset-gpios`, `vcc33-supply`, `vccio-supply`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/focaltech,ft8112.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 66-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/focaltech,ft8112.yaml -->
