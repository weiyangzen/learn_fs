<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Apple touchscreens attached using the Z2 protocol**. A series of touschscreen controllers used in Apple products It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `apple,j293-touchbar`, `apple,j493-touchbar`.
- Required top-level fields: `compatible`, `interrupts`, `reset-gpios`, `firmware-name`, `touchscreen-size-x`, `touchscreen-size-y`.
- Maintainers: Sasha Finkelstein <k@chaosmail.tech>.
- Top-level properties: `compatible`, `interrupts`, `reset-gpios`, `firmware-name`, `apple,z2-cal-blob`.
- `compatible`: enum `apple,j293-touchbar`, `apple,j493-touchbar`.
- `interrupts`: maxItems 1.
- `reset-gpios`: maxItems 1.
- `firmware-name`: maxItems 1.
- `apple,z2-cal-blob`: ref `/schemas/types.yaml#/definitions/uint8-array`; maxItems 4096; Calibration blob supplied by the bootloader.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen.yaml#`, `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint8-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `interrupts`, `reset-gpios`, `firmware-name`.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- Integrates with SPI peripheral validation; compatible-specific constraints must not conflict with SPI bus requirements.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 70-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/apple,z2-multitouch.yaml -->
